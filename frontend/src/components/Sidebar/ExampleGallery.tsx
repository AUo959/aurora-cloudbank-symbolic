import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { PlaygroundExample } from '@/types/playground';
import { BadgeCheck, LibraryBig } from 'lucide-react';

interface ExampleGalleryProps {
  examples: PlaygroundExample[];
  selectedId: string;
  onSelect: (id: string) => void;
}

export function ExampleGallery({ examples, selectedId, onSelect }: ExampleGalleryProps) {
  return (
    <Card className="bg-black/40 text-white">
      <CardHeader className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <LibraryBig className="h-5 w-5 text-primary-400" aria-hidden />
          <CardTitle className="text-lg">Example Gallery</CardTitle>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        {examples.map((example) => {
          const isSelected = example.id === selectedId;

          return (
            <div
              key={example.id}
              className="rounded-lg border border-white/10 bg-white/5 p-3"
              aria-label={`Example ${example.title}`}
            >
              <div className="flex items-start justify-between gap-2">
                <div>
                  <p className="font-semibold text-primary-50">{example.title}</p>
                  <p className="text-sm text-gray-400">{example.description}</p>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {example.tags.map((tag) => (
                      <span
                        key={tag}
                        className="rounded-full bg-primary-500/10 px-2 py-1 text-xs text-primary-200"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
                {isSelected && <BadgeCheck className="h-5 w-5 text-accent-400" aria-label="Selected example" />}
              </div>
              <div className="mt-3 flex justify-end">
                <Button
                  variant={isSelected ? 'secondary' : 'outline'}
                  size="sm"
                  onClick={() => onSelect(example.id)}
                  aria-pressed={isSelected ? 'true' : 'false'}
                  className="gap-2"
                >
                  Load
                </Button>
              </div>
            </div>
          );
        })}
      </CardContent>
    </Card>
  );
}
