import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Share2, Copy, ExternalLink } from 'lucide-react';

interface SharePanelProps {
  shareUrl: string | null;
  onShare: () => Promise<void>;
}

export function SharePanel({ shareUrl, onShare }: SharePanelProps) {
  const copyLink = async () => {
    if (shareUrl && navigator.clipboard) {
      try {
        await navigator.clipboard.writeText(shareUrl);
      } catch (error) {
        console.error('Failed to copy to clipboard:', error);
      }
    }
  };

  return (
    <Card className="bg-black/40 text-white">
      <CardHeader>
        <div className="flex items-center gap-2">
          <Share2 className="h-5 w-5 text-primary-400" aria-hidden />
          <CardTitle className="text-lg">Share & Embed</CardTitle>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <p className="text-sm text-gray-400">
          Generate a secure link for this session. Aurora metadata anchors (T1) remain embedded in code snippets for provenance.
        </p>
        <div className="flex flex-col gap-2">
          <Button variant="secondary" onClick={onShare} className="gap-2">
            <ExternalLink className="h-4 w-4" />
            Create share link
          </Button>
          <Button variant="outline" onClick={copyLink} disabled={!shareUrl} className="gap-2">
            <Copy className="h-4 w-4" />
            Copy link
          </Button>
        </div>
        {shareUrl && (
          <div className="rounded-md border border-white/10 bg-white/5 p-2 text-xs text-primary-50 break-all" aria-live="polite">
            {shareUrl}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
