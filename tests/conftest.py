from unittest import mock

import numpy as np
import pytest

from .constants import PAD_VALUE, SHAPE, PADDED_SHAPE, OFFSET, TEST_DIR, PROJECT_DIR
from .file_helpers import file_constructors


@pytest.fixture
def array():
    np.random.seed(1)
    return np.random.randint(PAD_VALUE + 1, 256, SHAPE, dtype=np.uint8)


@pytest.fixture
def padded_array(array):
    padded = np.ones(shape=PADDED_SHAPE, dtype=np.uint8) * PAD_VALUE
    slices = tuple(slice(o, o+s) for o, s in zip(OFFSET, SHAPE))
    padded[slices] = array
    return padded


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


@pytest.fixture
def data_dir():
    dpath = TEST_DIR / "data"
    if not dpath.is_dir():
        rel_path = dpath.relative_to(PROJECT_DIR)
        pytest.fail("Test data directory at '{}' required but not found: run `make data`".format(rel_path))
    return dpath


@pytest.fixture
def data_tif(data_dir):
    fpath = data_dir / "data.tif"
    if not fpath.is_file():
        rel_path = fpath.relative_to(PROJECT_DIR)
        pytest.fail("Test data at '{}' required but not found: run `make data`".format(rel_path))
    return fpath
