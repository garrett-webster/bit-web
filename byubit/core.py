from dataclasses import dataclass
from typing import Optional, Protocol, Tuple, List

import matplotlib
import matplotlib.markers
import numpy as np
from matplotlib import pyplot as plt
import webcolors

SCALE = 0.5

EMPTY = 0
BLACK = 1
ORANGE = 2
GREEN = 4
YELLOW = 5
BLUE = 6
RED = 7
PURPLE = 8


_names_to_colors = {
    None: EMPTY,
    'black': BLACK,
    'orange': ORANGE,
    'green': GREEN,
    'yellow': YELLOW,
    'blue': BLUE,
    'red': RED,
    'purple': PURPLE
}

light_colors = {
    'orange': '#E69F00',
    'green': '#009E73',
    'yellow': '#F0E442',
    'blue': '#0072B2',
    'red': '#DC3220',
    'purple': '#5D3A9B'
}

_bw_colors_to_names = {
    v: light_colors.get(k, k)
    for k, v in _names_to_colors.items()
}
DARKBIT = '#005555'

_codes_to_colors = {
    "-": EMPTY,
    "k": BLACK,
    'o': ORANGE,
    'g': GREEN,
    'y': YELLOW,
    'b': BLUE,
    'r': RED,
    'p': PURPLE
}

css_colors = [color for color in webcolors.CSS3_NAMES_TO_HEX.keys() if color not in _names_to_colors.keys()]

for i, name in enumerate(css_colors):
    if name not in _codes_to_colors:
        _names_to_colors[name] = ord('¡') + i
        _codes_to_colors[name] = ord('¡') + i


_colors_to_names = {v: k for k, v in _names_to_colors.items()}

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

class ParenthesesException(Exception):
    def __init__(self, message, name,line_number):
        self.message = message
        self.name = name
        self.line_number = line_number

    def __str__(self):
        return self.message


@dataclass
class BitHistoryRecord:
    name: str  # What event produced the associated state?
    error_message: Optional[str]  # Error info
    world: np.array  # 2D list indexed with [x,y]
    pos: np.array  # [x, y]
    orientation: int
    annotations: Optional[Tuple[np.array, np.array, int]]  # world, pos, orientation
    filename: str
    line_number: int


def determine_figure_size(world_shape, min_size=(5.5, 2), max_size=(12, 6)):
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


def draw_record(ax, record: BitHistoryRecord, bwmode=False):
    dims = record.world.shape
    ax.set_aspect('equal')
    color_map = _bw_colors_to_names if bwmode else _colors_to_names

    # Draw squares
    for y in range(dims[1]):
        for x in range(dims[0]):
            ax.add_patch(plt.Rectangle(
                (x, y),
                1, 1,
                color=color_map[record.world[x, y]] or "white")
            )
            if bwmode and record.world[x, y] in [RED, GREEN, BLUE]:
                # Scatter R,G,B symbols on colored patches
                ax.text(x + 0.1, y + 0.1, _colors_to_codes[record.world[x, y]].upper(),
                        fontsize=20, fontweight='bold')

    # Draw the "bit"
    ax.scatter(
        record.pos[0] + 0.5,
        record.pos[1] + 0.5,
        c=DARKBIT if bwmode else 'cyan',
        s=500 if max(dims) < 25 else 300,
        marker=(3, 0, 90 * (-1 + record.orientation))
    )

    if record.annotations is not None:
        annot_world, annot_pos, annot_orient = record.annotations
        # Compare colors
        for x in range(record.world.shape[0]):
            for y in range(record.world.shape[1]):
                if record.world[x, y] != annot_world[x, y]:
                    ax.text(x + 0.6, y + 0.6, "!",
                            fontsize=16, weight='bold',
                            bbox={'facecolor': color_map[annot_world[x, y]] or "white"})
        # Compare Bit position and orientation
        if record.pos[0] != annot_pos[0] \
                or record.pos[1] != annot_pos[1] \
                or record.orientation != annot_orient:
            ax.scatter(
                annot_pos[0] + 0.5,
                annot_pos[1] + 0.5,
                c=DARKBIT if bwmode else 'cyan',
                s=500 if max(dims) < 25 else 300,
                marker=matplotlib.markers.MarkerStyle((3, 1, 90 * (-1 + annot_orient)), fillstyle='none')
            )

    ax.get_xaxis().set_label_position('top')
    ax.get_xaxis().set_ticks([])

    ax.set_xlim([0, dims[0]])
    ax.set_ylim([0, dims[1]])
    ax.get_yaxis().set_visible(False)

    # Draw Grid
    grid_style = dict(c='gray', lw=1)
    for x in range(0, dims[0]):
        ax.plot((x, x), [0, dims[1]], **grid_style)
    for y in range(0, dims[1]):
        ax.plot([0, dims[0]], (y, y), **grid_style)




class BitHistoryRenderer(Protocol):
    def render(self, histories: List[Tuple[str, List[BitHistoryRecord]]]) -> bool:
        """Present the history.
        Return True if there were no errors
        Return False if there were errors
        """
