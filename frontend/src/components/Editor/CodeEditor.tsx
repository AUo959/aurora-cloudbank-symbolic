import Editor from '@monaco-editor/react';
import { useMemo } from 'react';
import { cn } from '@/lib/utils';
import { PlaygroundLanguage, PlaygroundTheme } from '@/types/playground';

interface CodeEditorProps {
  code: string;
  language: PlaygroundLanguage;
  theme: PlaygroundTheme;
  fontSize: number;
  onChange: (value: string) => void;
}

export function CodeEditor({ code, language, theme, fontSize, onChange }: CodeEditorProps) {
  const monacoTheme = useMemo(() => (theme === 'dark' ? 'vs-dark' : 'light'), [theme]);

  return (
    <div
      className={cn('relative h-full w-full overflow-hidden rounded-lg border border-white/10 bg-black/30')}
      aria-label="Code editor"
    >
      <Editor
        height="100%"
        language={language}
        theme={monacoTheme}
        value={code}
        onChange={(value) => onChange(value ?? '')}
        options={{
          fontSize,
          minimap: { enabled: false },
          automaticLayout: true,
          padding: { top: 12, bottom: 12 },
          scrollBeyondLastLine: false,
        }}
      />
    </div>
  );
}
