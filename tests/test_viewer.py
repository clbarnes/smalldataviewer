import numpy as np
import pytest

from smalldataviewer.viewer import DataViewer

from tests.common import array, subplots_patch


def test_can_instantiate(array, subplots_patch):
    dv = DataViewer(array)


@pytest.mark.parametrize('dims,match', [
    [2, '2D'],
    [4, 'colour channels'],
    [5, 'more than 4']
])
def test_error_on_wrong_dims(dims, match, subplots_patch):
    array = np.ones((10,) * dims)
    with pytest.raises(ValueError, match=match):
        DataViewer(array)


class DummyEvent(object):
    def __init__(self, button):
        self.button = button


@pytest.mark.parametrize('button,should_draw', [
    ('up', True),
    ('down', True),
    ('other', False)
])
def test_onscroll_event_updates(button, should_draw, array, subplots_patch):
    dv = DataViewer(array)
    event = DummyEvent(button)
    dv.idx = int(array.shape[0]/2)
    dv.im.axes.figure.canvas.draw.reset_mock()
    starting_idx = dv.idx
    dv._onscroll(event)
    assert dv.im.axes.figure.canvas.draw.call_count == int(should_draw)
    if should_draw:
        assert starting_idx != dv.idx
    else:
        assert starting_idx == dv.idx


@pytest.mark.parametrize('button,starting_idx,finishing_idx', [
    ('up', 0, 1),
    ('down', 0, 0)
])
def test_onscroll_event_has_limits(button, starting_idx, finishing_idx, array, subplots_patch):
    dv = DataViewer(array)
    event = DummyEvent(button)
    dv.idx = starting_idx
    dv.im.axes.figure.canvas.draw.reset_mock()
    dv._onscroll(event)
    assert dv.idx == finishing_idx
