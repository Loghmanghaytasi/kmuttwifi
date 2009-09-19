import os

if os.name == 'nt':
    from distutils.core import setup
    import py2exe
    setup(
        windows=['wifi.py'],
        options=dict(py2exe=dict(includes=['sip']))
    )

elif os.name == 'posix':
    from setuptools import setup
    setup(
        app=['wifi.py'],
        setup_requires=['py2app']
    )
