# setup.py
from distutils.core import setup

setup(
    name = 'ogfx-ui',
    version = '0.1',
    packages = ['ogfx_ui'],
    package_data = {
        'ogfx_ui': [ 'views/*.tpl', 'static/*.css' ]
    }
)
