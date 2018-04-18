import os

import numpy as np
import pytest
try:
    from unittest import mock
except ImportError:
    import mock

from smalldataviewer import DataViewer
from smalldataviewer.files import offset_shape_to_slicing, FileReader

from tests.common import (INTERNAL_PATH, OFFSET, SHAPE, data_file, array, padded_array, subplots_patch)


@pytest.mark.parametrize('offset,shape,expected', [
    [None, None, Ellipsis],
    [(1, 1, 1), (2, 2, 2), (slice(1, 3), slice(1, 3), slice(1, 3))],
    [None, (2, 2, 2), (slice(None, 2), slice(None, 2), slice(None, 2))],
    [(1, 1, 1), None, (slice(1, None), slice(1, None), slice(1, None))],
    [(1, None, 1), (None, 2, None), (slice(1, None), slice(None, 2), slice(1, None))]
])
def test_offset_shape_to_slicing(offset, shape, expected):
    assert offset_shape_to_slicing(offset, shape) == expected


def test_read_file(data_file, array):
    path, has_ipath = data_file

    ipath = INTERNAL_PATH if has_ipath else None

    data = FileReader(path, internal_path=ipath, offset=OFFSET, shape=SHAPE).read()

    if path.endswith('swf'):
        pytest.xfail('swf comparison is hard due to compression and dimensions')

    assert np.allclose(data, array)


def test_read_file_raises_or_warns(data_file):
    path, has_ipath = data_file

    if path.endswith('.json'):
        return  # json can have either internal path or not

    if has_ipath:
        with pytest.raises(ValueError):
            FileReader(path).read()
    else:
        with pytest.warns(UserWarning):
            FileReader(path, internal_path=INTERNAL_PATH).read()


def test_read_file_ftype_overrides(data_file, array):
    path, has_ipath = data_file
    _, ext = os.path.splitext(path)
    new_path = path + '.txt'
    os.rename(path, new_path)

    read_array = FileReader(
        new_path, internal_path=INTERNAL_PATH if has_ipath else None, offset=OFFSET, shape=SHAPE, ftype=ext
    ).read()

    if path.endswith('swf'):
        pytest.xfail('swf comparison is hard due to compression and dimensions')

    assert np.allclose(read_array, array)


def test_dataviewer_from_file(data_file, array, subplots_patch):
    path, has_ipath = data_file

    if has_ipath:
        dv = DataViewer.from_file(path, internal_path=INTERNAL_PATH, offset=OFFSET, shape=SHAPE)
    else:
        dv = DataViewer.from_file(path, offset=OFFSET, shape=SHAPE)

    if path.endswith('swf'):
        pytest.xfail('swf comparison is hard due to compression and dimensions')

    assert np.allclose(dv.volume, array)
