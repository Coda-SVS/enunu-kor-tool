import os
import re
import pickle
import sys
import tempfile
from copy import deepcopy
from collections import deque

from jamo import h2j, j2hcj
from tqdm import tqdm

from enunu_kor_tool import utils
from enunu_kor_tool.g2pk4utau.hangul_dic import get_phn_dictionary, replace2pre_phn, replace2phn, Special_Character_Filter_joined
from enunu_kor_tool.g2pk4utau.enum_set import VerboseMode, CacheMode

g2p = None
is_loaded_tqdm = "tqdm" in (set(globals().keys()) & set(sys.modules.keys()))


def print_h(msg: str):
    global is_loaded_tqdm

    if is_loaded_tqdm:
        tqdm.write(msg)
    else:
        print(msg)


def is_in_special_character(text):
    char_count = len(list(filter(lambda t: t != "", re.findall("[" + Special_Character_Filter_joined + "]", text))))
    return char_count > 0


def is_only_special_character(text):
    error_count = len(list(filter(lambda t: t != "", re.findall("((?![" + Special_Character_Filter_joined + "]).)*", text))))
    return error_count == 0


def is_in_hangul(text):
    char_count = len(list(filter(lambda t: t != "", re.findall("[\u3130-\u318F\uAC00-\uD7A3]", text))))
    return char_count > 0


def is_only_hangul(text):
    error_count = len(list(filter(lambda t: t != "", re.findall("((?![\u3130-\u318F\uAC00-\uD7A3]).)*", text))))
    return error_count == 0


