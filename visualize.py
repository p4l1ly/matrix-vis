import base64
from io import BytesIO
import pickle
import sys

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.colors import LightSource, TABLEAU_COLORS
import mpl_toolkits.mplot3d
import numpy as np
import re
import json
import ruamel.yaml
import zmq

def flatten(l):
    for el in l:
        if el.__class__ is list:
            yield from flatten(el)
        else:
            yield el

data = ruamel.yaml.load(sys.stdin, Loader=ruamel.yaml.Loader)
ruamel.yaml.round_trip_dump(data['info'], sys.stdout)
dimensions = data['dimensions']
if 'matrix_numpy' in data:
    matrix = np.load(BytesIO(base64.b64decode(data['matrix_numpy'])))
else:
    for x in flatten(data['matrix']):
        assert x.__class__ in [int, float], Exception(f'Not a number {repr(x)}')

    matrix = np.array(data['matrix'])

assert len(dimensions) >= 2
assert all(len(tics) >= 1 for tics in dimensions.values())
assert matrix.shape == tuple(len(tics) for tics in dimensions.values())

keys = list(dimensions.keys())

config = [0 for _ in dimensions]

SLICE_ALL = slice(None, None, None)

if len(dimensions) >= 3:
    config[-3] = 'x', SLICE_ALL
    config[-2] = 'y', SLICE_ALL
    config[-1] = [(0, 1)]
else:
    config[-2] = 'y', SLICE_ALL
    config[-1] = [(0, 1)]

def plot_data():
    x_ix = next(i
        for i, x in enumerate(config)
        if x.__class__ is tuple and x[0] == 'x'
    )

    try:
        y_ix = next(i
            for i, x in enumerate(config)
            if x.__class__ is tuple and x[0] == 'y'
        )
        is_3d = True
    except StopIteration:
        is_3d = False

    change_dimension_count = is_3d != plot_data.is_3d
    plot_data.is_3d = is_3d

    series_ix, series = next((i, x)
        for i, x in enumerate(config)
        if x.__class__ is list
    )

    slices = tuple(
        {
            int: (lambda x: x),
            tuple: (lambda x: x[1]),
            list: (lambda _: SLICE_ALL)
        }[x.__class__](x)
        for x in config
    )

    arr = matrix[slices]

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

def mypause(interval):
    backend = plt.rcParams['backend']
    if backend in matplotlib.rcsetup.interactive_bk:
        figManager = matplotlib._pylab_helpers.Gcf.get_active()
        if figManager is not None:
            canvas = figManager.canvas
            if canvas.figure.stale:
                canvas.draw()
            canvas.start_event_loop(interval)
            return

def show_plot():
    fig = plt.figure()
    ax = replot(fig, None)

    ctx = zmq.Context()
    socket = ctx.socket(zmq.REP)
    socket.bind('tcp://0.0.0.0:8989')

    fig.show()

    while plt.fignum_exists(fig.number):
        mypause(0.1)

        rs, _, es = zmq.select([socket], [], [socket], timeout=0)
        if rs or es:
            config[:] = pickle.loads(socket.recv())
            ax = replot(fig, ax)
            socket.send(b'')


show_plot()
sys.exit()
