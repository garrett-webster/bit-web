from .bit import Bit, set_verbose
from . import bit, core, renderers


def use_text_renderer():
    bit.RENDERER = renderers.TextRenderer
