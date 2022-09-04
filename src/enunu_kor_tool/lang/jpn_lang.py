from copy import deepcopy
from .kor_lang import KOR_DICT

JPN_DICT = deepcopy(KOR_DICT)

# fmt: off
JPN_DICT.update(
    {
    "analysis4vb (ENUNU 통계)": "analysis4vb (ENUNU 統計)",
    "g2pk4utau (한국어 자소 -> 음소 변환기)": "g2pk4utau (韓国語文字 -> 音素変換器)",
    "ustx2lab (ustx, ust -> lab 변환기)": "ustx2lab (ustx, ust -> lab 変換器)",
    "lab2ntlab (lab 시간 표시 제거)": "lab2ntlab (lab 時刻表示除去)",
    "check4lab (ustx, ust <-> lab 일치 여부 검사 모듈) (beta.)": "check4lab (ustx, ust <-> lab 一致有無検査モジュール) (beta.)",
    
    "> 설명: 해당 모듈은 ENUNU 데이터 베이스 통계를 볼 수 있습니다.": "> 説明:該当モジュールはENUNUデータベース統計を見ることができます。",
    "ENUNU 데이터 셋의 통계를 생성합니다.": "ENUNUデータセットの統計を作成します。",
    
    "* TIP: 파일이나 폴더의 경로를 입력할 때, 드래그 & 드롭으로 쉽게 입력할 수 있습니다.": "* TIP:ファイルやフォルダの経路を入力するとき、ドラッグ&ドロップで簡単に入力できます。",
    
    "데이터 셋의 경로": "データセットの経路",
    "g2pk4utau 사용 여부": "g2pk4utau 使用有無",
    "사용할 모듈을 선택하세요.": "使用するモジュールを選択してください。",
    "DB 폴더의 경로를 입력하세요.": "DBフォルダの経路を入力してください。",
    "table 파일 경로를 입력하세요.": "tableファイル経路を入力してください。",
    "ustx, ust <-> lab 일치 여부 검사 모듈": "ustx, ust <-> lab 一致有無検査モジュール",
    "종료는 [Ctrl + C]를 눌러주세요.": "終了は、[Ctrl + C]を押してください。",
    
    "[{selected_lang}] 언어가 설정되었습니다.": "[{selected_lang}] 言語が設定されました。",
    "{path}에 파일이 존재하지 않습니다.": "{path}にファイルが存在しません。",
    "변경사항이 감지되었습니다. Path={path}": "変更事項が感知されました。 Path={path}",
    "{filename}.lab 파일을 찾을 수 없습니다.": "{filename}.lab ファイルが見つかりません。",
    "{filename}.ustx 또는 {filename}.ust 파일을 찾을 수 없습니다.": "{filename}.ustx または {filename}.ust ファイルが見つかりません。",
    (
        "라벨 파일에 오류가 있습니다.\n"
        "DB 라벨 파일: LineNum=[{line}], Start=[{align_start}], End=[{align_end}], Phoneme=[{align_phn}]\n"
        "UST(X)에서 생성된 라벨 파일: Start=[{score_start}], End=[{score_end}], Phoneme=[{score_phn}]"
    ): (
        "ラベルファイルにエラーがあります。\n"
        "DBラベルファイル: LineNum=[{line}], Start=[{align_start}], End=[{align_end}], Phoneme=[{align_phn}]\n"
        "UST(X)で生成されたラベルファイル: Start=[{score_start}], End=[{score_end}], Phoneme=[{score_phn}]"
    ),
    "라벨 파일에 시작 시간이 종료 시간 보다 느린 음소가 있습니다.\nLineNum=[{line}], Start=[{align_start}], End=[{align_end}], Phoneme=[{align_phn}]": "ラベルファイルに開始時間が終了時間より遅い音素があります。\nLineNum=[{line}], Start=[{align_start}], End=[{align_end}], Phoneme=[{align_phn}]",
    "DB의 라벨 파일과 악보에서 생성한 라벨 파일의 길이가 다릅니다. filename=[{filename}]": "DBのラベルファイルと楽譜で生成したラベルファイルの長さが異なります。 filename=[{filename}]",
    "라벨 파일을 점검하는 도중 파싱 오류가 발생했습니다. LineNum=[{line}]": "ラベルファイルを点検中にパッシングエラーが発生しました。 LineNum=[{line}]",
    "라벨 파일에 불필요한 문자가 포함된 표현이 있습니다. LineNum=[{line}]": "ラベルファイルに不要な文字が含まれた表現があります。 LineNum=[{line}]",
    "라벨 파일에서 오류를 발견하지 못했습니다.": "ラベルファイルでエラーが発見できませんでした。",
    "DB 감시를 시작했습니다.": "DB監視を開始しました。",
    "입력한 경로에서 DB를 찾을 수 없습니다.": "入力した経路でDBが見つかりません。",
    "Config 파일이 존재하지 않습니다. (DB 내부에 기본 Config 파일을 생성합니다)\nPath=[{config_path}]": "Configファイルが存在しません。 (DB内部に基本Configファイルを生成します)\nPath=[{config_path}]",
    "Config 파일을 DB에 알맞게 수정 후, 엔터를 눌러주세요.": "ConfigファイルをDBに合わせて修正後、Enterを押してください。",
    "성공적으로 Config를 읽었습니다.": "成功的にConfigファイルを読みました。",
    "데이터의 개수가 일치하지 않습니다.\nustx=[{ustx_file_count} 개]\nust=[{ust_file_count} 개]\nlab=[{lab_file_count} 개]\nwav=[{wav_file_count} 개]": "データの個数が一致しません。\nustx=[{ustx_file_count} 個]\nust=[{ust_file_count} 個]\nlab=[{lab_file_count} 個]\nwav=[{wav_file_count} 個]",
    "ustx -> ust 변환 중...": "ustx -> ust 変換中...",
    
    "lab 파일을 로드하는 중 오류가 발견되었습니다. 이후 작업에 영향을 끼칠 수 있습니다.": "labファイルをロード中にエラーが発見されました。 今後の作業に影響を及ぼす可能性があります。",
    "[{filepath}] 파일 로드 중...": "[{filepath}] ファイルロード中...",
    "파싱 작업 중...": "パーシング作業中...",
    '[Line {line_num}] 파싱할 수 없는 라인을 건너뛰었습니다. [Content: "{p_line}"]': '[Line {line_num}] パーシングできないラインをスキップしました。 [Content: "{p_line}"]',
    "[Line {line_num}] [{phn}] Config에 명시되지 않은 음소가 사용되었습니다.": "[Line {line_num}] [{phn}] Configに明示されていない音素が使用されました。",
    "[Line {line_num}] 종료 시점이 시작 지점보다 빠릅니다.": "[Line {line_num}] 終了時点が開始地点より早いです。",
    "[Line {line_num}] 시작 시점이 이전 종료 지점과 다릅니다.": "[Line {line_num}] 開始時点が以前の終了地点と異なります。",
    "총 [{line_num}] 개의 오류가 발견되었습니다.\n({file})": "合計 [{line_num}] 個のエラーが発見されました。\n({file})",
    "lab 파일을 로드했습니다. [총 라인 수: {line_num}] [길이: {round_length}s ({length} 100ns)] [오류 라인 수: {error_line_count}]": "labファイルをロードしました。 [総ライン数: {line_num}] [長さ: {round_length}s ({length} 100ns)] [エラーライン数: {error_line_count}]",
    "모든 lab 파일을 로드했습니다. [lab 파일 수: {labs_len}] [총 라인 수: {lab_global_line_count}] [오류 라인 수: {lab_global_error_line_count}]": "すべてのlabファイルをロードしました。 [labファイル数: {labs_len}] [総ライン数: {lab_global_line_count}] [エラーライン数: {lab_global_error_line_count}]",
    "검사 완료.": "検査完了。",
    "그래프 출력 중...": "グラフ出力中...",
    "Phonemes Count Statistics (음소 개수 통계)": "Phonemes Count Statistics (音素数統計)",
    "Phoneme (음소)": "Phoneme (音素)",
    "Count (개수)": "Count (個数)",
    "Phonemes Count Statistics by Group (그룹별 음소 개수 통계)": "Phonemes Count Statistics by Group (グループ別音素個数統計)",
    "Phoneme Group (음소 그룹)": "Phoneme Group (音素グループ)",
    "Phonemes Length Statistics (음소 길이 통계)": "Phonemes Length Statistics (音素長さ統計)",
    "Length (길이)": "Length (長さ)",
    "Phonemes Length Statistics by Group (그룹별 음소 길이 통계)": "Phonemes Length Statistics by Group (グループ別音素長さ統計)",
    "Phonemes Length Statistics (음소 길이 통계) [Box plot]": "Phonemes Length Statistics (音素長さ統計) [Box plot]",

    "ust 파일을 로드하는 중 오류가 발견되었습니다. 이후 작업에 영향을 끼칠 수 있습니다.": "ustファイルをロード中にエラーが発見されました。 今後の作業に影響を及ぼす可能性があります。",
    "ust 파일을 로드했습니다. [총 노트 수: {notes_len} (무음 제외: {notes_voiced_len})] [총 길이: {round_notes_length_sum}s (무음 제외: {round_notes_voiced_length_sum}s)]": "ustファイルをロードしました。 [総ノート数: {notes_len} (無音除外: {notes_voiced_len})] [総長さ: {round_notes_length_sum}s (無音除外: {round_notes_voiced_length_sum}s)]",
    "모든 ust 파일을 로드했습니다. [ust 파일 수: {usts_len}] [총 노트 수: {global_notes_len} (무음 제외: {global_notes_voiced_len})] [총 길이: {global_notes_length_sum}s (무음 제외: {global_notes_voiced_length_sum}s)]": "すべてのustファイルをロードしました。 [ustファイル数: {usts_len}] [総ノート数: {global_notes_len} (無音除外: {global_notes_voiced_len})] [総長さ: {global_notes_length_sum}s (無音除外: {global_notes_voiced_length_sum}s)]",
    "Pitch and Note Count Statistics (피치 및 노트 개수 통계)": "Pitch and Note Count Statistics (ピッチおよびノート数統計)",
    "Pitch (피치)": "Pitch (ピッチ)",
    "Note Count (노트 개수)": "Note Count (ノート数)",
    "Pitch and Note Length Statistics (피치 및 노트 길이 통계)": "Pitch and Note Length Statistics (ピッチおよびノート長さ統計)",
    "Note Length (노트 길이)": "Note Length (ノート長さ)",
    }
)
# fmt: on
