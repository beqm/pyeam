from pyeam.core.builder import Builder


def command(func):
    from pyeam.core.ipc import IPC
    IPC._route(func.__name__, command=func, method="GET")
    return func