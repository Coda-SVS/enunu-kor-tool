from pprint import pformat
import time
import logging

from tqdm import tqdm

from enunu_kor_tool.analysis4vb.model import DB_Info

FUNC_LIST = {
}


def analysis_runner(db_info: DB_Info, logger: logging.Logger):
    for func_name in (func_tqdm := tqdm(db_info.config.funcs, leave=False)):
        func_tqdm.set_description(f"Processing... [\033[1;33m{func_name}\033[0m]")

        start = time.time()
        func = FUNC_LIST.get(func)
        if func == None:
            logger.error("찾을 수 없는 기능을 건너뛰었습니다.")
            continue

        result = func(db_info, logger)

        log_str = f"[{func_name}] Running time: {time.time() - start}"
        if result != None:
            if isinstance(result, str):
                if "\n" in result:
                    log_str += f"\nResult: {result}"
                else:
                    log_str += f", Result: {result}"
            else:
                log_str += f"\nResult: {pformat(result)}"
        logger.info(log_str)
