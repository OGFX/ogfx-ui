# setup.py
from distutils.core import setup

setup(
    name = 'ogfx-ui',
    version = '0.1',
    scripts = ['ogfx-ui.py',],
    packages = ['ogfx'],
    data_files = [
        ('views', [ 'views/add_unit.tpl', 'views/index.tpl' ]),
        ('static', [ 'static/index.css', 'static/range.css' ])
    ]
)

