import { PlaygroundLanguage, PlaygroundRunResponse } from '@/types/playground';

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

const buildSessionId = () =>
  (typeof crypto !== 'undefined' && crypto.randomUUID ? crypto.randomUUID() : `session-${Date.now()}`);

export interface ExecutionPayload {
  code: string;
  language: PlaygroundLanguage;
  sessionId?: string | null;
}

export const executeCodeSnippet = async (
  payload: ExecutionPayload
): Promise<PlaygroundRunResponse> => {
  await delay(400);

  const sessionId = payload.sessionId ?? buildSessionId();
  const executionTime = 0.42;
  const intro = `▶ Running ${payload.language} scenario (session ${sessionId.slice(0, 8)})`;

  return {
    sessionId,
    output: [intro, '... processing quantum-safe pipeline', 'T1-anchor: execution-handshake'],
    error: null,
    executionTime,
    status: 'success',
  };
};

export const sharePlaygroundSession = async (
  payload: ExecutionPayload
): Promise<string> => {
  await delay(200);
  const encoded = encodeURIComponent(payload.code.slice(0, 120));
  return `https://aurora.cloudbank/playground?lang=${payload.language}&seed=T1-share&code=${encoded}`;
};

export const savePlaygroundSession = async (
  payload: ExecutionPayload
): Promise<{ sessionId: string }> => {
  await delay(200);
  return { sessionId: payload.sessionId ?? buildSessionId() };
};

export const forkPlaygroundSession = async (
  payload: ExecutionPayload
): Promise<{ sessionId: string; parentId: string | null }> => {
  await delay(200);
  const parentId = payload.sessionId ?? buildSessionId();
  const forkedId = buildSessionId();
  return { sessionId: forkedId, parentId };
};
