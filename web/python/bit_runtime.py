import copy
import functools
import inspect
import json
import sys
import traceback
import types

ORIENTATIONS = [
    (0, 1),
    (1, 0),
    (0, -1),
    (-1, 0),
]

MAX_STEP_COUNT = 15000
MAX_REPEAT_STATE = 10
BLACK = "black"
WHITE = "white"

CODES_TO_COLORS = {
    "-": "white",
    "k": "black",
    "o": "orange",
    "g": "green",
    "y": "yellow",
    "b": "blue",
    "r": "red",
    "p": "purple",
}

try:
    SCENARIOS = json.loads(EXTERNAL_SCENARIOS_JSON)
except NameError:
    SCENARIOS = {}


class MoveOutOfBoundsException(Exception):
    pass


class MoveBlockedByBlackException(Exception):
    pass


class BitComparisonException(Exception):
    def __init__(self, message, annotations=None):
        super().__init__(message)
        self.annotations = annotations


class BitInfiniteLoopException(BitComparisonException):
    pass


class NewBit:
    def __getattr__(self, item):
        raise Exception("You can only pass Bit.new_bit to a function with an @Bit decorator")


def _parse_lines_from_string(content):
    lines = [line.split() for line in content.splitlines() if line.strip()]
    lines[:-2] = [list(line[0]) for line in lines[:-2]]
    return lines


def _parse_bit_from_lines(name, content):
    pos = (int(content[-2][1]), int(content[-2][0]))
    orientation = int(content[-1][0])
    world = [
        [CODES_TO_COLORS[code] for code in row]
        for row in content[:-2][::-1]
    ]
    return Bit(name, world, pos, orientation)


def _load_bit_from_string(name, content):
    return _parse_bit_from_lines(name, _parse_lines_from_string(content))


def _registered(func):
    @functools.wraps(func)
    def new_func(self, *args, **kwargs):
        ret = func(self, *args, **kwargs)
        title = " ".join([func.__name__, *(str(a) for a in args)])
        if ret is not None:
            title += f": {ret}"
        self._register(title)
        return ret

    return new_func


def _check_extraneous_args(func):
    @functools.wraps(func)
    def new_func(self, *args):
        try:
            return func(self, *args)
        except TypeError as err:
            if "positional arguments" in str(err):
                raise Exception(f"{func.__name__} was called with the wrong number of arguments.")
            raise

    return new_func


def _evaluate_all(bit_function, scenarios, *args, **kwargs):
    results = {}
    for scenario_name in scenarios:
        scenario = SCENARIOS.get(scenario_name)
        if scenario is None:
            raise FileNotFoundError(f"Could not find world: {scenario_name}")

        start_bit = _load_bit_from_string(scenario_name, scenario["start"])
        end_bit = None
        if scenario.get("finish"):
            end_bit = _load_bit_from_string(scenario_name + " finish", scenario["finish"])

        name, history = start_bit._evaluate(bit_function, end_bit, *args, **kwargs)
        results[name] = history
    return results


