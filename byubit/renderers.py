import matplotlib
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QTabWidget
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from byubit.core import BitHistoryRecord, BitHistoryRenderer, draw_record, determine_figure_size


def print_histories(histories: list[tuple[str, list[BitHistoryRecord]]]):
    for name, history in histories:
        print(name)
        print('-' * len(name))
        for num, record in enumerate(history):
            print(f"{num}: {record.name}")
        print()


class TextRenderer(BitHistoryRenderer):
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.latest_histories = None

    def render(self, histories: list[tuple[str, list[BitHistoryRecord]]]):
        self.latest_histories = histories

        if self.verbose:
            print_histories(histories)

        return all(history[-1].error_message is None for _, history in histories)


class LastFrameRenderer(BitHistoryRenderer):
    """Displays the last frame
    Similar to the <=0.1.6 functionality
    """

    def __init__(self, verbose=False):
        self.verbose = verbose

    def render(self, histories: list[tuple[str, list[BitHistoryRecord]]]):
        if self.verbose:
            print_histories(histories)

        for name, history in histories:
            last_record = history[-1]

            fig, axs = plt.subplots(1, 1, figsize=determine_figure_size(last_record.world.shape))
            ax: plt.Axes = fig.gca()

            draw_record(ax, last_record)
            fig.suptitle(name, fontsize=14)
            ax.set_title(ax.get_title())
            fig.tight_layout()

            plt.show()

        return all(history[-1].error_message is None for _, history in histories)


class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, figsize=(5, 4), dpi=100):
        fig = Figure(figsize=figsize, dpi=dpi)
        self.axes = fig.add_axes([0.02, 0.05, 0.96, 0.85])
        super(MplCanvas, self).__init__(fig)


class MainWindow(QtWidgets.QMainWindow):
    histories: list[tuple[str, list[BitHistoryRecord]]]
    cur_pos: list[int]

    def __init__(self, histories, verbose=False, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        matplotlib.use('Qt5Agg')

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
        self.canvases = [
            MplCanvas(
                parent=self,
                figsize=size,
                dpi=100
            )
            for _ in histories
        ]

        layout = QtWidgets.QVBoxLayout()

        # Add tabs of canvases
        tabs = QtWidgets.QTabWidget()
        tabs.setTabPosition(QTabWidget.South)
        for index, (name, _) in enumerate(histories):
            tabs.addTab(self.canvases[index], name)
            self._display_current_record(index)
        layout.addWidget(tabs)

        # Add buttons
        button_widget = QtWidgets.QWidget()
        button_layout = QtWidgets.QHBoxLayout()

        # Start
        start_button = QtWidgets.QPushButton()
        start_button.setText("⬅️⬅️ First Step")
        button_layout.addWidget(start_button)

        def start_click():
            which = tabs.currentIndex()
            self.cur_pos[which] = 0
            self._display_current_record(which)

        start_button.clicked.connect(start_click)

        # Prev snapshot
        if has_snapshots:
            prev_snap_button = QtWidgets.QPushButton()
            prev_snap_button.setText("⬅️ Prev Snapshot")
            button_layout.addWidget(prev_snap_button)

            def prev_snap_click():
                which = tabs.currentIndex()
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

            prev_snap_button.clicked.connect(prev_snap_click)

        # Back
        back_button = QtWidgets.QPushButton()
        back_button.setText("⬅️ Prev Step")
        button_layout.addWidget(back_button)

        def back_click():
            which = tabs.currentIndex()
            if self.cur_pos[which] > 0:
                self.cur_pos[which] -= 1
            self._display_current_record(which)

        back_button.clicked.connect(back_click)

        # Next
        next_button = QtWidgets.QPushButton()
        next_button.setText("Next Step ➡️")
        button_layout.addWidget(next_button)

        def next_click():
            which = tabs.currentIndex()
            if self.cur_pos[which] < len(self.histories[which][1]) - 1:
                self.cur_pos[which] += 1
            self._display_current_record(which)

        next_button.clicked.connect(next_click)

        # Next snapshot
        if has_snapshots:
            next_snap_button = QtWidgets.QPushButton()
            next_snap_button.setText("Next Snapshot ➡️")
            button_layout.addWidget(next_snap_button)

            def next_snap_click():
                which = tabs.currentIndex()
                cur_pos = self.cur_pos[which]
                _, history = self.histories[which]
                snapshots = [
                    pos + cur_pos + 1
                    for pos, event in enumerate(history[cur_pos+1:])
                    if event.name.startswith('snapshot')
                ]
                next_pos = snapshots[0] if snapshots else len(history) - 1
                self.cur_pos[which] = next_pos
                self._display_current_record(which)

            next_snap_button.clicked.connect(next_snap_click)

        # Last
        last_button = QtWidgets.QPushButton()
        last_button.setText("Last Step ➡️➡️")
        button_layout.addWidget(last_button)

        def last_click():
            which = tabs.currentIndex()
            self.cur_pos[which] = len(self.histories[which][1]) - 1
            self._display_current_record(which)

        last_button.clicked.connect(last_click)

        button_widget.setLayout(button_layout)

        layout.addWidget(button_widget)  # will become the controls

        master_widget = QtWidgets.QWidget()
        master_widget.setLayout(layout)

        self.setCentralWidget(master_widget)
        self.show()

    def _display_current_record(self, which):
        self._display_record(which, self.cur_pos[which], self.histories[which][1][self.cur_pos[which]])

    def _display_record(self, which: int, index: int, record: BitHistoryRecord):
        if self.verbose:
            print(f"{index}: {record.name}")

        self.canvases[which].axes.clear()  # Clear the canvas.

        draw_record(self.canvases[which].axes, record)
        self.canvases[which].axes.set_title(f"{index}: {record.name}")
        self.canvases[which].axes.set_xlabel(record.error_message)

        # Trigger the canvas to update and redraw.
        self.canvases[which].draw()


class AnimatedRenderer(BitHistoryRenderer):
    """Displays the world, step-by-step
    The User can pause the animation, or step forward or backward manually
    """

    def __init__(self, verbose=False):
        self.verbose = verbose

    def render(self, histories: list[tuple[str, list[BitHistoryRecord]]]):
        """
        Run QT application
        """
        qtapp = QtWidgets.QApplication([])
        w = MainWindow(histories, self.verbose)
        qtapp.exec_()

        return all(history[-1].error_message is None for _, history in histories)
