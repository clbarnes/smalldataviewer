#!/usr/bin/env python
from __future__ import division

import json
import logging
import os
import functools
import warnings

import numpy as np

from smalldataviewer.ext import h5py, z5py, imageio

__all__ = ['FileReader']


logger = logging.getLogger(__name__)


NORMALISED_TYPES = {
    'n5': 'n5',
    'hdf': 'hdf5',
    'h5': 'hdf5',
    'hdf5': 'hdf5',
    'zarr': 'zarr',
    'zr': 'zarr',
    'npy': 'npy',
    'npz': 'npz',
    'json': 'json',
}


def check_internal_path(has_ipath):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapped(obj):
            if has_ipath and obj.internal_path is None:
                raise ValueError('internal_path required by this file format')
            if not has_ipath and obj.internal_path is not None:
                warnings.warn(
                    'internal_path not required by this file format: {} will be ignored'.format(check_internal_path)
                )
            return fn(obj)
        return wrapped
    return decorator


def offset_shape_to_slicing(offset=None, shape=None):
    if offset is None and shape is None:
        return Ellipsis

    slices = []
    for o, s in zip(offset or (None, None, None), shape or (None, None, None)):
        if s is None:
            end = None
        elif o is None:
            end = s
        else:
            end = o + s
        slices.append(slice(o, end))
    return tuple(slices)


class FileReader:
    def __init__(self, path, offset=None, shape=None, internal_path=None, ftype=None):
        """
        A class which can read a variety of volumetric data formats.

        Parameters
        ----------
        path : str or PathLike
            Path to data file
        offset : array-like, optional
            Default (0, 0, 0)
        shape : array-like, optional
            Default everything from ``offset`` to the end
        internal_path : str, optional
            Path to data within file, if required
        ftype : str, optional
            Override file format inferred from ``path``
        """
        self.path = str(path)
        self.slicing = offset_shape_to_slicing(offset, shape)
        self.internal_path = internal_path
        self.explicit_ftype = ftype
        if ftype is None:
            ftype = os.path.splitext(str(path))[1]

        self.inferred_ftype = NORMALISED_TYPES.get(ftype.lstrip('.').lower())

    def read(self):
        """

        Returns
        -------
        np.ndarray
        """
        if not self.inferred_ftype:
            return self._read_imageio()

        return getattr(self, '_read_' + self.inferred_ftype)()

    def _slice_if_necessary(self, arr):
        """Slice if self.slicing is not all, otherwise do not (avoid copying)"""
        if self.slicing == Ellipsis:
            return np.asarray(arr)
        else:
            return np.asarray(arr)[self.slicing]

    @check_internal_path(False)
    def _read_npy(self):
        whole_arr = np.load(self.path)
        return self._slice_if_necessary(whole_arr)

    @check_internal_path(True)
    def _read_n5(self):
        with z5py.File(self.path, False, mode='r') as f:
            return np.asarray(f[self.internal_path][self.slicing])

    @check_internal_path(True)
    def _read_zarr(self):
        with z5py.File(self.path, True, mode='r') as f:
            return np.asarray(f[self.internal_path][self.slicing])

    @check_internal_path(True)
    def _read_hdf5(self):
        with h5py.File(self.path, mode='r') as f:
            return np.asarray(f[self.internal_path][self.slicing])

    @check_internal_path(True)
    def _read_npz(self):
        with np.load(self.path) as f:
            return self._slice_if_necessary(f[self.internal_path])

    @check_internal_path(False)
    def _read_imageio(self):
        slicing = [slice(None, None) for _ in range(3)] if self.slicing == Ellipsis else self.slicing
        zmin, zmax = slicing[0].start or 0, slicing[0].stop
        reader = imageio.get_reader(self.path, format=self.explicit_ftype)

        tiles = []
        for idx, frame in enumerate(reader):
            if idx < zmin:
                continue
            if zmax is not None and idx >= zmax:
                break

            subframe = frame[slicing[1:]]
            tiles.append(np.asarray(subframe))
        return np.array(tiles)

    def _read_json(self):
        with open(self.path) as f:
            obj = json.load(f)

        if self.internal_path:
            obj = obj[self.internal_path]

        return self._slice_if_necessary(obj)
