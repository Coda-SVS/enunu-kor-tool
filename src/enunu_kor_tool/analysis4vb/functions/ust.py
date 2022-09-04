import logging
import os
from typing import Dict

from tqdm import tqdm
import utaupy as up
from utaupy.ust import notenum_as_abc

from enunu_kor_tool import lang, log, utils
from enunu_kor_tool.analysis4vb.model import DB_Info

L = lang.get_global_lang()


def __preprocess(func):
    def preprocess_wrapper(db_info: DB_Info, logger: logging.Logger):
        if "usts" not in db_info.cache:
            ust_loader_logger = log.get_logger("ust_loader", db_info.config.options["log_level"])
            is_exist_error = __ust_loader(db_info, ust_loader_logger)
            if is_exist_error:
                ust_loader_logger.warning(L("ust 파일을 로드하는 중 오류가 발견되었습니다. 이후 작업에 영향을 끼칠 수 있습니다."))

        return func(db_info, logger)

    return preprocess_wrapper


def __ust_loader(db_info: DB_Info, logger: logging.Logger) -> bool:
    """
    ust 파일을 로드 및 검사합니다.

    cache.usts에 ust 파일들을 로드하여 저장합니다.

    Returns:
        bool: 오류의 존재 여부
    """

    ust_files = db_info.files.ust
    group_config = db_info.config.group
    encoding = db_info.config.options.get("encoding", "utf-8")
    line_num_formatter = lambda ln: str(ln).rjust(4)

    error_flag = False
    usts = {}

    global_notes_len = 0  # 모든 노트 개수
    global_notes_voiced_len = 0  # 무음을 제외한 노트 개수
    global_notes_length_sum = 0  # 모든 노트의 길이 (s)
    global_notes_voiced_length_sum = 0  # 무음을 제외한 노트의 길이 (s)

    for file in (file_tqdm := tqdm(ust_files, leave=False)):
        file_tqdm.set_description(f"Processing... [{file}]")
        logger.info(L("[{filepath}] 파일 로드 중...", filepath=os.path.relpath(file)))

        ust = up.ust.load(file, encoding=encoding)

        notes_len = 0  # 모든 노트 개수
        notes_voiced_len = 0  # 무음을 제외한 노트 개수
        notes_length_sum = 0  # 모든 노트의 길이 (s)
        notes_voiced_length_sum = 0  # 무음을 제외한 노트의 길이 (s)

        for note in ust.notes:
            if note.lyric not in group_config.silence:
                notes_voiced_len += 1
                notes_voiced_length_sum += note.length_ms / 1000
            notes_len += 1
            notes_length_sum += note.length_ms / 1000

        global_notes_len += notes_len
        global_notes_voiced_len += notes_voiced_len
        global_notes_length_sum += notes_length_sum
        global_notes_voiced_length_sum += notes_voiced_length_sum

        logger.info(
            L(
                "ust 파일을 로드했습니다. [총 노트 수: {notes_len} (무음 제외: {notes_voiced_len})] [총 길이: {round_notes_length_sum}s (무음 제외: {round_notes_voiced_length_sum}s)]",
                notes_len=line_num_formatter(notes_len),
                notes_voiced_len=line_num_formatter(notes_voiced_len),
                round_notes_length_sum=round(notes_length_sum, 3),
                round_notes_voiced_length_sum=round(notes_voiced_length_sum, 3),
            )
        )

        usts[file] = ust
    # logger.info(f"모든 ust 파일을 로드했습니다. [ust 파일 수: {len(usts)}] [총 노트 수: {ust_global_note_count}] [총 길이: {round(ust_global_notes_length_sum, 3)}s]")
    logger.info(
        L(
            "모든 ust 파일을 로드했습니다. [ust 파일 수: {usts_len}] [총 노트 수: {global_notes_len} (무음 제외: {global_notes_voiced_len})] [총 길이: {global_notes_length_sum}s (무음 제외: {global_notes_voiced_length_sum}s)]",
            usts_len=len(usts),
            global_notes_len=line_num_formatter(global_notes_len),
            global_notes_voiced_len=line_num_formatter(global_notes_voiced_len),
            global_notes_length_sum=round(global_notes_length_sum, 3),
            global_notes_voiced_length_sum=round(global_notes_voiced_length_sum, 3),
        )
    )
    db_info.cache["usts"] = usts

    return error_flag


@__preprocess
def ust_error_check(db_info: DB_Info, logger: logging.Logger):
    # 이미 로딩 과정에서 검사가 이루어지므로, 이 함수는 더미 함수임.
    logger.info(L("검사 완료."))


