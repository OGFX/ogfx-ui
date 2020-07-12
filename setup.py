# setup.py
from distutils.core import setup

setup(
    name = 'ogfx-ui',
    version = '0.1',
    packages = ['ogfx_ui'],
    scripts = [ 'ogfx_frontend_server.py' ],
    package_data = {
        'ogfx_ui': [ 'views/*.tpl', 'static/*.css', 'static/*.js' ]
    }
)
