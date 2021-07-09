from enum import IntEnum
from typing import TypeVar, Generic


class Action(IntEnum):
    DROP = 0
    ACCEPT = 1


T = TypeVar('T')


class Firewall(Generic[T]):
    def add_rule(self, rule: T):
        pass

    def remove_rule(self, rule: T):
        pass

    def filter(self, *args, **kwargs) -> Action:
        pass
