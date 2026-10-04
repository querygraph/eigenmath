# Eigenmath

The six notebooks are complete, immutable released teaching editions. Preserve
all prose, figures, code, saved outputs, cell IDs and provenance. Verify the
manifest and execute both languages with complete matching receipts before
publishing notebook changes. A correction requires a new notebook patch version;
never overwrite an earlier release's bytes or source revision.

Mobile controls live once in mobile/src and mobile/style as a standard prebuilt
Jupyter extension for Notebook 7 and JupyterLab 4. Never embed per-notebook control
copies, hostnames, owner identities, credentials or deployment paths. Kernels and
save locations belong to the user's Jupyter installation. Keep authentication
and transport configuration outside the controls package.

Checks: npm ci, npm test and npm run build in mobile/; build a wheel, install it
in an isolated Jupyter environment and verify run-to-here, run-all, save, notebook
switching, printed OCaml diagnostics and keyboard-sized viewport geometry.
Run scripts/validate_notebooks.py for notebook changes. Do not commit working
notebooks, local configs/logs/credentials or node_modules. Python remains portable
and tests use fresh kernels and empty temporary working directories.
