# Copyright (c) 2022 cardroid

from glob import glob
import os

import yaml
from tqdm import tqdm


class Ustx2Ust_Converter:
    def __init__(self, path, encoding="cp932") -> None:
        try:
            with open(path, mode="r", encoding=encoding) as f:
                self.ustx = yaml.load(f, Loader=yaml.FullLoader)
        except UnicodeDecodeError:
            try:
                with open(path, mode="r", encoding="utf-8") as f:
                    self.ustx = yaml.load(f, Loader=yaml.FullLoader)
            except UnicodeDecodeError:
                with open(path, mode="r", encoding="utf-8_sig") as f:
                    self.ustx = yaml.load(f, Loader=yaml.FullLoader)

    def save_ust(self, path: str):
        project = self.ustx
        project_body = project["voice_parts"][0]

        with open(path, "w", encoding="utf-8") as ust:
            # Header
            ust.write("[#SETTING]\n")
            ust.write(f"Tempo={project['bpm']}\n")
            ust.write("Tracks=1\n")
            ust.write(f"Project={project_body['name']}.ust\n")
            ust.write(f"CacheDir={project_body['name']}.cache\n")
            ust.write("Mode2=True\n")

            # Body
            position = 0
            idx = 0
            for note in project_body["notes"]:
                current_pos = note["position"]
                current_dur = note["duration"]
                if position < current_pos:
                    ust.write(f"[#{str(idx).zfill(4)}]\n")
                    ust.write(f"Length={current_pos - position}\n")
                    ust.write("Lyric=R\n")
                    ust.write("NoteNum=60\n")
                    ust.write("PreUtterance=\n")

                    idx += 1

                ust.write(f"[#{str(idx).zfill(4)}]\n")
                ust.write(f"Length={current_dur}\n")
                ust.write(f"Lyric={note['lyric']}\n")
                ust.write(f"NoteNum={note['tone']}\n")
                ust.write("PreUtterance=\n")

                idx += 1
                position = current_pos + current_dur

            # Footer

            ust.write(f"[#TRACKEND]\n")

    def __str__(self) -> str:
        # result = ""

        # for k, v in self.ustx:
        #     result += f"{k} = {v}"

        return str(self.ustx)


def ustx2ust(db_root, out_dir):
    target_files = glob(f"{db_root}/**/*.ustx", recursive=True)
    if len(target_files) != 0:
        os.makedirs(out_dir, exist_ok=True)
        print(f"Converting ustx files")
        for path in tqdm(target_files):
            converter = Ustx2Ust_Converter(path)
            name, ext = os.path.splitext(os.path.basename(path))
            converter.save_ust(os.path.join(out_dir, f"{name}.ust"))


import shutil
from sys import argv


def ustx2ust_main(path_config_yaml):
    with open(path_config_yaml, "r") as fy:
        config = yaml.load(fy, Loader=yaml.FullLoader)
    db_root = os.path.expanduser(config["stage0"]["db_root"]).strip('"')
    out_dir = os.path.join(db_root, "ust_auto_exp")

    if os.path.isdir(out_dir):
        shutil.rmtree(out_dir)

    ustx2ust(db_root, out_dir)


if __name__ == "__main__":
    ustx2ust_main(argv[1].strip('"'))
