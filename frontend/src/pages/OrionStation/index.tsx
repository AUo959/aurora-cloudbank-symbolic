import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Rocket, Info } from 'lucide-react';

export default function OrionStation() {
  return (
    <div className="h-full p-8">
      <div className="mb-8">
        <h1 className="text-4xl font-display font-bold text-gradient">Orion Station</h1>
        <p className="mt-2 text-gray-400">Multi-agent research hub with autonomous AI agents</p>
      </div>

      <Card className="glass-morphism">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Rocket className="h-5 w-5 text-secondary-500" />
            <span>Research Hub</span>
          </CardTitle>
          <CardDescription>Multi-agent collaboration platform coming soon</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex h-96 items-center justify-center border border-dashed border-white/20 rounded-lg">
            <div className="text-center">
              <Info className="mx-auto h-12 w-12 text-gray-500" />
              <p className="mt-4 text-gray-400">
                Orion Station - Multi-Agent Research Hub
              </p>
              <p className="mt-2 text-sm text-gray-500">
                Agent fleet • Research tasks • Autonomous experiments • Collaboration graph
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
