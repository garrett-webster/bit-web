import runpy

import numpy as np
import pytest
from byubit.bit import Bit
import byubit
from byubit.core import GREEN, RED, MoveOutOfBoundsException, BLACK, BLUE

byubit.use_text_renderer()


def test_decorator():
    @Bit.worlds('test-world-right', 'test-world-wrong')
    def paint_green(bit):
        bit.paint("green")

    paint_green(Bit.new_bit)


def test_decorator_test_context():
    runpy.run_path("testing_module.py", {}, '__main__')
    assert Bit._results
    assert Bit._results[0][0] == 'test-world-right.start'


def test_decorator_test_context_failing_method():
    runpy.run_path("testing_module2.py", {}, '__main__')
    assert Bit._results
    name, history = Bit._results[0]
    assert history[-1].error_message


def test_must_call_decorated_method():
    try:
        runpy.run_path("testing_module3.py", {}, '__main__')
        pytest.fail("Should have raised an exception")
    except Exception as ex:
        print(ex)
        assert "@Bit" in str(ex)


def test_must_pass_new_bit_to_decorated_method():
    runpy.run_path("testing_module4.py", {}, '__main__')
    assert Bit._results
    name, history = Bit._results[0]
    assert "Bit.new_bit" in history[-1].error_message


def test_run_pass():
    exp_bit = Bit.new_world(3, 3)
    exp_bit.world[1, 1] = RED
    exp_bit.pos = np.array((1, 1))

    def paint_middle_red(bit):
        bit.move()
        bit.turn_left()
        bit.move()
        bit.paint("red")

    assert Bit._evaluate(paint_middle_red, [(Bit.new_world(3, 3), exp_bit)])


def test_run_fail():
    exp_bit = Bit.new_world(3, 3)
    exp_bit.world[1, 1] = RED
    exp_bit.pos = np.array((1, 1))

    def do_nothing(bit):
        bit.paint("green")

    assert not Bit._evaluate(do_nothing, [(Bit.new_world(3, 3), exp_bit)])


def test_move():
    bit = Bit.new_world(3, 3)
    bit.move()
    bit.move()
    assert (bit.pos == np.array((2, 0))).all()


def test_move_and_turn():
    bit = Bit.new_world(3, 3)
    bit.move()
    assert (bit.pos == np.array((1, 0))).all()

    bit.turn_left()
    bit.move()
    assert (bit.pos == np.array((1, 1))).all()

    bit.turn_left()
    bit.move()
    assert (bit.pos == np.array((0, 1))).all()

    bit.turn_left()
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

    bit.turn_left()
    bit.move()
    assert all(bit.pos == [0, 1])

    bit.turn_right()
    bit.move()
    assert all(bit.pos == [1, 1])


def test_clear():
    bit = Bit.new_world(3, 3)
    bit.world[2, 0] = RED
    bit.world[2, 1] = BLACK

    assert not bit.can_move_right()  # edge of grid

    bit.move()
    assert bit.can_move_front()  # red square ahead is OK

    bit.move()  # to edge of grid
    assert not bit.can_move_front()
    assert not bit.can_move_left()  # black square on right

    bit.turn_left()  # turn to face black square
    assert not bit.can_move_front()


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

    bit2 = Bit.parse("name", exp)
    assert repr(bit2) == repr(bit)
