import pickle
from typing import Dict, Optional


class DisplayBundle:
    """
    Bundle that manages saving and loading data
    """
    ext: str = '.pik'
    data: Dict

    def __init__(self, data=None):
        if data is not None:
            self.data = data
        else:
            self.data = {}

    def set(self, key: str, obj: object):
        self.data[key] = obj

    def get(self, key: str) -> object:
        return self.data[key]

    def dump(self, path: str):
        with open(path + DisplayBundle.ext, 'wb') as f:
            pickle.dump(self.data, f)

    @staticmethod
    def load(path: str) -> Optional['DisplayBundle']:
        try:
            with open(path + DisplayBundle.ext, 'rb') as f:
                data = pickle.load(f)
                return DisplayBundle(data)
        except OSError:
            return None
