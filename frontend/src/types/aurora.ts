/**
 * Aurora CloudBank Symbolic - TypeScript Type Definitions
 * Complete type safety for all Aurora features
 */

// ===== Memory Types =====
export interface Memory {
  id: string;
  content: Record<string, unknown>;
  memory_type: 'agent' | 'system' | 'user';
  importance: number;
  quantum_properties?: {
    magnitude?: number;
    phase?: number;
    entangled_with?: string[];
  };
  tags: string[];
  created_at: string;
  accessed_count: number;
  last_accessed?: string;
}

export interface MemoryCreateRequest {
  content: Record<string, unknown>;
  memory_type?: 'agent' | 'system' | 'user';
  importance: number;
  quantum_properties?: {
    magnitude?: number;
    phase?: number;
  };
  tags?: string[];
  context_tag?: string;
}

export interface MemoryRetrieveRequest {
  query: string;
  top_k?: number;
  memory_type?: 'agent' | 'system' | 'user';
  min_importance?: number;
  tags?: string[];
}

export interface MemoryRetrieveResponse {
  memories: Array<{
    memory: Memory;
    relevance_score: number;
    distance: number;
  }>;
  query_time_ms: number;
  total_searched: number;
}

// ===== Quantum Types =====
export type QuantumScenarioType =
  | 'supply_chain'
  | 'energy_grid'
  | 'risk_analysis'
  | 'molecular_simulation'
  | 'portfolio_optimization'
  | 'cryptography'
  | 'general_optimization';

export type QuantumBackend = 'aws_braket' | 'azure_quantum' | 'ibm_quantum' | 'google_cirq' | 'simulator';

export interface QuantumSimulationRequest {
  scenario_type: QuantumScenarioType;
  parameters: Record<string, unknown>;
  backend?: QuantumBackend;
  num_qubits?: number;
}

export interface QuantumSimulationResponse {
  simulation_id: string;
  status: 'queued' | 'running' | 'completed' | 'failed';
  result?: {
    optimal_solution: unknown;
    objective_value: number;
    quantum_cost: number;
    classical_cost?: number;
    speedup_factor?: number;
    convergence_data?: unknown[];
  };
  performance_metrics: {
    execution_time_ms: number;
    backend_queue_time_ms?: number;
    speedup_factor?: number;
  };
  error?: string;
}

// ===== AI Agent Types =====
export interface AgentMessage {
  content: string;
  role?: 'user' | 'assistant' | 'system';
  context?: Record<string, unknown>;
  use_memory?: boolean;
  memory_query?: string;
}

export interface AgentResponse {
  response: string;
  model_used: 'claude-3.5-sonnet' | 'claude-4.5-opus' | 'gpt-4o' | 'gpt-5';
  memory_retrieval?: {
    memories_retrieved: number;
    relevant_memories: Memory[];
    retrieval_time_ms: number;
  };
  ethics_score?: {
    alignment_score: number;
    transparency_level: 'low' | 'medium' | 'high';
    safety_score: number;
  };
  drift_detected?: boolean;
  generation_time_ms: number;
  token_usage?: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
}

// ===== Compliance Types =====
export interface AuditEvent {
  id: string;
  timestamp: string;
  event_type: string;
  user_id?: string;
  resource_type: string;
  resource_id: string;
  action: string;
  context_tag: string;
  symbolic_hash: string;
  metadata?: Record<string, unknown>;
}

export interface ComplianceReport {
  id: string;
  generated_at: string;
  period_start: string;
  period_end: string;
  total_events: number;
  pii_detections: number;
  ethics_violations: number;
  drift_incidents: number;
  compliance_score: number;
  events: AuditEvent[];
}

// ===== Orion Station Types =====
export interface OrionAgent {
  id: string;
  name: string;
  role: string;
  specialization: string;
  status: 'idle' | 'working' | 'blocked' | 'offline';
  current_task?: string;
  completed_tasks: number;
  created_at: string;
  last_active?: string;
}

export interface ResearchTask {
  id: string;
  title: string;
  description: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  assigned_agents: string[];
  created_at: string;
  started_at?: string;
  completed_at?: string;
  results?: unknown;
}

export interface Experiment {
  id: string;
  name: string;
  status: 'initializing' | 'running' | 'completed' | 'failed';
  parameters: Record<string, unknown>;
  started_at: string;
  completed_at?: string;
  results?: {
    data: unknown;
    metrics: Record<string, number>;
    insights: string[];
  };
  progress?: number;
}

// ===== System Metrics Types =====
export interface SystemMetrics {
  timestamp: string;
  memory: {
    total_memories: number;
    active_memories: number;
    compressed_memories: number;
    archived_memories: number;
    cache_hit_rate: number;
  };
  quantum: {
    simulations_running: number;
    total_simulations: number;
    average_speedup: number;
  };
  agents: {
    total_agents: number;
    active_agents: number;
    total_tasks: number;
    completed_tasks: number;
  };
  system: {
    cpu_usage: number;
    memory_usage: number;
    api_requests_per_minute: number;
    average_response_time_ms: number;
  };
}

// ===== WebSocket Message Types =====
export interface WebSocketMessage {
  type: 'agent_message' | 'memory_update' | 'simulation_update' | 'system_alert' | 'agent_status';
  data: unknown;
  timestamp: string;
}

// ===== UI Component Types =====
export interface Toast {
  id: string;
  title: string;
  description?: string;
  type: 'success' | 'error' | 'warning' | 'info';
  duration?: number;
}

export interface ChartDataPoint {
  timestamp: string;
  value: number;
  label?: string;
}

// ===== Simulation Types =====
export type SimulationType =
  | 'institutional_behavior'
  | 'colony_dynamics'
  | 'social_system'
  | 'astronomical'
  | 'genomic'
  | 'custom';

export interface Simulation {
  id: string;
  name: string;
  type: SimulationType;
  description: string;
  status: 'draft' | 'running' | 'paused' | 'completed' | 'failed';
  parameters: Record<string, unknown>;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  progress?: number;
  results?: unknown;
}

export interface SimulationAgent {
  id: string;
  type: string;
  position?: { x: number; y: number; z?: number };
  state: Record<string, unknown>;
  interactions: number;
}

export interface SimulationEnvironment {
  dimensions: 2 | 3;
  bounds: { x: [number, number]; y: [number, number]; z?: [number, number] };
  rules: Record<string, unknown>;
  constraints: Record<string, unknown>;
}

// ===== Developer Playground Types =====
export interface APIEndpoint {
  path: string;
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  description: string;
  parameters?: Record<string, { type: string; required: boolean; description: string }>;
  requestBody?: Record<string, unknown>;
  responseExample?: Record<string, unknown>;
}

export interface CodeExample {
  id: string;
  title: string;
  description: string;
  language: 'python' | 'javascript' | 'curl';
  code: string;
  category: 'memory' | 'quantum' | 'agent' | 'compliance' | 'orion';
}
