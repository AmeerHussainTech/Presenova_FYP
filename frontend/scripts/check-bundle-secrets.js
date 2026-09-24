/**
 * Pre-deploy Bundle Secret Scanner (AGENTS.md §2 Security Mandate)
 * Scans production build output in dist/ for leaked private keys, API secrets,
 * or credentials before any deployment.
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const distDir = path.resolve(__dirname, '../dist');

if (!fs.existsSync(distDir)) {
  console.log('[BUNDLE-SCAN] No dist/ directory found. Skipping scan.');
  process.exit(0);
}

// Patterns of secrets that must NEVER appear in the production client bundle
const SECRET_PATTERNS = [
  {
    name: 'Private Key PEM',
    regex: /-----BEGIN (?:RSA )?PRIVATE KEY-----/g,
  },
  {
    name: 'Google Service Account Credential',
    regex: /"private_key_id"|"client_email"\s*:\s*"[^"]+@.*\.iam\.gserviceaccount\.com"/g,
  },
  {
    name: 'OpenAI Secret Key',
    regex: /sk-[a-zA-Z0-9]{20,}/g,
  },
  {
    name: 'Groq API Key',
    regex: /gsk_[a-zA-Z0-9]{20,}/g,
  },
  {
    name: 'Exposed JWT Secret',
    regex: /(?:jwt_secret|jwt_secret_key)\s*[:=]\s*['"][^'"]{8,}['"]/gi,
  },
];

// Allowed public keys (Firebase Web SDK public client identifiers)
const allowedPublicKeys = new Set(
  [
    process.env.VITE_FIREBASE_API_KEY,
    'AIzaSyCyjQw9-oy4gulqi_2tYRllLLIqVXcedHU', // fyp-firebase-df1f6 dev key
    'AIzaSyBgcwJCx3_ajBXSe6fg2L4cDz1H2izjOqM', // fyp-firebase-df1f6 prod key
  ].filter(Boolean)
);

// Also dynamically read all .env* files to include any configured VITE_FIREBASE_API_KEY
const frontendDir = path.resolve(__dirname, '..');
for (const envFileName of fs.readdirSync(frontendDir)) {
  if (envFileName.startsWith('.env')) {
    try {
      const envContent = fs.readFileSync(path.join(frontendDir, envFileName), 'utf8');
      const match = envContent.match(/VITE_FIREBASE_API_KEY\s*=\s*([^\r\n]+)/);
      if (match && match[1]) {
        allowedPublicKeys.add(match[1].trim());
      }
    } catch {}
  }
}

function scanFile(filePath) {
  const content = fs.readFileSync(filePath, 'utf8');
  const violations = [];

  // Check generic secret patterns
  for (const pattern of SECRET_PATTERNS) {
    if (pattern.regex.test(content)) {
      violations.push(pattern.name);
    }
  }

  // Check for any Google API keys (AIza...) that are not the allowed public web key
  const aizaMatches = content.match(/AIza[0-9A-Za-z-_]{35}/g);
  if (aizaMatches) {
    for (const match of aizaMatches) {
      if (!allowedPublicKeys.has(match)) {
        violations.push(`Unwhitelisted Google/Gemini API Key: ${match.slice(0, 8)}...`);
      }
    }
  }

  return violations;
}

function walkDir(dir) {
  let files = [];
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      files = files.concat(walkDir(fullPath));
    } else if (/\.(js|mjs|html|json|css)$/i.test(entry.name)) {
      files.push(fullPath);
    }
  }
  return files;
}

const files = walkDir(distDir);
let totalViolations = 0;

for (const file of files) {
  const violations = scanFile(file);
  if (violations.length > 0) {
    console.error(`\x1b[31m[SECURITY ALERT] Secret detected in client bundle: ${file}\x1b[0m`);
    violations.forEach((v) => console.error(`  -> ${v}`));
    totalViolations += violations.length;
  }
}

if (totalViolations > 0) {
  console.error(`\x1b[31m\n[BUILD FAILED] ${totalViolations} secret violation(s) found in production bundle!\x1b[0m`);
  process.exit(1);
} else {
  console.log(`\x1b[32m[SECURITY AUDIT PASS] Scanned ${files.length} bundle files in dist/. Zero secret leaks found.\x1b[0m`);
  process.exit(0);
}
