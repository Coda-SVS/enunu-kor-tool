from typing import List

from enunu_kor_tool.abc import DictBase


class DB_Files(DictBase):
    def __init__(self, ustx_files: List[str], ust_files: List[str], lab_files: List[str], wav_files: List[str]) -> None:
        self._data = {
            "ustx": ustx_files,
            "ust": ust_files,
            "lab": lab_files,
            "wav": wav_files,
        }

    @property
    def ustx(self) -> List[str]:
        return self._data["ustx"]

    @property
    def ust(self) -> List[str]:
        return self._data["ust"]

    @property
    def lab(self) -> List[str]:
        return self._data["lab"]

    @property
    def wav(self) -> List[str]:
        return self._data["wav"]
