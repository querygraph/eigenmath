# Eigenmath

Six complete mathematics companions, with executable Python and native OCaml editions. Each notebook includes the full text, embedded figures, numerical inputs, code, and saved outputs. The notebooks are self-contained; execution needs no private datasets or credentials.

| Companion | Python | OCaml |
| --- | --- | --- |
| Eigen Times mathematics | [Notebook](notebooks/eigentimes-math-python.ipynb) | [Notebook](notebooks/eigentimes-math-ocaml.ipynb) |
| Eigen Times history mathematics | [Notebook](notebooks/eigentimes-history-math-python.ipynb) | [Notebook](notebooks/eigentimes-history-math-ocaml.ipynb) |
| Mathematics of anthropology | [Notebook](notebooks/anthropology-math-python.ipynb) | [Notebook](notebooks/anthropology-math-ocaml.ipynb) |

These are the unchanged 1.0.0 teaching editions. [The manifest](notebooks/manifest.json) records their original source revisions and checksums. The public repository contains a fresh history of the notebooks and shared controls; book manuscripts and deployment configuration stay in their owning repositories.

## Run locally

```sh
git clone https://github.com/querygraph/eigenmath.git
cd eigenmath
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m ipykernel install --sys-prefix --name eigenmath-python --display-name 'Eigenmath Python'
jupyter notebook notebooks
```

Choose **Eigenmath Python** when opening a Python notebook. For OCaml, install the native [ocaml-jupyter kernel](https://github.com/akabe/ocaml-jupyter) in an opam switch and register its generated kernelspec with the same Jupyter environment. Choose that kernel in the notebook. The released notebook metadata is preserved, so its original kernel name may differ from yours.

## Shared mobile controls — 0.1.0

Install the prebuilt wheel in the environment that runs Jupyter, then restart Jupyter and reload the page:

```sh
pip install https://github.com/querygraph/eigenmath/releases/download/v0.1.0/eigenmath_mobile-0.1.0-py3-none-any.whl
```

The extension supports Notebook 7.5+ and JupyterLab 4.5+ and automatically appears on **every open notebook**, regardless of its filename or kernel. No notebook edits, Node installation, proxy changes, or per-notebook scripts are needed to install the wheel.

- **Run to here** runs all earlier cells, then the selected cell. Use it when a lesson depends on setup cells. Earlier cells execute again, including any side effects.
- **Run all** executes the whole notebook in order.
- **Save** saves the notebook and outputs to its Jupyter server.
- **Done** dismisses the keyboard. The controls follow the visible viewport while editing on a phone.

Kernel errors are shown in the controls, including OCaml diagnostics printed by a kernel that reports a successful protocol reply. Server authentication and access controls remain the server's responsibility. A public source repository does not expose a running notebook server.

The implementation is shared once in [mobile/](mobile/README.md), with its version defined in [package.json](mobile/package.json). Releases contain the installable wheel and notebook archive.

## Verify the teaching editions

```sh
python scripts/validate_notebooks.py --checksums-only
python scripts/validate_notebooks.py --python-kernel eigenmath-python --ocaml-kernel ocaml-jupyter
```

Full validation executes all six notebooks in fresh kernels and empty temporary working directories. It compares 356 scalar results with the released outputs and checks 178 Python/OCaml pairs across 188 code cells. Executed validation copies and reports do not overwrite the released notebooks.

To generate a future edition from its book source, clone this repository beside the owning book repository, or set `EIGENMATH_ROOT` to this checkout. The book authoring scripts resolve notebook artifacts here. Preserve existing editions in Git tags and update the manifest when releasing a new edition.
