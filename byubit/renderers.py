import matplotlib
from PyQt5 import QtWidgets
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from byubit.core import BitHistoryRecord, BitHistoryRenderer, draw_record, determine_figure_size


class TextRenderer(BitHistoryRenderer):
    def __init__(self, verbose=False):
        self.verbose = verbose

    def render(self, history: list[BitHistoryRecord]):
        if self.verbose:
            print()
            for num, record in enumerate(history):
                print(f"{num}: {record.name}")

        return history[-1].error_message is None


class LastFrameRenderer(BitHistoryRenderer):
    """Displays the last frame
    Similar to the <=0.1.6 functionality
    """
    def __init__(self, verbose=False):
        self.verbose = verbose

    def render(self, history: list[BitHistoryRecord]):
        if self.verbose:
            print()
            for num, record in enumerate(history):
                print(f"{num}: {record.name}")

        last_record = history[-1]

        fig, axs = plt.subplots(1, 1, figsize=determine_figure_size(last_record.world.shape))
        ax = fig.gca()

        draw_record(ax, last_record)

        plt.show()

        return history[-1].error_message is None


class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_axes([0.02, 0.05, 0.96, 0.85])
        super(MplCanvas, self).__init__(fig)


class MainWindow(QtWidgets.QMainWindow):
    history: list[BitHistoryRecord]
    cur_pos: int

    def __init__(self, history, verbose=False, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        matplotlib.use('Qt5Agg')

        self.history = history
        self.cur_pos = len(history) - 1
        self.verbose = verbose

        # Create the maptlotlib FigureCanvas object,
        # which defines a single set of axes as self.axes.
        size = determine_figure_size(history[0].world.shape)
        self.canvas = MplCanvas(parent=self, width=size[0], height=size[1], dpi=100)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.canvas)

        button_widget = QtWidgets.QWidget()
        button_layout = QtWidgets.QHBoxLayout()

        # Start
        start_button = QtWidgets.QPushButton()
        start_button.setText("⬅️⬅️ First Step")
        button_layout.addWidget(start_button)

        def start_click():
            self.cur_pos = 0
            self._display_current_record()

        start_button.clicked.connect(start_click)

        # Back
        back_button = QtWidgets.QPushButton()
        back_button.setText("⬅️ Prev Step")
        button_layout.addWidget(back_button)

        def back_click():
            if self.cur_pos > 0:
                self.cur_pos -= 1
            self._display_current_record()

        back_button.clicked.connect(back_click)

        # Next
        next_button = QtWidgets.QPushButton()
        next_button.setText("Next Step ➡️")
        button_layout.addWidget(next_button)

        def next_click():
            if self.cur_pos < len(self.history) - 1:
                self.cur_pos += 1
            self._display_current_record()

        next_button.clicked.connect(next_click)

        # Last
        last_button = QtWidgets.QPushButton()
        last_button.setText("Last Step ➡️➡️")
        button_layout.addWidget(last_button)

        def last_click():
            self.cur_pos = len(self.history) - 1
            self._display_current_record()

        last_button.clicked.connect(last_click)

        button_widget.setLayout(button_layout)

        layout.addWidget(button_widget)  # will become the controls

        master_widget = QtWidgets.QWidget()
        master_widget.setLayout(layout)
        self.setCentralWidget(master_widget)
        self._display_current_record()
        self.show()

    def _display_current_record(self):
        self._display_record(self.cur_pos, self.history[self.cur_pos])

    def _display_record(self, index: int, record: BitHistoryRecord):
        if self.verbose:
            print(f"{index}: {record.name}")

        self.canvas.axes.clear()  # Clear the canvas.

        draw_record(self.canvas.axes, record)
        self.canvas.axes.set_title(f"{index}: {record.name}")
        self.canvas.axes.set_xlabel(record.error_message)

        # Trigger the canvas to update and redraw.
        self.canvas.draw()


class AnimatedRenderer(BitHistoryRenderer):
    """Displays the world, step-by-step
    The User can pause the animation, or step forward or backward manually
    """

    def __init__(self, verbose=False):
        self.verbose = verbose

    def render(self, history: list[BitHistoryRecord]):
        """
        Run QT application
        """
        qtapp = QtWidgets.QApplication([])
        w = MainWindow(history, self.verbose)
        qtapp.exec_()

        return history[-1].error_message is None
