import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';
import { INotebookTracker, NotebookActions, NotebookPanel } from '@jupyterlab/notebook';
import { assertOutputs, CellSnapshot, dockPosition, Runner, runAll, runToHere } from './core';
import '../style/index.css';

const plugin: JupyterFrontEndPlugin<void> = {
  id: '@querygraph/eigenmath-mobile:controls',
  description: 'Mobile run-to-here, run-all, save and keyboard controls for every notebook.',
  autoStart: true,
  requires: [INotebookTracker],
  activate: (app: JupyterFrontEnd, tracker: INotebookTracker): void => {
    const dock = document.createElement('section');
    dock.id = 'eigenmath-controls';
    dock.setAttribute('aria-label', 'Notebook actions');
    dock.hidden = true;
    dock.innerHTML = '<div class="actions"><button data-action="through">Run to here</button><button data-action="all">Run all</button><button data-action="save">Save</button><button data-action="done">Done</button></div><div class="status" role="status" aria-live="polite">Run to here includes earlier cells.</div>';
    document.body.appendChild(dock);
    const status = dock.querySelector<HTMLDivElement>('.status')!;
    const buttons = [...dock.querySelectorAll<HTMLButtonElement>('button')];
    let busy = false;

    function current(): NotebookPanel | null {
      const panel = tracker.currentWidget;
      return panel && !panel.isDisposed && app.shell.currentWidget === panel ? panel : null;
    }
    function position(): void {
      const viewport = window.visualViewport;
      const geometry = dockPosition({
        offsetTop: viewport?.offsetTop ?? 0, offsetLeft: viewport?.offsetLeft ?? 0,
        height: viewport?.height ?? window.innerHeight, width: viewport?.width ?? window.innerWidth
      }, dock.offsetHeight);
      dock.style.top = `${geometry.top}px`;
      dock.style.left = `${geometry.left}px`;
      dock.style.width = `${geometry.width}px`;
    }
    function update(): void {
      const panel = current();
      dock.hidden = !panel;
      document.body.classList.toggle('eigenmath-mobile-active', !!panel);
      for (const button of buttons) {
        if (button.dataset.action !== 'done') button.disabled = busy || !panel?.content.activeCell;
      }
      position();
    }
    function runner(panel: NotebookPanel): Runner {
      const notebook = panel.content;
      return {
        index: notebook.activeCellIndex,
        select: index => {notebook.deselectAll(); notebook.activeCellIndex = index;},
        above: () => NotebookActions.runAllAbove(notebook, panel.sessionContext),
        selected: () => NotebookActions.run(notebook, panel.sessionContext),
        all: () => NotebookActions.runAll(notebook, panel.sessionContext),
        check: (end = notebook.model!.cells.length - 1) => {
          const cells: CellSnapshot[] = [];
          for (let i = 0; i <= end; i++) cells.push(notebook.model!.cells.get(i).toJSON() as CellSnapshot);
          assertOutputs(cells, end, panel.context.model.defaultKernelLanguage);
        }
      };
    }
    async function action(kind: string): Promise<void> {
      if (kind === 'done') {
        (document.activeElement as HTMLElement | null)?.blur(); position(); return;
      }
      const panel = current();
      if (!panel || busy || !panel.content.activeCell) return;
      const actions = runner(panel);
      (document.activeElement as HTMLElement | null)?.blur();
      busy = true; update();
      try {
        await panel.context.ready;
        await panel.sessionContext.ready;
        if (kind === 'save') {
          status.textContent = 'Saving…';
          await panel.context.save();
          status.textContent = 'Saved';
        } else {
          status.textContent = kind === 'through' ? 'Running earlier cells, then this cell…' : 'Running all cells…';
          if (kind === 'through') await runToHere(actions); else await runAll(actions);
          status.textContent = 'Finished. Tap Save to keep the outputs.';
        }
      } catch (error) {
        status.textContent = error instanceof Error ? error.message : String(error);
      } finally {
        busy = false; update();
      }
    }
    for (const button of buttons) {
      button.addEventListener('pointerdown', event => event.preventDefault());
      button.addEventListener('click', () => {void action(button.dataset.action!);});
    }
    tracker.currentChanged.connect(update);
    tracker.activeCellChanged.connect(update);
    app.shell.currentChanged?.connect(update);
    window.addEventListener('resize', position);
    window.visualViewport?.addEventListener('resize', position);
    window.visualViewport?.addEventListener('scroll', position);
    new ResizeObserver(position).observe(dock);
    void app.restored.then(update);
    update();
  }
};
export default plugin;
