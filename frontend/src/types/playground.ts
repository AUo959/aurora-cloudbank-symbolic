export type ExecutionLanguage = 'python' | 'javascript';

export interface SessionCreateRequest {
  language: ExecutionLanguage;
  seed_code?: string;
  metadata?: Record<string, unknown>;
}

export interface SessionCreateResponse {
  session_id: string;
  expires_at: number;
}

export interface ExecuteRequest {
  session_id?: string;
  code: string;
  language: ExecutionLanguage;
  stdin?: string;
}

export interface ExecutionResult {
  task_id: string;
  session_id: string;
  status: string;
  output: string;
  redacted_output?: string;
  errors: string[];
  duration_ms?: number;
}

export interface ExecutionStatusResponse {
  task_id: string;
  session_id: string;
  status: string;
  result?: ExecutionResult;
}

export interface ShareRequest {
  session_id: string;
  code: string;
  language: ExecutionLanguage;
}

export interface ShareResponse {
  short_code: string;
  session_id: string;
  url: string;
  embed_html: string;
}

export interface StreamMessage {
  event: string;
  session_id: string;
  task_id?: string;
  payload: Record<string, unknown>;
}
