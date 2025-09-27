import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { pathToFileURL } from 'node:url';
import { createRequire } from 'node:module';
import { setImmediate, clearImmediate } from 'node:timers';

export function loadCommonJsModule(modulePath, options = {}) {
  const resolvedPath = path.resolve(modulePath);
  const source = fs.readFileSync(resolvedPath, 'utf8');
  const module = { exports: {} };
  const overrideMap = options.requireMap ?? new Map();
  const baseRequire = createRequire(pathToFileURL(resolvedPath));

  const resolveOverride = request => {
    if (!overrideMap || overrideMap.size === 0) {
      return undefined;
    }

    if (overrideMap.has(request)) {
      return overrideMap.get(request);
    }

    const dirname = path.dirname(resolvedPath);
    const candidates = [
      path.resolve(dirname, request),
      path.resolve(dirname, `${request}.js`),
      path.resolve(dirname, `${request}.cjs`),
      path.resolve(dirname, `${request}.mjs`),
    ];

    for (const candidate of candidates) {
      if (overrideMap.has(candidate)) {
        return overrideMap.get(candidate);
      }
    }

    return undefined;
  };

  const customRequire = request => {
    const override = resolveOverride(request);
    if (override !== undefined) {
      return override;
    }
    return baseRequire(request);
  };

  const sandbox = {
    module,
    exports: module.exports,
    require: customRequire,
    __dirname: path.dirname(resolvedPath),
    __filename: resolvedPath,
    process,
    console,
    Buffer,
    setTimeout,
    clearTimeout,
    setInterval,
    clearInterval,
    setImmediate,
    clearImmediate,
  };

  vm.createContext(sandbox);
  const script = new vm.Script(source, {
    filename: resolvedPath,
    displayErrors: true,
  });
  script.runInContext(sandbox);
  return sandbox.module.exports;
}
