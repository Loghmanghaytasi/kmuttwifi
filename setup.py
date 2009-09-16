from distutils.core import setup
import py2exe

setup(
    windows=['wifi.py'],
    options=dict(py2exe=dict(includes=['sip']))
)
