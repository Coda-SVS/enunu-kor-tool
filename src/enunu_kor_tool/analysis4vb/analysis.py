from glob import glob
import os
import shutil

from enunu_kor_tool import utils, log
from enunu_kor_tool.utaupyk._ustx2ust import Ustx2Ust_Converter
from enunu_kor_tool.analysis4vb.runner import analysis_runner
from enunu_kor_tool.analysis4vb.model import DB_Info, DB_Files
from enunu_kor_tool.analysis4vb.config import DEFAULT_CONFIG, DEFAULT_YAML_CONFIG


def main():
    import argparse

    parser = argparse.ArgumentParser(description="ENUNU 데이터 셋의 통계를 생성합니다.")

    parser.add_argument("-p", dest="config", help="Config 파일 경로")
    parser.add_argument("-i", dest="input", required=True, help="데이터 셋의 경로")
    # parser.add_argument("-o", dest="output", required=True, help="출력 디렉토리 경로")

    args = vars(parser.parse_args())

    args["input"] = args["input"].rstrip("\\")

    log.DIR_PATH = os.path.join(args["input"], "logs")

    logger = log.get_logger("analysis4vb")

    if not isinstance(args.get("config"), str) or not os.path.isfile(args["config"]):
        args["config"] = os.path.join(args["input"], "analysis_config.yaml")

        if os.path.isfile(args["config"]):
            config = utils.load_yaml(args["config"])
        else:
            config = DEFAULT_CONFIG
            logger.warning(f"Config 파일이 존재하지 않습니다. Path=[{args['config']}]\n[{args['input']}] 내부에 Config 파일을 생성합니다.")

            with open(args["config"], "w", encoding="utf-8") as f:
                f.write(DEFAULT_YAML_CONFIG)
    else:
        config = utils.load_yaml(args["config"])

    db_path = args["input"]
    db_temp_path = os.path.join(db_path, "temp")
    db_name = os.path.basename(db_path)

    db_raw_ustx_files = glob(os.path.join(db_path, "**", "*.ustx"), recursive=True)

    if len(db_raw_ustx_files) > 0:
        os.makedirs(db_temp_path, exist_ok=True)
        for ustx_path in db_raw_ustx_files:
            if (ustx_path_split := os.path.splitext(ustx_path))[1] == ".ustx":
                converter = Ustx2Ust_Converter(ustx_path, encoding="utf-8")
                converter.save_ust(os.path.join(db_temp_path, os.path.basename(ustx_path_split[0]) + ".ust"))

    db_files = DB_Files(
        db_raw_ustx_files,
        glob(os.path.join(db_path, "**", "*.ust"), recursive=True),
        glob(os.path.join(db_path, "**", "*.lab"), recursive=True),
        glob(os.path.join(db_path, "**", "*.wav"), recursive=True),
    )

    if not (len(db_files.ustx) == len(db_files.ust) == len(db_files.lab) == len(db_files.wav)):
        logger.warning(f"데이터의 개수가 일치하지 않습니다.\nustx=[{len(db_files.ustx)} 개]\nust=[{len(db_files.ust)} 개]\nlab=[{len(db_files.lab)} 개]\nwav=[{len(db_files.wav)} 개]")

    db_info = DB_Info(db_path, db_name, db_temp_path, db_files, config)

    analysis_runner(db_info, logger)

    # logger.info(db_info)

    logger.info("Done.")

    if os.path.exists(db_temp_path):
        shutil.rmtree(db_temp_path)

    logger.info("Cleaned up.")


if __name__ == "__main__":
    main()
