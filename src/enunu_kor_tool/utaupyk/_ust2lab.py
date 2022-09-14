#!/usr/bin/env python3
# Copyright (c) 2021 oatsu
"""
UST版
フルラベルを生成する。また、DB中のモノラベルを複製する。

- '{out_dir}/sinsy_full' にフルラベルを生成する。
- '{out_dir}/sinsy_mono' にモノラベルを生成する。(この工程は省略した)
- '{out_dir}/mono_label' にDBのモノラベルを複製する
"""
from glob import glob
from os import makedirs
from os.path import basename, join, splitext
from sys import argv

import yaml
from natsort import natsorted
from tqdm import tqdm

from enunu_kor_tool import log


def ust2full(path_ust_dir_in, path_full_dir_out, path_table, exclude_songs, lang_mode):
    """
    複数のUSTファイルから、フルラベルファイルを一括生成する。
    """
    makedirs(path_full_dir_out, exist_ok=True)
    ust_files = glob(f"{path_ust_dir_in}/**/*.ust", recursive=True)

    if lang_mode == "kor":
        from enunu_kor_tool import g2pk4utau
        from enunu_kor_tool.utaupyk import _ust2hts as utaupyk_ust2hts

        # 객체 생성 시 높은 오버헤드 때문에 시간이 오래걸리는 문제 해결
        # 모든 작업이 끝나고 해제되도록 외부에서 초기화
        g2p_converter = g2pk4utau.g2pk4utau.get_instance()
    else:
        from utaupy.utils import ust2hts

    for path_ust in tqdm(ust_files):
        songname = splitext(basename(path_ust))[0]
        if songname in exclude_songs:
            print(f"Skip excluded song: {songname}")
        else:
            path_full = f"{path_full_dir_out}/{songname}.lab"
            if lang_mode == "kor":
                utaupyk_ust2hts.ust2hts(path_ust, path_full, path_table, g2p_converter=g2p_converter, strict_sinsy_style=False)
            else:
                ust2hts(path_ust, path_full, path_table, strict_sinsy_style=False)

    # if lang_mode == "kor" and g2p_converter != None:
    #     del g2p_converter


def compare_number_of_ustfiles_and_labfiles(ust_dir, mono_align_dir):
    """
    入力ファイルの数が一致するか点検する。
    """
    # UST一覧を取得
    ust_files = natsorted(glob(f"{ust_dir}/*.ust"))
    # DB内のラベルファイル一覧を取得
    mono_files = natsorted(glob(f"{mono_align_dir}/*.lab"))
    # 個数が合うか点検
    assert len(ust_files) == len(mono_files), f"USTファイル数({len(ust_files)})とLABファイル数({len(mono_files)})が一致しません"


def compare_name_of_ustfiles_and_labfiles(ust_dir, mono_align_dir):
    """
    入力ファイルの名前が一致するか点検する。
    """

    logger = log.get_logger(compare_name_of_ustfiles_and_labfiles)
    
    # UST一覧を取得
    ust_files = natsorted(glob(f"{ust_dir}/*.ust"))
    # DB内のラベルファイル一覧を取得
    mono_files = natsorted(glob(f"{mono_align_dir}/*.lab"))

    # 名前が合うか点検
    songnames_dont_match = []
    for path_ust, path_lab in zip(ust_files, mono_files):
        ust_songname = splitext(basename(path_ust))[0]
        mono_songname = splitext(basename(path_lab))[0]
        if ust_songname != mono_songname:
            songnames_dont_match.append([path_ust, path_lab])
    # すべての名前が一致したか確認
    if len(songnames_dont_match) != 0:
        for path_ust_and_path_lab in songnames_dont_match:
            logger.error("USTファイル名とLABファイル名が一致しません:")
            logger.error("  path_ust: %s", path_ust_and_path_lab[0])
            logger.error("  path_lab: %s", path_ust_and_path_lab[1])
        raise ValueError("USTファイル名とLABファイル名が一致しませんでした。ファイル名を点検してください")


def ust2lab_main(path_config_yaml):
    """
    1. yamlを読み取って、以下の項目を取得する。
        - 歌唱DBのパス
        - 変換辞書のパス
        - 学習用データ出力フォルダ
    2. USTファイルとLABファイルの数と名前が一致するか点検する。
    3. USTファイルからフルラベルを生成する。
    """
    # 設定ファイルを読み取る
    with open(path_config_yaml, "r") as fy:
        config = yaml.load(fy, Loader=yaml.FullLoader)
    exclude_songs = config["exclude_songs"]
    out_dir = config["out_dir"].strip('"')
    path_table = config["table_path"].strip('"')

    lang_mode = config["stage0"].get("lang_mode", "jpn").strip('"')

    ust_dir = join(out_dir, "ust")
    mono_align_dir = join(out_dir, "lab")
    full_score_dir = join(out_dir, "full_score")

    # ファイル数と名前が一致するか点検
    compare_number_of_ustfiles_and_labfiles(ust_dir, mono_align_dir)
    compare_name_of_ustfiles_and_labfiles(ust_dir, mono_align_dir)

    print("Converting UST files to full-LAB files")
    # USTからフルラベルを生成
    ust2full(ust_dir, full_score_dir, path_table, exclude_songs=exclude_songs, lang_mode=lang_mode)


if __name__ == "__main__":
    ust2lab_main(argv[1].strip('"'))
