__all__ = ["ColumnRegistry"]
from typing import Optional, Dict
import carb
from .delegate.abstract_column_delegate import AbstractColumnDelegate


class ColumnRegistry:
    """
    Registry for action columns.
    """
    def __init__(self):
        self._max_column_id = -1
        self._delegates: Dict[int, AbstractColumnDelegate] = {}

    @property
    def max_column_id(self) -> int:
        """
        Max column id registered.
        """
        return self._max_column_id

    def register_delegate(self, delegate: AbstractColumnDelegate, column_id: int=-1,  overwrite_if_exists: bool=True) -> bool:
        """
        Register a delegate for a column.

        Args:
            delegate (AbstractColumnDelegate): Delegate to show a column.
        
        Kwargs:
            column_id (int): Column id. Default -1 means auto generation.
            overwrite_if_exists (bool): Overwrite exising delegate if True. Otherwise False.
        """
        if column_id < 0:
            column_id = self._max_column_id + 1
        if column_id in self._delegates:
            if not overwrite_if_exists:
                carb.log_warn(f"A delegate already registered for column {column_id}!")
                return False
        self._delegates[column_id] = delegate
        self._max_column_id = column_id
        return True

    def unregister_delegate(self, column_id: int) -> bool:
        """
        Unregister a delegate for a column.

        Args:
            column_id (int): Column id to unregister.
        """
        if column_id in self._delegates:
            self._delegates.pop(column_id)
            if column_id == self._max_column_id:
                self._max_column_id -= 1

    def get_delegate(self, column_id: int) -> Optional[AbstractColumnDelegate]:
        """
        Retrieve a delegate for a column.

        Args:
            column_id (int): Column id.
        """
        if column_id in self._delegates:
            return self._delegates[column_id]
        else:
            return None
