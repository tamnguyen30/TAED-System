import { execFileSync } from 'node:child_process';

/** Pass email content as one literal argument; never invoke a shell. */
export function runPythonAnalysis(
  content: string,
  scriptPath: string,
  cwd: string,
  executable: string = 'python3',
): string {
  return execFileSync(executable, [scriptPath, content], {
    cwd,
    encoding: 'utf8',
    timeout: 120_000,
    maxBuffer: 1024 * 1024,
    shell: false,
  });
}
