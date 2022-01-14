# Inspired by Stanford: http://web.stanford.edu/class/cs106a/handouts_w2021/reference-bit.html
from dataclasses import dataclass
from typing import Literal, Protocol, Optional

import numpy as np
import matplotlib.pyplot as plt


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

MAX_STEP_COUNT = 1_000


@dataclass
class BitHistoryRecord:
    name: str  # What event produced the associated state?
    error_message: Optional[str]  # Error info
    world: np.array  # 2D list indexed with [x,y]
    pos: np.array  # [x, y]
    orientation: int
    annotations: np.array  # 2D list of expected colors


class BitHistoryRenderer(Protocol):
    def register_record(self, record: BitHistoryRecord):
        """Record the state of Bit"""

    def render(self) -> bool:
        """Present the history.
        Return True if there were no errors
        Return False if there were errors
        """


class TextRenderer(BitHistoryRenderer):
    history: list[BitHistoryRecord]

    def __init__(self):
        self.history = []

    def register_record(self, record: BitHistoryRecord):
        self.history.append(record)
        if len(self.history) > MAX_STEP_COUNT:
            message = "Bit has done too many things. Is he stuck in an infinite loop?"
            raise Exception(message)

    def render(self):
        print()
        for num, record in enumerate(self.history):
            print(f"{num}: {record.name}")

        return self.history[-1].error_message is None


class LastFrameRenderer(BitHistoryRenderer):
    """Displays the last frame
    Similar to the <=0.1.6 functionality
    """
    history: list[BitHistoryRecord]

    def __init__(self):
        self.history = []

    def register_record(self, record: BitHistoryRecord):
        self.history.append(record)
        if len(self.history) > MAX_STEP_COUNT:
            message = "Bit has done too many things. Is he stuck in an infinite loop?"
            raise Exception(message)

    def render(self):
        print()
        for num, record in enumerate(self.history):
            print(f"{num}: {record.name}")

        last_record = self.history[-1]

        fig, axs = plt.subplots(1, 1, figsize=(6, 6))
        ax = fig.gca()

        self._draw(ax, last_record)

        if last_record.annotations is not None:
            for x in range(last_record.world.shape[0]):
                for y in range(last_record.world.shape[1]):
                    if last_record.world[x, y] != last_record.annotations[x, y]:
                        ax.text(x + 0.6, y + 0.6, "!",
                                fontsize=16, weight='bold',
                                bbox={'facecolor': _colors_to_names[last_record.annotations[x, y]] or "white"})
        ax.set_title(last_record.name)
        if last_record.error_message is not None:
            ax.set_xlabel("⚠️" + last_record.error_message)
        plt.show()

        return self.history[-1].error_message is None

    @staticmethod
    def _draw(ax, record):
        dims = record.world.shape

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
            s=500,
            marker=(3, 0, 90 * (-1 + record.orientation))
        )

        ax.set_xlim([0, dims[0]])
        ax.set_ylim([0, dims[1]])
        ax.set_xticks(range(0, dims[0]))
        ax.set_yticks(range(0, dims[1]))
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.grid(True)


class AnimatedRenderer(BitHistoryRenderer):
    """Displays the world, step-by-step
    The User can pause the animation, or step forward or backward manually
    """
    # Step forward
    # Step backward
    # Turn on auto-advance (play)
    # Turn off auto-advance (pause)
    # Event loop


# RENDERER = TextRenderer
RENDERER = LastFrameRenderer


