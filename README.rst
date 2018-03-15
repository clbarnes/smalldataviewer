smalldataviewer
===============

Simple matplotlib-based tool for viewing small amounts of 3D image data;
helpful for debugging. Supports python 2.7 and 3.4+.

Adapted from `this matplotlib recipe <https://matplotlib.org/gallery/animation/image_slices_viewer.html>`_.

Installation
------------

.. code:: bash

    pip install smalldataviewer

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

.. code::

    usage: smalldataviewer [-h] [-i INTERNAL_PATH] [-t TYPE] [-o ORDER]
                           [-f OFFSET] [-s SHAPE] [-v]
                           path

    positional arguments:
      path                  Path to HDF5, N5, zarr, npy, npz or JSON file
                            containing a 3D dataset

    optional arguments:
      -h, --help            show this help message and exit
      -i INTERNAL_PATH, --internal_path INTERNAL_PATH
                            Internal path of dataset inside HDF5, N5, zarr or npz
                            file. If JSON, assumes the outerobject is a dict, and
                            internal_path is the key of the array
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
                            3D offset of ROI from (0, 0, 0) in pixels, in the form
                            "<scroll>,<vertical>,<horizontal>"
      -s SHAPE, --shape SHAPE
                            3D shape of ROI in pixels, in the form
                            "<scroll>,<vertical>,<horizontal>"
      -v, --verbose         Increase logging verbosity

.. code:: bash

    smalldataviewer my_data.hdf5 -i /my_group/my_volume

Note: because of the circumstances under which python holds file descriptors open,
and under which matplotlib blocks, the executable form reads the data into memory
in its entirety. If your data are too big for this, look at small chunks with the
oFfset and Shape options.

As library
~~~~~~~~~~

.. code:: python

    from smalldataviewer import DataViewer, dataviewer_from_file

    import numpy as np
    data = np.random.random((30, 100, 100))

    viewer = DataViewer(data)
    viewer.show()  # or matplotlib.pyplot.show()

    viewer2 = dataviewer_from_file(dataviewer, "my_data.npz", "volume")
    viewer2.show()

Note: ``dataviewer_from_file`` reads the requested data into memory. ``DataViewer``
does not, by default. However, you may need to, depending on the rest of your script.
