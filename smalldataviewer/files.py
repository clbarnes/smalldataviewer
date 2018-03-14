#!/usr/bin/env python
"""Adapted from https://matplotlib.org/gallery/animation/image_slices_viewer.html"""

from __future__ import division

import json
import logging
import os
import functools

import numpy as np

from smalldataviewer.viewer import DataViewer

__all__ = ['dataviewer_from_file']


logger = logging.getLogger(__name__)


def requires_internal_path(fn):
    @functools.wraps(fn)
    def wrapped(path, internal_path, slicing):
        if internal_path is None:
            raise ValueError('internal_path required by this file format')
        return fn(path, internal_path, slicing)

    return wrapped


def _read_npy(path, internal_path, slicing):
    return np.load(path)[slicing]


@requires_internal_path
def _read_n5(path, internal_path, slicing):
    try:
        import z5py
    except ImportError:
        raise ImportError('z5py is required to open N5 files')

    with z5py.File(path, False) as f:
        return np.asarray(f[internal_path][slicing])


@requires_internal_path
def _read_zarr(path, internal_path, slicing):
    try:
        import z5py
    except ImportError:
        raise ImportError('z5py is required to open zarr files')

    with z5py.File(path, True) as f:
        return np.asarray(f[internal_path][slicing])


@requires_internal_path
def _read_hdf5(path, internal_path, slicing):
    try:
        import h5py
    except ImportError:
        raise ImportError('h5py is required to open h5py files')

    with h5py.File(path, mode='r') as f:
        return np.asarray(f[internal_path][slicing])


@requires_internal_path
def _read_npz(path, internal_path, slicing):
    with np.load(path) as f:
        return np.asarray(f[internal_path][slicing])


def _read_json(path, internal_path, slicing):
    with open(path) as f:
        obj = json.load(f)

    if internal_path:
        obj = obj[internal_path]

    return np.asarray(obj)[slicing]


FILE_CONSTRUCTORS = {
    'n5': _read_n5,
    'hdf': _read_hdf5,
    'h5': _read_hdf5,
    'hdf5': _read_hdf5,
    'zarr': _read_zarr,
    'zr': _read_zarr,
    'npy': _read_npy,
    'npz': _read_npz,
    'json': _read_json
}


def offset_shape_to_slicing(offset=None, shape=None):
    slices = tuple(slice(o, s) for o, s in zip(offset or (None, None, None), shape or (None, None, None)))
    return slices


def read_file(path, internal_path=None, ftype=None, offset=None, shape=None):
    if ftype is None:
        ftype = os.path.splitext(str(path))[1]

    stripped = ftype.lstrip('.').lower()

    if stripped not in FILE_CONSTRUCTORS:
        raise KeyError('File type {} not recognised; use one of \n\t{}'.format(
            ftype, ', '.join(sorted(FILE_CONSTRUCTORS)))
        )
    slicing = offset_shape_to_slicing(offset, shape)
    return FILE_CONSTRUCTORS[stripped](path, internal_path, slicing)


def dataviewer_from_file(path, internal_path=None, ftype=None, offset=None, shape=None, **kwargs):
    """
    Instantiate a DataViewer from a path to a file in a variety of formats.

    Note: if this is not assigned to a variable, it may be garbage collected before plt.show() is called.

    Parameters
    ----------
    path : str or PathLike
        Path to dataset file
    internal_path : str, optional
        For dataset file types which need it, an internal path to the dataset
    ftype : {'n5', 'hdf5', 'zarr', 'npy', 'npz', 'json'}, optional
        File type. By default, infer from path extension.
    offset : array-like, optional
        Offset of ROI from (0, 0, 0). By default, start at (0, 0, 0)
    shape : array-like, optional
        Shape of ROI. By default, take the whole array.
    kwargs
        Passed to DataViewer constructor after ``volume``

    Returns
    -------
    DataViewer
    """

    vol = read_file(path, internal_path, ftype, offset, shape)
    return DataViewer(vol, **kwargs)
