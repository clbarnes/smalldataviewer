#!/usr/bin/env python
from __future__ import division

import json
import logging
import os
import functools
import warnings

import numpy as np

from smalldataviewer.ext import h5py, z5py, PIL

__all__ = ['read_file']


logger = logging.getLogger(__name__)


def internal_path(has_ipath):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapped(path, internal_path, slicing):
            if has_ipath and internal_path is None:
                raise ValueError('internal_path required by this file format')
            if not has_ipath and internal_path is not None:
                warnings.warn(
                    'internal_path not required by this file format: {} will be ignored'.format(internal_path)
                )
            return fn(path, internal_path, slicing)
        return wrapped
    return decorator


@internal_path(False)
def _read_npy(path, internal_path, slicing):
    return np.load(path)[slicing]


@internal_path(True)
def _read_n5(path, internal_path, slicing):
    with z5py.File(path, False) as f:
        return np.asarray(f[internal_path][slicing])


@internal_path(True)
def _read_zarr(path, internal_path, slicing):
    with z5py.File(path, True) as f:
        return np.asarray(f[internal_path][slicing])


@internal_path(True)
def _read_hdf5(path, internal_path, slicing):
    with h5py.File(path, mode='r') as f:
        return np.asarray(f[internal_path][slicing])


@internal_path(True)
def _read_npz(path, internal_path, slicing):
    with np.load(path) as f:
        return np.asarray(f[internal_path][slicing])


@internal_path(False)
def _read_imagesequence(path, internal_path, slicing):
    """multitiff"""
    img = PIL.Image.open(path)
    zmin, zmax = slicing[0].start, slicing[0].stop
    tiles = []
    for idx, frame in enumerate(PIL.ImageSequence.Iterator(img)):
        if idx < (zmin or 0):
            continue
        if zmax is not None and idx >= zmax:
            break

        width = frame.size[0]
        height = frame.size[1]
        subframe = frame.crop((
            slicing[2].start or 0,  # xmin
            slicing[1].start or 0,  # ymin
            slicing[2].stop or width,  # xmax
            slicing[1].stop or height  # ymax
        ))
        tiles.append(np.asarray(subframe))
    return np.array(tiles)


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
    'json': _read_json,
    'tif': _read_imagesequence,
    'tiff': _read_imagesequence,
}


def offset_shape_to_slicing(offset=None, shape=None):
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


def read_file(path, internal_path=None, offset=None, shape=None, ftype=None):
    if ftype is None:
        ftype = os.path.splitext(str(path))[1]

    stripped = ftype.lstrip('.').lower()

    if stripped not in FILE_CONSTRUCTORS:
        raise KeyError('File type {} not recognised; use one of \n\t{}'.format(
            ftype, ', '.join(sorted(FILE_CONSTRUCTORS)))
        )
    slicing = offset_shape_to_slicing(offset, shape)
    return FILE_CONSTRUCTORS[stripped](path, internal_path, slicing)
