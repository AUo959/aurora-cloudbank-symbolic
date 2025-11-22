/**
 * Aurora API Client
 * Type-safe API calls to Aurora backend
 */

import apiClient from './client';
import type {
  Memory,
  MemoryCreateRequest,
  MemoryRetrieveRequest,
  MemoryRetrieveResponse,
  QuantumSimulationRequest,
  QuantumSimulationResponse,
  AgentMessage,
  AgentResponse,
  ComplianceReport,
  AuditEvent,
  SystemMetrics,
} from '@/types/aurora';

export const auroraAPI = {
  // ===== AuMemManager =====
  memory: {
    create: (data: MemoryCreateRequest) =>
      apiClient.post<{ memory_id: string }>('/api/aumem/memory/create', data),

    retrieve: (data: MemoryRetrieveRequest) =>
      apiClient.post<MemoryRetrieveResponse>('/api/aumem/retrieve', data),

    get: (memoryId: string) =>
      apiClient.get<Memory>(`/api/aumem/memory/${memoryId}`),

    delete: (memoryId: string) =>
      apiClient.delete(`/api/aumem/memory/${memoryId}`),

    metrics: () =>
      apiClient.get<{
        total_memories: number;
        active_memories: number;
        compressed_memories: number;
        archived_memories: number;
        cache_hit_rate: number;
      }>('/api/aumem/metrics'),
  },

  // ===== Quantum Simulator =====
  quantum: {
    simulate: (data: QuantumSimulationRequest) =>
      apiClient.post<QuantumSimulationResponse>('/api/quantum/simulate', data),

    scenarios: () =>
      apiClient.get<string[]>('/api/quantum/scenarios'),

    backends: () =>
      apiClient.get<string[]>('/api/quantum/backends'),

    status: (simulationId: string) =>
      apiClient.get<{ status: string; progress: number }>(`/api/quantum/status/${simulationId}`),
  },

  // ===== AI Agent =====
  agent: {
    chat: (message: AgentMessage) =>
      apiClient.post<AgentResponse>('/api/agent/chat', message),

    stream: (message: AgentMessage) =>
      // For streaming, we'll use EventSource in a separate hook
      `/api/agent/stream`,
  },

  // ===== Compliance =====
  compliance: {
    audit: (params?: { start_date?: string; end_date?: string; limit?: number }) =>
      apiClient.get<AuditEvent[]>('/api/compliance/audit', { params }),

    report: (reportId: string) =>
      apiClient.get<ComplianceReport>(`/api/compliance/report/${reportId}`),

    generateReport: (params: { start_date: string; end_date: string }) =>
      apiClient.post<{ report_id: string }>('/api/compliance/generate-report', params),

    piiDetect: (text: string) =>
      apiClient.post<{ pii_found: boolean; redacted_text: string; entities: unknown[] }>(
        '/api/compliance/pii-detect',
        { text }
      ),
  },

  // ===== Orion Station (Multi-Agent) =====
  orion: {
    agents: () =>
      apiClient.get<unknown[]>('/api/orion/agents'),

    createAgent: (data: { name: string; role: string; specialization: string }) =>
      apiClient.post('/api/orion/agents', data),

    getAgent: (agentId: string) =>
      apiClient.get(`/api/orion/agents/${agentId}`),

    tasks: () =>
      apiClient.get<unknown[]>('/api/orion/tasks'),

    createTask: (data: { title: string; description: string; assigned_agents: string[] }) =>
      apiClient.post('/api/orion/tasks', data),

    experiments: () =>
      apiClient.get<unknown[]>('/api/orion/experiments'),

    runExperiment: (data: { name: string; parameters: unknown }) =>
      apiClient.post('/api/orion/experiments', data),
  },

  // ===== System Metrics =====
  system: {
    metrics: () =>
      apiClient.get<SystemMetrics>('/api/system/metrics'),

    health: () =>
      apiClient.get<{ status: string; components: Record<string, boolean> }>('/api/health'),
  },
};

export default auroraAPI;
