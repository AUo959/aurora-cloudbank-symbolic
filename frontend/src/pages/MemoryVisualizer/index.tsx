import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { ChevronRight, Database, ExternalLink, Info, Network, Search, Zap } from 'lucide-react';
import { Link } from 'react-router-dom';

// Sample data for onboarding preview
const SAMPLE_MEMORY_CLUSTERS = [
  { name: 'Agent Memories', count: 12500, color: 'from-primary-500 to-primary-400' },
  { name: 'Faction Knowledge', count: 8300, color: 'from-secondary-500 to-secondary-400' },
  { name: 'Station Records', count: 15200, color: 'from-accent-500 to-accent-400' },
  { name: 'Mission Logs', count: 9800, color: 'from-success to-green-400' },
  { name: 'Research Data', count: 10200, color: 'from-warning to-yellow-400' },
];

const QUICK_ACTIONS = [
  {
    title: 'Search Memories',
    description: 'Query the quantum memory network with semantic search',
    icon: Search,
    href: '/agent',
    available: true,
  },
  {
    title: 'View Statistics',
    description: 'Explore memory metrics and cache performance',
    icon: Database,
    href: '/',
    available: true,
  },
  {
    title: 'Interactive Playground',
    description: 'Execute code against the memory API directly',
    icon: Zap,
    href: '/playground',
    available: true,
  },
];

export default function MemoryVisualizer() {
  return (
    <div className="h-full overflow-auto p-8">
      <div className="mb-8">
        <h1 className="text-4xl font-display font-bold text-gradient">Memory Topology Visualizer</h1>
        <p className="mt-2 text-gray-400">3D visualization of quantum memory network</p>
      </div>

      {/* Main Visualization Card - Coming Soon with Progress */}
      <Card className="glass-morphism mb-8">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Network className="h-5 w-5 text-primary-500" aria-hidden="true" />
            <span>3D Memory Network</span>
            <span className="ml-2 text-xs bg-primary-500/20 text-primary-400 px-2 py-0.5 rounded-full">Coming Soon</span>
          </CardTitle>
          <CardDescription>Interactive React Three Fiber visualization in development</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex h-64 items-center justify-center border border-dashed border-white/20 rounded-lg bg-gradient-to-br from-primary-500/5 to-secondary-500/5">
            <div className="text-center">
              <Network className="mx-auto h-16 w-16 text-primary-500/50 animate-pulse" aria-hidden="true" />
              <p className="mt-4 text-gray-400 font-medium">
                3D Memory Topology Visualizer
              </p>
              <p className="mt-2 text-sm text-gray-500">
                React Three Fiber • 56K+ memory nodes • Quantum entanglement links
              </p>
              <div className="mt-4 flex items-center justify-center space-x-2 text-xs text-gray-500">
                <span className="flex items-center space-x-1">
                  <div className="h-2 w-2 rounded-full bg-success animate-pulse" />
                  <span>Backend Ready</span>
                </span>
                <span>•</span>
                <span className="flex items-center space-x-1">
                  <div className="h-2 w-2 rounded-full bg-yellow-500" />
                  <span>Frontend In Progress</span>
                </span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Memory Cluster Preview */}
        <Card className="glass-morphism">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2 text-base">
              <Database className="h-4 w-4 text-accent-500" aria-hidden="true" />
              <span>Memory Clusters</span>
            </CardTitle>
            <CardDescription>Current distribution of quantum memory types</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {SAMPLE_MEMORY_CLUSTERS.map((cluster) => (
                <div key={cluster.name} className="space-y-1">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-400">{cluster.name}</span>
                    <span className="font-mono text-gray-300">{cluster.count.toLocaleString()}</span>
                  </div>
                  <div className="h-2 w-full overflow-hidden rounded-full bg-gray-700">
                    <div
                      className={`h-full bg-gradient-to-r ${cluster.color} transition-all`}
                      style={{ width: `${(cluster.count / 56000) * 100}%` }}
                    />
                  </div>
                </div>
              ))}
              <div className="pt-2 border-t border-white/10 mt-4">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-500">Total Capacity</span>
                  <span className="font-mono text-primary-400">56,000+</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Card className="glass-morphism">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2 text-base">
              <Zap className="h-4 w-4 text-warning" aria-hidden="true" />
              <span>Explore Memory Data</span>
            </CardTitle>
            <CardDescription>Alternative ways to interact with the memory network</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {QUICK_ACTIONS.map((action) => {
                const Icon = action.icon;
                return (
                  <Link
                    key={action.title}
                    to={action.href}
                    className="flex items-center justify-between p-3 rounded-lg border border-white/10 bg-white/5 hover:bg-white/10 hover:border-primary-500/30 transition-all group"
                  >
                    <div className="flex items-center space-x-3">
                      <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary-500/20">
                        <Icon className="h-5 w-5 text-primary-400" aria-hidden="true" />
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-200 group-hover:text-white">
                          {action.title}
                        </p>
                        <p className="text-xs text-gray-500">{action.description}</p>
                      </div>
                    </div>
                    <ChevronRight className="h-4 w-4 text-gray-500 group-hover:text-primary-400 transition-colors" aria-hidden="true" />
                  </Link>
                );
              })}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* API Documentation Link */}
      <div className="mt-6 p-4 rounded-lg border border-white/10 bg-white/5">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Info className="h-5 w-5 text-gray-400" aria-hidden="true" />
            <div>
              <p className="text-sm text-gray-300">Looking to integrate with the Memory API?</p>
              <p className="text-xs text-gray-500">Full documentation available for AuMemManager quantum memory system</p>
            </div>
          </div>
          <Link to="/playground">
            <Button variant="outline" size="sm">
              <ExternalLink className="h-4 w-4 mr-2" aria-hidden="true" />
              Try Playground
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
}
