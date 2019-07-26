import os
from setuptools import setup, find_packages
from itertools import chain

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.md')) as f:
    readme = f.read()

with open(os.path.join(here, 'smalldataviewer', 'version.py')) as f:
    exec(f.read())

extras_require = {
    'hdf5': ['h5py>=2.0'],
    'img': ['imageio>=2.3'],
    'fits': ['imageio[fits]>=2.3'],
    'itk': ['imageio[itk]>=2.3'],
    # 'n5': ['z5py'],  # n.b. must be installed with conda
    # 'zarr': ['z5py'],  # n.b. must be installed with conda
}

full_requires = set(chain.from_iterable(extras_require.values()))
extras_require['all'] = sorted(full_requires)

setup(
    name='smalldataviewer',
    version=__version__,
    packages=find_packages(include=('smalldataviewer', )),
    url='https://github.com/clbarnes/smalldataviewer',
    license='MIT',
    install_requires=[
        'numpy>=1.7.1',
        'matplotlib>=3.0',
        'mpl_colors',
    ],
    extras_require=extras_require,
    author='Chris L Barnes',
    author_email='barnesc@janelia.hhmi.org',
    description='Command-line tool and python library for visualising small 3D datasets',
    long_description=readme,
    long_description_content_type='text/markdown',
    entry_points={
        'console_scripts': [
            'smalldataviewer = smalldataviewer.__main__:_main',
            'sdv = smalldataviewer.__main__:_main',
        ]
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='image volume 3d hdf5 n5 zarr',
    python_requires='>=3.6.*'
)
