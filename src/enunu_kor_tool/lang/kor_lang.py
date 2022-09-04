# fmt: off
KOR_DICT = {
    "analysis4vb (ENUNU 통계)": "",
    "g2pk4utau (한국어 자소 -> 음소 변환기)": "",
    "ustx2lab (ustx, ust -> lab 변환기)": "",
    "lab2ntlab (lab 시간 표시 제거)": "",
    "check4lab (ustx, ust <-> lab 일치 여부 검사 모듈) (beta.)": "",

    "> 설명: 해당 모듈은 ENUNU 데이터 베이스 통계를 볼 수 있습니다.": "",
    "ENUNU 데이터 셋의 통계를 생성합니다.": "",
    
    "* TIP: 파일이나 폴더의 경로를 입력할 때, 드래그 & 드롭으로 쉽게 입력할 수 있습니다.": "",
    
    "데이터 셋의 경로": "",
    "g2pk4utau 사용 여부": "",
    "사용할 모듈을 선택하세요.": "",
    "DB 폴더의 경로를 입력하세요.": "",
    "table 파일 경로를 입력하세요.": "",
    "ustx, ust <-> lab 일치 여부 검사 모듈": "",
    "종료는 [Ctrl + C]를 눌러주세요.": "",
    
    "[{selected_lang}] 언어가 설정되었습니다.": "",
    "{path}에 파일이 존재하지 않습니다.": "",
    "변경사항이 감지되었습니다. Path={path}": "",
    "{filename}.lab 파일을 찾을 수 없습니다.": "",
    "{filename}.ustx 또는 {filename}.ust 파일을 찾을 수 없습니다.": "",
    (
        "라벨 파일에 오류가 있습니다.\n"
        "DB 라벨 파일: LineNum=[{line}], Start=[{align_start}], End=[{align_end}], Phoneme=[{align_phn}]\n"
        "UST(X)에서 생성된 라벨 파일: Start=[{score_start}], End=[{score_end}], Phoneme=[{score_phn}]"
    ): "",
    "라벨 파일에 시작 시간이 종료 시간 보다 느린 음소가 있습니다.\nLineNum=[{line}], Start=[{align_start}], End=[{align_end}], Phoneme=[{align_phn}]": "",
    "DB의 라벨 파일과 악보에서 생성한 라벨 파일의 길이가 다릅니다. filename=[{filename}]": "",
    "라벨 파일을 점검하는 도중 파싱 오류가 발생했습니다. LineNum=[{line}]": "",
    "라벨 파일에 불필요한 문자가 포함된 표현이 있습니다. LineNum=[{line}]": "",
    "라벨 파일에서 오류를 발견하지 못했습니다.": "",
    "DB 감시를 시작했습니다.": "",
    "입력한 경로에서 DB를 찾을 수 없습니다.": "",
    "Config 파일이 존재하지 않습니다. (DB 내부에 기본 Config 파일을 생성합니다)\nPath=[{config_path}]": "",
    "Config 파일을 DB에 알맞게 수정 후, 엔터를 눌러주세요.": "",
    "성공적으로 Config를 읽었습니다.": "",
    "데이터의 개수가 일치하지 않습니다.\nustx=[{ustx_file_count} 개]\nust=[{ust_file_count} 개]\nlab=[{lab_file_count} 개]\nwav=[{wav_file_count} 개]": "",
    "ustx -> ust 변환 중...": "",
    
    "lab 파일을 로드하는 중 오류가 발견되었습니다. 이후 작업에 영향을 끼칠 수 있습니다.": "",
    "[{filepath}] 파일 로드 중...": "",
    "파싱 작업 중...": "",
    '[Line {line_num}] 파싱할 수 없는 라인을 건너뛰었습니다. [Content: "{p_line}"]': "",
    "[Line {line_num}] [{phn}] Config에 명시되지 않은 음소가 사용되었습니다.": "",
    "[Line {line_num}] 종료 시점이 시작 지점보다 빠릅니다.": "",
    "[Line {line_num}] 시작 시점이 이전 종료 지점과 다릅니다.": "",
    "총 [{line_num}] 개의 오류가 발견되었습니다.\n({file})": "",
    "lab 파일을 로드했습니다. [총 라인 수: {line_num}] [길이: {round_length}s ({length} 100ns)] [오류 라인 수: {error_line_count}]": "",
    "모든 lab 파일을 로드했습니다. [lab 파일 수: {labs_len}] [총 라인 수: {lab_global_line_count}] [오류 라인 수: {lab_global_error_line_count}]": "",
    "검사 완료.": "",
    "그래프 출력 중...": "",
    "Phonemes Count Statistics (음소 개수 통계)": "",
    "Phoneme (음소)": "",
    "Count (개수)": "",
    "Phonemes Count Statistics by Group (그룹별 음소 개수 통계)": "",
    "Phoneme Group (음소 그룹)": "",
    "Phonemes Length Statistics (음소 길이 통계)": "",
    "Length (길이)": "",
    "Phonemes Length Statistics by Group (그룹별 음소 길이 통계)": "",
    "Phonemes Length Statistics (음소 길이 통계) [Box plot]": "",

    "ust 파일을 로드하는 중 오류가 발견되었습니다. 이후 작업에 영향을 끼칠 수 있습니다.": "",
    "ust 파일을 로드했습니다. [총 노트 수: {notes_len} (무음 제외: {notes_voiced_len})] [총 길이: {round_notes_length_sum}s (무음 제외: {round_notes_voiced_length_sum}s)]": "",
    "모든 ust 파일을 로드했습니다. [ust 파일 수: {usts_len}] [총 노트 수: {global_notes_len} (무음 제외: {global_notes_voiced_len})] [총 길이: {global_notes_length_sum}s (무음 제외: {global_notes_voiced_length_sum}s)]": "",
    "Pitch and Note Count Statistics (피치 및 노트 개수 통계)": "",
    "Pitch (피치)": "",
    "Note Count (노트 개수)": "",
    "Pitch and Note Length Statistics (피치 및 노트 길이 통계)": "",
    "Note Length (노트 길이)": "",
}
# fmt: on