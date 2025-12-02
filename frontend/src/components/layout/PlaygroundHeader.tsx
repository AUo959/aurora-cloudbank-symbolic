import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Sparkles, ShieldCheck, Clock } from 'lucide-react';

interface PlaygroundHeaderProps {
  lastRunAt: string | null;
}

export function PlaygroundHeader({ lastRunAt }: PlaygroundHeaderProps) {
  return (
    <Card className="bg-black/40 text-white">
      <CardHeader className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <CardTitle className="flex items-center gap-2 text-3xl font-display">
            <Sparkles className="h-6 w-6 text-primary-400" aria-hidden />
            Aurora Playground
          </CardTitle>
          <CardDescription className="text-gray-400">
            Experiment with Aurora APIs in a sandboxed Monaco editor. Preserve T1 anchors for provenance and reproducibility.
          </CardDescription>
        </div>
        <div className="flex flex-wrap items-center gap-3 text-sm text-primary-100">
          <span className="flex items-center gap-1 rounded-full bg-primary-500/10 px-3 py-1">
            <ShieldCheck className="h-4 w-4 text-primary-300" aria-hidden />
            Sandboxed
          </span>
          {lastRunAt && (
            <span className="flex items-center gap-1 rounded-full bg-white/5 px-3 py-1">
              <Clock className="h-4 w-4" aria-hidden />
              Last run {new Date(lastRunAt).toLocaleTimeString()}
            </span>
          )}
        </div>
      </CardHeader>
      <CardContent className="text-sm text-gray-300">
        The playground executes code using stubbed backend actions for now. Production integration should route to the FastAPI
        execution controller with ORION safeguards. Avoid pasting PII—outputs are trimmed and retained only in-session.
      </CardContent>
    </Card>
  );
}
