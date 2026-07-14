---
name: factory-doctor
description: Shorts_Factory 공장의 환경·의존성·설정을 진단하고 고친다. 파이썬 패키지(moviepy, edge-tts, anthropic, PIL, requests, numpy), ffmpeg, 폰트, 출력 폴더, API 키 노출 여부를 점검한다. "에러 나요", "환경 점검", "왜 안 돼", "설치 확인", "공장 점검" 요청에 사용.
---

# 공장 정밀 진단 스킬 (factory-doctor)

Shorts_Factory가 안 돌아갈 때 원인을 찾아 고친다. 아래를 순서대로 점검한다.

## 0. 인터프리터 (가장 먼저!)
이 PC엔 파이썬이 둘 있다. 기본 `python`=3.14(**패키지 없음**), 실사용은 **3.13**(`py -3.13`).
공장 명령은 전부 `py -3.13`으로 실행한다.
```powershell
py -0p   # 설치된 파이썬 목록 확인 (3.13 경로 확인)
```

## 1. 파이썬 의존성
필수 패키지: `anthropic`, `moviepy`, `edge-tts`, `pillow`(PIL), `requests`, `numpy`.
```powershell
py -3.13 -c "import anthropic, moviepy, edge_tts, PIL, requests, numpy; print('py-deps OK')"
```
없으면(반드시 3.13에 설치):
```powershell
py -3.13 -m pip install anthropic moviepy edge-tts pillow requests numpy
```

## 2. ffmpeg (moviepy 인코딩 필수)
```powershell
(Get-Command ffmpeg -ErrorAction SilentlyContinue) | Select-Object -ExpandProperty Source
```
없으면 안내: `winget install Gyan.FFmpeg` 또는 imageio-ffmpeg 사용
(`pip install imageio-ffmpeg`). moviepy는 imageio-ffmpeg를 자동 사용할 수 있다.

## 3. 폰트 & 자산 폴더
- `assets/fonts/font.ttf` **필수** (없으면 `build_video_with_subtitles`가 즉시 False 반환).
- `assets/backgrounds/` 존재. (bg1~3.jpg는 매 생산마다 새로 생성됨)
- `assets/bgm.mp3` 는 선택(있으면 자동 BGM 믹싱).
- 출력 폴더는 `main.py`의 `initialize_factory()`가 자동 생성하므로,
  독립 실행 시엔 `outputs/scripts`, `outputs/audios`, `outputs/videos` 존재를 확인.

## 4. API 키 점검 — 🚨 보안 최우선
현재 키가 **소스에 평문으로 하드코딩**되어 있다:
- `src/claude_engine.py` → `CLAUDE_API_KEY = "sk-ant-..."`
- `src/llm_module.py` → `OPENAI_API_KEY = "sk-proj-..."`

**권고(순서대로):**
1. 노출된 두 키를 각 콘솔에서 **즉시 폐기(rotate)** 하고 새 키 발급.
2. 새 키는 코드가 아니라 **환경변수**로 이관:
   `os.environ["ANTHROPIC_API_KEY"]`, `os.environ["OPENAI_API_KEY"]` 를 읽도록 수정.
3. `.gitignore`에 키가 담긴 파일/`.env`를 추가(이 프로젝트는 아직 git repo 아님 —
   git 초기화 시점에 반드시 선반영).
- 이 변경을 사용자가 원하면 실제 코드 수정까지 진행한다.

## 5. 모델 ID 점검
`src/claude_engine.py`의 `model="claude-sonnet-4-6"` 값이 유효한 현행 모델 ID인지
확인한다. 인증/모델 오류가 나면 사용 가능한 최신 Claude 모델 ID로 교체를 제안한다.
(정확한 현행 ID가 불확실하면 claude-api 스킬/공식 문서를 참조.)

## 6. 스모크 테스트
비용 0원 테스트 모드로 라인 전체가 도는지 확인:
```powershell
py -3.13 -c "import sys; sys.path.insert(0,'.'); from src.llm_module import generate_shorts_source; from src.video_module import build_video_with_subtitles; d=generate_shorts_source('테스트', True); print('build:', build_video_with_subtitles(d, '_doctor_test.mp4'))"
```
성공 후 `outputs/videos/_doctor_test.mp4` 생성 확인 → 정리 원하면 삭제.

## 보고
점검 결과를 항목별 ✅/❌로 요약하고, ❌는 위 수정 명령과 함께 제시한다.
