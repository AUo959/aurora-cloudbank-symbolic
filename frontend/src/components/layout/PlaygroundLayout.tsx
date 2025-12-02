import { ReactNode } from 'react';
import { cn } from '@/lib/utils';

interface PlaygroundLayoutProps {
  sidebar: ReactNode;
  children: ReactNode;
  className?: string;
}

export function PlaygroundLayout({ sidebar, children, className }: PlaygroundLayoutProps) {
  return (
    <div className={cn('flex h-full flex-col gap-4 p-6', className)}>
      <div className="grid flex-1 grid-cols-12 gap-4">
        <div className="col-span-12 space-y-3 lg:col-span-4">{sidebar}</div>
        <div className="col-span-12 flex flex-col gap-4 lg:col-span-8">{children}</div>
      </div>
    </div>
  );
}
