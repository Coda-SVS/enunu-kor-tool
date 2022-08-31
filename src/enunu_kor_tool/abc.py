from pprint import pformat
from typing import Dict


class DictBase:
    _data: Dict = {}

    def as_dict(self) -> Dict:
        return self._data

    def __str__(self) -> str:
        return pformat(self._data)