# Convention:
# We'll have 0,0 be the origin
# The position defines the X,Y coordinates
class Bit:
    world: np.array
    pos: np.array  # x and y
    orientation: int  # _orientations[orientation] => dx and dy

    renderer: BitHistoryRenderer

    @staticmethod
    def run(bit1, bit2, bit_function) -> bool:
        """Return value communicates whether the run succeeded or not"""
        if isinstance(bit1, str):
            bit1 = Bit.load(bit1)

        if isinstance(bit2, str):
            bit2 = Bit.load(bit2)
        try:
            bit_function(bit1)

            if bit2 is not None:
                bit1.compare(bit2)

        except BitComparisonException as ex:
            bit1._record("comparison error", str(ex), ex.annotations)

        except Exception as ex:
            bit1._record("error", str(ex))

        finally:
            return bit1.render()

    @staticmethod
    def new_world(size_x, size_y):
        return Bit(RENDERER(), np.zeros((size_x, size_y)), (0, 0), 0)

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

        return Bit(RENDERER, world, pos, orientation)

    def __init__(self,
                 renderer: BitHistoryRenderer,
                 world: np.array,
                 pos: np.array,
                 orientation: int
                 ):
        self.world = world
        self.pos = np.array(pos)
        self.orientation = orientation
        self.renderer = renderer
        self._record("initial state")

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

    def render(self) -> bool:
        return self.renderer.render()

    def _record(self, name, message=None, annotations=None):
        self.renderer.register_record(BitHistoryRecord(
            name, message, self.world, self.pos, self.orientation,
            annotations if annotations is not None else self.world
        ))

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

    def draw(self, filename=None, message=None):
        """Display the current state of the world"""
        fig = plt.figure()
        ax = fig.gca()
        self._draw(ax)
        if message:
            ax.set_title(message)
        if filename:
            print("Saving bit world to " + filename)
            fig.savefig(filename)
        else:
            plt.show()

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
            message = f"Bit tried to move to {next_pos}, but that is out of bounds"
            raise MoveOutOfBoundsException(message)

        elif self._get_color_at(next_pos) == BLACK:
            message = f"Bit tried to move to {next_pos}, but that space is blocked"
            raise MoveBlockedByBlackException(message)

        else:
            self.pos = next_pos
            self._record("move")

    def left(self):
        """Turn the bit to the left"""
        self.orientation = self._next_orientation(1)
        self._record("left")

    def right(self):
        """Turn the bit to the right"""
        self.orientation = self._next_orientation(-1)
        self._record("right")

    def _get_color_at(self, pos):
        return self.world[pos[0], pos[1]]

    def _space_is_clear(self, pos):
        return self._pos_in_bounds(pos) and self._get_color_at(pos) != BLACK

    def front_clear(self) -> bool:
        """Can a move to the front succeed?

        The edge of the world is not clear.

        Black squares are not clear.
        """
        ret = self._space_is_clear(self._get_next_pos())
        self._record(f"front_clear: {ret}")
        return ret

    def left_clear(self) -> bool:
        ret = self._space_is_clear(self._get_next_pos(1))
        self._record(f"left_clear: {ret}")
        return ret

    def right_clear(self) -> bool:
        ret = self._space_is_clear(self._get_next_pos(-1))
        self._record(f"right_clear: {ret}")
        return ret

    def _paint(self, color: int):
        self.world[self.pos[0], self.pos[1]] = color

    def erase(self):
        """Clear the current position"""
        self._paint(EMPTY)
        self._record("erase")

    def paint(self, color):
        """Color the current position with the specified color"""
        if color not in _names_to_colors:
            message = f"Unrecognized color: {color}. Known colors are: {list(_names_to_colors.keys())}"
            raise Exception(message)
        self._paint(_names_to_colors[color])
        self._record(f"paint {color}")

    def get_color(self) -> str:
        """Return the color at the current position"""
        ret = _colors_to_names[self._get_color_at(self.pos)]
        self._record(f"get_color: {ret}")
        return ret

    def compare(self, other: 'Bit'):
        """Compare this bit to another"""
        if not self.world.shape == other.world.shape:
            raise Exception(
                f"Cannot compare Bit worlds of different dimensions: {tuple(self.pos)} vs {tuple(other.pos)}")

        self._record("compare", annotations=other.world)

        if not np.array_equal(self.world, other.world):
            raise BitComparisonException(f"Bit world does not match expected world", other.world)

        if self.pos[0] != other.pos[0] or self.pos[1] != other.pos[1]:
            raise Exception(f"Location of Bit does not match: {tuple(self.pos)} vs {tuple(other.pos)}")