@__preprocess
def pitch_note_count(db_info: DB_Info, logger: logging.Logger):
    config_group = db_info.config.group
    is_show_graph = db_info.config.options["graph_show"]
    is_save_graph = db_info.config.options["graph_save"]
    usts: Dict[str, up.ust.Ust] = db_info.cache["usts"]

    pitch_note_count_dict = {}
    for note_pitch in range(12, 128):  # 12 ~ 127 까지 미리 초기화
        pitch_note_count_dict[note_pitch] = 0

    for file, ust in (usts_tqdm := tqdm(usts.items(), leave=False)):
        usts_tqdm.set_description(f"[{file}] Calculating...")

        for note in ust.notes:
            if note.lyric not in config_group.silence:
                pitch_note_count_dict[note.notenum] += 1

    if is_show_graph or is_save_graph:
        logger.info(L("그래프 출력 중..."))
        graph_path = db_info.config.output.graph
        graph_show_dpi = db_info.config.options["graph_show_dpi"]

        utils.matplotlib_init(db_info.config.options["graph_darkmode"])
        from matplotlib import pyplot as plt

        #####
        # * # 피치 및 노트 개수 통계 그래프
        #####
        plot_name = "pitch_and_note_count_stats"
        plt.figure(utils.get_plot_num(plot_name), figsize=(16, 8), dpi=graph_show_dpi)

        plt_pitch_note_count_dict = {}
        for k, v in pitch_note_count_dict.items():
            if v > 0:
                plt_pitch_note_count_dict[k] = v
        keys, values = list(plt_pitch_note_count_dict.keys()), list(plt_pitch_note_count_dict.values())
        plt_x_tick_labels = []
        for x in keys:
            plt_x_tick_labels.append(f"{notenum_as_abc(x)}\n({x})")

        b1 = plt.bar(keys, values, width=0.7)
        plt.bar_label(b1)

        plt.xticks(keys, plt_x_tick_labels)

        plt.title(L("Pitch and Note Count Statistics"))
        plt.xlabel(L("Pitch"))
        plt.ylabel(L("Note Count"))
        plt.tight_layout()

        if is_save_graph:
            plt.savefig(os.path.join(graph_path, f"{plot_name}.jpg"), dpi=200)
        if is_show_graph:
            plt.show(block=False)

    db_info.stats["pitch_note_count"] = pitch_note_count_dict
    return pitch_note_count_dict


@__preprocess
def pitch_note_length(db_info: DB_Info, logger: logging.Logger):
    config_group = db_info.config.group
    is_show_graph = db_info.config.options["graph_show"]
    is_save_graph = db_info.config.options["graph_save"]
    usts: Dict[str, up.ust.Ust] = db_info.cache["usts"]

    pitch_note_length_dict = {}
    for note_pitch in range(12, 128):  # 12 ~ 127 까지 미리 초기화
        pitch_note_length_dict[note_pitch] = 0

    for file, ust in (usts_tqdm := tqdm(usts.items(), leave=False)):
        usts_tqdm.set_description(f"[{file}] Calculating...")

        for note in ust.notes:
            if note.lyric not in config_group.silence:
                pitch_note_length_dict[note.notenum] += note.length_ms / 1000

    if is_show_graph or is_save_graph:
        logger.info(L("그래프 출력 중..."))
        graph_path = db_info.config.output.graph
        graph_show_dpi = db_info.config.options["graph_show_dpi"]

        utils.matplotlib_init(db_info.config.options["graph_darkmode"])
        from matplotlib import pyplot as plt
        import matplotlib.ticker as mticker

        #####
        # * # 피치 및 노트 길이 통계 그래프
        #####
        plot_name = "pitch_and_note_length_stats"
        plt.figure(utils.get_plot_num(plot_name), figsize=(16, 8), dpi=graph_show_dpi)

        plt_pitch_note_length_dict = {}
        for k, v in pitch_note_length_dict.items():
            if v > 0:
                plt_pitch_note_length_dict[k] = v
        keys, values = list(plt_pitch_note_length_dict.keys()), list(plt_pitch_note_length_dict.values())
        plt_x_tick_labels = []
        for x in keys:
            plt_x_tick_labels.append(f"{notenum_as_abc(x)}\n({x})")

        b1 = plt.bar(keys, values, width=0.7)
        plt.bar_label(b1, fmt="%.1fs")

        plt.xticks(keys, plt_x_tick_labels)

        plt.gca().yaxis.set_major_formatter(mticker.FormatStrFormatter("%.2fs"))

        plt.title(L("Pitch and Note Length Statistics"))
        plt.xlabel(L("Pitch"))
        plt.ylabel(L("Note Length"))
        plt.tight_layout()

        if is_save_graph:
            plt.savefig(os.path.join(graph_path, f"{plot_name}.jpg"), dpi=200)
        if is_show_graph:
            plt.show(block=False)

    db_info.stats["pitch_note_length"] = pitch_note_length_dict
    return pitch_note_length_dict
