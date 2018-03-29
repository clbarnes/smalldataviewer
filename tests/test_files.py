import os

import numpy as np
import pytest
try:
    from unittest import mock
except ImportError:
    import mock

from smalldataviewer import DataViewer
from smalldataviewer.files import (read_file, offset_shape_to_slicing)

from tests.common import (INTERNAL_PATH, OFFSET, SHAPE, data_file, array, padded_array, subplots_patch)


@pytest.mark.parametrize('offset,shape,expected', [
    [None, None, (slice(None), slice(None), slice(None))],
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

    data = read_file(path, internal_path=ipath, offset=OFFSET, shape=SHAPE)
    assert np.allclose(data, array)


def test_read_file_raises_or_warns(data_file):
    path, has_ipath = data_file

    if path.endswith('.json'):
        return  # json can have either internal path or not

    if has_ipath:
        with pytest.raises(ValueError):
            read_file(path)
    else:
        with pytest.warns(UserWarning):
            read_file(path, INTERNAL_PATH)


def test_read_file_ftype_overrides(data_file, array):
    path, has_ipath = data_file
    _, ext = os.path.splitext(path)
    new_path = path + '.txt'
    os.rename(path, new_path)

    if has_ipath:
        assert np.allclose(
            read_file(new_path, internal_path=INTERNAL_PATH, offset=OFFSET, shape=SHAPE, ftype=ext), array
        )
    else:
        assert np.allclose(read_file(new_path, offset=OFFSET, shape=SHAPE, ftype=ext), array)


def test_dataviewer_from_file(data_file, array, subplots_patch):
    path, has_ipath = data_file

    if has_ipath:
        dv = DataViewer.from_file(path, internal_path=INTERNAL_PATH, offset=OFFSET, shape=SHAPE)
    else:
        dv = DataViewer.from_file(path, offset=OFFSET, shape=SHAPE)

    assert np.allclose(dv.volume, array)
