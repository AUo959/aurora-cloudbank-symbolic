import { cn } from '@/lib/utils';

interface ConsoleOutputProps {
  lines: string[];
  error?: string | null;
}

export function ConsoleOutput({ lines, error }: ConsoleOutputProps) {
  return (
    <div
      className={cn(
        'h-full rounded-lg border border-white/10 bg-gradient-to-b from-black/60 to-black/80 p-4 font-mono text-sm text-gray-100'
      )}
      role="log"
      aria-live="polite"
    >
      <div className="space-y-2">
        {lines.length === 0 && !error && <p className="text-gray-500">Console output will appear here.</p>}
        {lines.map((line, index) => (
          <p key={`${line}-${index}`} className="whitespace-pre-wrap text-primary-100">
            {line}
          </p>
        ))}
        {error && (
          <p className="whitespace-pre-wrap text-red-300" role="alert">
            {error}
          </p>
        )}
      </div>
    </div>
  );
}
