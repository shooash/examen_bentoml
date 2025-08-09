import os

class _MetaPaths:
    raw = os.path.abspath(os.path.join(os.path.dirname(__file__), r'../data/raw'))
    processed = os.path.abspath(os.path.join(os.path.dirname(__file__), r'../data/processed'))
    logs = os.path.abspath(os.path.join(os.path.dirname(__file__), r'../'))

    def __init__(self, *name):
        pass
        
    def __getattribute__(cls, name):
        if name.startswith('_'):
            return object.__getattribute__(cls, name)
        return object.__getattribute__(cls, '_get')(name)
    def __class_getitem__(cls, name):
        return object.__getattribute__(cls, '_get')(name)
    @classmethod
    def _get(cls, name : str):
        target_key = name.lower()
        if target_key in cls.__dict__:
            target_dir = object.__getattribute__(cls, target_key)
            return object.__getattribute__(cls, '_get_path_loader')(target_dir)
        raise KeyError(f'Target folder {name} is unknown.')
    @staticmethod
    def _get_path_loader(path : str):
        return lambda *filename: os.path.abspath(os.path.join(path, *filename or ''))

class Targets(metaclass=_MetaPaths):
    pass

# Usage:
# Targets.processed('X_train.csv') # => "C:\\Users\\...\\data\\processed\\X_train.csv"
