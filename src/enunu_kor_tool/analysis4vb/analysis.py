from copy import deepcopy
import os
import shutil
from glob import glob

from tqdm import tqdm

from enunu_kor_tool import utils, log, lang
from enunu_kor_tool.analysis4vb.model.config import DB_Config
from enunu_kor_tool.utaupyk._ustx2ust import Ustx2Ust_Converter
from enunu_kor_tool.analysis4vb.runner import analysis_runner
from enunu_kor_tool.analysis4vb.model import DB_Info, DB_Files
from enunu_kor_tool.analysis4vb import config as config_module

L = lang.get_global_lang()


def cli_ui_main():
    import cli_ui

    global L

    print(L("> 설명: 해당 모듈은 ENUNU 데이터 베이스 통계를 볼 수 있습니다."))
    print(L("* TIP: 파일이나 폴더의 경로를 입력할 때, 드래그 & 드롭으로 쉽게 입력할 수 있습니다."))

    args = {}

    args["input"] = cli_ui.ask_string(L("DB 폴더의 경로를 입력하세요."))

    main(args)


def main(args=None):
    if not isinstance(args, dict):
        import argparse

        parser = argparse.ArgumentParser(description=L("ENUNU 데이터 셋의 통계를 생성합니다."))

        parser.add_argument("-i", dest="input", required=True, help=L("데이터 셋의 경로"))

        args = vars(parser.parse_args())

    args["input"] = args["input"].rstrip("\\")

    assert os.path.isdir(args["input"]), L("입력한 경로에서 DB를 찾을 수 없습니다.")

    output_path = os.path.join(args["input"], "analysis")
    log.DIR_PATH = os.path.join(output_path, "logs")
    config_path = os.path.join(output_path, "analysis_config.yaml")

    def get_root_module_logger():
        loglevel = options.get("log_level", "info") if (options := config.get("options")) != None else "info"
        return log.get_logger("analysis4vb", loglevel)

    if not os.path.isfile(config_path):
        config = deepcopy(config_module.DEFAULT_CONFIG)

        config_module.save_default_config2yaml(config_path)

        logger = get_root_module_logger()
        logger.warning(L("Config 파일이 존재하지 않습니다. (DB 내부에 기본 Config 파일을 생성합니다)\nPath=[{config_path}]", config_path=config_path))

        input(L("Config 파일을 DB에 알맞게 수정 후, 엔터를 눌러주세요."))
        config = utils.load_yaml(config_path)
    else:
        config = utils.load_yaml(config_path)
        logger = get_root_module_logger()
        logger.debug(L("성공적으로 Config를 읽었습니다."))

    db_path = args["input"]
    db_config = DB_Config(db_path, config)
    db_name = os.path.basename(db_path)

    db_raw_ustx_files = glob(os.path.join(db_path, "**", "*.ustx"), recursive=True)

    if len(db_raw_ustx_files) > 0:
        logger.info(L("ustx -> ust 변환 중..."))
        os.makedirs(db_config.output.temp, exist_ok=True)
        for ustx_path in (db_raw_ustx_files_tqdm := tqdm(db_raw_ustx_files)):
            db_raw_ustx_files_tqdm.set_description(f"ustx -> ust Converting... [{os.path.relpath(ustx_path)}]")
            if (ustx_path_split := os.path.splitext(ustx_path))[1] == ".ustx":
                converter = Ustx2Ust_Converter(ustx_path, encoding="utf-8")
                converter.save_ust(os.path.join(db_config.output.temp, os.path.basename(ustx_path_split[0]) + ".ust"))

    db_files = DB_Files(
        db_raw_ustx_files,
        glob(os.path.join(db_path, "**", "*.ust"), recursive=True),
        glob(os.path.join(db_path, "**", "*.lab"), recursive=True),
        glob(os.path.join(db_path, "**", "*.wav"), recursive=True),
    )

    ustx_file_count = len(db_files.ustx)
    ust_file_count = len(db_files.ust) - ustx_file_count
    lab_file_count = len(db_files.lab)
    wav_file_count = len(db_files.wav)

    if not (ustx_file_count == ust_file_count == lab_file_count == wav_file_count):
        logger.warning(
            L(
                "데이터의 개수가 일치하지 않습니다.\nustx=[{ustx_file_count} 개]\nust=[{ust_file_count} 개]\nlab=[{lab_file_count} 개]\nwav=[{wav_file_count} 개]",
                ustx_file_count=ustx_file_count,
                ust_file_count=ust_file_count,
                lab_file_count=lab_file_count,
                wav_file_count=wav_file_count,
            )
        )

    db_info = DB_Info(db_path, db_name, db_files, db_config)

    analysis_runner(db_info)

    logger.info("Done.")

    if db_info.config.options["graph_show"]:
        from matplotlib import pyplot

        pyplot.show()

    if os.path.exists(db_info.config.output.temp):
        shutil.rmtree(db_info.config.output.temp)

    del config

    logger.info("Cleaned up.")


if __name__ == "__main__":
    main()
