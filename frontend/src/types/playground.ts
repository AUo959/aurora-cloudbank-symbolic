export type PlaygroundLanguage = 'python' | 'javascript';
export type PlaygroundTheme = 'light' | 'dark';

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
