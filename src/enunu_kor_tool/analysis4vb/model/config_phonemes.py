from typing import Dict, List

from enunu_kor_tool.abc import DictBase


class DB_Config_Phonemes(DictBase):
    def __init__(self, config_phonemes: Dict) -> None:
        self._data = config_phonemes

    @property
    def silence(self) -> List[str]:
        return self._data["silence"]

    @property
    def consonant(self) -> List[str]:
        return self._data["consonant"]

    @property
    def vowel(self) -> List[str]:
        return self._data["vowel"]

    @property
    def other(self) -> List[str]:
        return self._data["other"]
