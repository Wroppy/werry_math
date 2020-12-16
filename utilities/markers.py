from typing import Callable, Optional


class Marker:
    """
    Marker that tells the gui to ignore scanning something
    """
    attribute = "_ignored"

    @staticmethod
    def ignore_this(fn):
        fn._ignored = True
        return fn

    @staticmethod
    def is_ignored(fn) -> bool:
        return hasattr(fn, Marker.attribute) and fn._ignored


class ProxyPackage:
    def __init__(self, fn, args, kwargs):
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    def call(self):
        self.fn(*self.args, **self.kwargs)


class Proxy:
    """
    Allow running stuff in main thread
    """
    # have to resort to this global state
    proxy_fn: Optional[Callable] = None

    @staticmethod
    def runInMainThread(fn):
        def wrapper(*args, **kwargs):
            if Proxy.proxy_fn is None:
                return fn(*args, **kwargs)
            return Proxy.proxy_fn(fn, args, kwargs)

        return wrapper
