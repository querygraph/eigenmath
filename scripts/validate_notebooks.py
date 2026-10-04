#!/usr/bin/env python3
"""Verify immutable bytes and execute all notebooks in fresh, empty workspaces."""
from __future__ import annotations
import argparse,hashlib,json,math,os,re,tempfile
from pathlib import Path
import nbformat
from nbclient import NotebookClient

ROOT=Path(__file__).resolve().parents[1]

def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate receipt key: {key}")
        result[key] = value
    return result


def output_text(cell):
    """Also reject diagnostics printed by kernels that report protocol success."""
    parts = []
    for output in cell.get("outputs", []):
        if output.get("output_type") == "error":
            raise ValueError(f"Kernel error in {cell.id}: {output}")
        for raw in (output.get("text", ""), output.get("data", {}).get("text/plain", "")):
            parts.append("".join(raw) if isinstance(raw, list) else raw)
    text = "\n".join(parts)
    if re.search(r"(?:^|\n)\s*(?:Error:|Exception:|Fatal error:|Traceback)", text):
        raise ValueError(f"Printed kernel diagnostic in {cell.id}: {text[:500]}")
    return text


def result_dictionary(notebook, expected_keys, prefix="RESULT_JSON:"):
    codes = [cell for cell in notebook.cells if cell.cell_type == "code"]
    receipts = [cell for cell in codes if "result_receipt" in cell.metadata.get("tags", [])]
    if len(receipts) != 1 or receipts[0] is not codes[-1]:
        raise ValueError("Exactly one final code cell must contain the marked result receipt")
    cell = receipts[0]
    if cell.execution_count is None:
        raise ValueError("The result receipt has not executed")
    output_text(cell)
    streams = "".join(output.get("text", "") for output in cell.outputs if output.output_type == "stream")
    texts = ([streams] if streams else []) + [
        output.get("data", {}).get("text/plain", "") for output in cell.outputs
        if output.output_type in ("execute_result", "display_data")
    ]
    decoder = json.JSONDecoder(object_pairs_hook=unique_object)
    candidates = []
    for text in texts:
        variants = [text]
        # The native OCaml toplevel quotes and escapes a returned string once.
        for match in re.finditer(r'"(?:\\.|[^"\\])*"', text, re.S):
            try:
                value = json.loads(match[0])
            except json.JSONDecodeError:
                continue
            if isinstance(value, str) and prefix in value:
                variants.append(value)
        for variant in variants:
            for match in re.finditer(re.escape(prefix), variant):
                rest = variant[match.end():].lstrip()
                try:
                    value, end = decoder.raw_decode(rest)
                except json.JSONDecodeError:
                    continue
                if rest[end:].strip():
                    raise ValueError("Unexpected text after numerical receipt")
                if not isinstance(value, dict):
                    raise ValueError("The numerical receipt must be an object")
                candidates.append(value)
    if len(candidates) != 1:
        raise ValueError(f"Expected exactly one marked numerical receipt, found {len(candidates)}")
    if not expected_keys or len(set(expected_keys)) != len(expected_keys):
        raise ValueError("Complete, unique expected result keys must be declared")
    result = candidates[0]
    if set(result) != set(expected_keys):
        raise ValueError(f"Result coverage differs: missing={sorted(set(expected_keys) - set(result))}, "
                         f"extra={sorted(set(result) - set(expected_keys))}")
    for key, value in result.items():
        if type(value) not in (int, float) or not math.isfinite(value):
            raise ValueError(f"Nonfinite or nonnumeric receipt result: {key}")
    return result


def receipt(notebook):
    codes = [c for c in notebook.cells if c.cell_type == 'code']
    for cell in codes:
        output_text(cell)
    keys = notebook.metadata.companion.get('expected_result_keys', [])
    prefixes = [p for p in ('RESULT_JSON:', 'COMPANION_RESULTS_V1:') if p in codes[-1].source]
    if len(prefixes) != 1:
        raise ValueError('The final cell must declare one supported receipt prefix')
    return result_dictionary(notebook, keys, prefixes[0])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--python-kernel',default='python3')
    parser.add_argument('--ocaml-kernel',default='ocaml-jupyter')
    parser.add_argument('--checksums-only',action='store_true')
    args=parser.parse_args()
    rows=json.loads((ROOT/'notebooks/manifest.json').read_text())
    results=[];pairs={}
    assert len(rows)==6
    for row in rows:
        path=ROOT/row['file'];raw=path.read_bytes()
        assert hashlib.sha256(raw).hexdigest()==row['sha256'],row['file']
        assert len(raw)==row['bytes']
        notebook=nbformat.read(path,as_version=4)
        nbformat.validate(notebook)
        assert notebook.metadata.companion.get('draft') is False, path.name
        assert notebook.metadata.companion.source_commit == row['source_commit'], path.name
        assert notebook.metadata.companion.notebook_version == row['notebook_version'], path.name
        assert sum(c.cell_type=='code' for c in notebook.cells)==row['code_cells']
        expected=receipt(notebook)
        if args.checksums_only:
            print('CHECKSUM',path.name);continue
        kernel=args.python_kernel if row['language']=='python' else args.ocaml_kernel
        with tempfile.TemporaryDirectory(prefix='eigenmath-validation-') as work:
            environment = os.environ.copy()
            environment['IPYTHONDIR'] = str(Path(work) / '.ipython')
            environment['MPLCONFIGDIR'] = str(Path(work) / '.matplotlib')
            NotebookClient(notebook,kernel_name=kernel,timeout=300,allow_errors=False,record_timing=False,resources={'metadata':{'path':work}}).execute(env=environment)
        actual=receipt(notebook)
        assert actual.keys()==expected.keys(),path.name
        for key,value in actual.items():
            assert math.isfinite(value) and math.isclose(value,expected[key],rel_tol=1e-8,abs_tol=1e-8),(path.name,key)
        key=path.stem.rsplit('-',1)[0]
        if key in pairs:
            prior=pairs[key];assert prior.keys()==actual.keys()
            assert all(math.isclose(prior[k],actual[k],rel_tol=1e-8,abs_tol=1e-8) for k in actual)
        pairs[key]=actual
        results.append({'file':row['file'],'sha256':row['sha256'],'kernel':kernel,'code_cells':row['code_cells'],'scalar_results':len(actual),'matches_released':True})
        print('PASS',path.name,row['code_cells'],'cells',len(actual),'results',flush=True)
    if not args.checksums_only:
        out=ROOT/'.validation';out.mkdir(exist_ok=True)
        (out/'results.json').write_text(json.dumps(results,indent=2)+'\n')
        print('All six passed in fresh kernels and empty working directories.')

if __name__=='__main__':main()
