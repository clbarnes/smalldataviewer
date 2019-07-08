import json
import warnings

import numpy as np
import pytest

from smalldataviewer.ext import h5py, NoSuchModule, z5py, imageio
from tests.constants import INTERNAL_PATH


def hdf5_file(path, array):
    if isinstance(h5py, NoSuchModule):
        pytest.skip("h5py not installed")

    with h5py.File(path, "w") as f:
        f.create_dataset(INTERNAL_PATH, data=array)
    return True


def npy_file(path, array):
    np.save(path, array)
    return False


def npz_file(path, array):
    np.savez(path, **{INTERNAL_PATH: array})
    return True


def json_file(path, array):
    with open(path, "w") as f:
        json.dump({INTERNAL_PATH: array.tolist()}, f)
    return True


def json_file_no_path(path, array):
    with open(path, "w") as f:
        json.dump(array.tolist(), f)
    return False


def n5_file(path, array):
    if isinstance(z5py, NoSuchModule):
        pytest.skip("z5py not installed")

    with z5py.File(path, use_zarr_format=False) as f:
        ds = f.create_dataset(
            INTERNAL_PATH, shape=array.shape, dtype=array.dtype, chunks=(10, 10, 10)
        )
        ds[:] = array
    return True


def zarr_file(path, array):
    if isinstance(z5py, NoSuchModule):
        pytest.skip("z5py not installed")

    with z5py.File(path, use_zarr_format=True) as f:
        ds = f.create_dataset(
            INTERNAL_PATH, shape=array.shape, dtype=array.dtype, chunks=(10, 10, 10)
        )
        ds[:] = array
    return True


def imageio_mim_file(path, array):
    if isinstance(imageio, NoSuchModule):
        pytest.skip("imageio not installed")

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message=".*_tifffile")
        imageio.mimwrite(path, array)
    return False


def imageio_vol_file(path, array):
    if isinstance(imageio, NoSuchModule):
        pytest.skip("imageio not installed")

    imageio.volwrite(path, array)
    return False


file_constructors = [
    ("hdf5", hdf5_file),
    ("npy", npy_file),
    ("npz", npz_file),
    ("json", json_file),
    ("json", json_file_no_path),
    ("n5", n5_file),
    ("zarr", zarr_file),
    ("tiff", imageio_mim_file),
    ("gif", imageio_mim_file),
    ("bsdf", imageio_mim_file),
    # ('dcm', imageio_mim_file),  # imageio cannot write
    ("swf", imageio_mim_file),
]
