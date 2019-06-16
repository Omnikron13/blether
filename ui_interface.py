from abc import abstractmethod

from singleton import AbstractSingleton


class UIInterface(metaclass=AbstractSingleton):
    @abstractmethod
    def infodialogue(self):
        pass
