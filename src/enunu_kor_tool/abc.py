from pprint import pformat
from typing import Dict


class DictBase:
    data: Dict

    def as_dict(self) -> Dict:
        return self.data

    def __str__(self) -> str:
        return pformat(self.data)
