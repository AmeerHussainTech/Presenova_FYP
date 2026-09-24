/**
 * Gemini AI Service for Frontend
 * Direct connection to Google Gemini API (gemini-2.0-flash, gemini-1.5-flash)
 * for real-time presentation coaching, practice sessions, and defense prep.
 */

import { ChatMessage, ContextReport } from '../types';

const GEMINI_LOCAL_STORAGE_KEY = 'presenova_gemini_api_key';
const DEFAULT_MODEL = import.meta.env.VITE_GEMINI_MODEL || 'gemini-2.0-flash';
const FALLBACK_MODELS = ['gemini-2.0-flash', 'gemini-1.5-flash', 'gemini-2.5-flash'];

/**
 * Get active Gemini API Key (Priority: localStorage user override > VITE_GEMINI_API_KEY env)
 */
export const getStoredGeminiApiKey = (): string => {
  const localKey = localStorage.getItem(GEMINI_LOCAL_STORAGE_KEY);
  if (localKey && localKey.trim()) {
    return localKey.trim();
  }
  return '';
};

/**
 * Save user-provided Gemini API Key to localStorage
 */
export const setStoredGeminiApiKey = (key: string): void => {
  if (key && key.trim()) {
    localStorage.setItem(GEMINI_LOCAL_STORAGE_KEY, key.trim());
  } else {
    localStorage.removeItem(GEMINI_LOCAL_STORAGE_KEY);
  }
};

/**
 * Check if a Gemini API Key is configured
 */
export const hasGeminiApiKey = (): boolean => {
  return Boolean(getStoredGeminiApiKey());
};

/**
 * Build concise plain-text context from the user's presentation/speech analysis report
 */
const buildContextText = (context: ContextReport | null): string => {
  if (!context) return 'No prior analysis report provided.';

  const parts: string[] = [];
  const phase = context.phase || 'practice';
  parts.push(`Session Type: ${phase}`);

  const analysis: any =
    context.analysis ||
    context.v2Analysis ||
    context.v2Report ||
    context.v1Analysis ||
    context.v1Report;

  if (analysis && typeof analysis === 'object') {
    if (analysis.overall_score !== undefined) {
      parts.push(`Overall Score: ${analysis.overall_score}/100`);
    }
    if (analysis.strengths && Array.isArray(analysis.strengths) && analysis.strengths.length > 0) {
      parts.push(`Key Strengths: ${analysis.strengths.slice(0, 3).join('; ')}`);
    }
    if (analysis.recommendations && Array.isArray(analysis.recommendations) && analysis.recommendations.length > 0) {
      parts.push(`Key Recommendations: ${analysis.recommendations.slice(0, 3).join('; ')}`);
    }
    if (analysis.speech_speed_wpm) {
      parts.push(`Speaking Pace: ${analysis.speech_speed_wpm} WPM`);
    }
    if (analysis.filler_words_count !== undefined) {
      parts.push(`Filler Words Detected: ${analysis.filler_words_count}`);
    }
  }

  return parts.join('\n');
};

export interface GeminiCoachResult {
  ai_response: string;
  model: string;
  powered_by: 'gemini';
}

/**
 * Call Google Gemini REST API directly with multi-turn history and Presenova AI Coach system instruction
 */
export const callGeminiCoachApi = async (
  userMessage: string,
  history: ChatMessage[],
  contextReport: ContextReport | null,
  apiKeyOverride?: string
): Promise<GeminiCoachResult> => {
  const apiKey = (apiKeyOverride || getStoredGeminiApiKey()).trim();

  if (!apiKey) {
    throw new Error('Gemini API Key is missing. Please configure your Gemini API Key.');
  }

  const contextText = buildContextText(contextReport);

  const systemInstruction = `You are Presenova AI Coach, an elite AI Presentation, Defense, and Communication Coach for Presenova.
Your goal is to help the user master their presentation delivery, slide structure, voice pacing, body language, and Q&A defense.

Guidelines:
1. Tone: Professional, encouraging, sharp, and highly actionable.
2. Length: Concise and direct (strictly under 80 words / 2-4 sentences or 2-3 focused bullet points).
3. Context-Aware: Use any provided presentation context (scores, pacing WPM, strengths, recommendations) to tailor your advice.
4. Technical/Off-Topic Handling: If the user asks about technical or domain concepts (e.g. ethical hacking, AI architectures, engineering), give a sharp 1-2 sentence direct insight, then naturally connect it back to how to present or defend that topic effectively.
5. NEVER give repetitive canned greetings if the conversation is ongoing. Answer their prompt directly.`;

  // Filter and format previous turns for Gemini
  // Take last 8 turns to preserve tokens and response latency
  const recentHistory = history.slice(-8);
  const contents = [];

  for (const msg of recentHistory) {
    if (msg.role === 'user') {
      contents.push({
        role: 'user',
        parts: [{ text: msg.content }],
      });
    } else if (msg.role === 'ai') {
      contents.push({
        role: 'model',
        parts: [{ text: msg.content }],
      });
    }
  }

  // Append latest user message with analysis context if this is the first turn or relevant
  const messageWithContext =
    contents.length === 0 && contextText !== 'No prior analysis report provided.'
      ? `[Presentation Context:\n${contextText}]\n\nUser Question: ${userMessage}`
      : userMessage;

  contents.push({
    role: 'user',
    parts: [{ text: messageWithContext }],
  });

  const modelsToTry = [DEFAULT_MODEL, ...FALLBACK_MODELS.filter((m) => m !== DEFAULT_MODEL)];
  let lastError: Error | null = null;

  for (const model of modelsToTry) {
    try {
      const url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${encodeURIComponent(
        apiKey
      )}`;

      const payload = {
        contents,
        systemInstruction: {
          parts: [{ text: systemInstruction }],
        },
        generationConfig: {
          temperature: 0.7,
          maxOutputTokens: 350,
          topP: 0.9,
        },
      };

      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        const errMessage =
          errorData.error?.message || `HTTP ${response.status} ${response.statusText}`;

        // If quota or model not found, try next model in fallback chain
        if (response.status === 404 || response.status === 429) {
          lastError = new Error(`Model ${model}: ${errMessage}`);
          continue;
        }

        if (response.status === 400 && errMessage.includes('API_KEY_INVALID')) {
          throw new Error('Invalid Gemini API Key. Please check and re-enter your key.');
        }

        throw new Error(errMessage);
      }

      const data = await response.json();
      const candidate = data.candidates?.[0];
      const text = candidate?.content?.parts?.[0]?.text;

      if (!text || typeof text !== 'string') {
        throw new Error('Empty response received from Gemini.');
      }

      return {
        ai_response: text.trim(),
        model,
        powered_by: 'gemini',
      };
    } catch (err: any) {
      lastError = err instanceof Error ? err : new Error(String(err));
      // If it's an invalid key error, fail fast without trying other models
      if (lastError.message.includes('Invalid Gemini API Key')) {
        throw lastError;
      }
    }
  }

  throw lastError || new Error('Failed to generate response from Gemini API.');
};
