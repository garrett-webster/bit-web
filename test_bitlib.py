import numpy as np
import pytest

from bitlib import Bit, MoveOutOfBoundsException, BLACK, RED, GREEN, BLUE


def test_draw():
    assert False


def test_move():
    bit = Bit(
        world=np.zeros((3, 3)),
        pos=np.array((0, 0)),
        orientation=0
    )
    bit.move()
    bit.move()
    assert (bit.pos == np.array((2, 0))).all()


def test_move_and_turn():
    bit = Bit(
        world=np.zeros((3, 3)),
        pos=np.array((0, 0)),
        orientation=0
    )
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
    bit = Bit(
        world=np.zeros((3, 3)),
        pos=np.array((0, 0)),
        orientation=0
    )
    bit.move()
    bit.move()
    with pytest.raises(MoveOutOfBoundsException) as exinfo:
        bit.move()
    assert "[3 0]" in str(exinfo.value)


def test_left_and_right():
    bit = Bit(
        world=np.zeros((3, 3)),
        pos=np.array((0, 0)),
        orientation=0
    )

    assert all(bit.pos == [0, 0])

    bit.left()
    bit.move()
    assert all(bit.pos == [0, 1])

    bit.right()
    bit.move()
    assert all(bit.pos == [1, 1])


def test_clear():
    world = np.zeros((3, 3))
    world[2, 0] = RED
    world[2, 1] = BLACK

    bit = Bit(
        world=world,
        pos=np.array((0, 0)),
        orientation=0
    )

    assert not bit.left_clear()  # edge of grid

    bit.move()
    assert bit.front_clear()  # red square ahead is OK

    bit.move()  # to edge of grid
    assert not bit.front_clear()
    assert not bit.right_clear()  # black square on right

    bit.right()  # turn to face black square
    assert not bit.front_clear()


def test_paint():
    bit = Bit(
        world=np.zeros((3, 3)),
        pos=np.array((0, 0)),
        orientation=0
    )
    bit.paint('red')
    assert bit.get_color() == 'red'
    bit.erase()
    assert bit.get_color() is None


def test_repr_round_trip():
    world = np.zeros((3, 3))
    world[2, 0] = RED
    world[1, 1] = GREEN
    world[2, 1] = BLACK
    world[0, 2] = BLUE

    bit = Bit(
        world=world,
        pos=np.array((1, 2)),
        orientation=3
    )

    exp = "b--\n-gk\n--r\n1 2\n3"
    assert repr(bit).strip() == exp

    bit2 = Bit.parse(exp)
    assert repr(bit2) == repr(bit)

