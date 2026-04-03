# stem-voice-clone

한국어 | **[English](README.md)**

**멀티스템 보컬 음성 클로닝 도구**
모든 보컬 스템 트랙에 원하는 목소리를 입힐 수 있습니다 — 모든 레이어가 보존됩니다.

> 단일 오디오 파일로도 동작하지만, **멀티스템 트랙에서 진가를 발휘합니다** — 메인 보컬, 코러스, 애드리브 등 모든 레이어를 보존합니다.

---

## 문제점

기존 AI 음성 변환 도구들은 **보컬 트랙 하나만** 변환합니다. 하지만 전문적으로 제작된 노래에는 여러 보컬 레이어가 있습니다:

- **메인 보컬** — 리드 싱잉
- **백킹 보컬 (BGV)** — 코러스, 화음, "우~", "아~" 같은 배경 목소리
- **애드리브** — 즉흥 보컬, 꾸밈 프레이즈
- **보컬 이펙트** — 가공되거나 레이어된 보컬 텍스처

믹스된 곡에서 보컬을 분리(예: Demucs)하고 그 하나의 트랙만 변환하면, **이 모든 레이어가 하나로 뭉쳐집니다**. 결과는 얇고, 밋밋하고, 원곡의 프로덕션 퀄리티를 잃게 됩니다.

## 해결책

**stem-voice-clone**은 다른 접근을 취합니다: 원본 보컬 스템이 있다면 **각 스템을 개별적으로 변환**한 후 다시 조합합니다. 모든 보컬 레이어가 보존됩니다.

| | 단일 트랙 (기존 도구들) | 멀티스템 (stem-voice-clone) |
|---|---|---|
| 입력 | 오디오 파일 1개 | 보컬 스템 폴더 |
| 처리 | 분리 → 1트랙 변환 | 각 스템 개별 변환 |
| 보컬 레이어 | 하나로 합쳐짐 | 각각 보존 |
| 코러스/화음 | 손실 또는 열화 | 완전 보존 |
| 애드리브 | 섞여서 구분 어려움 | 개별 변환 |
| 결과 품질 | 얇고 밋밋함 | **풍성, 프로덕션 퀄리티** |

