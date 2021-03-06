from __future__ import print_function, division

import numpy as np
from skimage.morphology import binary_erosion, disk, ball

from _set_metrics import hausdorff_distance_onesided


def binary_find_boundaries(image):
    if image.dtype != np.bool:
        raise ValueError('image must have dtype = \'bool\'')
    if image.ndim == 2:
        selem = disk(1)
    elif image.ndim == 3:
        selem = ball(1)
    else:
        raise ValueError('image must be 2D or 3D')
    eroded = binary_erosion(image, selem)
    return (image & (~eroded))


def hausdorff_distance(a, b):
    """Calculate the Hausdorff distance [1] between two sets.

    :param a: Array containing the coordinates of ``N`` points in an ``M`` dimensional space.
    :type a: ndarray.
    :param b: Array containing the coordinates of ``N`` points in an ``M`` dimensional space.
    :type b: ndarray.
    :returns: float -- The Hausdorff distance between the sets represented by ``a`` and ``b`` using Euclidian distance to calculate the distance between members of the sets.

    .. [1] http://en.wikipedia.org/wiki/Hausdorff_distance

    """
    if a.ndim != 2 or b.ndim != 2:
        raise ValueError('Both input arrays must be two-dimensional')
    if a.shape[1] != b.shape[1]:
        raise ValueError('Second dimension of the arrays must be equal')

    # Handle empty sets properly
    if a.shape[0] == 0 or b.shape[0] == 0:
        if a.shape[0] == b.shape[0]:
            # Both sets are empty and thus the distance is zero
            return 0.
        else:
            # Exactly one set is empty; the distance is infinite
            return np.inf

    a = np.require(a, np.float64, ['C'])
    b = np.require(b, np.float64, ['C'])
    return max(hausdorff_distance_onesided(a, b),
               hausdorff_distance_onesided(b, a))


def hausdorff_distance_region(a, b):
    """Calculate the Hausdorff distance [2] between two binary images.

    :param a: Array where ``True`` represents a point that is included in a set of points. Both arrays must have the same shape.
    :type a: ndarray, dtype=bool.
    :param b: Array where ``True`` represents a point that is included in a set of points. Both arrays must have the same shape.
    :type b: ndarray, dtype=bool.
    :returns: float -- The Hausdorff distance between the sets represented by ``a`` and ``b`` using Euclidian distance to calculate the distance between members of the sets.

    .. [2] http://en.wikipedia.org/wiki/Hausdorff_distance

    """
    if a.dtype != np.bool or b.dtype != np.bool:
        raise ValueError('Arrays must have dtype = \'bool\'')
    if a.shape != b.shape:
        raise ValueError('Array shapes must be identical')

    a_points = np.transpose(np.nonzero(a))
    b_points = np.transpose(np.nonzero(b))
    return hausdorff_distance(a_points, b_points)
