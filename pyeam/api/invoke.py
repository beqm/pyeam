from pyeam.api.client import ClientServer


def command(func):
    # Register the route with ClientServer
    ClientServer._route(func.__name__, command=func, method="GET")
    return func