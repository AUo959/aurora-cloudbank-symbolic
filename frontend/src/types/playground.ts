export type PlaygroundLanguage = 'python' | 'javascript';
export type PlaygroundTheme = 'light' | 'dark';

// ---------------------------------------------------------------------------
// Playground API contract
//
// src/services/playground.ts imported these seven types, but they were never
// defined here — 7 of the 15 TypeScript errors that made `npm run build` fail.
// Each mirrors the Pydantic model of the same name in src/playground/models.py,
// which is the authoritative contract; field names are the wire names (snake
// case) rather than camelCase for that reason. PlaygroundLanguage already
// matches the backend's ExecutionLanguage enum exactly.
// ---------------------------------------------------------------------------

/** POST /playground/session */
export interface SessionCreateRequest {
  language: PlaygroundLanguage;
  /** Optional starter snippet. */
  seed_code?: string | null;
  metadata?: Record<string, unknown>;
}

export interface SessionCreateResponse {
  session_id: string;
  /** Unix timestamp (seconds). */
  expires_at: number;
}

/** POST /playground/execute */
export interface ExecuteRequest {
  /** Existing session identifier; omitted to start a new one. */
  session_id?: string | null;
  code: string;
  language: PlaygroundLanguage;
  stdin?: string | null;
}

export interface ExecutionResult {
  task_id: string;
  session_id: string;
  status: string;
  output: string;
  errors: string[];
  /** Unix timestamps (seconds). */
  started_at: number;
  completed_at?: number | null;
  duration_ms?: number | null;
  /** Present when PII redaction rewrote the output. */
  redacted_output?: string | null;
  metadata?: Record<string, unknown>;
}

/** Returned by POST /playground/execute and GET /playground/results/{id}. */
export interface ExecutionStatusResponse {
  task_id: string;
  session_id: string;
  status: string;
  /** Absent while the task is still queued or running. */
  result?: ExecutionResult | null;
}

/** POST /playground/share */
export interface ShareRequest {
  session_id: string;
  code: string;
  language: PlaygroundLanguage;
}

export interface ShareResponse {
  short_code: string;
  session_id: string;
  url: string;
  embed_html: string;
}

/** Frames pushed over GET /playground/ws/{session_id}. */
export interface StreamMessage {
  event: string;
  session_id: string;
  task_id?: string | null;
  payload?: Record<string, unknown>;
}

export interface PlaygroundExample {
  id: string;
  title: string;
  description: string;
  language: PlaygroundLanguage;
  code: string;
  tags: string[];
}

export interface PlaygroundRunResponse {
  sessionId: string;
  output: string[];
  error: string | null;
  executionTime: number;
  status: 'success' | 'error' | 'timeout';
}

export interface PlaygroundState {
  code: string;
  language: PlaygroundLanguage;
  theme: PlaygroundTheme;
  fontSize: number;
  output: string[];
  error: string | null;
  sessionId: string | null;
  shareUrl: string | null;
  selectedExampleId: string;
  isExecuting: boolean;
  lastRunAt: string | null;
}
