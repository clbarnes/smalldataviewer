# smalldataviewer

[![Travis](https://img.shields.io/travis/clbarnes/smalldataviewer.svg)](https://travis-ci.org/clbarnes/smalldataviewer)
[![PyPI](https://img.shields.io/pypi/v/smalldataviewer.svg)](https://pypi.org/project/smalldataviewer/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/smalldataviewer.svg)](https://www.python.org/)

Simple matplotlib-based tool for viewing small amounts of 3D image data;
helpful for debugging. Supports python 2.7 and 3.4+.

Adapted from [this matplotlib recipe](https://matplotlib.org/gallery/animation/image_slices_viewer.html).


![Small ssTEM Volume](https://media.giphy.com/media/fWggPcSFuQH0ZTAHKG/giphy.gif)


## Installation

```bash
pip install smalldataviewer[all]
```

The `all` installation includes all of these optional extras:

- `hdf5`: HDF5 file support via [h5py](http://docs.h5py.org/en/latest/build.html)
- `img`: volumetric and animated images via [imageio](https://imageio.readthedocs.io)
- `fits`: FITS images via `imageio[fits]`, which uses [astropy](http://www.astropy.org/)
- `itk`: ITK images via `imageio[simpleitk]`, which uses [SimpleITK](http://www.simpleitk.org/)

Support for N5 and zarr arrays is also available via [z5py](https://github.com/constantinpape/z5).
This must be installed with conda (`conda install -c conda-forge -c cpape z5py`).

## Usage

The `DataViewer` opens a `matplotlib` figure of the data volume.

-   Dimension 0 can be scrolled through with the mouse wheel
-   Dimension 1 is shown on the vertical axis
-   Dimension 2 is shown on the horizontal axis
-   Dimension 3, if it exists, is a colour tuple

### As executable

Available as a command-line utility at `smalldataviewer` or `sdv`

```help
usage: smalldataviewer [-h] [--version] [-i INTERNAL_PATH] [-t TYPE]
                       [-o ORDER] [-f OFFSET] [-s SHAPE] [-v] [-l]
                       path

positional arguments:
  path                  Path to file containing a 3D dataset

optional arguments:
  -h, --help            show this help message and exit
  --version             Print version information and exit
  -i INTERNAL_PATH, --internal_path INTERNAL_PATH
                        Internal path of dataset inside HDF5, N5, zarr or npz
                        file. If JSON, assumes the outer object is a dict, and
                        internal_path is the key of the array
  -t TYPE, --type TYPE  Dataset file type. Inferred from extension if not
                        given.
  -o ORDER, --order ORDER
                        Order of non-channel axes for axis labelling purposes
                        (data is not transposed): dimension 0 will be scrolled
                        through, dimension 1 will be on the up-down axis,
                        dimension 2 will be on the left-right axis, and
                        dimension 3, if it exists, will be used as the colour
                        channels. Default "zyx".
  -f OFFSET, --offset OFFSET
                        3D offset of ROI from (0, 0, 0) in pixels, in the form
                        "<scroll>,<vertical>,<horizontal>"
  -s SHAPE, --shape SHAPE
                        3D shape of ROI in pixels, in the form
                        "<scroll>,<vertical>,<horizontal>"
  -v, --verbose         Increase logging verbosity
  -l, --label           Whether to treat images as a label volume
```

e.g.

```bash
smalldataviewer my_data.hdf5 -i /my_group/my_volume
```

Note: because of the circumstances under which python holds file
descriptors open, and under which matplotlib blocks, the executable form
reads the data into memory in its entirety. If your data are too big for
this, look at small chunks with the `--offset` (`-f`) and `--shape`
(`-s`) options.

### As library

```python
import smalldataviewer as sdv

import numpy as np
data = np.random.random((30, 100, 100))
viewer = sdv.DataViewer(data)
viewer.show()  # or matplotlib.pyplot.show()

viewer2 = sdv.DataViewer.from_file(
    "my_data.npz", offset=(10, 20, 30), shape=(256, 512, 512), internal_path="volume"
)
viewer2.show()

reader = sdv.FileReader("my_cat_video.gif")
data2 = reader.read()  # returns a numpy array
viewer3 = sdv.DataViewer(data2)
viewer3.show()
```

Note: `FileReader` (and by extension `Dataviewer.from_file`) reads the requested data
from the file into memory.
Passing an indexable representation of a file, like a numpy memmap or an hdf5 dataset,
will not.
However, you may need to copy it into memory for performance, or depending on the rest of your script.

## Contributing

Install a development environment (not including z5py) with
`make install-dev`

Run tests in your current python environment with `make test`

Run tests against all supported python versions with `make test-all`

If you would like to add support for a new file type:

1. Add to `tests/common` a function which creates such a file and returns whether
    it needs an internal path, and add it to `file_constructors`.

2. Add to `smalldataviewer.files.FileReader` a method which reads such a file,
returning a numpy array, and add a mapping from likely file
extensions to a single file type in `NORMALISED_TYPES`
(see existing methods for examples).

3. Don't forget to specify any dependencies in `smalldataviewer.ext`,
`extras_require` in `setup.py`, and `requirements.txt`
