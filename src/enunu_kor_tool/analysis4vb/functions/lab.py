import logging
import os
from typing import Dict

from tqdm import tqdm

from enunu_kor_tool import log, utils
from enunu_kor_tool.analysis4vb.model import DB_Info


def __preprocess(func):
    def preprocess_wrapper(db_info: DB_Info, logger: logging.Logger):
        if "labs" not in db_info.cache:
            lab_loader_logger = log.get_logger("lab_loader", db_info.config.options["log_level"])
            is_exist_error = __lab_loader(db_info, lab_loader_logger)
            if is_exist_error:
                lab_loader_logger.warning("lab 파일을 로드하는 중 오류가 발견되었습니다. 이후 작업에 영향을 끼칠 수 있습니다.")

        return func(db_info, logger)

    return preprocess_wrapper


def __lab_loader(db_info: DB_Info, logger: logging.Logger) -> bool:
    """
    lab 파일을 로드 및 검사합니다.

    cache.labs에 lab 파일들을 로드하여 저장합니다.

    Returns:
        bool: 오류의 존재 여부
    """

    phonemes_files = db_info.files.lab
    encoding = db_info.config.options.get("encoding", "utf-8")
    line_num_formatter = lambda ln: str(ln).rjust(4)

    error_flag = False
    labs = {}
    lab_global_line_count = 0
    lab_global_error_line_count = 0
    for file in (file_tqdm := tqdm(phonemes_files, leave=False)):
        file_tqdm.set_description(f"Processing... [{file}]")
        logger.info(f"[{file}] 파일 로드 중...")

        lab = []

        logger.debug(f"파싱 작업 중...")
        error_line_count = 0
        with open(file, "r", encoding=encoding) as f:
            for idx, line in enumerate(f.readlines(), 1):
                line_pieces = list(filter(lambda p: p not in ["\n", ""] and not p.isspace(), line.split(" ")))
                if len(line_pieces) <= 2:
                    p_line = line.replace("\n", "\\n")
                    logger.warning(f'[Line {line_num_formatter(idx)}] 파싱할 수 없는 라인을 건너뛰었습니다. [Content: "{p_line}"]')
                    error_line_count += 1
                    continue
                start, end, *phn = line_pieces
                phn = " ".join(phn).rstrip("\n")
                lab.append((int(start), int(end), phn))
        length = lab[-1][1]
        lab_len = len(lab)
        lab_global_line_count += lab_len
        logger.info(f"lab 파일을 로드했습니다. [총 라인 수: {line_num_formatter(lab_len)}] [길이: {round(length / 10000000, 1)}s ({length} 100ns)] [오류 라인 수: {error_line_count}]")

        # TODO: 자음이 혼자 있을 경우 검출
        # TODO: 1 Frame 보다 짧은 음소 검출
        logger.debug(f"오류 검사 중...")
        global_length = 0
        for idx, (start, end, phn) in enumerate(lab, 1):
            if phn not in db_info.config.phonemes.all:
                logger.warning(f"[Line {line_num_formatter(idx)}] [{phn}] Config에 명시되지 않은 음소가 사용되었습니다.")
                error_line_count += 1
            if start >= end:
                logger.warning(f"[Line {line_num_formatter(idx)}] 종료시점이 시작지점보다 빠릅니다.")
                error_line_count += 1
            if global_length != start:
                logger.warning(f"[Line {line_num_formatter(idx)}] 시작시점이 이전 종료지점과 다릅니다.")
                error_line_count += 1

            global_length = end

        if error_line_count > 0:
            logger.warning(f"총 [{line_num_formatter(error_line_count)}] 개의 오류가 발견되었습니다.")
            error_flag = True
            lab_global_error_line_count += error_line_count

        labs[file] = lab
    logger.info(f"모든 lab 파일을 로드했습니다. [lab 파일 수: {len(labs)}] [총 라인 수: {lab_global_line_count}] [오류 라인 수: {lab_global_error_line_count}]")
    db_info.cache["labs"] = labs

    return error_flag


@__preprocess
def lab_error_check(db_info: DB_Info, logger: logging.Logger):
    # 이미 로딩 과정에서 검사가 이루어지므로, 이 함수는 더미 함수임.
    logger.info("검사 완료.")
    pass


@__preprocess
def phoneme_count(db_info: DB_Info, logger: logging.Logger):
    phonemes_config = db_info.config.phonemes
    is_show_graph = db_info.config.options["graph_show"]
    is_save_graph = db_info.config.options["graph_save"]
    labs: Dict = db_info.cache["labs"]

    group_phoneme_count_dict = {}
    single_phoneme_count_dict = {}
    phoneme_count_dict = {
        "group": group_phoneme_count_dict,
        "single": single_phoneme_count_dict,
    }

    def add_one(dic: Dict, name: str):
        if name not in dic:
            dic[name] = 1
        else:
            dic[name] += 1

    for file, lab in (labs_tqdm := tqdm(labs.items(), leave=False)):
        labs_tqdm.set_description(f"[{file}] Counting...")

        for start, end, phn in lab:
            add_one(single_phoneme_count_dict, phn)

            if phn in phonemes_config.consonant:
                add_one(group_phoneme_count_dict, "consonant")
            elif phn in phonemes_config.vowel:
                add_one(group_phoneme_count_dict, "vowel")
            elif phn in phonemes_config.silence:
                add_one(group_phoneme_count_dict, "silence")
            elif phn in phonemes_config.other:
                add_one(group_phoneme_count_dict, "other")
            else:
                add_one(group_phoneme_count_dict, "error")

    if is_show_graph or is_save_graph:
        logger.debug("그래프 출력 중...")
        graph_path = db_info.config.output.graph

        utils.matplotlib_init()
        from matplotlib import pyplot as plt

        plot_name = "phoneme_count_single"
        plt.figure(utils.get_plot_num(plot_name), figsize=(16, 6), dpi=100)

        single_phoneme_count_sorted_dict = dict(sorted(single_phoneme_count_dict.items(), key=lambda item: item[1], reverse=True))
        keys, values = list(single_phoneme_count_sorted_dict.keys()), list(single_phoneme_count_sorted_dict.values())
        b1 = plt.bar(keys, values, width=0.7)
        plt.bar_label(b1)

        plt.title("Phones Count Statistics (음소 개수 통계)")
        plt.xlabel("Phoneme (음소)")
        plt.ylabel("Count (개수)")
        plt.tight_layout()

        if is_save_graph:
            plt.savefig(os.path.join(graph_path, f"{plot_name}.jpg"), dpi=200)
        if is_show_graph:
            plt.show(block=False)

        plot_name = "phoneme_count_group"
        plt.figure(utils.get_plot_num(plot_name), dpi=100)

        keys, values = list(group_phoneme_count_dict.keys()), list(group_phoneme_count_dict.values())
        b1 = plt.bar(keys, values, width=0.7)
        plt.bar_label(b1)

        plt.title("Phones Count Statistics by Group (그룹별 음소 개수 통계)")
        plt.xlabel("Phoneme Group (음소 그룹)")
        plt.ylabel("Count (개수)")
        plt.tight_layout()

        if is_save_graph:
            plt.savefig(os.path.join(graph_path, f"{plot_name}.jpg"), dpi=200)
        if is_show_graph:
            plt.show(block=False)

    db_info.stats["phoneme_count"] = phoneme_count_dict
    return phoneme_count_dict
