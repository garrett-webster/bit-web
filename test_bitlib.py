import numpy as np
import pytest
import byubit
from importlib import import_module
from byubit import Bit, MoveOutOfBoundsException, BLACK, RED, GREEN, BLUE, TextRenderer, AnimatedRenderer

byubit.RENDERER = byubit.TextRenderer


def test_decorator():
    exp_bit = Bit.new_world(3, 3)
    exp_bit.world[0, 0] = GREEN

    @Bit.run(Bit.new_world(3, 3), exp_bit)
    def paint_green(bit):
        bit.paint("green")


def test_decorator_all():
    exp_bit = Bit.new_world(3, 3)
    exp_bit.world[0, 0] = GREEN

    @Bit.run_all([(Bit.new_world(3, 3), exp_bit), (Bit.new_world(3, 3), exp_bit)])
    def paint_green(bit):
        bit.paint("green")


def test_decorator_test_context():
    test_mod = import_module("testing_module")
    test_method = getattr(test_mod, "move_bit")
    exp_bit = getattr(test_mod, "exp_bit")

    assert Bit.evaluate(test_method, Bit.new_world(3, 3), exp_bit)


def test_run_pass():
    exp_bit = Bit.new_world(3, 3)
    exp_bit.world[1, 1] = RED
    exp_bit.pos = np.array((1, 1))

    def paint_middle_red(bit):
        bit.move()
        bit.left()
        bit.move()
        bit.paint("red")

    assert Bit.evaluate(paint_middle_red, Bit.new_world(3, 3), exp_bit, renderer=TextRenderer())


def test_run_fail():
    exp_bit = Bit.new_world(3, 3)
    exp_bit.world[1, 1] = RED
    exp_bit.pos = np.array((1, 1))

    def do_nothing(bit):
        bit.paint("green")

    assert not Bit.evaluate(do_nothing, Bit.new_world(3, 3), exp_bit, renderer=TextRenderer())


def test_move():
    bit = Bit.new_world(3, 3)
    bit.move()
    bit.move()
    assert (bit.pos == np.array((2, 0))).all()


def test_move_and_turn():
    bit = Bit.new_world(3, 3)
    bit.move()
    assert (bit.pos == np.array((1, 0))).all()

    bit.left()
    bit.move()
    assert (bit.pos == np.array((1, 1))).all()

    bit.left()
    bit.move()
    assert (bit.pos == np.array((0, 1))).all()

    bit.left()
    bit.move()
    assert (bit.pos == np.array((0, 0))).all()


def test_move_out_of_bounds():
    bit = Bit.new_world(3, 3)

    bit.move()
    bit.move()
    with pytest.raises(MoveOutOfBoundsException) as exinfo:
        bit.move()
    assert "[3 0]" in str(exinfo.value)


def test_left_and_right():
    bit = Bit.new_world(3, 3)

    assert all(bit.pos == [0, 0])

    bit.left()
    bit.move()
    assert all(bit.pos == [0, 1])

    bit.right()
    bit.move()
    assert all(bit.pos == [1, 1])


def test_clear():
    bit = Bit.new_world(3, 3)
    bit.world[2, 0] = RED
    bit.world[2, 1] = BLACK

    assert not bit.right_clear()  # edge of grid

    bit.move()
    assert bit.front_clear()  # red square ahead is OK

    bit.move()  # to edge of grid
    assert not bit.front_clear()
    assert not bit.left_clear()  # black square on right

    bit.left()  # turn to face black square
    assert not bit.front_clear()


def test_paint():
    bit = Bit.new_world(3, 3)

    bit.paint('red')
    assert bit.get_color() == 'red'
    bit.erase()
    assert bit.get_color() is None


def test_repr_round_trip():
    bit = Bit.new_world(3, 3)
    bit.world[2, 0] = RED
    bit.world[1, 1] = GREEN
    bit.world[2, 1] = BLACK
    bit.world[0, 2] = BLUE
    bit.pos = (1, 2)
    bit.orientation = 3

    exp = "b--\n-gk\n--r\n1 2\n3"
    assert repr(bit).strip() == exp

    bit2 = Bit.parse(exp)
    assert repr(bit2) == repr(bit)
