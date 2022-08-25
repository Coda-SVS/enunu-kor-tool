from typing import Dict, List

from enunu_kor_tool.abc import DictBase


class DB_Files(DictBase):
    def __init__(self, ustx_files: List[str], ust_files: List[str], lab_files: List[str], wav_files: List[str]) -> None:
        self.data = {
            "ustx": ustx_files,
            "ust": ust_files,
            "lab": lab_files,
            "wav": wav_files,
        }

    @property
    def ustx(self) -> List[str]:
        return self.data["ustx"]

    @property
    def ust(self) -> List[str]:
        return self.data["ust"]

    @property
    def lab(self) -> List[str]:
        return self.data["lab"]

    @property
    def wav(self) -> List[str]:
        return self.data["wav"]


class DB_Stats(DictBase):
    def __init__(self) -> None:
        self.data = {
            "lab_count": {},
        }

    @property
    def lab_count(self) -> Dict:
        return self.data["lab_count"]


class DB_Info(DictBase):
    def __init__(self, path: str, name: str, temp_path: str, files: DB_Files, config: Dict) -> None:
        self.db_stats = DB_Stats()
        self.db_files = files
        self.data = {
            "path": path,
            "name": name,
            "temp_path": temp_path,
            "files": self.db_files.as_dict(),
            "config": config,
            "stats": self.db_stats.as_dict(),
        }

    @property
    def path(self) -> str:
        return self.data["path"]

    @property
    def name(self) -> str:
        return self.data["name"]

    @property
    def temp_path(self) -> str:
        return self.data["temp_path"]

    @property
    def files(self):
        return self.db_files

    @property
    def config(self) -> Dict:
        return self.data["config"]

    @property
    def stats(self):
        return self.db_stats
