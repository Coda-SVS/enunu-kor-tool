from enunu_kor_tool.utaupyk._ustx2ust import ustx2ust


def cli_ui_main():
    import cli_ui

    print("> 설명: 해당 모듈은 USTX 파일을 UST 파일로 변환합니다. (학습에 필요한 정보만 변환됨)")
    print("* TIP: 파일이나 폴더의 경로를 입력할 때, 드래그 & 드롭으로 쉽게 입력할 수 있습니다.")

    args = {}

    args["input"] = cli_ui.ask_string("단일 Ust 또는 Ustx 파일, 또는 해당 파일이 모여있는 폴더 경로를 입력하세요.")
    args["output"] = cli_ui.ask_string("출력 폴더 경로를 입력하세요.")
    args["flag"] = cli_ui.ask_string("Flag 정보를 입력하세요.")

    main(args)


def main(args=None):
    if not isinstance(args, dict):
        import argparse

        parser = argparse.ArgumentParser(description="USTX 파일을 UST 파일로 변환합니다. (학습에 필요한 정보만 변환됨)")

        parser.add_argument("-i", dest="input", required=True, help="단일 Ust 또는 Ustx 파일, 또는 해당 파일이 모여있는 폴더 경로")
        parser.add_argument("-o", dest="output", required=True, help="출력 폴더 경로")
        parser.add_argument("--flag", dest="flag", default="", help="Flag 정보")

        args = vars(parser.parse_args())

    ustx2ust(args["input"], args["output"], args["flag"])

    print("done.")


if __name__ == "__main__":
    main()
