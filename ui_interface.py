from abc import abstractmethod

from singleton import AbstractSingleton


class UIInterface(metaclass=AbstractSingleton):
    @abstractmethod
    def runloop(self):
        pass

    @abstractmethod
    def infodialogue(self, title: str, message: str):
        pass

    @abstractmethod
    def addfeeddialogue(self):
        pass
