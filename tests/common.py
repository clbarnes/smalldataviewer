import json
import warnings

import pytest
try:
    from unittest import mock
except ImportError:
    import mock

import numpy as np
from smalldataviewer.ext import h5py, z5py, imageio, NoSuchModule


OFFSET = (10, 10, 10)
SHAPE = (20, 20, 20)
PADDED_SHAPE = tuple(s + o*2 for s, o in zip(SHAPE, OFFSET))

PAD_VALUE = 1

INTERNAL_PATH = 'volume'


@pytest.fixture
def array():
    np.random.seed(1)
    return np.random.randint(PAD_VALUE+1, 256, SHAPE, dtype=np.uint8)


@pytest.fixture
def padded_array(array):
    padded = np.ones(shape=PADDED_SHAPE, dtype=np.uint8) * PAD_VALUE
    slices = [slice(o, o+s) for o, s in zip(OFFSET, SHAPE)]
    padded[slices] = array
    return padded


def hdf5_file(path, array):
    if isinstance(h5py, NoSuchModule):
        pytest.skip('h5py not installed')

    with h5py.File(path, 'w') as f:
        f.create_dataset(INTERNAL_PATH, data=array)
    return True


def npy_file(path, array):
    np.save(path, array)
    return False


def npz_file(path, array):
    np.savez(path, **{INTERNAL_PATH: array})
    return True


def json_file(path, array):
    with open(path, 'w') as f:
        json.dump({INTERNAL_PATH: array.tolist()}, f)
    return True


def json_file_no_path(path, array):
    with open(path, 'w') as f:
        json.dump(array.tolist(), f)
    return False


def n5_file(path, array):
    if isinstance(z5py, NoSuchModule):
        pytest.skip('z5py not installed')

    with z5py.File(path, use_zarr_format=False) as f:
        ds = f.create_dataset(INTERNAL_PATH, shape=array.shape, dtype=array.dtype, chunks=(10, 10, 10))
        ds[:] = array
    return True


def zarr_file(path, array):
    if isinstance(z5py, NoSuchModule):
        pytest.skip('z5py not installed')

    with z5py.File(path, use_zarr_format=True) as f:
        ds = f.create_dataset(INTERNAL_PATH, shape=array.shape, dtype=array.dtype, chunks=(10, 10, 10))
        ds[:] = array
    return True


def imageio_mim_file(path, array):
    if isinstance(imageio, NoSuchModule):
        pytest.skip('imageio not installed')

    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', message='.*_tifffile')
        imageio.mimwrite(path, array)
    return False


def imageio_vol_file(path, array):
    if isinstance(imageio, NoSuchModule):
        pytest.skip('imageio not installed')

    imageio.volwrite(path, array)
    return False


file_constructors = [
    ('hdf5', hdf5_file),
    ('npy', npy_file),
    ('npz', npz_file),
    ('json', json_file),
    ('json', json_file_no_path),
    ('n5', n5_file),
    ('zarr', zarr_file),
    ('tiff', imageio_mim_file),
    ('gif', imageio_mim_file),
    ('bsdf', imageio_mim_file),
    # ('dcm', imageio_mim_file),  # imageio cannot write
    ('swf', imageio_mim_file),
]


@pytest.fixture(params=file_constructors, ids=lambda pair: pair[0])
def data_file(request, tmpdir, padded_array):
    ext, fn = request.param
    path = str(tmpdir.join('data.' + ext))
    requires_internal = fn(path, padded_array)
    return path, requires_internal


@pytest.fixture
def subplots_patch():
    with mock.patch('matplotlib.pyplot.subplots', return_value=(mock.Mock(), mock.Mock())) as sp_mock:
        yield sp_mock
