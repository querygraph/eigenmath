# Eigenmath

The public home of the executable mathematics companions for **Eigen Times, Eigen Hacks, and Anthropology**. The projects turn article text into vectors, organize news along measured directions, and explore the people and institutions behind technology. These companions explain the mathematics through small examples you can read, run, and change.

Six complete teaching notebooks provide paired Python and native OCaml editions of three companion papers. Each includes the full text, embedded figures, numerical inputs, code, and saved outputs. The notebooks are self-contained; execution needs no private datasets or credentials. Their synthetic and frozen examples preserve the published calculations rather than refreshing the live newspapers or fitting production models.

## The projects and sites

| Project | Site | What to explore |
| --- | --- | --- |
| Eigen Times | [eigentimes.com](https://eigentimes.com/) · [second edition](https://eigentimes.com/v2/) | A newspaper organized in a fixed eigenbasis of news; new articles are measured against the existing basis. |
| Eigen Hacks | [eigenhacks.com](https://eigenhacks.com/) · [people × news vectors](https://eigenhacks.com/people-vectors/) | The Hacker News corpus and its people and news directions. |
| Anthropology | [anthropolo.gy](https://anthropolo.gy/) · [people vectors](https://anthropolo.gy/vectors) · [daily edition](https://anthropolo.gy/daily) | A sourced graph of people, companies, institutions, and investors, with dated discoveries and coverage measurements. |
| First Pair Press | [firstpair.org](https://firstpair.org/) | The companion papers and related research in web, PDF, and EPUB reading editions. |

The daily people editions on [Eigen Hacks](https://eigenhacks.com/people-of-day/) and [Eigen Times](https://eigentimes.com/people-of-day/) connect newly sourced Anthropology events with recent article activity in the existing news spaces.

## Companion papers and notebooks

| Companion | Python | OCaml |
| --- | --- | --- |
| [The Mathematics of Eigen Times](https://firstpair.org/books/eigentimes-math/) | [Notebook](notebooks/eigentimes-math-python.ipynb) | [Notebook](notebooks/eigentimes-math-ocaml.ipynb) |
| [Eigen Times History Math](https://firstpair.org/books/eigentimes-history-math/) | [Notebook](notebooks/eigentimes-history-math-python.ipynb) | [Notebook](notebooks/eigentimes-history-math-ocaml.ipynb) |
| [The Mathematics of Anthropology](https://firstpair.org/books/anthropology-math/) | [Notebook](notebooks/anthropology-math-python.ipynb) | [Notebook](notebooks/anthropology-math-ocaml.ipynb) |

**The Mathematics of Eigen Times** develops text vectors, covariance, eigenvectors, SVD and latent semantic analysis, rotation, projection, and the newspaper's clustering and statistical tests. Read it on [FirstPair](https://firstpair.org/read/eigentimes-math/) or download the [PDF](https://firstpair.org/eigentimes-math/pdf/) and [EPUB](https://firstpair.org/eigentimes-math/epub/). Its manuscript and build tools belong to [alexy/eigentimes-math](https://github.com/alexy/eigentimes-math).

**Eigen Times History Math: A Worked Companion to Eigen Times Math History** extends the executable lessons with techniques from the history companion, including definitions, a glossary, an index, and paired numerical laboratories. Read it on [FirstPair](https://firstpair.org/read/eigentimes-history-math/) or download the [PDF](https://firstpair.org/eigentimes-history-math/pdf/) and [EPUB](https://firstpair.org/eigentimes-history-math/epub/). Its [paper source](https://github.com/alexy/eigentimes-math/tree/main/papers/eigentimes-history-math) belongs to the same book repository.

**The Mathematics of Anthropology** builds from article coordinates to people vectors, navigation in both directions, changing coverage, and ontology calibration. Read it on [FirstPair](https://firstpair.org/read/anthropology-math/) or download the [PDF](https://firstpair.org/anthropology-math/pdf/) and [EPUB](https://firstpair.org/anthropology-math/epub/). Its [paper source](https://github.com/querygraph/anthropology/tree/main/papers/mathematics-of-anthropology) belongs to [querygraph/anthropology](https://github.com/querygraph/anthropology); a [public tutorial-source bundle](https://firstpair.org/read/anthropology-math/chapters/anthropology-math-sources.zip) is also available from FirstPair.

For the research behind the teaching papers, see [Eigen Times: A Newspaper in the Eigenbasis of the News](https://firstpair.org/books/eigentimes/) and [The Dual Geometry of People and News](https://firstpair.org/books/anthropology/).

The shared Eigen Times/Eigen Hacks pair is notebook edition **1.0.1**, containing book **1.1.2** with stepwise foundations, worked derivations, a glossary and an index. The History Math and Anthropology Math pairs are now notebook and book edition **1.1.0**, with expanded definitions, intermediate arithmetic and derivatives, glossaries, indexes, and independent numerical checks. FirstPair provides these book editions in PDF, EPUB, and hosted HTML, with links to the current Python and OCaml notebooks in this repository. The original six editions are preserved in [tag v0.1.0](https://github.com/querygraph/eigenmath/tree/v0.1.0/notebooks). [The manifest](notebooks/manifest.json) records each notebook's original source revision and checksum. This [public GitHub repository](https://github.com/querygraph/eigenmath) owns the released notebooks and shared mobile controls. The book repositories linked above and the [Eigen Times implementation](https://github.com/alexy/eigentimes) currently require repository access; FirstPair provides the public reading editions.

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

Full validation executes all six notebooks in fresh kernels and empty temporary working directories. It compares 528 scalar results with the released outputs and checks 264 Python/OCaml pairs across 238 code cells. Executed validation copies and reports do not overwrite the released notebooks.

To generate a future edition from its book source, clone this repository beside the owning book repository, or set `EIGENMATH_ROOT` to this checkout. The book authoring scripts resolve notebook artifacts here. Preserve existing editions in Git tags and update the manifest when releasing a new edition.
