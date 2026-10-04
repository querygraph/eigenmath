# Eigenmath mobile controls

A prebuilt Jupyter frontend extension, version **0.1.0**, for Notebook 7.5+ and JupyterLab 4.5+. It uses the standard notebook tracker and notebook actions, so one installation serves every notebook and kernel. It contains no notebook content, hostnames, owner identities, or authentication settings.

Install the [release wheel](https://github.com/querygraph/eigenmath/releases/tag/v0.1.0) with `pip` in your Jupyter environment. Restart the server and reload the page. Verify installation with:

```sh
jupyter labextension list
```

The list should show `@querygraph/eigenmath-mobile v0.1.0 enabled OK`. Remove the extension with `pip uninstall eigenmath-mobile`, then restart Jupyter.

## Develop and build

Use Node 22 and Python 3.10+ with JupyterLab 4.5+ installed:

```sh
cd mobile
npm ci
npm test
npm run build
python -m pip wheel --no-deps . --wheel-dir dist
```

Install the resulting wheel in a Jupyter environment for browser verification. TypeScript and styles are bundled into the wheel; end users do not rebuild JupyterLab. `package.json` is the single source of the extension version, including the Python distribution metadata.

The tests cover viewport resizing, selection preservation, prerequisite failures, and native OCaml printed diagnostics. Browser verification should cover an arbitrary notebook filename, both kernels, editor focus with a phone-sized viewport, Run to here, Run all, Save, and hiding the controls when leaving a notebook.

With Playwright and WebKit installed in a test environment, verify an authenticated server with temporary notebooks:

```sh
python tests/browser.py --base-url http://localhost:8888 --python-kernel python3 --ocaml-kernel ocaml-jupyter
python tests/browser.py --base-url http://localhost:8888 --python-kernel python3 --ocaml-kernel ocaml-jupyter --frontend lab
```

The test creates randomly named scratch notebooks and removes them and their kernel sessions afterwards. `--proxy` accepts an optional browser proxy for servers accessible through a private network.
