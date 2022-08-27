import logging

from tqdm import tqdm

from enunu_kor_tool import log
from enunu_kor_tool.analysis4vb.model import DB_Info


def __preprocess(func):
    def preprocess_wrapper(db_info: DB_Info, logger: logging.Logger):
        if "labs" not in db_info.cache:
            __lab_loader(db_info, log.get_logger("lab_loader", db_info.config.options["log_level"]))
        return func(db_info, logger)

    return preprocess_wrapper


def __lab_loader(db_info: DB_Info, logger: logging.Logger):
    """
    lab 파일을 로드 및 검사합니다.
    cache.labs 에 lab 파일들을 로드하여 저장합니다.
    """

    phonemes_files = db_info.files.lab
    encoding = db_info.config.options.get("encoding", "utf-8")
    line_no_formatter = lambda ln: str(ln).rjust(4)

    lab_list = []
    lab_global_line_count = 0
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
                    logger.warning(f'[Line {line_no_formatter(idx)}] 파싱할 수 없는 라인을 건너뛰었습니다. [Content: "{p_line}"]')
                    error_line_count += 1
                    continue
                start, end, *phn = line_pieces
                phn = " ".join(phn).rstrip("\n")
                lab.append((int(start), int(end), phn))
        length = lab[-1][1]
        lab_len = len(lab)
        lab_global_line_count += lab_len
        logger.info(f"lab 파일을 로드했습니다. [총 라인 수: {line_no_formatter(lab_len)}] [길이: {round(length / 10000000, 1)}s ({length} 100ns)] [오류 라인 수: {error_line_count}]")

        logger.debug(f"오류 검사 중...")
        global_length = 0
        for idx, (start, end, phn) in enumerate(lab, 1):
            if phn not in db_info.config.phonemes.all:
                logger.warning(f"[Line {line_no_formatter(idx)}] [{phn}] Config에 명시되지 않은 음소가 사용되었습니다.")
            if start >= end:
                logger.warning(f"[Line {line_no_formatter(idx)}] 종료시점이 시작지점보다 빠릅니다.")
            if global_length != start:
                logger.warning(f"[Line {line_no_formatter(idx)}] 시작시점이 이전 종료지점과 다릅니다.")

            global_length = end

        lab_list.append(lab)
    logger.info(f"모든 lab 파일을 로드했습니다. [lab 파일 수: {len(lab_list)}] [총 라인 수: {lab_global_line_count}]")
    db_info.cache["labs"] = lab_list
