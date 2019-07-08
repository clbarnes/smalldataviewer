from unittest import mock

import numpy as np
import pytest

from tests.constants import PAD_VALUE, SHAPE, PADDED_SHAPE, OFFSET
from tests.file_helpers import file_constructors


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