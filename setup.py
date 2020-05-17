# setup.py
from distutils.core import setup

setup(
    name = 'ogfx-ui',
    version = '0.1',
    scripts = ['bin/ogfx-ui.py'],
    packages = ['ogfx'],
    data_files = [
        ('shared/ogfx-ui/views', list(map(lambda x: 'shared/ogfx-ui/views/' + x, [ 'add_unit.tpl', 'index.tpl', 'connect.tpl' , 'upload.tpl', 'file_chooser.tpl'  ]))),
        ('shared/ogfx-ui/static', list(map(lambda x: 'shared/ogfx-ui/static/' + x, [ 'index.css', 'range.css' ])))
    ]
)

