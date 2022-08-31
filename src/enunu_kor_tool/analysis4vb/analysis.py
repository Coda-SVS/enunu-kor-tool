import os
import shutil
from glob import glob

from enunu_kor_tool import utils, log
from enunu_kor_tool.analysis4vb.model.config import DB_Config
from enunu_kor_tool.utaupyk._ustx2ust import Ustx2Ust_Converter
from enunu_kor_tool.analysis4vb.runner import analysis_runner
from enunu_kor_tool.analysis4vb.model import DB_Info, DB_Files
from enunu_kor_tool.analysis4vb.config import DEFAULT_CONFIG, DEFAULT_YAML_CONFIG


def cli_ui_main():
    import cli_ui

    print("* TIP: 파일이나 폴더의 경로를 입력할 때, 드래그 & 드롭으로 쉽게 입력할 수 있습니다.")

    args = {}

    args["config"] = cli_ui.ask_string("Config 파일의 경로를 입력해주세요 (생략 가능): ")
    args["input"] = cli_ui.ask_string("DB 경로를 입력해주세요 (폴더만 가능): ")

    main(args)


def main(args=None):
    if not isinstance(args, dict):
        import argparse

        parser = argparse.ArgumentParser(description="ENUNU 데이터 셋의 통계를 생성합니다.")

        parser.add_argument("-p", dest="config", help="Config 파일 경로")
        parser.add_argument("-i", dest="input", required=True, help="데이터 셋의 경로")
        # parser.add_argument("-o", dest="output", required=True, help="출력 디렉토리 경로")

        args = vars(parser.parse_args())

    args["input"] = args["input"].rstrip("\\")

    assert os.path.isdir(args["input"]), "입력한 경로에서 DB를 찾을 수 없습니다."

    log.DIR_PATH = os.path.join(args["input"], "logs")

    def get_root_module_logger():
        loglevel = options.get("log_level", "info") if (options := config.get("options")) != None else "info"
        return log.get_logger("analysis4vb", loglevel)

    if not isinstance(args.get("config"), str) or not os.path.isfile(args["config"]):
        args["config"] = os.path.join(args["input"], "analysis_config.yaml")

        if os.path.isfile(args["config"]):
            config = utils.load_yaml(args["config"])
            logger = get_root_module_logger()

            logger.debug("DB 내부의 Config를 읽었습니다.")
        else:
            config = DEFAULT_CONFIG

            with open(args["config"], "w", encoding="utf-8") as f:
                f.write(DEFAULT_YAML_CONFIG)

            logger = get_root_module_logger()
            logger.warning(f"Config 파일이 존재하지 않습니다. Path=[{args['config']}]\n[{args['input']}] 내부에 기본값 Config 파일을 생성합니다.")
    else:
        config = utils.load_yaml(args["config"])
        logger = get_root_module_logger()
        logger.debug("성공적으로 Config를 읽었습니다.")

    db_path = args["input"]
    db_config = DB_Config(db_path, config)
    db_name = os.path.basename(db_path)

    db_raw_ustx_files = glob(os.path.join(db_path, "**", "*.ustx"), recursive=True)

    if len(db_raw_ustx_files) > 0:
        os.makedirs(db_config.output.temp, exist_ok=True)
        for ustx_path in db_raw_ustx_files:
            if (ustx_path_split := os.path.splitext(ustx_path))[1] == ".ustx":
                converter = Ustx2Ust_Converter(ustx_path, encoding="utf-8")
                converter.save_ust(os.path.join(db_config.output.temp, os.path.basename(ustx_path_split[0]) + ".ust"))

    db_files = DB_Files(
        db_raw_ustx_files,
        glob(os.path.join(db_path, "**", "*.ust"), recursive=True),
        glob(os.path.join(db_path, "**", "*.lab"), recursive=True),
        glob(os.path.join(db_path, "**", "*.wav"), recursive=True),
    )

    if not (len(db_files.ustx) == len(db_files.ust) == len(db_files.lab) == len(db_files.wav)):
        logger.warning(f"데이터의 개수가 일치하지 않습니다.\nustx=[{len(db_files.ustx)} 개]\nust=[{len(db_files.ust)} 개]\nlab=[{len(db_files.lab)} 개]\nwav=[{len(db_files.wav)} 개]")

    db_info = DB_Info(db_path, db_name, db_files, db_config)

    analysis_runner(db_info)

    logger.info("Done.")

    if db_info.config.options["graph_show"]:
        from matplotlib import pyplot

        pyplot.show()

    if os.path.exists(db_info.config.output.temp):
        shutil.rmtree(db_info.config.output.temp)

    logger.info("Cleaned up.")


if __name__ == "__main__":
    main()
