# Antigravity — Project Cleanup & Compression Instructions

## Role
You are acting as a senior codebase auditor. Your job on this task is NOT to add features. Your job is to make the existing project as lean, correct, and maintainable as possible without changing its behavior for the end user.

## Primary Objective
Do a full, file-by-file analysis of the entire project (every module, folder, and file — not just the files that look "important") and:
1. Identify and remove all dead, unused, duplicate, or unreachable code.
2. Keep only the code that is actually required for the app to function correctly.
3. Reduce overall project size/weight (bundle size, file count, dependency count, asset size) as much as safely possible.
4. Where you see a cleaner or more efficient way to implement something already in the project, refactor it — but only if it does not change existing behavior/output.

## Step-by-Step Process (follow in order)

### 1. Full Project Scan
- Walk the entire directory tree. Build a mental (or written) map of: entry points, routes/pages, components, services, models, utils, config files, assets, and dependencies.
- Note the tech stack and framework conventions before making changes (don't assume — check package.json / composer.json / requirements.txt / etc.).

### 2. Dead Code Detection
Flag and remove:
- Unused functions, classes, components, variables, and imports.
- Unused exported modules that nothing imports anywhere in the project.
- Commented-out code blocks left behind (unless clearly marked as intentional/TODO with a reason).
- Duplicate implementations of the same logic (merge into one shared version).
- Old/legacy files replaced by newer versions but never deleted.
- Unused routes, API endpoints, database migrations/tables no longer referenced.
- Unused CSS classes, unused images/fonts/icons, unused environment variables.
- Debug/console logs, test/demo code, and placeholder files not part of the real app.
- Unused npm/composer/pip packages in dependency files — remove from package manager files too, not just code.

### 3. Verification Before Deleting (mandatory — do not skip)
- Before removing anything, search the ENTIRE project for references to it (not just the same folder). Check dynamic imports, string-based references, and config-driven usage too.
- If something is used in only one obscure place and you're not 100% sure, do not delete blindly — flag it in your summary instead of removing it silently.
- Never remove code tied to payment, authentication, security, or data integrity without explicit confirmation — flag these separately for manual review even if they look unused.

### 4. Compression & Size Reduction
- Merge duplicate logic into shared utils/helpers.
- Remove unused dependencies and dev-dependencies.
- Minify/optimize large static assets if the project doesn't already do this in a build step.
- Simplify overly complex code paths (deeply nested conditionals, redundant abstractions, unnecessary wrapper functions) as long as output stays identical.
- Split or lazy-load heavy modules only if that's a safe, established pattern in this stack — don't introduce risky architecture changes.
- Remove unused config options, unused environment files, and stale build artifacts from the repo.

### 5. Enhancements (only after cleanup is done)
Once the project is clean, you may proactively suggest/apply small, safe improvements:
- Better naming, consistent formatting, consistent file structure.
- Replacing inefficient patterns with more performant equivalents (e.g., N+1 queries, redundant re-renders, unnecessary loops).
- Adding basic error handling where it's clearly missing and risky.
- Do NOT introduce new frameworks, major architectural changes, or new dependencies without asking first.

### 6. Final Report (always produce this)
At the end, give a clear summary with:
- Total files/lines removed and approximate size reduction.
- List of what was removed and why (grouped by type: dead code, unused deps, duplicate logic, unused assets, etc.).
- List of anything you were unsure about and left in place (flagged for manual review).
- Any enhancement you applied, explained in one line each.
- Confirmation that the app still builds/runs the same as before (or what you couldn't verify).

## Hard Rules
- Never change how the app behaves or looks to the end user.
- Never delete anything you're not sure is unused — flag instead of guessing.
- Never touch payment/auth/security-related code without flagging it first.
- Always check the full project for references before deleting anything.
- Keep changes minimal and functional — no rewrites for the sake of "style" unless asked.
- If the project has a build/test command, run it after cleanup to confirm nothing broke.
