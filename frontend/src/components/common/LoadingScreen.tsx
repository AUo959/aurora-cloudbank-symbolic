import { Loader2 } from 'lucide-react';

export function LoadingScreen() {
  return (
    <div className="flex h-screen items-center justify-center aurora-gradient">
      <div className="text-center">
        <Loader2 className="mx-auto h-12 w-12 animate-spin text-primary-500" />
        <p className="mt-4 text-lg text-gray-300">Loading Aurora...</p>
      </div>
    </div>
  );
}
