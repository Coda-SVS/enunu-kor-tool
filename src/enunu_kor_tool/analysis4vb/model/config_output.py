from os import makedirs
from typing import Dict

from enunu_kor_tool.abc import DictBase
from enunu_kor_tool.analysis4vb.config import DEFAULT_CONFIG


class DB_Config_Output(DictBase):
    def __init__(self, db_path: str, config: Dict) -> None:
        self._data.update(DEFAULT_CONFIG["output"])
        self._data.update(config)

        db_path = {"db_path": db_path}
        self._data["stats"] = self._data["stats"] % db_path
        self._data["graph"] = self._data["graph"] % db_path
        self._data["temp"] = self._data["temp"] % db_path

    @property
    def stats(self) -> str:
        path = self._data["stats"]
        makedirs(path, exist_ok=True)
        return path

    @property
    def graph(self) -> str:
        path = self._data["graph"]
        makedirs(path, exist_ok=True)
        return path

    @property
    def temp(self) -> str:
        path = self._data["temp"]
        makedirs(path, exist_ok=True)
        return path
