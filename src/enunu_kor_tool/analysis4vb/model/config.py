from typing import Dict, List

from enunu_kor_tool.abc import DictBase
from enunu_kor_tool.analysis4vb.config import DEFAULT_CONFIG
from enunu_kor_tool.analysis4vb.model.config_phonemes import DB_Config_Phonemes


class DB_Config(DictBase):
    def __init__(self, config: Dict) -> None:
        self._data.update(DEFAULT_CONFIG)
        self._data.update(config)
        self.__config_phonemes = DB_Config_Phonemes(config["phonemes"])

    @property
    def options(self) -> Dict:
        return self._data["options"]

    @property
    def funcs(self) -> List[str]:
        return self._data["funcs"]

    @property
    def phonemes(self):
        return self.__config_phonemes
