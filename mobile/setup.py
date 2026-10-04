from pathlib import Path
import json
from setuptools import setup

root = Path(__file__).parent
package = json.loads((root / 'package.json').read_text())
bundle = root / 'eigenmath_mobile/labextension'
if not (bundle / 'package.json').is_file():
    raise RuntimeError('Build the prebuilt extension first: npm ci && npm run build')

setup(
    name='eigenmath-mobile', version=package['version'],
    description=package['description'], packages=['eigenmath_mobile'],
    python_requires='>=3.10', install_requires=['jupyterlab>=4.5,<5'],
    package_data={'eigenmath_mobile': ['labextension/**/*', 'labextension/package.json']},
    data_files=[
        ('share/jupyter/labextensions/@querygraph/eigenmath-mobile/' + str(folder.relative_to(bundle)),
         [str(p.relative_to(root)) for p in folder.iterdir() if p.is_file()])
        for folder in [bundle, *[p for p in bundle.rglob('*') if p.is_dir()]]
    ],
    url='https://github.com/querygraph/eigenmath',
)
