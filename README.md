# enunu-kor-tool

> :pushpin: 이 저장소는 [NNSVS 한국어 지원 프로젝트](https://github.com/Kor-SVS/nnsvs-korean-support)의 일부분입니다.

이 저장소에서는 ENUNU 모델 제작에 도움이 되는 스크립트 및 도구가 제공됩니다.

## 설치방법

```
python -m pip install git+https://github.com/Kor-SVS/enunu-kor-tool.git
```

## 🛠️ 도구

-   ### analysis4vb

    > 명령줄 `analysis4vb` 사용가능

    -   데이터 베이스 통계를 출력하는 기능

-   ### g2pk4utau

    > 명령줄 `g2pk4utau` 사용가능

    -   한국어 자소 -> 음소 변환 기능을 제공하는 Utau 용 g2p 모듈 (g2pk와 mecab을 사용하여 영어 및 숫자도 변환 가능)
    -   한글 자모에 대응되는 알파벳 음소 사전 및 변환 기능 (해당 사전은 국어 표준 표기법과 다를 수 있음)

-   ### ustx2ust

    -   ustx 포멧 파일을 ust 포멧 파일로 변환합니다. (필요 정보만 변환됨.)

-   ### check4lab

    -   데이터 셋을 검사합니다. (자동 폴더 감시 구조)

-   ### lab2ust_fixer

    -   lab 파일을 기반으로 ust/ustx 파일을 보정합니다.

-   ### cut2sil

    -   lab을 기반으로 wav의 무음부(sil)를 제거합니다.

-   ### utaupyk

    -   ENUNU에 사용되는 [utaupy](https://github.com/oatsu-gh/utaupy) 라이브러리의 부분 개조 코드들의 집합
    -   ustx(OpenUTAU 포멧) -> ust 변환 기능 (필요한 정보만 변환됨)
    -   g2pk4utau를 사용한 가사 -> 음소 변환 기능 (한국어 발음은 앞/뒤 자음 및 모음에 영향을 받기 때문에 필요)

-   ### ustx2lab

    > 명령줄 `ustx2lab` 사용가능

    -   USTX 및 UST 파일로 라벨 파일(lab)을 생성하는 기능
    -   정확도는 낮지만, 음소가 비슷한 위치에 자동으로 배치되어 있으므로 타이밍만 정렬하면 됨
    -   USTX, UST 파일과 타이밍이 자동으로 맞아짐
    -   lab2ntlab 및 ustx2lab 모듈의 --no-time 옵션으로 (ust, ustx) <-> (lab) 오류 점검 가능

-   ### lab2ntlab

    > 명령줄 `lab2ntlab` 사용가능

    -   lab 파일의 음소만 남기고, 시간 표시를 모두 제거하는 기능

-   ### ustx2lab

    > 명령줄 `ustx2lab` 사용가능

    -   USTX 및 UST 파일로 라벨 파일(lab)을 생성하는 기능
    -   정확도는 낮지만, 음소가 비슷한 위치에 자동으로 배치되어 있으므로 타이밍만 정렬하면 됨
    -   USTX, UST 파일과 타이밍이 자동으로 맞아짐
    -   lab2ntlab 및 ustx2lab 모듈의 --no-time 옵션으로 (ust, ustx) <-> (lab) 오류 점검 가능
