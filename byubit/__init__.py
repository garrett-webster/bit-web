from .bit import Bit
from . import bit, core, renderers


def use_inline_renderer():
    bit.RENDERER = renderers.LastFrameRenderer
