smalldataviewer
===============

Simple matplotlib-based tool for viewing small amounts of 3D image data;
helpful for debugging.

Notes
-----

Due to the circumstances in which matplotlib holds open figure windows,
and stops updates during blocks, the entire array must be read into
memory before it can be viewed. It is a *small*\ dataviewer after all...

Installation
------------

.. code:: bash

    pip install git+https://github.com/clbarnes/smalldataviewer

Some file types require additional dependencies:

-  HDF5: h5py_

   -  ``pip install h5py``

-  zarr, N5: z5py_

   -  ``conda install -c cpape -c conda-forge z5py``

.. _h5py: http://docs.h5py.org/en/latest/build.html
.. _z5py: https://github.com/constantinpape/z5

Usage
-----

As executable
~~~~~~~~~~~~~

.. code:: bash

    usage: smalldataviewer [-h] [-i INTERNAL_PATH] [-t TYPE] [-o ORDER]
                           [-f OFFSET] [-s SHAPE] [-v]
                           path

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
      -f OFFSET, --offset OFFSET
                            3D offset of ROI from (0, 0, 0) in pixels
      -s SHAPE, --shape SHAPE
                            3D shape of ROI in pixels
      -v, --verbose         Increase output verbosity

    >>> smalldataviewer.py my_data.hdf5 -i /my_group/my_volume

As library
~~~~~~~~~~

.. code:: python

    from smalldataviewer import DataViewer, dataviewer_from_file

    # data can be anything which slices like a np.ndarray (e.g. h5py dataset)
    import numpy as np
    data = np.random.random((30, 100, 100))

    viewer = DataViewer(data)
    viewer.show()  # or matplotlib.pyplot.show()

    viewer2 = dataviewer_from_file(dataviewer, "my_data.npz", "volume") as viewer2:
    viewer2.show()

N.B.
~~~~

Because of the circumstances under which python holds file descriptors open and
matplotlib blocks, file-based volumes may need to read into numpy arrays to be
scrolled through if the ``.show()`` is at the end of the script.
