from functools import wraps
import pickle
import sys
import traceback

from PySide2.QtCore import Property, QObject, QUrl, Signal, Slot
import ruamel.yaml
import zmq

data = ruamel.yaml.load(sys.stdin.read(), Loader=ruamel.yaml.Loader)
ruamel.yaml.round_trip_dump(sys.stdin.read(), sys.stdout)
dimensions = [[name, tics] for name, tics in data['dimensions'].items()]

ctx = zmq.Context()
socket = ctx.socket(zmq.REQ)
socket.connect('tcp://0.0.0.0:8989')

def track_error(fn):
    @wraps(fn)
    def wrapped_fn(self, *largs, **kargs):
        try:
            fn(self, *largs, **kargs)
            self.error = ''
        except Exception as e:
            traceback.print_exc(); sys.stderr.flush()
            self.error = str(e)

    return wrapped_fn

def pause_update(fn):
    @wraps(fn)
    def wrapped_fn(self, *largs, **kargs):
        updated = [False]
        def update():
            updated[0] = True

        self.update, tmp = update, self.update
        try:
            fn(self, *largs, **kargs)
        finally:
            self.update = tmp
            if updated[0]:
                self.update()

    return wrapped_fn

class NotifP(QObject): pass

def notif(type_):
    class Notif(NotifP):
        def __init__(self, val=None):
            self._val = val
            super().__init__()

        @Signal
        def changed(self):
            pass
        def read(self): return self._val
        def write(self, val):
            if self._val != val:
                self._val = val
                self.changed.emit()
                py.update()

        val = Property(type_, read, write, notify=changed)

    return Notif

NBool = notif(bool)
NFloat  = notif(float)

def unnotif(x):
    if isinstance(x, NotifP):
        return x.val
    elif isinstance(x, list):
        return [unnotif(y) for y in x]

def set_notif(old, new):
    if isinstance(old, NotifP):
        old.val = new
    elif isinstance(old, list):
        for o, n in zip(old, new):
            set_notif(o, n)

dimensions = [
    [
        dimName,
        [NBool(False), NBool(False), NBool(False)],
        [[ticName, NBool(True), NFloat(1)] for ticName in tics]
    ]
    for dimName, tics in dimensions
]

if len(dimensions) >= 3:
    dimensions[-3][1][0]._val = True
    dimensions[-2][1][1]._val = True
else:
    dimensions[-2][1][0]._val = True

dimensions[-1][1][2]._val = True

class Py(QObject):
    def __init__(self):
        self._error = ''
        super().__init__()

    dimensions = Property('QVariantList', lambda _: dimensions, constant=True)

    error_changed = Signal()
    def read_error(self): return self._error
    def write_error(self, error):
        self._error = error
        self.error_changed.emit()
    error = Property(str, read_error, write_error, notify=error_changed)

    @Slot()
    @track_error
    def save_to_file(self):
        with open('setting.yaml', 'w') as f:
            f.write(yaml.dump(unnotif(dimensions)))

    @Slot()
    @track_error
    @pause_update
    def load_from_file(self):
        with open('setting.yaml', 'r') as f:
            set_notif(dimensions, yaml.load(f.read(), Loader=yaml.FullLoader))

    @Slot(int)
    @pause_update
    def clear_dimension(self, ix):
        for tic in dimensions[ix][2]:
            tic[1].val = False

    @Slot(int)
    @pause_update
    def invert_dimension_filter(self, ix):
        for tic in dimensions[ix][2]:
            tic[1].val = not tic[1].val

    @track_error
    def update(self):
        socket.send(pickle.dumps(self.translate_setting()))
        socket.recv()

    def check_setting(self, dims):
        if all(not axes[0] for _, axes, _ in dims):
            raise Exception('x must exist')
        if all(not axes[2] for _, axes, _ in dims):
            raise Exception('series must exist')
        if  any(sum(ax for ax in axes) > 1 for _, axes, _ in dims):
            raise Exception('multiple axes at the same dimension')
        if any(
            all(not enabled for _, enabled, _ in tics)
            for _, _, tics in dims
        ):
            raise Exception('empty filter')

    def translate_setting(self):
        dims = unnotif(dimensions)
        self.check_setting(dims)

        result = []
        for _, axes, tics in dims:
            if not any(axes):
                result.append(next(i for i, tic in enumerate(tics) if tic[1]))
            elif axes[2]:
                result.append([
                    (i, scale)
                    for i, (_, enabled, scale) in enumerate(tics)
                    if enabled
                ])
            else:
                dim = [i for i, (_, enabled, _) in enumerate(tics) if enabled]
                if len(dim) == len(tics):
                    dim = slice(None, None, None)
                result.append(('x' if axes[0] else 'y', dim))

        return result

from PySide2.QtWidgets import QApplication
from PySide2.QtQml import QQmlApplicationEngine

app = QApplication(sys.argv)
engine = QQmlApplicationEngine()
py = Py()
py.update()
engine.rootContext().setContextProperty("py", py)
engine.load(QUrl('main.qml'))

sys.exit(app.exec_())
