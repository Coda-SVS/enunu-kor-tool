from typing import Dict, List

from enunu_kor_tool.abc import DictBase


class DB_Config_Phonemes(DictBase):
    def __init__(self, config_phonemes: Dict) -> None:
        self._data = config_phonemes

        all_phn_list = []
        all_phn_list.extend(self.silence)
        all_phn_list.extend(self.consonant)
        all_phn_list.extend(self.vowel)
        all_phn_list.extend(self.other)

        self.__all_phn_list = all_phn_list

    @property
    def all(self) -> List[str]:
        return self.__all_phn_list

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
