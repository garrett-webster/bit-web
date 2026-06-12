# Bit Command Cheat Sheet

Bit follows the instructions you write from top to bottom. Most Bit commands
start with `bit.` and end with parentheses: `()`.

## Starting a Program

```python
@Bit.worlds("world-name")
def main(bit):
    bit.move()


main(Bit.new_bit)
```

You usually only need to change two parts:

1. Replace `"world-name"` with the name of your world.
2. Write your instructions below `def main(bit):`.

The instructions inside `main` must be indented by four spaces, as shown above.

## Moving Bit

### `bit.move()`

Move forward one square.

```python
bit.move()
```

Bit cannot move through a black square or past the edge of the world.

### `bit.turn_left()`

Turn left without moving to a new square.

```python
bit.turn_left()
```

You can also write `bit.left()`.

### `bit.turn_right()`

Turn right without moving to a new square.

```python
bit.turn_right()
```

You can also write `bit.right()`.

## Looking Before Moving

These commands answer a yes-or-no question:

- `True` means yes.
- `False` means no.

Use them with `if` when Bit should do something only when the answer is yes.

### `bit.can_move_front()`

Check whether Bit can move forward.

```python
if bit.can_move_front():
    bit.move()
```

You can also write `bit.front_clear()`.

### `bit.can_move_left()`

Check whether the square to Bit's left is open. This does not turn Bit.

```python
if bit.can_move_left():
    bit.turn_left()
```

You can also write `bit.left_clear()`.

### `bit.can_move_right()`

Check whether the square to Bit's right is open. This does not turn Bit.

```python
if bit.can_move_right():
    bit.turn_right()
```

You can also write `bit.right_clear()`.

## Using Colors

Color names go inside quotation marks, like `"blue"`.

Available colors are `"white"`, `"black"`, `"orange"`, `"green"`, `"yellow"`,
`"blue"`, `"red"`, and `"purple"`.

### `bit.paint("color")`

Paint the square Bit is standing on. Replace `"color"` with the color you want.

```python
bit.paint("blue")
```

### `bit.erase()`

Erase the color from Bit's square by painting it white.

```python
bit.erase()
```

### `bit.get_color()`

Find the color of the square Bit is standing on.

```python
color = bit.get_color()
```

This example remembers the answer using the name `color`.

### `bit.is_on_blue()`

Check whether Bit is on a blue square.

```python
if bit.is_on_blue():
    bit.erase()
```

You can also write `bit.is_blue()`.

### `bit.is_on_green()`

Check whether Bit is on a green square.

```python
if bit.is_on_green():
    bit.move()
```

You can also write `bit.is_green()`.

### `bit.is_on_red()`

Check whether Bit is on a red square.

```python
if bit.is_on_red():
    bit.turn_left()
```

You can also write `bit.is_red()`.

### `bit.is_on_white()`

Check whether Bit is on an empty white square.

```python
if bit.is_on_white():
    bit.paint("green")
```

You can also write `bit.is_empty()`.
