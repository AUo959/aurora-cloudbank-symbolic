import { create } from 'zustand';
import {
  executeCodeSnippet,
  forkPlaygroundSession,
  savePlaygroundSession,
  sharePlaygroundSession,
} from '@/lib/playground/api';
import { defaultPlaygroundCode, playgroundExamples } from '@/lib/playground/examples';
import { PlaygroundLanguage, PlaygroundState, PlaygroundTheme } from '@/types/playground';

interface PlaygroundStore extends PlaygroundState {
  setCode: (code: string) => void;
  setLanguage: (language: PlaygroundLanguage) => void;
  setTheme: (theme: PlaygroundTheme) => void;
  setFontSize: (fontSize: number) => void;
  loadExample: (id: string) => void;
  executeCode: () => Promise<void>;
  shareSession: () => Promise<string>;
  saveSession: () => Promise<string>;
  forkSession: () => Promise<string>;
  clearOutput: () => void;
}

const initialExample = playgroundExamples[0];

export const usePlaygroundStore = create<PlaygroundStore>((set, get) => ({
  code: initialExample?.code ?? defaultPlaygroundCode,
  language: initialExample?.language ?? 'python',
  theme: 'dark',
  fontSize: 14,
  output: [],
  error: null,
  sessionId: null,
  shareUrl: null,
  selectedExampleId: initialExample?.id ?? 'quantum/supply_chain',
  isExecuting: false,
  lastRunAt: null,

  setCode: (code) => set({ code }),
  setLanguage: (language) => set({ language }),
  setTheme: (theme) => set({ theme }),
  setFontSize: (fontSize) => set({ fontSize }),

  loadExample: (id) => {
    const example = playgroundExamples.find((item) => item.id === id);
    if (example) {
      set({
        code: example.code,
        language: example.language,
        selectedExampleId: id,
        output: [],
        error: null,
      });
    }
  },

  executeCode: async () => {
    const { code, language, sessionId } = get();
    set({ isExecuting: true, output: [], error: null });

    try {
      const result = await executeCodeSnippet({ code, language, sessionId });
      set({
        output: result.output,
        error: result.error,
        isExecuting: false,
        sessionId: result.sessionId,
        lastRunAt: new Date().toISOString(),
      });
    } catch (error) {
      console.error('Error executing code:', error);
      const message = error instanceof Error ? error.message : 'Unknown execution error';
      set({ error: message, isExecuting: false });
    }
  },

  shareSession: async () => {
    const { code, language, sessionId } = get();
    const url = await sharePlaygroundSession({ code, language, sessionId });
    set({ shareUrl: url });
    return url;
  },

  saveSession: async () => {
    const { code, language, sessionId } = get();
    const response = await savePlaygroundSession({ code, language, sessionId });
    set({ sessionId: response.sessionId });
    return response.sessionId;
  },

  forkSession: async () => {
    const { code, language, sessionId } = get();
    const response = await forkPlaygroundSession({ code, language, sessionId });
    set({ sessionId: response.sessionId });
    return response.sessionId;
  },

  clearOutput: () => set({ output: [], error: null }),
}));
