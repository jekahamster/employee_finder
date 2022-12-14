from abc import ABC
from abc import abstractmethod


class BaseParser(ABC):
    @abstractmethod
    def get_data(self, *args, **kwargs):
        return NotImplemented