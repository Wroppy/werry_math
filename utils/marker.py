class Marker:
    attribute = "_ignored"
    ignored = []

    @staticmethod
    def ignore_this(fn):
        fn._ignored = True
        return fn

    @staticmethod
    def is_ignored(fn) -> bool:
        return hasattr(fn, Marker.attribute) and fn._ignored
