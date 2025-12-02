import apiClient from '../lib/api/client';
import type {
  ExecuteRequest,
  ExecutionStatusResponse,
  SessionCreateRequest,
  SessionCreateResponse,
  ShareRequest,
  ShareResponse,
  StreamMessage,
} from '../types/playground';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const toWebSocketUrl = (url: string) => {
  if (url.startsWith('ws')) return url;
  return url.replace(/^http/, 'ws');
};

export const createPlaygroundSession = async (payload: SessionCreateRequest) =>
  apiClient.post<SessionCreateResponse>('/playground/session', payload);

export const executePlaygroundCode = async (payload: ExecuteRequest) =>
  apiClient.post<ExecutionStatusResponse>('/playground/execute', payload);

export const fetchExecutionResult = async (sessionId: string, taskId: string) =>
  apiClient.get<ExecutionStatusResponse>(`/playground/results/${sessionId}`, { params: { task_id: taskId } });

export const sharePlaygroundSession = async (payload: ShareRequest) =>
  apiClient.post<ShareResponse>('/playground/share', payload);

export const fetchSharedSnippet = async (shortCode: string) =>
  apiClient.get<ShareResponse | Record<string, unknown>>(`/playground/share/${shortCode}`);

export const connectPlaygroundStream = (sessionId: string): WebSocket => {
  const wsUrl = `${toWebSocketUrl(BASE_URL)}/playground/ws/${sessionId}`;
  return new WebSocket(wsUrl);
};

export type {
  ExecuteRequest,
  ExecutionStatusResponse,
  SessionCreateRequest,
  SessionCreateResponse,
  ShareRequest,
  ShareResponse,
  StreamMessage,
};
