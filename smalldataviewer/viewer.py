#!/usr/bin/env python
"""Adapted from https://matplotlib.org/gallery/animation/image_slices_viewer.html"""

from __future__ import division

import logging

import matplotlib.pyplot as plt

__all__ = ['DataViewer']


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

    def show(self):
        """Show the viewer. Note that the viewer will no longer scroll if the script ends: use ``plt.show`` for that"""
        self.fig.show()

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
