#!/usr/bin/env python
"""Adapted from https://matplotlib.org/gallery/animation/image_slices_viewer.html"""

from __future__ import division

import logging
import os
from argparse import ArgumentParser
from collections import namedtuple
from contextlib import contextmanager

import functools
import matplotlib.pyplot as plt
import numpy as np

__all__ = ['DataViewer', 'dataviewer_from_file']


logger = logging.getLogger(__name__)


class DataViewer(object):
    def __init__(self, volume, data_order='zyx', cmap=None, **kwargs):
        """
        Class used to view a dataset with 3 spatial dimensions as image slices. The dimension 0 will be scrolled
        through, dimension 1 will on the up-down axis, dimension 2 will be on the left-right axis, and dimension 3 will
        be interpreted as colour channels.

        Parameters
        ----------
        volume : array-like
            Anything with a numpy-like slicing interface, in 3 spatial dimensions and up to 4 colour channels
        data_order : str
            Permutation of ``'zyx'`` used for axis labelling (data is usually not transposed).
            If volume is VigraArray, volume is transposed to numpy order (``'zyx'``) and data_order is ignored.
            Default ``'zyx'``
        cmap : str
            ``cmap`` parameter as passed to ``matplotlib.pyplot.imshow``.
            If ``None`` (default), will be set to ``'gray'`` for 3D data and ``None`` for 4D.
        kwargs
            Passed to ``matplotlib.pyplot.imshow``.
        """
        logger.debug('Volume of shape {} and type {} received'.format(volume.shape, type(volume).__name__))

        if not all(dim in data_order for dim in 'zyx'):
            raise ValueError('Data order must include z, y and x dimensions')

        try:
            self.volume = volume.transposeToNumpyOrder()
            logger.info('Transposing VigraArray to numpy order, ignoring data_order argument')
            data_order = 'zyx'
        except AttributeError:
            self.volume = volume

        self.slices = self.volume.shape[0]
        self.idx = 0
        self.title_formatstr = '{} = {{}} (last = {})'.format(data_order[0], self.slices - 1)

        if self.volume.ndim == 2:
            raise ValueError('Data is 2D: just use plt.imshow')
        elif self.volume.ndim == 3:
            cmap = cmap or 'gray'
        elif self.volume.ndim == 4:
            if self.volume.shape[-1] > 4:
                raise ValueError('Data has >4 colour channels, cannot display')
        else:
            raise ValueError('Data has more than 4 dimensions including colour channels, cannot display')

        self.fig, self.ax = plt.subplots(1, 1)
        self.im = self.ax.imshow(self._slice, cmap=cmap, **kwargs)
        self.ax.set_ylabel(data_order[1])
        self.ax.set_xlabel(data_order[2])
        self._update()
        self.fig.canvas.mpl_connect('scroll_event', self._onscroll)

    def show(self, block=False):
        self.fig.show(block)

    def _onscroll(self, event):
        step = 1
        if event.button == 'up' and self.idx < self.slices - 1:
            logger.debug('Scrolling forward by %s', step)
            self.idx += step
        elif event.button == 'down' and self.idx > 0:
            logger.debug('Scrolling back by %s', step)
            self.idx -= step
        else:
            return
        self._update()

    @property
    def _slice(self):
        return self.volume[self.idx, ...]

    def _update(self):
        self.im.set_data(self._slice)
        self.ax.set_title(self.title_formatstr.format(self.idx))
        self.im.axes.figure.canvas.draw()


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


FILE_CONSTRUCTORS = {
    'n5': _read_n5,
    'hdf': _read_hdf5,
    'h5': _read_hdf5,
    'hdf5': _read_hdf5,
    'zarr': _read_zarr,
    'zr': _read_zarr,
    'npy': _read_npy,
    'npz': _read_npz
}


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
    Instantiate a DataViewer from a path to a file in a variety of formats. Should be used as a context manager.

    Parameters
    ----------
    path : str or PathLike
        Path to dataset file
    internal_path : str or None
        For dataset file types which need it, an internal path to the dataset
    ftype : str or None
    kwargs
        Passed to DataViewer constructor after ``volume``

    Returns
    -------
    DataViewer
    """

    vol = read_file(path, internal_path, ftype, offset, shape)
    return DataViewer(vol, **kwargs)


def str_to_ints(s):
    values = tuple(int(item.strip()) for item in s.split(','))
    if len(values) != 3:
        raise ValueError('Coordinates must have 3 elements')
    return values


def offset_shape_to_slicing(offset=None, shape=None):
    slices = tuple(slice(o, s) for o, s in zip(offset or (None, None, None), shape or (None, None, None)))
    return slices


def _main():
    parser = ArgumentParser()
    parser.add_argument('path',
                        help='Path to HDF5, N5, zarr, npy or npz file containing a 3D dataset')
    parser.add_argument('-i', '--internal_path', help='Internal path of dataset inside HDF5, N5, zarr or npz file')
    parser.add_argument('-t', '--type', help='Dataset file type. Inferred from extension if not given.')
    parser.add_argument('-o', '--order', default='zyx',
                        help='Order of spatial axes for axis labelling purposes. Data is not transposed: '
                             'dimension 0 will be scrolled through, '
                             'dimension 1 will be on the up-down axis, '
                             'dimension 2 will be on the left-right axis, and'
                             'dimension 3, if it exists, will be used as the colour channels. '
                             'Default "zyx".')
    parser.add_argument('-f', '--offset', type=str_to_ints, help='3D offset of ROI from (0, 0, 0) in pixels')
    parser.add_argument('-s', '--shape', type=str_to_ints, help='3D shape of ROI in pixels')
    parser.add_argument('-v', '--verbose', action='count', help='Increase output verbosity')

    parsed_args = parser.parse_args()

    level = {
        0: logging.WARNING,
        1: logging.INFO,
        2: logging.DEBUG,
    }
    logging.basicConfig(level=level.get(parsed_args.verbose, logging.NOTSET))

    dv = dataviewer_from_file(
        parsed_args.path, parsed_args.internal_path, parsed_args.type,
        offset=parsed_args.offset, shape=parsed_args.shape,
        data_order=parsed_args.order
    )
    plt.show()


if __name__ == '__main__':
    _main()
