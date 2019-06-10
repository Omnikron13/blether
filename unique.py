class Unique(type):
    _instances = dict()

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = dict()
        if args[0] not in cls._instances[cls]:
            cls._instances[cls][args[0]] = super().__call__(*args, **kwargs)
        return cls._instances[cls][args[0]]
