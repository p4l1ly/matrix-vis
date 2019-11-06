import base64
from io import BytesIO
import pickle
import sys

import matplotlib.pyplot as plt
from matplotlib.colors import LightSource, TABLEAU_COLORS
import mpl_toolkits.mplot3d
import numpy as np
import yaml
import zmq

data = yaml.load(sys.stdin.read(), Loader=yaml.FullLoader)
print(yaml.dump(data['info'], sort_keys=False))
dimensions = data['dimensions']
matrix = np.load(BytesIO(base64.b64decode(data['matrix'])))

assert len(dimensions) >= 2
assert all(len(tics) >= 1 for tics in dimensions.values())
assert matrix.shape == tuple(len(tics) for tics in dimensions.values())

keys = list(dimensions.keys())

config = [0 for _ in dimensions]

if len(dimensions) >= 3:
    config[-3] = 'x'
    config[-2] = 'y'
    config[-1] = [(0, 1)]
else:
    config[-2] = 'y'
    config[-1] = [(0, 1)]

def plot_data():
    slices = tuple(
        (x if x.__class__ is int else slice(None, None, None))
        for x in config
    )

    arr = matrix[slices]
    x_ix = next(i for i, x in enumerate(config) if x == 'x')

    try:
        y_ix = next(i for i, x in enumerate(config) if x == 'y')
        is_3d = True
    except StopIteration:
        is_3d = False

    change_dimension_count = is_3d != plot_data.is_3d
    plot_data.is_3d = is_3d

    series_ix, series = next((i, x)
        for i, x in enumerate(config)
        if x.__class__ is list
    )

    if is_3d:
        ixs = [series_ix, x_ix, y_ix]
        ser_pos, x_pos, y_pos = (sum(x > ix for ix in ixs) for x in ixs)
        arr = arr.transpose(ser_pos, x_pos, y_pos)
    else:
        if x_ix < series_ix:
            arr = arr.transpose()

    arr = arr[[x[0] for x in series]]

    if is_3d:
        arr = arr*np.array([[[x[1]]] for x in series])
    else:
        arr = arr*np.array([[x[1]] for x in series])

    labels = [str(dimensions[keys[series_ix]][i]) for i, _ in series]

    xlabel = keys[x_ix]
    ylabel = keys[y_ix] if is_3d else None
    zlabel = keys[series_ix]
    return change_dimension_count, arr, labels, xlabel, ylabel, zlabel


plot_data.is_3d = None
COLORS = list(TABLEAU_COLORS)

def replot(fig, ax):
    recreate_ax, arr, labels, xlabel, ylabel, zlabel = plot_data()

    if recreate_ax:
        fig.clf()
        if plot_data.is_3d:
            ax = fig.add_subplot(1, 1, 1, projection='3d')
        else:
            ax = fig.add_subplot(1, 1, 1)

    ax.clear()
    for i, (label, xs) in enumerate(zip(labels, arr)):
        if ylabel is None:
            ax.plot(xs, label=label)
        else:
            x = np.arange(0, xs.shape[1])
            y = np.arange(0, xs.shape[0])
            x, y = np.meshgrid(x, y)

            color = COLORS[i % len(COLORS)]

            ax.plot_wireframe(x, y, xs, color=color, label=label)

    ax.legend()

    ax.set_xlabel(xlabel)
    if ylabel is None:
        ax.set_ylabel(zlabel)
    else:
        ax.set_ylabel(ylabel)
        ax.set_zlabel(zlabel)

    fig.canvas.draw_idle()

    return ax


def show_plot():
    fig = plt.figure()

    ax = replot(fig, None)

    ctx = zmq.Context()
    socket = ctx.socket(zmq.REP)
    socket.bind('tcp://0.0.0.0:8989')

    plt.show(block=False)
    while plt.fignum_exists(fig.number):
        plt.pause(1)
        rs, _, es = zmq.select([socket], [], [socket], timeout=0)
        if rs or es:
            config[:] = pickle.loads(socket.recv())
            ax = replot(fig, ax)
            socket.send(b'')


show_plot()
sys.exit()

from multiprocessing import Process; Process(target=show_plot).start()


from PySide2.QtCore import Property, QObject, QUrl, Signal, Slot

ctx = zmq.Context()
socket = ctx.socket(zmq.REQ)
socket.connect('tcp://0.0.0.0:8989')

class Py(QObject):
    def __init__(self):
        self.points_ = [[0.2, 0.4], [0.4, 0.5]]
        self.minmax_ = [0, 0, 1, 1]
        super().__init__()

    @Slot(float, float)
    def fire(self, x, y):
        socket.send(pickle.dumps((x, y)))
        socket.recv()

from PySide2.QtWidgets import QApplication
from PySide2.QtQml import QQmlApplicationEngine

app = QApplication(sys.argv)
engine = QQmlApplicationEngine()
py = Py()
engine.rootContext().setContextProperty("py", py)
engine.load(QUrl('main.qml'))

sys.exit(app.exec_())
