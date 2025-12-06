import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { auroraAPI } from '@/lib/api/aurora';
import { formatDuration, formatNumber, percentage } from '@/lib/utils';
import { useQuery } from '@tanstack/react-query';
import {
  Activity,
  AlertCircle,
  Brain,
  CheckCircle2,
  Clock,
  Cpu,
  Database,
  FileText,
  Play,
  RefreshCw,
  Search,
  TrendingUp,
  WifiOff,
  Zap,
} from 'lucide-react';
import { Component, ErrorInfo, ReactNode } from 'react';
import { Link } from 'react-router-dom';

// Error Boundary Component for resilient rendering
interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

class DashboardErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Dashboard Error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <Card className="glass-morphism border-red-500/30">
          <CardContent className="flex flex-col items-center justify-center py-8">
            <AlertCircle className="h-12 w-12 text-red-500 mb-4" aria-hidden="true" />
            <p className="text-gray-400 text-center">Something went wrong loading this section.</p>
            <Button
              variant="outline"
              size="sm"
              className="mt-4"
              onClick={() => this.setState({ hasError: false, error: null })}
            >
              <RefreshCw className="mr-2 h-4 w-4" aria-hidden="true" />
              Try Again
            </Button>
          </CardContent>
        </Card>
      );
    }
    return this.props.children;
  }
}

// Stale data indicator component
interface DataFreshnessProps {
  dataUpdatedAt: number | undefined;
  isStale: boolean;
  isError: boolean;
  refetch: () => void;
}

function DataFreshnessIndicator({ dataUpdatedAt, isStale, isError, refetch }: DataFreshnessProps) {
  if (isError) {
    return (
      <div className="flex items-center space-x-2 text-xs text-red-400" role="status" aria-live="polite">
        <WifiOff className="h-3 w-3" aria-hidden="true" />
        <span>Connection lost</span>
        <Button variant="ghost" size="sm" className="h-6 px-2 text-xs" onClick={() => refetch()}>
          <RefreshCw className="h-3 w-3 mr-1" aria-hidden="true" />
          Retry
        </Button>
      </div>
    );
  }

  if (isStale) {
    return (
      <div className="flex items-center space-x-2 text-xs text-yellow-400" role="status" aria-live="polite">
        <Clock className="h-3 w-3" aria-hidden="true" />
        <span>Data may be stale</span>
        <Button variant="ghost" size="sm" className="h-6 px-2 text-xs" onClick={() => refetch()}>
          <RefreshCw className="h-3 w-3 mr-1" aria-hidden="true" />
          Refresh
        </Button>
      </div>
    );
  }

  if (dataUpdatedAt) {
    const secondsAgo = Math.floor((Date.now() - dataUpdatedAt) / 1000);
    return (
      <div className="flex items-center space-x-1 text-xs text-gray-500" role="status">
        <Clock className="h-3 w-3" aria-hidden="true" />
        <span>Updated {secondsAgo}s ago</span>
      </div>
    );
  }

  return null;
}

