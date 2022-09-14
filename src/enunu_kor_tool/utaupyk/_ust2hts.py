# Copyright (c) 2020 oatsu
# Copyright (c) 2022 cardroid
"""
USTファイルをHTSフルラベルに変換する。
Songオブジェクトを使って生成する。
いまのところ日本語にしか対応していないので注意。

対象
    CQS:
        p11, p12, p13, p14
        a1, a2, a3,
        b1, b2, b3,
        c1, c2, c3,
        d1, d2, d3, (d5), d6, d7, d8,
        e1, e2, e3, (e5), e6, e7, e8, e57, e58,
        f1, f2, f3, (f5), f6, f7, f8
    QS:
        p1, p3, p4, p5

d2, d3, e2, e3, f2, f3 はスケール判定が必要なため、実行時にキー(スケール)を指定する必要がある。
キーを指定しない場合は上記の値は'xx'のままにする。
d3, e3, f3 には 'xx' を代入する。歌うときに休符の学習データ引っ張ってきそうな気はする。
"""
from typing import Tuple
import utaupy as up

from tqdm import tqdm

from enunu_kor_tool import g2pk4utau, log


# def note_preprocessing(note: up.ust.Note) -> bool:
#     return g2pk4utau.isCanConvert(note.lyric)


def lyric_preprocessing(lyric: str) -> str:
    return lyric.replace("i'am", "i am").replace("we're", "we are").replace("you're", "you are").replace("'", " ")


def is_lyric(note: up.ust.Note, d_table: dict) -> bool:
    """가사 또는 음소의 여부를 반별합니다.

    Args:
        note (up.ust.Note): 노트

    Returns:
        bool: 가사일 경우 True, 아닐경우 False를 출력합니다.
    """
    # return not note.lyric.startswith("$")
    for ly in note.lyric.split(" "):
        if ly in d_table:
            return False
    return True


def ustnote2htsnote(ust_note_block: Tuple[up.ust.Note, up.ust.Note, up.ust.Note], d_table: dict, g2p_converter, key_of_the_note: int = None) -> up.hts.Note:
    """
    utaupy.ust.Note を utaupy.hts.Note に変換する。
    """
    assert len(ust_note_block) == 3

    logger = log.get_logger(ustnote2htsnote)

    # ノート全体の情報を登録
    hts_note = up.hts.Note()
    # e1
    hts_note.notenum = ust_note_block[1].notenum
    # e2-e3
    if key_of_the_note is not None:
        # e2
        hts_note.relative_pitch = (ust_note_block[1].notenum - key_of_the_note) % 12
        # e3
        hts_note.key = key_of_the_note
    # e5
    hts_note.tempo = round(ust_note_block[1].tempo)
    # e8
    hts_note.length = round(ust_note_block[1].length / 20)

    hts_syllable = up.hts.Syllable()

    phonemes = []

    ust_note_block[1].lyric = ust_note_block[1].lyric.replace("'", " ")

    if g2p_converter != None and is_lyric(ust_note_block[1], d_table):
        current_phn_idx = 1

        orginal_lyrics = ""
        for idx in range(3):
            if isinstance(ust_note_block[idx], up.ust.Note):
                if is_lyric(ust_note_block[idx], d_table):
                    orginal_lyrics += ust_note_block[idx].lyric

                    if idx != 2 and (
                        not g2pk4utau.is_in_hangul(ust_note_block[idx].lyric)
                        or (isinstance(ust_note_block[idx + 1], up.ust.Note) and not g2pk4utau.is_in_hangul(ust_note_block[idx + 1].lyric))
                    ):
                        orginal_lyrics += " "
                elif idx == 0:
                    current_phn_idx = 0

        kor_phn_result = g2p_converter(g2pk4utau.clear_Special_Character(lyric_preprocessing(orginal_lyrics)))
        if g2pk4utau.is_in_hangul(ust_note_block[1].lyric):
            kor_phn_tokens = kor_phn_result[2][current_phn_idx]
        else:
            kor_phn_tokens = kor_phn_result[3][current_phn_idx]

        # tqdm.write(f"[{kor_phn_tokens}]")
        # tqdm.write(f"flag = [{ust_note_block[1].flag}]")
        # tqdm.write(f"kor_phn_tokens = [{kor_phn_tokens}], current_phn_idx = [{current_phn_idx}]")
        # tqdm.write(f"[{ust_note_block[1].lyric}] -> [{orginal_lyrics}] -> [{kor_phn_tokens}]")

        if g2pk4utau.is_in_special_character(ust_note_block[1].lyric):
            # 특수문자 처리
            temp_phn_tokens = []
            for ly in ust_note_block[1].lyric:
                if g2pk4utau.is_in_special_character(ly):
                    temp_phn_tokens.extend(d_table.get(ly, [ly]))
                else:
                    temp_phn_tokens.append(kor_phn_tokens if isinstance(kor_phn_tokens, str) else " ".join(kor_phn_tokens))
            kor_phn_token = " ".join(temp_phn_tokens)

            logger.info(f"\033[1;33m G* [{orginal_lyrics}] -> [{kor_phn_result[1]}] -> [{kor_phn_tokens} ({current_phn_idx})] -> [{kor_phn_token}]\033[0m")
        else:
            kor_phn_token: str = kor_phn_tokens if isinstance(kor_phn_tokens, str) else " ".join(kor_phn_tokens)

            logger.info(f"\033[1;33m G  [{orginal_lyrics}] -> [{kor_phn_result[1]}] -> [{kor_phn_tokens} ({current_phn_idx})] -> [{kor_phn_token}]\033[0m")

        phonemes += kor_phn_token.split(" ")
    else:
        orginal_lyrics = ust_note_block[1].lyric.split()

        for lyric in orginal_lyrics:
            phonemes += d_table.get(lyric, [lyric])

        logger.info(f"\033[1;32m D  [{ust_note_block[1].lyric}] -> [{orginal_lyrics}] -> [{phonemes}]\033[0m")

    # tqdm.write(f"[{phonemes}]")

    # 音素を追加していく
    for phoneme in phonemes:
        hts_phoneme = up.hts.Phoneme()
        # p4
        hts_phoneme.identity = phoneme
        # p9
        # ustのローカルフラグが設定されている時だけp9に記入
        if ust_note_block[1].flags != "":
            hts_phoneme.flag = ust_note_block[1].flags
        # 音節に追加
        hts_syllable.append(hts_phoneme)
    hts_note.append(hts_syllable)

    return hts_note


