import { useCallback } from 'react';
import { toast } from 'sonner';
import { EditorToolbar } from '@/components/Editor/EditorToolbar';
import { CodeEditor } from '@/components/Editor/CodeEditor';
import { OutputPanel } from '@/components/Output/OutputPanel';
import { ExampleGallery } from '@/components/Sidebar/ExampleGallery';
import { SettingsPanel } from '@/components/Sidebar/SettingsPanel';
import { SharePanel } from '@/components/Sidebar/SharePanel';
import { PlaygroundHeader } from '@/components/layout/PlaygroundHeader';
import { PlaygroundLayout } from '@/components/layout/PlaygroundLayout';
import { usePlaygroundStore } from '@/stores/playgroundStore';
import { playgroundExamples } from '@/lib/playground/examples';

export default function Playground() {
  const {
    code,
    language,
    theme,
    fontSize,
    output,
    error,
    isExecuting,
    shareUrl,
    selectedExampleId,
    lastRunAt,
    setCode,
    setLanguage,
    setTheme,
    setFontSize,
    executeCode,
    shareSession,
    saveSession,
    forkSession,
    loadExample,
  } = usePlaygroundStore();

  const handleRun = useCallback(async () => {
    await executeCode();
    toast.success('Run request dispatched', { description: 'Stub executor invoked in sandbox mode.' });
  }, [executeCode]);

  const handleShare = useCallback(async () => {
    try {
      const url = await shareSession();
      toast.success('Share link created', { description: 'T1 anchors preserved in encoded payload.' });
      if (navigator?.clipboard) {
        await navigator.clipboard.writeText(url);
      }
    } catch (err) {
      toast.error('Failed to share session', {
        description: err instanceof Error ? err.message : 'An unexpected error occurred while sharing.',
      });
    }
  }, [shareSession]);

  const handleSave = useCallback(async () => {
    try {
      const id = await saveSession();
      toast.success('Session saved', { description: `Session id: ${id}` });
    } catch (err) {
      toast.error('Failed to save session', { description: err instanceof Error ? err.message : String(err) });
    }
  }, [saveSession]);

  const handleFork = useCallback(async () => {
    try {
      const id = await forkSession();
      toast.info('Session forked', { description: `New session id: ${id}` });
    } catch (err) {
      toast.error('Failed to fork session', { description: err instanceof Error ? err.message : String(err) });
    }
  }, [forkSession]);

  return (
    <div className="flex h-full flex-col gap-4">
      <PlaygroundHeader lastRunAt={lastRunAt} />
      <PlaygroundLayout
        sidebar={
          <div className="space-y-4">
            <ExampleGallery examples={playgroundExamples} selectedId={selectedExampleId} onSelect={loadExample} />
            <SettingsPanel
              language={language}
              theme={theme}
              fontSize={fontSize}
              onLanguageChange={setLanguage}
              onThemeChange={setTheme}
              onFontSizeChange={setFontSize}
            />
            <SharePanel shareUrl={shareUrl} onShare={handleShare} />
          </div>
        }
      >
        <EditorToolbar
          onRun={handleRun}
          onSave={handleSave}
          onShare={handleShare}
          onFork={handleFork}
          isExecuting={isExecuting}
          status={
            <div className="text-xs text-gray-300" aria-live="polite">
              <p className="font-mono text-primary-100">Language: {language}</p>
              {lastRunAt && <p className="text-gray-400">Last run at {new Date(lastRunAt).toLocaleTimeString()}</p>}
            </div>
          }
        />

        <div className="h-[520px] rounded-lg border border-white/10 bg-black/20 p-2 shadow-inner">
          <CodeEditor
            code={code}
            language={language}
            theme={theme}
            fontSize={fontSize}
            onChange={setCode}
          />
        </div>

        <OutputPanel output={output} error={error} />
      </PlaygroundLayout>
    </div>
  );
}