export default function Dashboard() {
  // Fetch system metrics with error handling
  const {
    data: metrics,
    isLoading: metricsLoading,
    isError: metricsError,
    isStale: metricsStale,
    dataUpdatedAt: metricsUpdatedAt,
    refetch: refetchMetrics,
  } = useQuery({
    queryKey: ['system-metrics'],
    queryFn: () => auroraAPI.system.metrics(),
    refetchInterval: 5000, // Refresh every 5 seconds
    staleTime: 10000, // Consider stale after 10 seconds
    retry: 3,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });

  // Fetch memory metrics with error handling
  const {
    data: memoryMetrics,
    isError: memoryError,
    isStale: memoryStale,
    dataUpdatedAt: memoryUpdatedAt,
    refetch: refetchMemory,
  } = useQuery({
    queryKey: ['memory-metrics'],
    queryFn: () => auroraAPI.memory.metrics(),
    refetchInterval: 5000,
    staleTime: 10000,
    retry: 3,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });

  const isLoading = metricsLoading;
  const hasAnyError = metricsError || memoryError;

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center" role="status" aria-live="polite">
        <div className="text-center">
          <Activity className="mx-auto h-12 w-12 animate-pulse text-primary-500" aria-hidden="true" />
          <p className="mt-4 text-gray-400">Loading system metrics...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full overflow-auto p-8">
      {/* Header with data freshness */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-display font-bold text-gradient">Aurora Dashboard</h1>
            <p className="mt-2 text-gray-400">Complex Systems Simulation Platform</p>
          </div>
          <div className="flex flex-col items-end space-y-1">
            <DataFreshnessIndicator
              dataUpdatedAt={metricsUpdatedAt}
              isStale={metricsStale}
              isError={metricsError}
              refetch={refetchMetrics}
            />
            {hasAnyError && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  refetchMetrics();
                  refetchMemory();
                }}
                className="text-xs"
              >
                <RefreshCw className="mr-2 h-3 w-3" aria-hidden="true" />
                Refresh All
              </Button>
            )}
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <DashboardErrorBoundary>
        <div className="mb-8 grid grid-cols-1 gap-4 md:grid-cols-3">
          <Link to="/simulations">
            <Card className="cursor-pointer transition-all hover:border-primary-500/50 hover:shadow-lg hover:quantum-glow">
              <CardHeader className="flex flex-row items-center space-x-4 pb-2">
                <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary-500/20">
                  <Play className="h-6 w-6 text-primary-400" />
                </div>
                <div>
                  <CardTitle className="text-base">Start Simulation</CardTitle>
                  <CardDescription>Run complex system simulation</CardDescription>
                </div>
              </CardHeader>
            </Card>
          </Link>

          <Link to="/memory">
            <Card className="cursor-pointer transition-all hover:border-accent-500/50 hover:shadow-lg">
              <CardHeader className="flex flex-row items-center space-x-4 pb-2">
                <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-accent-500/20">
                  <Search className="h-6 w-6 text-accent-400" />
                </div>
                <div>
                  <CardTitle className="text-base">Query Memory</CardTitle>
                  <CardDescription>Search quantum memory network</CardDescription>
                </div>
              </CardHeader>
            </Card>
          </Link>

          <Link to="/compliance">
            <Card className="cursor-pointer transition-all hover:border-secondary-500/50 hover:shadow-lg hover:neural-glow">
              <CardHeader className="flex flex-row items-center space-x-4 pb-2">
                <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-secondary-500/20">
                  <FileText className="h-6 w-6 text-secondary-400" />
                </div>
                <div>
                  <CardTitle className="text-base">Compliance Report</CardTitle>
                  <CardDescription>Generate audit trail report</CardDescription>
                </div>
              </CardHeader>
            </Card>
          </Link>
        </div>
      </DashboardErrorBoundary>

      {/* Metrics Grid */}
      <DashboardErrorBoundary>
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
          {/* Memory Metrics */}
          <Card className="glass-morphism">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Quantum Memory</CardTitle>
              <Database className="h-4 w-4 text-primary-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-gradient">
                {memoryMetrics ? formatNumber(memoryMetrics.total_memories) : '0'}
              </div>
              <p className="text-xs text-gray-500">
                {memoryMetrics && (
                  <>
                    {formatNumber(memoryMetrics.active_memories)} active •{' '}
                    {percentage(memoryMetrics.cache_hit_rate, 1).toFixed(0)}% cache hit
                  </>
                )}
              </p>
              <div className="mt-4 h-2 w-full overflow-hidden rounded-full bg-gray-700">
                <div
                  className="h-full bg-gradient-to-r from-primary-500 to-accent-500 transition-all"
                  style={{
                    width: memoryMetrics
                      ? `${percentage(memoryMetrics.active_memories, memoryMetrics.total_memories)}%`
                      : '0%',
                  }}
                />
              </div>
            </CardContent>
          </Card>

          {/* Quantum Simulations */}
          <Card className="glass-morphism">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Quantum Sims</CardTitle>
              <Cpu className="h-4 w-4 text-accent-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-gradient">
                {metrics?.quantum.total_simulations || 0}
              </div>
              <p className="text-xs text-gray-500">
                {metrics?.quantum.simulations_running || 0} running •{' '}
                {metrics?.quantum.average_speedup?.toFixed(1) || '0'}x speedup
              </p>
            </CardContent>
          </Card>

          {/* AI Agents */}
          <Card className="glass-morphism">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">AI Agents</CardTitle>
              <Brain className="h-4 w-4 text-secondary-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-gradient">
                {metrics?.agents.total_agents || 0}
              </div>
              <p className="text-xs text-gray-500">
                {metrics?.agents.active_agents || 0} active •{' '}
                {metrics?.agents.completed_tasks || 0} tasks done
              </p>
            </CardContent>
          </Card>

          {/* System Health */}
          <Card className="glass-morphism">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">System Health</CardTitle>
              <Activity className="h-4 w-4 text-success" />
            </CardHeader>
            <CardContent>
              <div className="flex items-center space-x-2">
                <CheckCircle2 className="h-5 w-5 text-success" />
                <span className="text-2xl font-bold text-success">Optimal</span>
              </div>
              <p className="text-xs text-gray-500">
                CPU: {metrics?.system.cpu_usage?.toFixed(0) || 0}% • Mem:{' '}
                {metrics?.system.memory_usage?.toFixed(0) || 0}%
              </p>
            </CardContent>
          </Card>
        </div>
      </DashboardErrorBoundary>

      {/* Performance Charts */}
      <DashboardErrorBoundary>
        <div className="mt-8 grid grid-cols-1 gap-6 lg:grid-cols-2">
          {/* API Performance */}
          <Card className="glass-morphism">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <TrendingUp className="h-5 w-5 text-primary-500" />
                <span>API Performance</span>
              </CardTitle>
              <CardDescription>Real-time request metrics</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-400">Requests/min</span>
                    <span className="font-mono font-semibold text-primary-400">
                      {metrics?.system.api_requests_per_minute || 0}
                    </span>
                  </div>
                </div>
                <div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-400">Avg Response Time</span>
                    <span className="font-mono font-semibold text-accent-400">
                      {formatDuration(metrics?.system.average_response_time_ms || 0)}
                    </span>
                  </div>
                </div>
                <div className="pt-4">
                  <Link to="/playground">
                    <Button variant="outline" className="w-full">
                      <Zap className="mr-2 h-4 w-4" />
                      Test API
                    </Button>
                  </Link>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Recent Activity */}
          <Card className="glass-morphism">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Activity className="h-5 w-5 text-secondary-500" />
                <span>Recent Activity</span>
              </CardTitle>
              <CardDescription>Latest system events</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <ActivityItem
                  icon={<CheckCircle2 className="h-4 w-4 text-success" />}
                  text="Quantum simulation completed"
                  time="2 minutes ago"
                />
                <ActivityItem
                  icon={<Database className="h-4 w-4 text-primary-500" />}
                  text="Memory network synchronized"
                  time="5 minutes ago"
                />
                <ActivityItem
                  icon={<Brain className="h-4 w-4 text-secondary-500" />}
                  text="AI agent task completed"
                  time="8 minutes ago"
                />
                <ActivityItem
                  icon={<AlertCircle className="h-4 w-4 text-warning" />}
                  text="Compliance check passed"
                  time="12 minutes ago"
                />
              </div>
            </CardContent>
          </Card>
        </div>
      </DashboardErrorBoundary>
    </div>
  );
}

interface ActivityItemProps {
  icon: React.ReactNode;
  text: string;
  time: string;
}

function ActivityItem({ icon, text, time }: ActivityItemProps) {
  return (
    <div className="flex items-start space-x-3">
      <div className="mt-0.5">{icon}</div>
      <div className="flex-1 space-y-0.5">
        <p className="text-sm text-gray-300">{text}</p>
        <p className="text-xs text-gray-500">{time}</p>
      </div>
    </div>
  );
}
