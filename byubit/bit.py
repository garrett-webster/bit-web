# Inspired by Stanford: http://web.stanford.edu/class/cs106a/handouts_w2021/reference-bit.html
import os
from typing import Literal

import matplotlib.pyplot as plt
import numpy as np
import importlib

# 0,0  1,0  2,0
# 0,1  1,1, 2,1
# 0,2  1,2, 2,2
# dx and dy
from byubit.core import BitHistoryRecord, BitHistoryRenderer, BitComparisonException, _codes_to_colors, \
    _colors_to_codes, draw_record, MoveOutOfBoundsException, BLACK, MoveBlockedByBlackException, EMPTY, \
    _names_to_colors, _colors_to_names, determine_figure_size, BitInfiniteLoopException
from byubit.renderers import AnimatedRenderer, LastFrameRenderer

_orientations = [
    np.array((1, 0)),  # Right
    np.array((0, 1)),  # Up
    np.array((-1, 0)),  # Left
    np.array((0, -1))  # Down
]

MAX_STEP_COUNT = 10_000

# Set default renderer
# - If running in IPython, use the LastFrameRenderer
# - Else use AnimatedRenderer
VERBOSE = False
try:
    RENDERER = AnimatedRenderer

    ipy = importlib.import_module("IPython")
    ip = getattr(ipy, "get_ipython")()
    if ip is not None:
        RENDERER = LastFrameRenderer

except Exception as ex:
    pass


def set_verbose():
    global VERBOSE
    VERBOSE = True


# Convention:
# We'll have 0,0 be the origin
# The position defines the X,Y coordinates
class Bit:
    name: str
    world: np.array
    pos: np.array  # x and y
    orientation: int  # _orientations[orientation] => dx and dy

    history: list[BitHistoryRecord]

    @staticmethod
    def run_from_empty(width, height, **kwargs):
        return Bit.run_all([(Bit.new_world(width, height), None)], **kwargs)

    @staticmethod
    def run(*bit_worlds, **kwargs):
        bits = []
        for bit_world in bit_worlds:
            if isinstance(bit_world, str):
                start = bit_world + '.start.txt'
                if not os.path.isfile(end := (bit_world + '.finish.txt')):
                    end = None
                bits.append((start, end))
            else:
                bits.append((bit_world, None))

        return Bit.run_all(bits, **kwargs)

    @staticmethod
    def run_all(bits, *args, **kwargs):
        def decorator(bit_func):
            Bit.evaluate(bit_func, bits, *args, **kwargs)
            return bit_func

        return decorator

    @staticmethod
    def evaluate(
            bit_function,
            bits,
            save=None,
            renderer: BitHistoryRenderer = None
    ) -> bool:
        """Return value communicates whether the run succeeded or not"""

        renderer = renderer or RENDERER(verbose=VERBOSE)

        results = []
        for bit1, bit2 in bits:
            if isinstance(bit1, str):
                bit1 = Bit.load(bit1)

            if isinstance(bit2, str):
                bit2 = Bit.load(bit2)
            try:
                bit_function(bit1)

                if bit2 is not None:
                    bit1._compare(bit2)

            except BitInfiniteLoopException as ex:
                print(ex)
                bit1._register("infinite loop 😵", str(ex), ex.annotations)

            except BitComparisonException as ex:
                bit1._register("comparison error", str(ex), ex.annotations)

            except MoveOutOfBoundsException as ex:
                print(ex)
                bit1._register("move out of bounds", str(ex))

            except MoveBlockedByBlackException as ex:
                print(ex)
                bit1._register("move blocked", str(ex))

            except Exception as ex:
                print(ex)
                bit1._register("error", str(ex))

            finally:
                if save:
                    bit1.save(save)

                results.append((bit1.name, bit1.history))

        return renderer.render(results)

    @staticmethod
    def new_world(size_x, size_y):
        return Bit(f"New World({size_x},{size_y})", np.zeros((size_x, size_y)), (0, 0), 0)

    @staticmethod
    def load(filename: str):
        """Parse the file into a new Bit"""
        with open(filename, 'rt') as f:
            return Bit.parse(filename[:filename.index('.')], f.read())

    @staticmethod
    def parse(name: str, content: str):
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

        return Bit(name, world, pos, orientation)

    def __init__(self, name: str, world: np.array, pos: np.array, orientation: int):
        self.name = name
        self.world = world
        self.pos = np.array(pos)
        self.orientation = orientation
        self.history = []
        self._register("initial state")

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

    def _record(self, name, message=None, annotations=None):
        return BitHistoryRecord(
            name, message, self.world.copy(), self.pos, self.orientation,
            annotations.copy() if annotations is not None else self.world.copy()
        )

    def _register(self, name, message=None, annotations=None):
        self.history.append(self._record(name, message, annotations))
        if message is None and len(self.history) > MAX_STEP_COUNT:
            message = "Bit has done too many things. Is he stuck in an infinite loop?"
            raise BitInfiniteLoopException(message, annotations)

    def save(self, filename: str):
        """Save your bit world to a text file"""
        with open(filename, 'wt') as f:
            f.write(repr(self))
        print(f"Bit saved to {filename}")

    def draw(self, filename=None, message=None, annotations=None):
        """Display the current state of the world"""
        record = self._record("", annotations=annotations)
        fig = plt.figure(figsize=determine_figure_size(record.world.shape))
        ax = fig.gca()
        draw_record(ax, record)

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
            self._register("move")

    def left(self):
        """Turn the bit to the left"""
        self.orientation = self._next_orientation(1)
        self._register("left")

    def right(self):
        """Turn the bit to the right"""
        self.orientation = self._next_orientation(-1)
        self._register("right")

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
        self._register(f"front_clear: {ret}")
        return ret

    def left_clear(self) -> bool:
        ret = self._space_is_clear(self._get_next_pos(1))
        self._register(f"left_clear: {ret}")
        return ret

    def right_clear(self) -> bool:
        ret = self._space_is_clear(self._get_next_pos(-1))
        self._register(f"right_clear: {ret}")
        return ret

    def _paint(self, color: int):
        self.world[self.pos[0], self.pos[1]] = color

    def erase(self):
        """Clear the current position"""
        self._paint(EMPTY)
        self._register("erase")

    def paint(self, color):
        """Color the current position with the specified color"""
        if color not in _names_to_colors:
            message = f"Unrecognized color: {color}. Known colors are: {list(_names_to_colors.keys())}"
            raise Exception(message)
        self._paint(_names_to_colors[color])
        self._register(f"paint {color}")

    def get_color(self) -> str:
        """Return the color at the current position"""
        ret = _colors_to_names[self._get_color_at(self.pos)]
        self._register(f"get_color: {ret}")
        return ret

    def _compare(self, other: 'Bit'):
        """Compare this bit to another"""
        if not self.world.shape == other.world.shape:
            raise Exception(
                f"Cannot compare Bit worlds of different dimensions: {tuple(self.pos)} vs {tuple(other.pos)}")

        if not np.array_equal(self.world, other.world):
            raise BitComparisonException(f"Bit world does not match expected world", other.world)

        if self.pos[0] != other.pos[0] or self.pos[1] != other.pos[1]:
            raise Exception(f"Location of Bit does not match: {tuple(self.pos)} vs {tuple(other.pos)}")

        self._register("compare correct!", annotations=other.world)

    def compare(self, other: 'Bit'):
        try:
            self._compare(other)
            return True
        except BitComparisonException as ex:
            self.draw(message=str(ex), annotations=ex.annotations)

        finally:
            self.draw()

        return False
