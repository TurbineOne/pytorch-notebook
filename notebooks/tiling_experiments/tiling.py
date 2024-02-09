# Python libraries
from dataclasses import dataclass
from typing import List

# Third-party libraries
import numpy as np


@dataclass
class Point:
    """A point in 2D space."""
    x: int
    y: int


@dataclass
class ImageTile:
    """A tile of an image."""
    tile: np.ndarray
    x: int
    y: int
    image_width: int
    image_height: int

    def get_global(self, x: int, y: int) -> (int, int):
        """Returns the global coordinates of a point in the tile."""
        return Point(x + self.x, y + self.y)
    
    def get_global_relative(self, x: int, y: int) -> (int, int):
        """Returns the global coordinates of a relative point in the tile."""
        return Point(
            (x + self.x) / self.image_width,
            (y + self.y) / self.image_height
        )


def get_stride_points(
        image_dim: int, tile_dim: int, overlap: float) -> np.ndarray:
    """Returns the origin points along a 1D axis.

    When tiling an image, it is necessary to determine the origin (upper left)
    coordinates of each tile. This method returns the origin points along a 1D
    axis given the image width and the overlap between tiles.

    Args:
        image_dim: The length of the image along a given dimension.
        tile_dim: The length of the tile along the same dimension.
        overlap: The percentage of overlap between tiles. This value must be
            between 0 and 1.

    Returns:
        A numpy array of origin points.
    """
    if tile_dim >= image_dim:
        return np.array([0])
    stride = int(tile_dim * (1 - overlap))
    entries = int(((image_dim - tile_dim) / stride) + 1)
    indices = np.indices((entries,)).reshape((-1,))
    coords = np.multiply(indices, stride)
    if coords[-1] + tile_dim < image_dim:
        coords = np.append(coords, image_dim - tile_dim)
    return coords


def tile_image(
        image: np.ndarray, tile_width: int = 640, tile_height: int = 480,
        overlap: float = 0.25) -> List[ImageTile]:
    """Tiles an image into smaller images as needed.

    The methods returns a list of views onto the original data to prevent from
    making copies.

    Args:
        image: The image to tile. The image is expected to have height and width
            as the first two dimensions.
        tile_width: The width of the tiles.
        tile_height: The height of the tiles.
        overlap: The amount of overlap between tiles.

    Returns:
        A tuple where the first array contains (y,x) coordinates and the second
        array contains the image tiles. Corresponding indices into the first
        dimension of both arrays will correlate. For example, given:
            `(indices, images) = tile_image(...)`
        Then `indices[0]` might be the array `[0, 0]` which are the y, x
        coordinates of the upper left corner of the image in `images[0]` as it
        appears in the original image.
    """
    image = np.array(image) if not isinstance(image, np.ndarray) else image
    image_height, image_width = image.shape[:2]

    if tile_width >= image_width and tile_height >= image_height:
        return [ImageTile(image, 0, 0, image_width, image_height)]

    window_height = tile_height if tile_height < image_height else image_height
    window_width = tile_width if tile_width < image_width else image_width

    # Create the origin points for the tiles.
    y_coords = get_stride_points(image_height, window_height, overlap)
    x_coords = get_stride_points(image_width, window_width, overlap)
    coords = np.array(np.meshgrid(y_coords, x_coords)).T.reshape((-1, 2))

    # Create the tiles.
    return [
        ImageTile(
            image[y:y + window_height, x:x + window_width],
            x, y, image_width, image_height)
        for (y, x) in coords
    ]


def pad_square(image: np.ndarray) -> np.ndarray:
    """Pads an image with black pixels to make it square.

    This method assumes that image is a height x width x channels array. The
    padding is added to the right or the bottom of the image so that it can be
    removed without affecting annotations in the coordinate space.
    """
    height, width = image.shape[:2]
    if height == width:
        return image
    
    if height > width:
        pad_value = np.zeros((
            height, height - width, image.shape[2]), dtype=image.dtype)
        return np.concatenate((image, pad_value), axis=1)
    else:
        pad_value = np.zeros((
            width - height, width, image.shape[2]), dtype=image.dtype)
        return np.concatenate((image, pad_value), axis=0)