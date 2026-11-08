import assert from 'node:assert/strict';
import { test } from 'node:test';
import { fileURLToPath, URL } from 'node:url';
import { JSDOM } from 'jsdom';
import createDOMPurify from 'dompurify';
import { build } from 'vite';

for (const fragments of [
  ['$', '{probe()}'],
  ['{', '{probe}', '}'],
  ['<', '%probe()%>'],
]) {
  test(`shadow-root template fragments are scrubbed: ${fragments.join('')}`, () => {
    const { window } = new JSDOM('');
    const purify = createDOMPurify(window);
    const host = window.document.createElement('div');
    const root = host.attachShadow({ mode: 'open' });
    for (const fragment of fragments) {
      root.append(
        window.document.createTextNode(fragment),
        window.document.createElement('object')
      );
    }
    purify.sanitize(host, { IN_PLACE: true, SAFE_FOR_TEMPLATES: true });
    root.normalize();
    assert.ok(!root.textContent.includes(fragments.join('')));
    window.close();
  });
}

test('ordinary formatted content and shadow-root text remain usable', () => {
  const { window } = new JSDOM('');
  const purify = createDOMPurify(window);
  assert.equal(
    purify.sanitize('<b>Hello</b><img src=x onerror="probe()">'),
    '<b>Hello</b><img src="x">'
  );
  const host = window.document.createElement('div');
  host.attachShadow({ mode: 'open' }).textContent = 'ordinary editor help';
  purify.sanitize(host, { IN_PLACE: true, SAFE_FOR_TEMPLATES: true });
  assert.equal(host.shadowRoot.textContent, 'ordinary editor help');
  window.close();
});

test('production editor graph uses the pinned sanitizer instead of the vendored copy', async () => {
  const root = fileURLToPath(new URL('../../', import.meta.url));
  const result = await build({
    root,
    logLevel: 'error',
    build: { write: false, sourcemap: false },
  });
  const outputs = Array.isArray(result) ? result : [result];
  const modules = outputs.flatMap((output) =>
    output.output.flatMap((chunk) => (chunk.type === 'chunk' ? Object.keys(chunk.modules) : []))
  );
  assert.ok(
    modules.some((id) =>
      id.replaceAll('\\', '/').endsWith('/node_modules/dompurify/dist/purify.es.mjs')
    )
  );
  assert.ok(
    !modules.some((id) =>
      id.replaceAll('\\', '/').includes('/monaco-editor/esm/vs/base/browser/dompurify/')
    )
  );
});
