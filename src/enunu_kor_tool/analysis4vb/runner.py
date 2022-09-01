import time
from pprint import pformat

from tqdm import tqdm

from enunu_kor_tool import log
from enunu_kor_tool.analysis4vb.model import DB_Info

from enunu_kor_tool.analysis4vb.functions import FUNC_LIST


def analysis_runner(db_info: DB_Info):
    log_level = db_info.config.options["log_level"]
    logger = log.get_logger("analysis_runner", log_level)

    check_funcs = []
    funcs = []
    for f in db_info.config.funcs:
        f = f.lower()
        if f.endswith("check"):
            check_funcs.append(f)
        else:
            funcs.append(f)
    funcs = check_funcs + funcs

    for func_name in (func_tqdm := tqdm(funcs, leave=False)):
        func_info = FUNC_LIST.get(func_name)
        if func_info == None:
            logger.error("찾을 수 없는 기능을 건너뛰었습니다.")
            continue

        func_tqdm.set_description(f"Processing... [\033[1;33m{func_name}\033[0m]")

        module = __import__(func_info["module"], fromlist=[func_info["module"]])
        func = getattr(module, func_info["func"])

        start = time.time()
        result = func(db_info, log.get_logger(func_name, log_level))
        db_info.stats[func_name] = result

        if logger.isEnabledFor(log.LOG_LEVEL_DICT["debug"]):
            log_str = f"[{func_name}] Running time: {time.time() - start}"
            if result != None:
                if isinstance(result, str):
                    if "\n" in result:
                        log_str += f"\nResult: {result}"
                    else:
                        log_str += f", Result: {result}"
                else:
                    log_str += f"\nResult: {pformat(result)}"
            logger.debug(log_str)