스템이 없어도 괜찮습니다 — **Single 모드**가 [Demucs](https://github.com/facebookresearch/demucs)로 보컬을 자동 분리하고 변환합니다. 다만 멀티레이어 효과는 없습니다.

---

## 데모

모든 데모 오디오는 [Suno](https://suno.com/)로 생성되었습니다 — 저작권 문제 없음.

**[Before/After 비교 청취하기](https://daewooki.github.io/stem-voice-clone/)**

| 원본 곡 | 타겟 목소리 | 변환 결과 |
|:---:|:---:|:---:|
| [재생](docs/audio/original.mp4) | [재생](docs/audio/target.mp4) | [재생](docs/audio/converted.mp4) |
| 팝 발라드, 남성 보컬 | 소프트 발라드, 여성 보컬 | 같은 곡, 새로운 목소리 |

> 각 보컬 스템(메인 + 백킹 보컬)이 **개별적으로 변환**되었습니다 — 이것이 풍성한 레이어 사운드를 유지하는 핵심입니다.

---

## 빠른 시작

### 요구사항

- **Python 3.10+**
- **NVIDIA GPU** (6GB+ VRAM)
- **CUDA** (11.8 이상)

### 설치

```bash
git clone --recursive https://github.com/Daewooki/stem-voice-clone.git
cd stem-voice-clone

# Windows
install.bat

# Linux/Mac
chmod +x install.sh && ./install.sh
```

설치 스크립트가 자동으로:
1. Python 가상환경 생성
2. PyTorch + CUDA 설치
3. 모든 의존성 설치
4. YingMusic-SVC 모델 체크포인트 다운로드 (~700MB, 첫 실행 시 자동)

### 사용법

**대화형 모드** — 실행하면 입력을 안내합니다:
```bash
python convert.py
```
```
  stem-voice-clone v0.1.0
  Multi-stem singing voice cloning toolkit

  [1/3] Input path (stems folder or audio file): ./my_stems/
  [2/3] Reference voice file: ./singer.mp3
  [3/3] Output folder (Enter for ./output):

  Mode: STEM
  Vocal tracks: 13
  Instrumental: inst.wav

  Converting 13 tracks...

  [1/13] Vocal Main 1.wav -> done
  [2/13] Vocal Main 2.wav -> done
  ...

  Clean tracks: output/clean/
  Done!
```

**명령어 모드:**
```bash
# 멀티스템 모드 (추천)
python convert.py ./my_stems/ --ref singer.mp3 --output ./result/

# 싱글 파일 모드 (Demucs로 자동 보컬 분리)
python convert.py song.mp3 --ref singer.mp3

# 개별 트랙만 출력 (자동 믹스 건너뛰기)
python convert.py ./stems/ --ref singer.mp3 --no-mix
```

**포함된 데모로 테스트:**
```bash
python convert.py ./examples/demo_stems/ --ref ./examples/reference_voice.wav
```

---

## 작동 원리

### 아키텍처

```
                         ┌─────────────────────────────────┐
                         │     YingMusic-SVC (Zero-shot)    │
                         │                                   │
                         │  Whisper ──> 콘텐츠 (가사/멜로디)  │
                         │  RMVPE ───> F0 (음높이)           │
                         │  CAMPPlus ─> 스타일 (음색)         │
                         │         ↓                         │
                         │  DiT + Flow Matching ──> 출력     │
                         └─────────────────────────────────┘
```

### 스템 모드 (추천)

각 보컬 스템을 독립적으로 변환한 후, 원본 반주와 재조합합니다:

```
보컬 스템 1  ──> SVC ──> 무음 마스크 ──> Clean 트랙 1 ─┐
보컬 스템 2  ──> SVC ──> 무음 마스크 ──> Clean 트랙 2  ├──> 믹스
...                                                    │
보컬 스템 N  ──> SVC ──> 무음 마스크 ──> Clean 트랙 N ──┤
반주          ─────────────────────────────────────────┘
```

### 싱글 모드

스템이 없을 때, 도구가 자동으로 보컬을 분리합니다:

```
오디오 파일 ──> Demucs ──> 보컬    ──> SVC ──> 변환된 보컬 ─┐
                       └── 반주 ──────────────────────────┘──> 믹스
```

---

## 핵심 기술

### 무음 마스크 (Silence Masking)

SVC 모델은 무음 구간에서 소리를 "환각(hallucinate)"하는 경향이 있습니다 — 원본이 완전히 조용한 곳에서 희미한 소리를 생성합니다. 원본 스템에서 마스크를 만들어 변환 결과에 적용하여 해결합니다. 무음은 무음 그대로 유지됩니다.

### 트랙별 볼륨 매칭

각 변환 트랙의 볼륨(RMS)을 원본 트랙에 맞춥니다. 원본 믹스의 보컬 밸런스가 변환 후에도 유지됩니다.

### 자동 레퍼런스 추출

참조 음성은 어떤 길이든 제공할 수 있습니다. 도구가 자동으로 가장 에너지가 높은 25초 구간을 찾습니다 — YingMusic-SVC의 최적 입력 길이입니다.

### 모델 1회 로드

SVC 모델을 한 번만 로드하고 모든 스템을 순차 처리합니다. 15개 이상의 스템 트랙이 있어도 모델을 다시 로드하지 않습니다.

---

## 입력

### 폴더 구조

스캐너가 폴더 구조를 자동 감지합니다:

**하위 폴더 사용 (추천):**
```
my_stems/
├── Main/
│   ├── vocal_main_1.wav
│   ├── vocal_main_2.wav
│   └── vocal_adlib.wav
├── BGV/
│   ├── vocal_bgv_1.wav
│   └── vocal_bgv_2.wav
└── instrumental.wav
```

**플랫 구조 (이것도 가능):**
```
my_stems/
├── vocal_verse.wav
├── vocal_chorus.wav
├── bgv_harmony.wav
└── instrumental.wav
```

### 자동 분류 규칙

| 분류 | 키워드 / 규칙 |
|---|---|
| **보컬** (변환됨) | `Main/`, `BGV/`, `Vocal/` 폴더 안의 파일, 또는 파일명에 `vocal`, `voice`, `main`, `bgv`, `chorus`, `harmony`, `backing`, `adlib`, `lead` 포함 |
| **반주** (그대로 유지) | 파일명에 `instrumental`, `inst`, `karaoke`, `bgm`, `mr` 포함 |

### 참조 목소리

- 아무 오디오 형식 가능 (WAV, MP3, FLAC 등)
- **노래하는** 목소리 15~25초가 가장 좋음
- 파일이 더 길어도 자동으로 최적 구간을 추출
- **팁:** 원본과 비슷한 장르/에너지의 참조 목소리를 사용하면 결과가 훨씬 자연스럽습니다

---

## 출력

```
output/
├── clean/              # 개별 변환 트랙 (DAW에서 활용 가능)
│   ├── vocal_main_1.wav
│   ├── vocal_main_2.wav
│   ├── vocal_bgv_1.wav
│   └── ...
├── mix_final.wav       # 자동 믹스 결과 (모든 트랙 + 반주)
└── _raw/               # SVC 원본 출력 (무음 마스크 적용 전)
```

**팁:** 최상의 결과를 위해서는 `clean/` 폴더의 트랙들과 원본 반주를 [Audacity](https://www.audacityteam.org/) 또는 DAW에서 직접 로드하여 수동으로 믹싱하는 것을 추천합니다. 자동 믹스는 편리하지만, 수동 믹싱이 더 세밀한 제어를 제공합니다.

---

## 스템을 어디서 구하나요?

| 출처 | 설명 |
|---|---|
| **DAW 프로젝트** | FL Studio, Logic Pro, Ableton 등에서 스템 내보내기 |
| **AI 음악 생성기** | [Suno](https://suno.com/), [Udio](https://udio.com/)에서 스템 내보내기 지원 |
| **리믹스 팩** | 많은 아티스트가 리믹스 콘테스트용으로 공식 스템 공개 |
| **크리에이티브 커먼즈** | [Cambridge-MT](https://www.cambridge-mt.com/ms/mtk/), [MUSDB18](https://sigsep.github.io/datasets/musdb.html) |
| **스템이 아예 없다면?** | Single 모드를 사용하세요 — 아무 오디오 파일이나 가능합니다 |

---

## 성능

NVIDIA RTX 3070 (8GB VRAM) 기준:

| 단계 | 시간 |
|---|---|
| 모델 로딩 | ~30초 (첫 실행 시만) |
| 트랙당 변환 (100 diffusion steps) | ~45초 |
| 무음 마스크 + 볼륨 매칭 | ~5초/트랙 |
| 17트랙 곡 (예: 메인 5개 + BGV 12개) | ~15분 전체 |

---

## 사용 기술

- **[YingMusic-SVC](https://github.com/GiantAILab/YingMusic-SVC)** — 최신 Zero-shot 보컬 음성 변환 SOTA ([논문](https://arxiv.org/abs/2512.04793))
- **[Demucs](https://github.com/facebookresearch/demucs)** — Meta의 음악 소스 분리 도구
- **[PyTorch](https://pytorch.org/)** — 딥러닝 프레임워크

---

## 기여

기여를 환영합니다! 이슈나 풀 리퀘스트를 자유롭게 열어주세요.

## 라이선스

[MIT](LICENSE)
