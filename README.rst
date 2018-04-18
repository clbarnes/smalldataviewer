.. image:: https://travis-ci.org/clbarnes/smalldataviewer.svg?branch=master
    :target: https://travis-ci.org/clbarnes/smalldataviewer

smalldataviewer
===============

Simple matplotlib-based tool for viewing small amounts of 3D image data;
helpful for debugging. Supports python 2.7 and 3.4+.

Adapted from `this matplotlib recipe <https://matplotlib.org/gallery/animation/image_slices_viewer.html>`_.

Installation
------------

.. code:: bash

    pip install smalldataviewer[full]

The ``full`` installation includes all of these optional extras:

- ``hdf5``: HDF5 file support via h5py_
- ``img``: volumetric and animated images via imageio_
- ``fits``: FITS images via ``imageio[fits]``, which uses astropy_
- ``itk``: ITK images via ``imageio[simpleitk]``, which uses SimpleITK_

Support for N5 and zarr arrays is also available via z5py_ .
This must be installed with conda (``conda install -c conda-forge -c cpape z5py``).

.. _h5py: http://docs.h5py.org/en/latest/build.html
.. _imageio: https://imageio.readthedocs.io
.. _astropy: http://www.astropy.org/
.. _SimpleITK: http://www.simpleitk.org/
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
      path                  Path to file containing a 3D dataset

    optional arguments:
      -h, --help            show this help message and exit
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

.. code:: bash

    smalldataviewer my_data.hdf5 -i /my_group/my_volume

Note: because of the circumstances under which python holds file descriptors open,
and under which matplotlib blocks, the executable form reads the data into memory
in its entirety. If your data are too big for this, look at small chunks with the
``--offset`` (``-f``) and ``--shape`` (``-s``) options.

As library
~~~~~~~~~~

.. code:: python

    from smalldataviewer import DataViewer, dataviewer_from_file

    import numpy as np
    data = np.random.random((30, 100, 100))

    viewer = DataViewer(data)
    viewer.show()  # or matplotlib.pyplot.show()

    viewer2 = DataViewer.from_file("my_data.npz", "volume")
    viewer2.show()

Note: ``Dataviewer.from_file`` reads the requested data from the file into memory.
``DataViewer`` does not, by default. However, you may need to, depending on the rest
of your script.

Contributing
~~~~~~~~~~~~

Install a development environment (not including z5py) with ``make install-dev``

Run tests in your current python environment with ``make test``

Run tests against all supported python versions with ``make test-all``

If you would like to add support for a new file type:

1. Add to ``tests/common`` a function which creates such a file and returns whether
    it needs an internal path, and add it to ``file_constructors``.
2. Add to ``smalldataviewer.files.FileReader`` a function which reads such a file,
    returning a numpy array, and add a mapping from likely file extensions to a single file
    type in ``NORMALISED_TYPES`` (see examples).
3. Don't forget to specify any dependencies in ``smalldataviewer.ext``,
    ``extras_require`` in ``setup.py``, and ``requirements.txt``
