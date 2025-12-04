import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { ConsoleOutput } from './ConsoleOutput';
import { Activity } from 'lucide-react';

interface OutputPanelProps {
  output: string[];
  error?: string | null;
}

export function OutputPanel({ output, error }: OutputPanelProps) {
  return (
    <Card className="h-full bg-black/40 text-white">
      <CardHeader className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Activity className="h-5 w-5 text-primary-400" aria-hidden />
          <CardTitle className="text-lg">Console Output</CardTitle>
        </div>
      </CardHeader>
      <CardContent className="h-[320px] p-4">
        <ConsoleOutput lines={output} error={error} />
      </CardContent>
    </Card>
  );
}
