export interface CellOutput {
  output_type?: string;
  text?: string | string[];
  data?: Record<string, unknown>;
}
export interface CellSnapshot { outputs?: CellOutput[] }

/** OCaml may print a diagnostic while reporting a successful protocol reply. */
export function assertOutputs(cells: CellSnapshot[], end: number, language: string): void {
  for (let i = 0; i <= end; i++) {
    for (const output of cells[i]?.outputs || []) {
      const raw = output.text ?? output.data?.['text/plain'] ?? '';
      const text = Array.isArray(raw) ? raw.join('') : String(raw);
      const diagnostic = language.toLowerCase() === 'ocaml' && /(^|\n)\s*(Error:|Exception:|Fatal error:)/.test(text);
      if (output.output_type === 'error' || diagnostic) {
        throw new Error(`Cell ${i + 1} failed. Check its output.`);
      }
    }
  }
}

export interface Runner {
  index: number;
  select(index: number): void;
  above(): Promise<boolean>;
  selected(): Promise<boolean>;
  all(): Promise<boolean>;
  check(end?: number): void;
}

export async function runToHere(runner: Runner): Promise<void> {
  const index = runner.index;
  runner.select(index);
  if (index > 0) {
    if (!await runner.above()) throw new Error('An earlier cell failed. Check its output.');
    runner.check(index - 1);
  }
  runner.select(index);
  if (!await runner.selected()) throw new Error('A cell failed. Check its output.');
  runner.check(index);
}

export async function runAll(runner: Runner): Promise<void> {
  if (!await runner.all()) throw new Error('A cell failed. Check its output.');
  runner.check();
}

export function dockPosition(viewport: {offsetTop: number; offsetLeft: number; height: number; width: number}, dockHeight: number) {
  return {
    top: Math.max(viewport.offsetTop + 4, viewport.offsetTop + viewport.height - dockHeight - 10),
    left: viewport.offsetLeft + 10,
    width: Math.min(500, Math.max(0, viewport.width - 20))
  };
}
