import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Code2, Info } from 'lucide-react';

export default function Playground() {
  return (
    <div className="h-full p-8">
      <div className="mb-8">
        <h1 className="text-4xl font-display font-bold text-gradient">Developer Playground</h1>
        <p className="mt-2 text-gray-400">Interactive API exploration and code generation</p>
      </div>

      <Card className="glass-morphism">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Code2 className="h-5 w-5 text-accent-500" />
            <span>API Explorer</span>
          </CardTitle>
          <CardDescription>Interactive playground coming soon</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex h-96 items-center justify-center border border-dashed border-white/20 rounded-lg">
            <div className="text-center">
              <Info className="mx-auto h-12 w-12 text-gray-500" />
              <p className="mt-4 text-gray-400">
                Developer Playground
              </p>
              <p className="mt-2 text-sm text-gray-500">
                API explorer • Code generator • Request builder • Example gallery
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
