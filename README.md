# enunu-kor-tool

> :pushpin: 이 저장소는 [NNSVS 한국어 지원 프로젝트](https://github.com/Kor-SVS/nnsvs-korean-support)의 일부분입니다.

이 저장소에서는 한국어 ENUNU 모델의 학습 및 추론(음성 합성)에 도움이 되는 스크립트 및 도구가 제공됩니다.

## 🛠️ 도구

-   ### g2pk4utau

    -   한국어 자소 -> 음소 변환 기능을 제공하는 Utau 용 g2p 모듈 (g2pk와 mecab을 사용하여 영어 및 숫자도 변환 가능)
    -   한글 자모에 대응되는 알파벳 음소 사전 및 변환 기능 (해당 사전은 국어 표준 표기법과 다를 수 있음)

-   ### utaupyk

    -   ENUNU에 사용되는 [utaupy](https://github.com/oatsu-gh/utaupy) 라이브러리의 부분 개조 코드들의 집합
    -   ustx(OpenUTAU 포멧) -> ust 변환 기능 (필요한 정보만 변환됨)
    -   g2pk4utau를 사용한 가사 -> 음소 변환 기능 (한국어 발음은 앞/뒤 자음 및 모음에 영향을 받기 때문에 필요)
