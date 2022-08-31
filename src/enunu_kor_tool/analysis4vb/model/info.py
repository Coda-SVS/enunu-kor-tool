from typing import Dict

from enunu_kor_tool.abc import DictBase
from enunu_kor_tool.analysis4vb.model.files import DB_Files
from enunu_kor_tool.analysis4vb.model.config import DB_Config


class DB_Info(DictBase):
    def __init__(self, path: str, name: str, files: DB_Files, config: DB_Config) -> None:
        self.__db_files = files
        self.__db_config = config
        self._data = {
            "path": path,
            "name": name,
            "files": self.__db_files.as_dict(),
            "config": self.__db_config.as_dict(),
            "cache": {},
            "stats": {},
        }

    @property
    def path(self) -> str:
        return self._data["path"]

    @property
    def name(self) -> str:
        return self._data["name"]

    @property
    def cache(self) -> Dict:
        return self._data["cache"]

    @property
    def files(self):
        return self.__db_files

    @property
    def config(self):
        return self.__db_config

    @property
    def stats(self):
        return self._data["stats"]
