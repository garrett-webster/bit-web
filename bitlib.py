# Inspired by Stanford: http://web.stanford.edu/class/cs106a/handouts_w2021/reference-bit.html
from typing import Tuple, Literal

import numpy as np


class MoveOutOfBoundsException(Exception):
    """Raised when Bit tries to move out of bounds"""


class MoveBlockedByBlackException(Exception):
    """Raised when Bit tries to move out of bounds"""


# 0,0  1,0  2,0
# 0,1  1,1, 2,1
# 0,2  1,2, 2,2
# dx and dy
_orientations = [
    np.array((1, 0)),
    np.array((0, 1)),
    np.array((-1, 0)),
    np.array((0, -1))
]

EMPTY = 0
BLACK = 1
RED = 2
GREEN = 3
BLUE = 4

_names_to_colors = {
    'empty': EMPTY,
    'black': BLACK,
    'red': RED,
    'green': GREEN,
    'blue': BLUE
}

_colors_to_names = {v: k for k, v in _names_to_colors.items()}

_codes_to_colors = {
    ".": EMPTY,
    "k": BLACK,
    "r": RED,
    "g": GREEN,
    "b": BLUE
}

_colors_to_codes = {v: k for k, v in _codes_to_colors.items()}


class Bit:
    world: np.array
    pos: np.array  # x and y
    orientation: int  # _orientations[orientation] => dx and dy

    @staticmethod
    def load(filename: str):
        """Parse the file into a new Bit"""
        # open file, parse, return new Bit
        return None

    @staticmethod
    def parse(content: str):
        """Parse the bitmap from a string representation"""
        # Empty lines are ignored
        lines = [line for line in content.split('\n') if line]

        # There must be at least three lines
        assert len(lines) >= 3

        # Position is the second-to-last line
        pos = np.fromstring(lines[-2], sep=" ", dtype=int)

        # Orientation is the last line: 0, 1, 2, 3
        orientation = int(lines[-1].strip())

        # World lines are all lines up to the second-to-last
        # The matrix is stored in transpose of how it is visualized
        #  for convenience with how numpy indexes into 2D arrays
        world = np.array([[_codes_to_colors[code] for code in line] for line in lines[:-2]]).transpose()

        return Bit(world, pos, orientation)

    def __init__(self, world: np.ndarray, pos: np.array, orientation: int):
        self.world = world
        self.pos = pos
        self.orientation = orientation

    def __repr__(self) -> str:
        """Present the bit information as a string"""
        # Transpose self.world because we have it storing x,y
        # but we want to iterate over rows
        world_str = "\n".join("".join(_colors_to_codes[code] for code in row) for row in self.world.transpose())
        pos_str = f"{self.pos[0]} {self.pos[1]}"
        orientation = self.orientation
        return f"{world_str}\n{pos_str}\n{orientation}\n"

    def draw(self):
        """Display the current state of the world"""

    def _next_orientation(self, direction: Literal[1, 0, -1]) -> np.array:
        return (len(_orientations) + self.orientation + direction) % len(_orientations)

    def _get_next_pos(self, turn: Literal[1, 0, -1] = 0) -> np.array:
        return self.pos + _orientations[self._next_orientation(turn)]

    def _pos_in_bounds(self, pos) -> bool:
        return np.logical_and(pos >= 0, pos < self.world.shape).all()

    def move(self):
        """If the direction is clear, move that way"""
        next_pos = self._get_next_pos()
        if not self._pos_in_bounds(next_pos):
            raise MoveOutOfBoundsException(next_pos)
        elif self._get_color_at(next_pos) == BLACK:
            raise MoveBlockedByBlackException(next_pos)
        else:
            self.pos = next_pos

    def left(self):
        """Turn the bit to the left"""
        self.orientation = self._next_orientation(-1)

    def right(self):
        """Turn the bit to the right"""
        self.orientation = self._next_orientation(1)

    def _get_color_at(self, pos):
        return self.world[pos[0], pos[1]]

    def _space_is_clear(self, pos):
        return self._pos_in_bounds(pos) and self._get_color_at(pos) != BLACK

    def front_clear(self) -> bool:
        """Can a move to the front succeed?

        The edge of the world is not clear.

        Black squares are not clear.
        """
        return self._space_is_clear(self._get_next_pos())

    def left_clear(self) -> bool:
        return self._space_is_clear(self._get_next_pos(-1))

    def right_clear(self) -> bool:
        return self._space_is_clear(self._get_next_pos(1))

    def _paint(self, color: int):
        self.world[self.pos[0], self.pos[1]] = color

    def erase(self):
        """Clear the current position"""
        self._paint(EMPTY)

    def paint(self, color):
        """Color the current position with the specified color"""
        if color not in _names_to_colors:
            raise Exception(f"Unrecognized color: {color}. Known colors are: {list(_names_to_colors.keys())}")
        self._paint(_names_to_colors[color])

    def get_color(self) -> str:
        """Return the color at the current position"""
        return _colors_to_names[self._get_color_at(self.pos)]
