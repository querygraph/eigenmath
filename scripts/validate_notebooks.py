#!/usr/bin/env python3
"""Verify immutable bytes and execute all notebooks in fresh, empty workspaces."""
from __future__ import annotations
import argparse,hashlib,json,math,re,tempfile
from pathlib import Path
import nbformat
from nbclient import NotebookClient

ROOT=Path(__file__).resolve().parents[1]

def output_text(cell):
    parts=[]
    for output in cell.get('outputs',[]):
        if output.get('output_type')=='error':
            raise AssertionError(str(output))
        for raw in [output.get('text',''),output.get('data',{}).get('text/plain','')]:
            parts.append(''.join(raw) if isinstance(raw,list) else raw)
    text='\n'.join(parts)
    if re.search(r'(^|\n)\s*(Error:|Exception:|Fatal error:|Traceback)',text):
        raise AssertionError('Printed kernel diagnostic: '+text[:500])
    return text

def receipt(notebook):
    text='\n'.join(output_text(c) for c in notebook.cells if c.cell_type=='code')
    for raw in reversed(re.findall(r'\{[^{}]+\}',text)):
        try:
            value=json.loads(raw.replace('\\"','"'))
            if isinstance(value,dict) and len(value)>40 and all(isinstance(v,(int,float)) for v in value.values()):
                return value
        except ValueError:
            pass
    raise AssertionError('Missing complete result receipt')

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
        assert sum(c.cell_type=='code' for c in notebook.cells)==row['code_cells']
        expected=receipt(notebook)
        if args.checksums_only:
            print('CHECKSUM',path.name);continue
        kernel=args.python_kernel if row['language']=='python' else args.ocaml_kernel
        with tempfile.TemporaryDirectory(prefix='eigenmath-validation-') as work:
            NotebookClient(notebook,kernel_name=kernel,timeout=300,allow_errors=False,resources={'metadata':{'path':work}}).execute()
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
