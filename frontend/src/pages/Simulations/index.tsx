import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Sparkles, Info } from 'lucide-react';

export default function Simulations() {
  return (
    <div className="h-full p-8">
      <div className="mb-8">
        <h1 className="text-4xl font-display font-bold text-gradient">Complex System Simulations</h1>
        <p className="mt-2 text-gray-400">
          Model institutional behavior, colony dynamics, social systems, and more
        </p>
      </div>

      <Card className="glass-morphism">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Sparkles className="h-5 w-5 text-primary-500" />
            <span>Simulation Manager</span>
          </CardTitle>
          <CardDescription>High-fidelity complex systems simulation coming soon</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex h-96 items-center justify-center border border-dashed border-white/20 rounded-lg">
            <div className="text-center">
              <Info className="mx-auto h-12 w-12 text-gray-500" />
              <p className="mt-4 text-gray-400">
                Complex System Simulations
              </p>
              <p className="mt-2 text-sm text-gray-500">
                Institutional behavior • Colony dynamics • Social systems • Astronomical phenomena •
                Genomics
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
