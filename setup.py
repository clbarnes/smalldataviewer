import os
from distutils.core import setup

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'requirements.txt')) as f:
    requirements = [line.strip() for line in f]

with open(os.path.join(here, 'README.md')) as f:
    readme = f.read()

setup(
    name='smalldataviewer',
    version='0.2.0',
    py_modules=['smalldataviewer'],
    url='https://github.com/clbarnes/smalldataviewer',
    license='MIT',
    install_requires=requirements,
    extras_require={
        'hdf5': ['h5py'],
        'n5': ['z5py'],
        'zarr': ['z5py']
    },
    author='Chris L Barnes',
    author_email='barnesc@janelia.hhmi.org',
    description='Command-line tool and python library for visualising small 3D datasets',
    long_description=readme,
    entry_points={'console_scripts': ['smalldataviewer = smalldataviewer:_main']},
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 2.7',
    ],
)
