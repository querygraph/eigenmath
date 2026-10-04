#!/usr/bin/env python3
"""Verify the installed extension through authenticated Jupyter browser access.

Creates disposable notebooks with arbitrary names, and deletes them afterwards.
Requires Playwright with its WebKit browser installed in the test environment.
"""
import argparse
import asyncio
import json
from uuid import uuid4
from urllib.parse import quote

from playwright.async_api import async_playwright


async def api(page, path, method='GET', body=None):
    return await page.evaluate('''async ({path, method, body}) => {
      const cookie = document.cookie.split(';').map(s => s.trim()).find(s => s.startsWith('_xsrf='));
      const headers = {'Content-Type': 'application/json'};
      if (cookie) headers['X-XSRFToken'] = decodeURIComponent(cookie.slice(6));
      const response = await fetch(path, {method, headers, body: body === null ? undefined : JSON.stringify(body)});
      if (!response.ok) throw new Error(`${method} ${path}: ${response.status}`);
      return response.status === 204 ? null : await response.json();
    }''', {'path': path, 'method': method, 'body': body})


async def finished(page):
    await page.wait_for_function('!document.querySelector("#eigenmath-controls button").disabled', timeout=90000)
    status = await page.locator('#eigenmath-controls .status').inner_text()
    assert status.startswith('Finished.'), status


async def main(args):
    results = []
    async with async_playwright() as playwright:
        proxy = {'server': args.proxy} if args.proxy else None
        browser = await playwright.webkit.launch(proxy=proxy)
        context = await browser.new_context(viewport={'width': 1440 if args.frontend == 'lab' else 390, 'height': 844}, is_mobile=True, has_touch=True)
        page = await context.new_page()
        await page.goto(args.base_url.rstrip('/') + '/tree', wait_until='networkidle')
        for language, kernel in [('python', args.python_kernel), ('ocaml', args.ocaml_kernel)]:
            name = 'reusable-controls-' + uuid4().hex + '.ipynb'
            path = '/api/contents/' + quote(name)
            code = (['def matvec(xs):\n    return sum(xs)', 'response = matvec([1., 2.])', 'print(f"REUSABLE_CONTROLS_OK {response:.1f}")']
                    if language == 'python' else
                    ['let matvec xs = List.fold_left (+.) 0. xs;;', 'let response = matvec [1.; 2.];;', 'print_endline ("REUSABLE_CONTROLS_OK " ^ Printf.sprintf "%.1f" response);;'])
            notebook = {'nbformat': 4, 'nbformat_minor': 5,
                        'metadata': {'kernelspec': {'name': kernel, 'display_name': kernel, 'language': language}, 'language_info': {'name': language}},
                        'cells': [{'id': uuid4().hex[:8], 'cell_type': 'code', 'metadata': {}, 'source': source, 'outputs': [], 'execution_count': None} for source in code]}
            await api(page, path, 'PUT', {'type': 'notebook', 'format': 'json', 'content': notebook})
            try:
                route = '/notebooks/' if args.frontend == 'notebook' else '/lab/workspaces/eigenmath-mobile-test/tree/'
                await page.goto(args.base_url.rstrip('/') + route + quote(name), wait_until='networkidle')
                await page.wait_for_selector('#eigenmath-controls:not([hidden])', timeout=45000)
                await page.wait_for_function('!document.querySelector("#eigenmath-controls button").disabled')
                assert await page.locator('#eigenmath-controls').count() == 1
                panel = page.locator('.jp-NotebookPanel:visible')
                editor = panel.locator('.jp-CodeCell .cm-content').nth(2)
                await editor.click()
                await page.set_viewport_size({'width': 390, 'height': 360})
                box = await page.locator('#eigenmath-controls').bounding_box()
                assert box and box['y'] >= 0 and box['y'] + box['height'] <= 360, box
                await page.get_by_role('button', name='Run to here', exact=True).click()
                await finished(page)
                # Saved model outputs also verify virtualized/offscreen cells.
                await page.get_by_role('button', name='Save', exact=True).click()
                await page.wait_for_function('document.querySelector("#eigenmath-controls .status").textContent === "Saved"')
                saved = await api(page, path)
                assert 'REUSABLE_CONTROLS_OK 3.0' in json.dumps(saved['content']['cells'][-1]['outputs'])
                await page.get_by_role('button', name='Done', exact=True).click()
                assert await page.evaluate('!document.activeElement?.closest(".cm-editor")')
                await page.set_viewport_size({'width': 390, 'height': 844})
                await page.get_by_role('button', name='Run all', exact=True).click()
                await finished(page)
                await page.get_by_role('button', name='Save', exact=True).click()
                await page.wait_for_function('document.querySelector("#eigenmath-controls .status").textContent === "Saved"')
                saved = await api(page, path)
                assert 'REUSABLE_CONTROLS_OK 3.0' in json.dumps(saved['content']['cells'][-1]['outputs'])
                if language == 'ocaml':
                    await editor.fill('unknown_eigenmath_mobile_value;;')
                    await page.get_by_role('button', name='Run to here', exact=True).click()
                    await page.wait_for_function('!document.querySelector("#eigenmath-controls button").disabled', timeout=90000)
                    assert 'failed' in await page.locator('#eigenmath-controls .status').inner_text()
                    await editor.fill(code[-1])
                    await page.get_by_role('button', name='Run all', exact=True).click()
                    await finished(page)
                    await page.get_by_role('button', name='Save', exact=True).click()
                    await page.wait_for_function('document.querySelector("#eigenmath-controls .status").textContent === "Saved"')
                results.append({'frontend': args.frontend, 'language': language, 'arbitrary_filename': True, 'keyboard_viewport': True, 'run_to_here': True, 'run_all': True, 'save': True, 'done': True, 'printed_error_detected': language == 'ocaml'})
                print('PASS', args.frontend, language, flush=True)
            finally:
                sessions = await api(page, '/api/sessions')
                for session in sessions:
                    if session['path'] == name:
                        await api(page, '/api/sessions/' + session['id'], 'DELETE')
                await page.goto(args.base_url.rstrip('/') + '/tree', wait_until='networkidle')
                assert await page.locator('#eigenmath-controls:not([hidden])').count() == 0
                await api(page, path, 'DELETE')
        await browser.close()
    print(json.dumps(results, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url', required=True)
    parser.add_argument('--proxy')
    parser.add_argument('--python-kernel', default='python3')
    parser.add_argument('--ocaml-kernel', default='ocaml-jupyter')
    parser.add_argument('--frontend', choices=['notebook', 'lab'], default='notebook')
    asyncio.run(main(parser.parse_args()))
