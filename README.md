# smalldataviewer

Simple matplotlib-based tool for viewing small amounts of 3D image data;
helpful for debugging.

## Installation

```bash
pip install git+https://github.com/clbarnes/smalldataviewer
```

Some file types require additional dependencies:

- HDF5: [`h5py`](http://docs.h5py.org/en/latest/build.html)
    - `pip install h5py`
- zarr, N5: [`z5py`](https://github.com/constantinpape/z5)
    - `conda install -c cpape z5py`

## Usage

### As executable

```bash
>>> smalldataviewer.py --help

usage: smalldataviewer.py [-h] [-i INTERNAL_PATH] [-t TYPE] [-o ORDER] path

positional arguments:
  path                  Path to HDF5, N5, zarr, npy or npz file containing a
                        3D dataset

optional arguments:
  -h, --help            show this help message and exit
  -i INTERNAL_PATH, --internal_path INTERNAL_PATH
                        Internal path of dataset inside HDF5, N5, zarr or npz
                        file
  -t TYPE, --type TYPE  Dataset file type. Inferred from extension if not
                        given.
  -o ORDER, --order ORDER
                        Order of spatial axes for axis labelling purposes.
                        Data is not transposed: dimension 0 will be scrolled
                        through, dimension 1 will be on the up-down axis,
                        dimension 2 will be on the left-right axis,
                        anddimension 3, if it exists, will be used as the
                        colour channels. Default "zyx".

>>> smalldataviewer.py my_data.hdf5 -i /my_group/my_volume
```

### As library

```python
from smalldataviewer import DataViewer, dataviewer_from_file

# data can be anything which slices like a np.ndarray (e.g. h5py dataset)
import numpy as np
data = np.random.random((30, 100, 100))

viewer = DataViewer(data)
viewer.show()  # or matplotlib.pyplot.show()

with dataviewer_from_file(dataviewer, "my_data.npz", "volume") as viewer2:
    viewer2.show()
```
