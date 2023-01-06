import os

import matplotlib
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

import tkinter as tk
from tkinter import ttk

from typing import List, Tuple

from byubit.core import BitHistoryRecord, BitHistoryRenderer, draw_record, determine_figure_size


def print_histories(histories: List[Tuple[str, List[BitHistoryRecord]]]):
    for name, history in histories:
        print(name)
        print('-' * len(name))
        for num, record in enumerate(history):
            print(f"{num}: {record.name}")
        print()


class TextRenderer(BitHistoryRenderer):
    def __init__(self, verbose=False):
        self.verbose = verbose

    def render(self, histories: List[Tuple[str, List[BitHistoryRecord]]]):
        if self.verbose:
            print_histories(histories)

        return all(history[-1].error_message is None for _, history in histories)


class LastFrameRenderer(BitHistoryRenderer):
    """Displays the last frame
    Similar to the <=0.1.6 functionality
    """

    def __init__(self, verbose=False, bwmode=False):
        self.verbose = verbose
        self.bwmode = bwmode

    def render(self, histories: List[Tuple[str, List[BitHistoryRecord]]]):
        if self.verbose:
            print_histories(histories)

        for name, history in histories:
            last_record = history[-1]

            fig, axs = plt.subplots(1, 1, figsize=determine_figure_size(last_record.world.shape))
            ax: plt.Axes = fig.gca()

            draw_record(ax, last_record, bwmode=self.bwmode)
            fig.suptitle(name, fontsize=14)
            fig.tight_layout()

            plt.show()

        return all(history[-1].error_message is None for _, history in histories)


class MplCanvas(FigureCanvasTkAgg):

    def __init__(self, parent, figsize=(5, 4), dpi=100):
        self.fig = Figure(figsize=figsize, dpi=dpi)
        self.axes = self.fig.add_axes([0.02, 0.05, 0.96, 0.75])
        super(MplCanvas, self).__init__(self.fig, master=parent)


class MainWindow(tk.Frame):
    histories: List[Tuple[str, List[BitHistoryRecord]]]
    cur_pos: List[int]

    def __init__(self, parent, histories, verbose=False, *args, **kwargs):
        super(MainWindow, self).__init__(parent, *args, **kwargs)

        self.histories = histories
        self.cur_pos = [len(history) - 1 for _, history in histories]
        self.verbose = verbose

        has_snapshots = any(
            any(
                event.name.startswith('snapshot')
                for event in history
            )
            for _, history in histories
        )

        # Create the maptlotlib FigureCanvas objects,
        # each which defines a single set of axes as self.axes.
        sizes = [determine_figure_size(history[0].world.shape) for _, history in histories]
        size = (max(x for x, _ in sizes), max(y for _, y in sizes))
        self.canvases = []

        # Add tabs of canvases
        style = ttk.Style(self)
        style.configure('TNotebook', tabposition='s')

        tabs = ttk.Notebook(self, style='TNotebook', height=int(size[1] * 100), width=int(size[0] * 100))
        tabs.grid(row=0, column=0, pady=(10, 0))

        for index, (name, _) in enumerate(histories):
            tab = ttk.Frame(master=tabs)
            canvas = MplCanvas(
                parent=tab,
                figsize=size,
                dpi=100
            )
            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            tab.pack()
            self.canvases.append(canvas)
            tabs.add(tab, text=name)

            self._display_current_record(index)

        # Add buttons
        button_widget = tk.Frame(self)

        # Start
        def start_click():
            which = tabs.index('current')
            self.cur_pos[which] = 0
            self._display_current_record(which)

        start_button = ttk.Button(
            master=button_widget,
            text="<<< First",
            command=start_click,
            width=8
        )
        start_button.pack(side=tk.LEFT, ipadx=0)

        # Prev snapshot
        if has_snapshots:
            def prev_snap_click():
                which = tabs.index('current')
                cur_pos = self.cur_pos[which]
                _, tab_histories = self.histories[which]
                snapshots = [
                    pos
                    for pos, event in enumerate(tab_histories[:cur_pos])
                    if event.name.startswith('snapshot')
                ]
                prev_pos = snapshots[-1] if snapshots else 0
                self.cur_pos[which] = prev_pos
                self._display_current_record(which)

            prev_snap_button = ttk.Button(
                master=button_widget,
                text="<< Jump",
                command=prev_snap_click,
                width=7
            )

            prev_snap_button.pack(side=tk.LEFT)

        # Back
        def back_click():
            which = tabs.index('current')
            if self.cur_pos[which] > 0:
                self.cur_pos[which] -= 1
            self._display_current_record(which)

        back_button = ttk.Button(
            master=button_widget,
            text="< Prev",
            command=back_click,
            width=6
        )
        back_button.pack(side=tk.LEFT)

        # Next
        def next_click():
            which = tabs.index("current")
            if self.cur_pos[which] < len(self.histories[which][1]) - 1:
                self.cur_pos[which] += 1
            self._display_current_record(which)

        next_button = ttk.Button(
            master=button_widget,
            text="Next >",
            command=next_click,
            width=6
        )
        next_button.pack(side=tk.LEFT)

        # Next snapshot
        if has_snapshots:
            def next_snap_click():
                which = tabs.index("current")
                cur_pos = self.cur_pos[which]
                _, history = self.histories[which]
                snapshots = [
                    pos + cur_pos + 1
                    for pos, event in enumerate(history[cur_pos + 1:])
                    if event.name.startswith('snapshot')
                ]
                next_pos = snapshots[0] if snapshots else len(history) - 1
                self.cur_pos[which] = next_pos
                self._display_current_record(which)

            next_snap_button = ttk.Button(
                master=button_widget,
                text="Jump >>",
                command=next_snap_click,
                width=7
            )
            next_snap_button.pack(side=tk.LEFT)

        # Last
        def last_click():
            which = tabs.index("current")
            self.cur_pos[which] = len(self.histories[which][1]) - 1
            self._display_current_record(which)

        last_button = ttk.Button(
            master=button_widget,
            text="Last >>>",
            command=last_click,
            width=8
        )
        last_button.pack(side=tk.LEFT)

        button_widget.grid(row=1, column=0, padx=20, pady=(0, 10))

    def _display_current_record(self, which):
        self._display_record(which, self.cur_pos[which], self.histories[which][1][self.cur_pos[which]])

    def _display_record(self, which: int, index: int, record: BitHistoryRecord):
        if self.verbose:
            print(f"{index}: {record.name}")

        self.canvases[which].axes.clear()  # Clear the canvas.

        draw_record(self.canvases[which].axes, record)
        title = f"{index}: {record.name}  [{record.filename} line {record.line_number}]"
        self.canvases[which].axes.set_title(title)

        # Trigger the canvas to update and redraw.
        self.canvases[which].draw()


class AnimatedRenderer(BitHistoryRenderer):
    """Displays the world, step-by-step
    The User can pause the animation, or step forward or backward manually
    """

    def __init__(self, verbose=False):
        self.verbose = verbose

    def render(self, histories: List[Tuple[str, List[BitHistoryRecord]]]):
        """
        Run TKinter application
        """
        matplotlib.use("TkAgg")

        root = tk.Tk()
        root.title('CS 110 Bit')

        bit_panel = MainWindow(root, histories, self.verbose)
        bit_panel.pack()

        root.protocol('WM_DELETE_WINDOW', root.quit)
        tk.mainloop()

        return all(history[-1].error_message is None for _, history in histories)
