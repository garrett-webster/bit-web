from dataclasses import dataclass
from typing import Optional, Protocol

import numpy as np
from matplotlib import pyplot as plt

SCALE = 0.5

EMPTY = 0
BLACK = 1
RED = 2
GREEN = 3
BLUE = 4

_names_to_colors = {
    None: EMPTY,
    'black': BLACK,
    'red': RED,
    'green': GREEN,
    'blue': BLUE
}

_colors_to_names = {v: k for k, v in _names_to_colors.items()}

_codes_to_colors = {
    "-": EMPTY,
    "k": BLACK,
    "r": RED,
    "g": GREEN,
    "b": BLUE
}

_colors_to_codes = {v: k for k, v in _codes_to_colors.items()}


class MoveOutOfBoundsException(Exception):
    """Raised when Bit tries to move out of bounds"""


class MoveBlockedByBlackException(Exception):
    """Raised when Bit tries to move out of bounds"""


class BitComparisonException(Exception):
    def __init__(self, message, annotations):
        self.message = message
        self.annotations = annotations

    def __str__(self):
        return self.message


class BitInfiniteLoopException(BitComparisonException):
    def __init__(self, message, annotations):
        self.message = message
        self.annotations = annotations

    def __str__(self):
        return self.message

@dataclass
class BitHistoryRecord:
    name: str  # What event produced the associated state?
    error_message: Optional[str]  # Error info
    world: np.array  # 2D list indexed with [x,y]
    pos: np.array  # [x, y]
    orientation: int
    annotations: np.array  # 2D list of expected colors


def determine_figure_size(world_shape, min_size=(5.5, 2), max_size=(12, 8)):
    size = (world_shape[0] * SCALE, world_shape[1] * SCALE)

    # Enforce Min
    if size[0] < min_size[0]:
        size = (min_size[0], world_shape[1] * min_size[0] / world_shape[0])

    if size[1] < min_size[1]:
        size = (world_shape[0] * min_size[1] / world_shape[1], min_size[1])

    # Enforce Max
    if size[0] > max_size[0]:
        size = (max_size[0], world_shape[1] * max_size[0] / world_shape[0])

    if size[1] > max_size[1]:
        size = (world_shape[0] * max_size[1] / world_shape[1], max_size[1])

    return size


def draw_record(ax, record: BitHistoryRecord):
    dims = record.world.shape
    ax.set_aspect('equal')

    # Draw squares
    for y in range(dims[1]):
        for x in range(dims[0]):
            ax.add_patch(plt.Rectangle(
                (x, y),
                1, 1,
                color=_colors_to_names[record.world[x, y]] or "white")
            )

    # Draw the "bit"
    ax.scatter(
        record.pos[0] + 0.5,
        record.pos[1] + 0.5,
        c='cyan',
        s=500 if max(dims) < 25 else 300,
        marker=(3, 0, 90 * (-1 + record.orientation))
    )

    if record.annotations is not None:
        for x in range(record.world.shape[0]):
            for y in range(record.world.shape[1]):
                if record.world[x, y] != record.annotations[x, y]:
                    ax.text(x + 0.6, y + 0.6, "!",
                            fontsize=16, weight='bold',
                            bbox={'facecolor': _colors_to_names[record.annotations[x, y]] or "white"})

    ax.set_title(record.name)
    if record.error_message is not None:
        ax.set_xlabel("⚠️" + record.error_message)

    ax.set_xlim([0, dims[0]])
    ax.set_ylim([0, dims[1]])
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)

    # Draw Grid
    grid_style = dict(c='k', alpha=0.3, lw=0.5)
    for x in range(0, dims[0]):
        ax.plot((x, x), [0, dims[1]], **grid_style)
    for y in range(0, dims[1]):
        ax.plot([0, dims[0]], (y, y), **grid_style)


class BitHistoryRenderer(Protocol):
    def render(self, histories: list[tuple[str, list[BitHistoryRecord]]]) -> bool:
        """Present the history.
        Return True if there were no errors
        Return False if there were errors
        """
