import os

import numpy as np
import pytest
try:
    from unittest import mock
except ImportError:
    import mock

from smalldataviewer.files import (
    requires_internal_path, _read_npy, _read_hdf5, _read_json, _read_npz, read_file,
    offset_shape_to_slicing, dataviewer_from_file
)

from tests.common import (
    INTERNAL_PATH, OFFSET, SHAPE,
    hdf5_file, npy_file, npz_file, json_file, json_file_no_path, array, padded_array, subplots_patch
)


@pytest.fixture
def files_with_ipath(hdf5_file, npz_file, json_file):
    return [hdf5_file, npz_file, json_file]


@pytest.fixture
def files_with_no_ipath(npy_file, json_file_no_path):
    return [npy_file, json_file_no_path]


def test_requires_internal_path():
    def undecorated(path, internal_path, slicing):
        return path, internal_path, slicing

    decorated = requires_internal_path(undecorated)

    path = 'path'
    internal_path = 'internal_path'
    slicing = 'slicing'

    assert undecorated(path, None, slicing) == (path, None, slicing)
    with pytest.raises(ValueError):
        decorated(path, None, slicing)
    assert decorated(path, internal_path, slicing) == (path, internal_path, slicing)


@pytest.mark.parametrize('offset,shape,expected', [
    [None, None, (slice(None), slice(None), slice(None))],
    [(1, 1, 1), (2, 2, 2), (slice(1, 3), slice(1, 3), slice(1, 3))],
    [None, (2, 2, 2), (slice(None, 2), slice(None, 2), slice(None, 2))],
    [(1, 1, 1), None, (slice(1, None), slice(1, None), slice(1, None))],
    [(1, None, 1), (None, 2, None), (slice(1, None), slice(None, 2), slice(1, None))]
])
def test_offset_shape_to_slicing(offset, shape, expected):
    assert offset_shape_to_slicing(offset, shape) == expected


def test_read_npy(npy_file, array):
    slicing = offset_shape_to_slicing(OFFSET, SHAPE)
    assert np.allclose(_read_npy(npy_file, None, slicing), array)


def test_read_hdf5(hdf5_file, array):
    slicing = offset_shape_to_slicing(OFFSET, SHAPE)
    with pytest.raises(ValueError):
        _read_hdf5(hdf5_file, None, slicing)
    assert np.allclose(_read_hdf5(hdf5_file, INTERNAL_PATH, slicing), array)


def test_read_npz(npz_file, array):
    slicing = offset_shape_to_slicing(OFFSET, SHAPE)
    assert np.allclose(_read_npz(npz_file, INTERNAL_PATH, slicing), array)


def test_read_json(json_file, array):
    slicing = offset_shape_to_slicing(OFFSET, SHAPE)
    assert np.allclose(_read_json(json_file, INTERNAL_PATH, slicing), array)


def test_read_json_no_path(json_file_no_path, array):
    slicing = offset_shape_to_slicing(OFFSET, SHAPE)
    assert np.allclose(_read_json(json_file_no_path, None, slicing), array)


def test_read_file_infers_type(files_with_ipath, files_with_no_ipath, array):
    for path in files_with_ipath:
        assert np.allclose(read_file(path, internal_path=INTERNAL_PATH, offset=OFFSET, shape=SHAPE), array)
    for path in files_with_no_ipath:
        assert np.allclose(read_file(path, offset=OFFSET, shape=SHAPE), array)


def test_read_file_ftype_overrides(files_with_ipath, files_with_no_ipath, array):
    for path in files_with_ipath:
        _, ext = os.path.splitext(path)
        new_path = path + '.txt'
        os.rename(path, new_path)
        assert np.allclose(read_file(new_path, internal_path=INTERNAL_PATH, offset=OFFSET, shape=SHAPE, ftype=ext), array)
    for path in files_with_no_ipath:
        _, ext = os.path.splitext(path)
        new_path = path + '.txt'
        os.rename(path, new_path)
        assert np.allclose(read_file(new_path, None, offset=OFFSET, shape=SHAPE, ftype=ext), array)


def test_dataviewer_from_file(npy_file, array, subplots_patch):
    dv = dataviewer_from_file(npy_file, offset=OFFSET, shape=SHAPE)
    assert np.allclose(dv.volume, array)
