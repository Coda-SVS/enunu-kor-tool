from typing import Dict, Union

from enunu_kor_tool.abc import DictBase
from enunu_kor_tool.analysis4vb.model.files import DB_Files
from enunu_kor_tool.analysis4vb.model.config import DB_Config


class DB_Info(DictBase):
    def __init__(self, path: str, name: str, temp_path: str, files: DB_Files, config: Union[Dict, DB_Config]) -> None:
        self.__db_files = files
        self.__db_config = config if isinstance(config, DB_Config) else DB_Config(config)
        self._data = {
            "path": path,
            "name": name,
            "temp_path": temp_path,
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
    def temp_path(self) -> str:
        return self._data["temp_path"]

    @property
    def cache(self) -> str:
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
