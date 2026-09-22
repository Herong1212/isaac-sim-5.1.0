from typing import TypeVar, List, Optional, Iterable, Iterator, Callable

T = TypeVar('T')


class SparseList(Iterable[T]):
    def __init__(self):
        self._callback_list: List[T] = []

    def __iter__(self) -> Iterator[T]:
        return self._callback_list.__iter__()

    def add(self, callback: Callable) -> Optional[int]:
        if not callback:
            return None
        for i in range(len(self._callback_list)):
            if self._callback_list[i] is None:
                self._callback_list[i] = callback
                return i
        self._callback_list.append(callback)
        return len(self._callback_list) - 1

    def remove(self, index: int) -> bool:
        if index is not None and 0 <= index < len(self._callback_list):
            self._callback_list[index] = None
            return True
        return False
