import { loader } from '@monaco-editor/react';
import EditorWorker from 'monaco-editor/editor/editor.worker.js?worker';
import TypeScriptWorker from 'monaco-editor/language/typescript/ts.worker.js?worker';

let ready: Promise<void> | undefined;

/** Use the locked local ESM editor, including the patched sanitizer binding. */
export function prepareLocalMonaco(): Promise<void> {
  ready ??= import('monaco-editor').then((monaco) => {
    self.MonacoEnvironment = {
      getWorker(_moduleId, label) {
        return label === 'typescript' || label === 'javascript'
          ? new TypeScriptWorker()
          : new EditorWorker();
      },
    };
    loader.config({ monaco });
  });
  return ready;
}
