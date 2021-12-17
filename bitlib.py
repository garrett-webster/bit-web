# Inspired by Stanford: http://web.stanford.edu/class/cs106a/handouts_w2021/reference-bit.html
from typing import Tuple, Literal

import numpy as np
import matplotlib.pyplot as plt


class MoveOutOfBoundsException(Exception):
    """Raised when Bit tries to move out of bounds"""


class MoveBlockedByBlackException(Exception):
    """Raised when Bit tries to move out of bounds"""


# 0,0  1,0  2,0
# 0,1  1,1, 2,1
# 0,2  1,2, 2,2
# dx and dy
_orientations = [
    np.array((1, 0)),  # Right
    np.array((0, 1)),  # Up
    np.array((-1, 0)),  # Left
    np.array((0, -1))  # Down
]

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


MAX_STEP_COUNT = 1_000_000


# Convention:
# We'll have 0,0 be the origin
# The position defines the X,Y coordinates
class Bit:
    _step_count: int
    world: np.array
    pos: np.array  # x and y
    orientation: int  # _orientations[orientation] => dx and dy

    @staticmethod
    def new_world(size_x, size_y):
        return Bit(np.zeros((size_x, size_y)), (0, 0), 0)

    @staticmethod
    def load(filename: str):
        """Parse the file into a new Bit"""
        with open(filename, 'rt') as f:
            return Bit.parse(f.read())

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
        # We transpose because numpy stores our lines as columns
        #  and we want them represented as rows in memory
        world = np.array([[_codes_to_colors[code] for code in line] for line in lines[-3::-1]]).transpose()

        return Bit(world, pos, orientation)

    def __init__(self, world: np.ndarray, pos: np.array, orientation: int):
        self.world = world
        self.pos = np.array(pos)
        self.orientation = orientation
        self._step_count = 0

    def __repr__(self) -> str:
        """Present the bit information as a string"""
        # We print out each row in reverse order so 0,0 is at the bottom of the text, not the top
        world_str = "\n".join(
            "".join(_colors_to_codes[self.world[x, self.world.shape[1] - 1 - y]] for x in range(self.world.shape[0]))
            for y in range(self.world.shape[1])
        )
        pos_str = f"{self.pos[0]} {self.pos[1]}"
        orientation = self.orientation
        return f"{world_str}\n{pos_str}\n{orientation}\n"

    def _step(self):
        self._step_count += 1
        if self._step_count > MAX_STEP_COUNT:
            raise Exception("Bit has done too many things. Is he stuck in an infinite loop?")

    def save(self, filename: str):
        """Save your bit world to a text file"""
        with open(filename, 'wt') as f:
            f.write(repr(self))
        print(f"Bit saved to {filename}")

    def _draw(self, ax):
        dims = self.world.shape

        # Draw squares
        for y in range(dims[1]):
            for x in range(dims[0]):
                ax.add_patch(plt.Rectangle(
                    (x, y),
                    1, 1,
                    color=_colors_to_names[self._get_color_at((x, y))] or "white")
                )

        # Draw the "bit"
        ax.scatter(
            self.pos[0] + 0.5,
            self.pos[1] + 0.5,
            c='cyan',
            s=500,
            marker=(3, 0, 90 * (-1 + self.orientation))
        )

        ax.set_xlim([0, dims[0]])
        ax.set_ylim([0, dims[1]])
        ax.set_xticks(range(0, dims[0]))
        ax.set_yticks(range(0, dims[1]))
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.grid(True)

    def draw(self, filename=None):
        """Display the current state of the world"""
        fig = plt.figure()
        ax = fig.gca()
        self._draw(ax)
        if filename:
            print("Saving bit world to " + filename)
            fig.savefig(filename)
        else:
            plt.show()
        fig.show()

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
            raise MoveOutOfBoundsException(f"Bit tried to move to {next_pos}, but that is out of bounds")
        elif self._get_color_at(next_pos) == BLACK:
            raise MoveBlockedByBlackException(next_pos)
        else:
            self.pos = next_pos
            self._step()

    def left(self):
        """Turn the bit to the left"""
        self.orientation = self._next_orientation(1)
        self._step()

    def right(self):
        """Turn the bit to the right"""
        self.orientation = self._next_orientation(-1)
        self._step()

    def _get_color_at(self, pos):
        return self.world[pos[0], pos[1]]

    def _space_is_clear(self, pos):
        return self._pos_in_bounds(pos) and self._get_color_at(pos) != BLACK

    def front_clear(self) -> bool:
        """Can a move to the front succeed?

        The edge of the world is not clear.

        Black squares are not clear.
        """
        self._step()
        return self._space_is_clear(self._get_next_pos())

    def left_clear(self) -> bool:
        self._step()
        return self._space_is_clear(self._get_next_pos(1))

    def right_clear(self) -> bool:
        self._step()
        return self._space_is_clear(self._get_next_pos(-1))

    def _paint(self, color: int):
        self.world[self.pos[0], self.pos[1]] = color

    def erase(self):
        """Clear the current position"""
        self._step()
        self._paint(EMPTY)

    def paint(self, color):
        """Color the current position with the specified color"""
        self._step()
        if color not in _names_to_colors:
            raise Exception(f"Unrecognized color: {color}. Known colors are: {list(_names_to_colors.keys())}")
        self._paint(_names_to_colors[color])

    def get_color(self) -> str:
        """Return the color at the current position"""
        self._step()
        return _colors_to_names[self._get_color_at(self.pos)]

    def compare(self, other: 'Bit'):
        """Compare this bit to another"""
        if not self.world.shape == other.world.shape:
            raise Exception(f"Cannot compare Bit worlds of different dimensions: {tuple(self.pos)} vs {tuple(other.pos)}")

        fig, axs = plt.subplots(1, 3, figsize=(12, 4))

        # Draw this
        self._draw(axs[0])
        axs[0].set_title("This Bit")

        # Draw that
        other._draw(axs[2])
        axs[2].set_title("That Bit")

        # Compare
        equal = True
        self._draw(axs[1])
        for x in range(self.world.shape[0]):
            for y in range(self.world.shape[1]):
                if self._get_color_at((x, y)) != other._get_color_at((x, y)):
                    equal = False
                    # print(f"Color at {x},{y} does not match: {_colors_to_names[self._get_color_at((x, y))]} "
                    #       f"vs {_colors_to_names[other._get_color_at((x, y))]}")
                    axs[1].text(x + 0.6, y+0.6, "!",
                                fontsize=16, weight='bold', bbox={'facecolor': 'yellow', 'alpha': 0.5})
        axs[1].set_title("This vs That")
        if self.pos[0] != other.pos[0] or self.pos[1] != other.pos[1]:
            equal = False
            print(f"Location of Bit does not match: {tuple(self.pos)} vs {tuple(other.pos)}")

        plt.show()

        return equal