class g2pk4utau(object):
    @staticmethod
    def get_instance(cache_mode: CacheMode = CacheMode.FILE):
        global g2p

        if g2p == None:
            g2p = g2pk4utau(cache_mode)

        return g2p

    def __init__(self, cache_mode: CacheMode = CacheMode.FILE):
        global g2p

        if g2p != None and cache_mode == CacheMode.FILE:
            print_h("WARNING: Multiple instances have been created. Concurrent reference errors in cache files may occur.")

        self.g2p = None
        self.empty_str_remover = lambda text: not text.isspace()
        self.dictionary = get_phn_dictionary(False)
        self.dictionary_label_mode = get_phn_dictionary(True)

        assert isinstance(cache_mode, CacheMode), f"Invalid type of 'cache_mode'. [{cache_mode}]"

        self.cache_mode = cache_mode
        if cache_mode == CacheMode.FILE:
            cache_filepath = os.path.join(tempfile.gettempdir(), "g2pk4utau_cache.pkl")
            if os.path.isfile(cache_filepath):
                print_h(f"> Cache Size: {utils.convert_size(os.path.getsize(cache_filepath))}")
                try:
                    with open(cache_filepath, "rb") as f:
                        cache = pickle.load(f)
                except Exception as ex:
                    print_h(f"> Failed to load cache file. [Ex={ex}]")
                    cache = {}
            else:
                cache = {}
        elif cache_mode == CacheMode.MEMORY:
            cache = {}
            cache_filepath = None
        else:
            cache = None
            cache_filepath = None

        self.cache_path = cache_filepath
        self.cache = cache

    def __call__(
        self,
        text: str,
        use_g2pK: bool = True,
        descriptive: bool = False,
        group_vowels: bool = False,
        labeling_mode: bool = True,
        verbose: VerboseMode = VerboseMode.NONE,
    ):
        if self.cache_mode != CacheMode.NONE and text in self.cache:
            if verbose.is_flag(VerboseMode.PARAMETER) or verbose.is_flag(VerboseMode.INPUT):
                print_h("> Use Cache Dict")

            result = deepcopy(self.cache[text])

            if verbose.is_flag(VerboseMode.OUTPUT):
                txt, phn_list, token_phn_list, word_phn_list = result

                print_h("\033[1;96m[Output]\033[0m")
                print_h(f"> 0 Source Text: {txt}")
                word_phn_temp_list = []
                for tokens in word_phn_list:
                    word_phn_temp_list.append("\033[1;32m,\033[0m ".join(tokens))
                temp_output = "\033[1;32m,\033[0m ".join(phn_list)
                print_h(f"> 1 Phoneme List: {temp_output}")
                temp_output = "\033[1;32m,\033[0m ".join(token_phn_list)
                print_h(f"> 2 Character Phoneme List: {temp_output}")
                temp_output = "\033[1;33m(\033[0m" + "\033[1;33m) (\033[0m".join(word_phn_temp_list) + "\033[1;33m)\033[0m"
                print_h(f"> 3 Word Phoneme List: {temp_output}")

            return result

        if not use_g2pK:
            print_h("The g2pk option is disabled. Conversion results may contain many errors.")

        if verbose.is_flag(VerboseMode.PARAMETER):
            print_h("\033[1;96m[Parameter]\033[0m")
            print_h(f"> use_g2pK = {use_g2pK}")
            print_h(f"> descriptive = {descriptive}")
            print_h(f"> group_vowels = {group_vowels}")
            print_h(f"> labeling_mode = {labeling_mode}")

        # 여러 줄의 입력 처리
        text_list = text.splitlines()

        if verbose.is_flag(VerboseMode.PREPHN):
            print_h("\033[1;96m[Pre-Phonemes Processing]\033[0m")

        # 앞뒤공백 제거, 특수문자 제거
        for idx in range(len(text_list)):
            text_list[idx] = text_list[idx].strip()

            # 공백을 구분자로 사용하므로, 불필요한 2개 이상의 공백을 제거 (단어는 공백 3개, 문자는 공백 2개로 구분)
            text_list[idx] = re.sub(r"\s{2,}|\t", r" ", text_list[idx])

            txt, pre_phns = replace2pre_phn(text_list[idx], verbose=verbose)

            text_list[idx] = (txt, pre_phns)

        # 비어있는 문자열 제거
        text_list = list(filter(lambda t: not t[0].isspace(), text_list))

        # 전처리 후 입력 문자열이 없을 경우
        if len(text_list) == 0:
            return "", [], [], []

        phn_list = []
        token_phn_list = []
        word_phn_list = []

        for idx in range(len(text_list)):
            txt, pre_phns = text_list[idx]
            pre_phns = deque(pre_phns)

            if verbose.is_flag(VerboseMode.INPUT):
                print_h("\033[1;96m[Input]\033[0m")
                print_h(txt)

            # g2pk로 전처리
            if use_g2pK:
                if self.g2p == None:
                    import g2pk

                    self.g2p = g2pk.G2p()

                if verbose.is_flag(VerboseMode.G2PK):
                    print_h("\033[1;96m[g2pk Processing]\033[0m")

                txt = self.g2p(txt, descriptive=descriptive, group_vowels=group_vowels, verbose=verbose.is_flag(VerboseMode.G2PK))

            # 자모 분리
            jamo_text = j2hcj(h2j(" ".join(txt)))

            # 사전을 바탕으로 로마자 음소로 변환
            phn_text = replace2phn(self.dictionary_label_mode if labeling_mode else self.dictionary, jamo_text, verbose=verbose)

            # 단어 단위 묶음
            cursor_idx = 0
            inner_word_phn_list = list(filter(self.empty_str_remover, phn_text.split("   ")))
            for word_idx, phn_word in enumerate(inner_word_phn_list):
                phn_tokens = list(filter(self.empty_str_remover, [phn_tokens.strip() for phn_tokens in phn_word.split("  ")]))

                # pre_phns 삽입
                idx = 0
                idx_offset = 0
                currnet_token_len = len(phn_tokens)
                while True:
                    if len(pre_phns) == 0 or pre_phns[0][1] != word_idx:
                        break

                    if pre_phns[0][0] - cursor_idx + idx_offset == idx:
                        _, _, pre_phn = pre_phns.popleft()

                        if currnet_token_len + idx_offset == idx:
                            phn_tokens.append(pre_phn)
                        else:
                            phn_tokens.insert(idx, pre_phn)

                        idx_offset += 1

                    idx += 1

                cursor_idx += currnet_token_len + 1

                word_phn_list.append(phn_tokens)

            # 글자 단위 묶음
            for phn_word in word_phn_list:
                token_phn_list.extend(phn_word)

            # 음소 단위 묶음
            for token_phn in token_phn_list:
                for phn in token_phn.split(" "):
                    phn_list.append(phn)

            if verbose.is_flag(VerboseMode.OUTPUT):
                print_h("\033[1;96m[Output]\033[0m")
                print_h(f"> 0 G2P Processed: {txt}")
                word_phn_temp_list = []
                for tokens in word_phn_list:
                    word_phn_temp_list.append("\033[1;32m,\033[0m ".join(tokens))
                temp_output = "\033[1;32m,\033[0m ".join(phn_list)
                print_h(f"> 1 Phoneme List: {temp_output}")
                temp_output = "\033[1;32m,\033[0m ".join(token_phn_list)
                print_h(f"> 2 Character Phoneme List: {temp_output}")
                temp_output = "\033[1;33m(\033[0m" + "\033[1;33m) (\033[0m".join(word_phn_temp_list) + "\033[1;33m)\033[0m"
                print_h(f"> 3 Word Phoneme List: {temp_output}")

        result = ("\n".join([t[0] for t in text_list]), phn_list, token_phn_list, word_phn_list)

        if self.cache != None:
            self.cache[text] = deepcopy(result)

            if self.cache_mode == CacheMode.FILE:
                try:
                    with open(self.cache_path, "wb") as f:
                        pickle.dump(self.cache, f)
                except Exception as ex:
                    print_h(f"Error saving cache file. [Ex={ex}]")

        return result


def cli_ui_main():
    print("> 설명: 해당 모듈은 한국어 자소를 음소로 변환합니다.")
    print("* [Ctrl + C]로 종료할 수 있습니다.")

    main()


def main():
    g2p = g2pk4utau.get_instance()

    try:
        while True:
            g2p(input("변환할 문장을 입력하세요: "), verbose=VerboseMode.ALL)
    except KeyboardInterrupt:
        print("\nDone.")


if __name__ == "__main__":
    main()