def ustobj2songobj(ust: up.ust.Ust, d_table: dict, g2p_converter=None, key_of_the_note: int = None) -> up.hts.Song:
    """
    Ustオブジェクトをノートごとに処理して、HTS用に変換する。
    日本語歌詞を想定するため、音節数は1とする。促音に注意。

    ust: Ustオブジェクト
    d_table: 日本語→ローマ字変換テーブル

    key_of_the_note:
        曲のキーだが、USTからは判定できない。
        Sinsyでは 0 ~ 11 または 'xx' である。
    """

    logger = log.get_logger(ustobj2songobj)

    if g2p_converter == None:
        logger.info("> Unable g2p_converter")
    else:
        logger.info("> Apply g2p_converter")

    song = up.hts.Song()
    # Noteオブジェクトの種類を変換
    notes_len = len(ust.notes)

    logger.debug(f"notes_len: {notes_len}")

    for idx in tqdm(range(notes_len), leave=False):
        prev_note = ust.notes[idx - 1] if idx != 0 else ""
        next_note = ust.notes[idx + 1] if idx + 1 < notes_len else ""

        note_block = (prev_note, ust.notes[idx], next_note)

        hts_note = ustnote2htsnote(note_block, d_table, g2p_converter, key_of_the_note=key_of_the_note)
        song.append(hts_note)

    # ノート長や位置などを自動補完
    song.autofill()
    # 発声開始時刻と終了時刻をノート長に応じて設定
    song.reset_time()
    return song


def ust2hts(path_ust: str, path_hts: str, path_table: str, g2p_converter=None, strict_sinsy_style: bool = True, as_mono: bool = False):
    """
    USTファイルをLABファイルに変換する。
    """
    ust = up.ust.load(path_ust)
    d_table = up.table.load(path_table, encoding="utf-8")

    # Ust → HTSFullLabel
    hts_song = ustobj2songobj(ust, d_table, g2p_converter)
    # HTSFullLabel中の重複データを削除して整理
    # ファイル出力
    hts_song.write(path_hts, strict_sinsy_style=strict_sinsy_style, as_mono=as_mono)


# def main():
#     """
#     USTファイルをLABファイルおよびJSONファイルに変換する。
#     """
#     from os.path import dirname, splitext, basename
#     from utaupy.utils import hts2json

#     # 各種パスを指定
#     # path_table = input("path_table: ")
#     # path_ust_in = input("path_ust: ")
#     path_table = "dic\\hangul.table"
#     path_ust_in = "singing_database\\ust_auto_exp\\1_80.ust"
#     path_hts_out = dirname(path_ust_in) + "/" + splitext(basename(path_ust_in))[0] + "_ust2hts.lab"
#     path_json_out = dirname(path_ust_in) + "/" + splitext(basename(path_ust_in))[0] + "_ust2hts.json"
#     # 変換
#     ust2hts(path_ust_in, path_hts_out, path_table, g2pk4utau.g2pk4utau(), strict_sinsy_style=False)
#     # jsonファイルにも出力する。
#     hts2json(path_hts_out, path_json_out)


# if __name__ == "__main__":
#     main()
