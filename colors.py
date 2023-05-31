"""An unfinished attempt to sort css_colors by color"""
import colorsys
from matplotlib import colors
from byubit.core import css_colors

color_list = css_colors

def rgb_to_hsl(r, g, b):
    r /= 255.0
    g /= 255.0
    b /= 255.0
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    h = int(h * 360)
    s = int(s * 100)
    l = int(l * 100)
    return h, s, l


def color_key(color_name):
    r, g, b = colors.to_rgb(color_name)
    h, s, l = rgb_to_hsl(r, g, b)
    return h, l, s


sorted_colors = sorted(color_list, key=color_key)