class Bit:
    _results = {}
    new_bit = NewBit()

    @staticmethod
    def get_json_results():
        return Bit._results

    @staticmethod
    def empty_world(width, height, name=None, **kwargs):
        if name is None:
            name = f"New World ({width}, {height})"
        scenario_name = "__empty_world__"
        SCENARIOS[scenario_name] = {
            "start": "\n".join(["-" * width for _ in range(height)] + ["0 0", "0"]),
            "finish": None,
        }
        return Bit.worlds(scenario_name, **kwargs)

    @staticmethod
    def worlds(*scenario_names, **world_kwargs):
        def decorator(bit_func):
            @functools.wraps(bit_func)
            def new_function(bit, *args, **kwargs):
                if not isinstance(bit, NewBit):
                    raise TypeError("You must pass Bit.new_bit to your main function.")
                Bit._results = _evaluate_all(bit_func, scenario_names, *args, **kwargs, **world_kwargs)

            return new_function

        return decorator

    @staticmethod
    def new_world(width, height, name=None):
        if name is None:
            name = f"New World ({width}, {height})"
        world = [[WHITE for _ in range(width)] for _ in range(height)]
        return Bit(name, world, (0, 0), 0)

    def __init__(self, name, world, pos, orientation):
        self.name = name
        self.world = world
        self.pos = pos
        self.orientation = orientation
        self.n_rows = len(world)
        self.n_cols = len(world[0])
        self.state_counts = {}
        self.history = []
        self._register("initial state")

    def _record(self, name, message=None, annotations=None, ex=None):
        line_number = 0
        if ex is not None:
            stack = traceback.extract_tb(ex.__traceback__)
            user_frames = [frame for frame in stack if frame.filename == "<user_code>"]
            if user_frames:
                line_number = user_frames[-1].lineno
        else:
            stack = inspect.stack()
            user_frames = [frame for frame in stack if frame.filename == "<user_code>"]
            if user_frames:
                line_number = user_frames[0].lineno
        return {
            "name": name,
            "error_message": message,
            "world": copy.deepcopy(self.world),
            "pos": list(self.pos),
            "orientation": self.orientation,
            "annotations": copy.deepcopy(annotations),
            "filename": "<browser>",
            "line_number": line_number,
        }

    def _register(self, name, message=None, annotations=None, ex=None):
        self.history.append(self._record(name, message, annotations, ex))
        world_tuple = tuple(tuple(row) for row in self.world)
        bit_state = (name, world_tuple, self.pos, self.orientation)
        self.state_counts[bit_state] = self.state_counts.get(bit_state, 0) + 1

        if message is None and self.state_counts[bit_state] >= MAX_REPEAT_STATE:
            raise BitInfiniteLoopException(
                "Bit's been doing the same thing for a while. Is he stuck in an infinite loop?",
                annotations,
            )
        if message is None and len(self.history) > MAX_STEP_COUNT:
            raise BitInfiniteLoopException(
                "Bit has done too many things. Is he stuck in an infinite loop?",
                annotations,
            )

    def _next_orientation(self, turn):
        return (len(ORIENTATIONS) + self.orientation + turn) % len(ORIENTATIONS)

    def _get_next_pos(self, turn=0):
        row, col = self.pos
        drow, dcol = ORIENTATIONS[self._next_orientation(turn)]
        return row + drow, col + dcol

    def _pos_in_bounds(self, pos):
        row, col = pos
        return 0 <= row < self.n_rows and 0 <= col < self.n_cols

    def _compare(self, other):
        if (self.n_rows, self.n_cols) != (other.n_rows, other.n_cols):
            raise Exception("Cannot compare Bit worlds of different dimensions.")
        if any(self.world[r][c] != other.world[r][c] for r in range(self.n_rows) for c in range(self.n_cols)):
            raise BitComparisonException(
                "Bit world does not match expected world",
                [other.world, list(other.pos), other.orientation],
            )
        if self.pos != other.pos:
            raise BitComparisonException(
                f"Location of Bit does not match: {self.pos} vs {other.pos}",
                [other.world, list(other.pos), other.orientation],
            )
        self._register("compare correct!")

    def _evaluate(self, bit_function, other_bit, *args, **kwargs):
        try:
            bit_function(self, *args, **kwargs)
            if other_bit is not None:
                self._compare(other_bit)
        except BitInfiniteLoopException as ex:
            self._register("infinite loop", str(ex), ex.annotations)
        except BitComparisonException as ex:
            self._register("comparison error", str(ex), ex.annotations)
        except MoveOutOfBoundsException as ex:
            self._register("move out of bounds", str(ex), ex=ex)
        except MoveBlockedByBlackException as ex:
            self._register("move blocked", str(ex), ex=ex)
        except Exception as ex:
            self._register("error", str(ex), ex=ex)
        return self.name, self.history

    def __getattr__(self, usr_attr):
        raise Exception(f"bit.{usr_attr} does not exist.")

    @_check_extraneous_args
    @_registered
    def move(self):
        next_pos = self._get_next_pos()
        if not self._pos_in_bounds(next_pos):
            raise MoveOutOfBoundsException(f"Bit tried to move to {next_pos}, but that is out of bounds")
        if self._get_color_at(next_pos) == BLACK:
            raise MoveBlockedByBlackException(f"Bit tried to move to {next_pos}, but that space is blocked")
        self.pos = next_pos

    @_check_extraneous_args
    @_registered
    def turn_left(self):
        self.orientation = self._next_orientation(1)

    left = turn_left

    @_check_extraneous_args
    @_registered
    def turn_right(self):
        self.orientation = self._next_orientation(-1)

    right = turn_right

    def _get_color_at(self, pos):
        row, col = pos
        return self.world[row][col]

    def _space_is_clear(self, pos):
        return self._pos_in_bounds(pos) and self._get_color_at(pos) != BLACK

    @_check_extraneous_args
    @_registered
    def can_move_front(self):
        return self._space_is_clear(self._get_next_pos())

    front_clear = can_move_front

    @_check_extraneous_args
    @_registered
    def can_move_left(self):
        return self._space_is_clear(self._get_next_pos(1))

    left_clear = can_move_left

    @_check_extraneous_args
    @_registered
    def can_move_right(self):
        return self._space_is_clear(self._get_next_pos(-1))

    right_clear = can_move_right

    def _paint(self, color):
        row, col = self.pos
        self.world[row][col] = color

    @_check_extraneous_args
    @_registered
    def erase(self):
        self._paint(WHITE)

    @_check_extraneous_args
    @_registered
    def paint(self, color):
        self._paint(color)

    def _get_color(self):
        return self._get_color_at(self.pos)

    @_check_extraneous_args
    @_registered
    def get_color(self):
        return self._get_color()

    @_check_extraneous_args
    @_registered
    def is_on_blue(self):
        return self._get_color() == "blue"

    is_blue = is_on_blue

    @_check_extraneous_args
    @_registered
    def is_on_green(self):
        return self._get_color() == "green"

    is_green = is_on_green

    @_check_extraneous_args
    @_registered
    def is_on_red(self):
        return self._get_color() == "red"

    is_red = is_on_red

    @_check_extraneous_args
    @_registered
    def is_on_white(self):
        return self._get_color() == "white"

    is_empty = is_on_white

    @_check_extraneous_args
    @_registered
    def snapshot(self, title):
        pass


module = types.ModuleType("byubit")
module.Bit = Bit
sys.modules["byubit"] = module
