import { Button } from '@/components/ui/Button';
import { cn } from '@/lib/utils';
import { Play, Save, Share2, GitFork, RefreshCw } from 'lucide-react';
import { ReactNode } from 'react';

interface EditorToolbarProps {
  onRun: () => void;
  onSave: () => void;
  onShare: () => void;
  onFork: () => void;
  isExecuting?: boolean;
  status?: ReactNode;
}

export function EditorToolbar({ onRun, onSave, onShare, onFork, isExecuting, status }: EditorToolbarProps) {
  return (
    <div className={cn(
      'flex flex-wrap items-center justify-between gap-3 rounded-lg border border-white/10 bg-black/30 px-4 py-3 shadow-md'
    )}
      aria-label="Playground actions">
      <div className="flex flex-wrap items-center gap-2">
        <Button variant="secondary" onClick={onSave} className="gap-2">
          <Save className="h-4 w-4" />
          Save
        </Button>
        <Button variant="ghost" onClick={onShare} className="gap-2">
          <Share2 className="h-4 w-4" />
          Share
        </Button>
        <Button variant="ghost" onClick={onFork} className="gap-2">
          <GitFork className="h-4 w-4" />
          Fork
        </Button>
      </div>
      <div className="flex items-center gap-3">
        {status}
        <Button variant="quantum" onClick={onRun} isLoading={isExecuting} className="gap-2">
          {isExecuting ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
          Run
        </Button>
      </div>
    </div>
  );
}
