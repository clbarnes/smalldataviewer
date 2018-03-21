import json

import pytest
try:
    from unittest import mock
except ImportError:
    import mock

import numpy as np
import h5py


OFFSET = (10, 10, 10)
SHAPE = (20, 20, 20)
PADDED_SHAPE = tuple(s + o*2 for s, o in zip(SHAPE, OFFSET))

VALUE = 10
PAD_VALUE = 1

INTERNAL_PATH = 'volume'


@pytest.fixture
def array():
    return np.ones(SHAPE, dtype=np.uint8) * VALUE


@pytest.fixture
def padded_array(array):
    padded = np.ones(shape=PADDED_SHAPE, dtype=np.uint8) * PAD_VALUE
    slices = [slice(o, o+s) for o, s in zip(OFFSET, SHAPE)]
    padded[slices] = array
    return padded


@pytest.fixture
def hdf5_file(tmpdir, padded_array):
    path = str(tmpdir.join('data.hdf5'))
    with h5py.File(path, 'w') as f:
        f.create_dataset(INTERNAL_PATH, data=padded_array)
    return path


@pytest.fixture
def npy_file(tmpdir, padded_array):
    path = str(tmpdir.join('data.npy'))
    np.save(path, padded_array)
    return path


@pytest.fixture
def npz_file(tmpdir, padded_array):
    path = str(tmpdir.join('data.npz'))
    np.savez(path, **{INTERNAL_PATH: padded_array})
    return path


@pytest.fixture
def json_file(tmpdir, padded_array):
    path = str(tmpdir.join('data.json'))
    with open(path, 'w') as f:
        json.dump({INTERNAL_PATH: padded_array.tolist()}, f)
    return path


@pytest.fixture
def json_file_no_path(tmpdir, padded_array):
    path = str(tmpdir.join('data_no_path.json'))
    with open(path, 'w') as f:
        json.dump(padded_array.tolist(), f)
    return path


@pytest.fixture
def n5_file(tmpdir, padded_array):
    pytest.xfail('z5py is incompatible with tox, cannot test N5 utilities')


@pytest.fixture
def zarr_file(tmpdir, padded_array):
    pytest.xfail('z5py is incompatible with tox, cannot test Zarr utilities')


@pytest.fixture
def subplots_patch():
    with mock.patch('matplotlib.pyplot.subplots', return_value=(mock.Mock(), mock.Mock())) as sp_mock:
        yield sp_mock
