import logging

from matplotlib import pyplot as plt
from mpl_colors import LabelColorMap

from smalldataviewer import DataViewer, __version__


def str_to_ints(s):
    values = tuple(int(item.strip()) for item in s.split(","))
    if len(values) != 3:
        raise ValueError("Coordinates must have 3 elements")
    return values


def _main():
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("path", help="Path to file containing a 3D dataset")
    parser.add_argument(
        "--version",
        action="version",
        version="smalldataviewer " + __version__,
        help="Print version information and exit",
    )
    parser.add_argument(
        "-i",
        "--internal_path",
        help="Internal path of dataset inside HDF5, N5, zarr or npz file. If JSON, assumes the outer "
        "object is a dict, and internal_path is the key of the array",
    )
    parser.add_argument(
        "-t", "--type", help="Dataset file type. Inferred from extension if not given."
    )
    parser.add_argument(
        "-o",
        "--order",
        default="zyx",
        help="Order of non-channel axes for axis labelling purposes (data is not transposed): "
        "dimension 0 will be scrolled through, "
        "dimension 1 will be on the up-down axis, "
        "dimension 2 will be on the left-right axis, and "
        "dimension 3, if it exists, will be used as the colour channels. "
        'Default "zyx".',
    )
    parser.add_argument(
        "-f",
        "--offset",
        type=str_to_ints,
        help="3D offset of ROI from (0, 0, 0) in pixels, "
        'in the form "<scroll>,<vertical>,<horizontal>"',
    )
    parser.add_argument(
        "-s",
        "--shape",
        type=str_to_ints,
        help='3D shape of ROI in pixels, in the form "<scroll>,<vertical>,<horizontal>"',
    )
    parser.add_argument(
        "-v", "--verbose", action="count", help="Increase logging verbosity"
    )
    parser.add_argument(
        "-l", "--label", action="store_true",
        help="Whether to treat images as a label volume"
    )

    parsed_args = parser.parse_args()

    level = {
        None: logging.WARNING,
        0: logging.WARNING,
        1: logging.INFO,
        2: logging.DEBUG,
    }.get(parsed_args.verbose, logging.NOTSET)

    logging.basicConfig(level=level)

    dv = DataViewer.from_file(
        path=parsed_args.path,
        internal_path=parsed_args.internal_path,
        ftype=parsed_args.type,
        offset=parsed_args.offset,
        shape=parsed_args.shape,
        data_order=parsed_args.order,
        cmap=LabelColorMap(8916) if parsed_args.label else None
    )
    plt.show()


if __name__ == "__main__":
    _main()
