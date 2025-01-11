from pathlib import Path
from typing import TypedDict, Optional, Protocol

Grid = list[list[str]]
Pos = tuple[int, int]


class BitHistoryRecord(TypedDict):
    name: str  # What event produced the associated state?
    error_message: Optional[str]  # Error info
    world: Grid
    pos: Pos
    orientation: int
    annotations: Optional[tuple[Grid, Pos, int]]  # world, pos, orientation
    filename: str
    line_number: int


class BitRenderer(Protocol):
    def render(self, code_file: Path, histories: dict[str, list[BitHistoryRecord]]):
        ...
