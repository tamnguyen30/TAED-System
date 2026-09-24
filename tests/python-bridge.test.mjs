import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, writeFileSync, existsSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { runPythonAnalysis } from '../templates/web-app/server/python-bridge.ts';

test('email metacharacters remain literal and cannot execute shell commands', () => {
  const folder = mkdtempSync(join(tmpdir(), 'taed-bridge-'));
  try {
    const script = join(folder, 'echo.mjs');
    writeFileSync(script, 'process.stdout.write(JSON.stringify(process.argv[2]));');
    const content = '"; touch INJECTED; $(touch INJECTED) `touch INJECTED`\nUnicode: café';
    const output = runPythonAnalysis(content, script, folder, process.execPath);
    assert.equal(JSON.parse(output), content);
    assert.equal(existsSync(join(folder, 'INJECTED')), false);
  } finally {
    rmSync(folder, { recursive: true, force: true });
  }
});

test('failed analyzer is surfaced rather than returning a fabricated verdict', () => {
  const folder = mkdtempSync(join(tmpdir(), 'taed-bridge-'));
  try {
    const script = join(folder, 'fail.mjs');
    writeFileSync(script, 'process.exit(2);');
    assert.throws(() => runPythonAnalysis('email', script, folder, process.execPath));
  } finally {
    rmSync(folder, { recursive: true, force: true });
  }
});
