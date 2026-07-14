# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

프로젝트별 상세 규칙(Commands / Directory Structure / Conventions / Guidelines)은 [AGENTS.md](AGENTS.md)에도
동일하게 유지된다. 여기서는 큰 그림 위주로 설명한다.

## Interpreter (필수)

이 PC엔 파이썬이 둘 있다. 기본 `python`은 **3.14이며 의존성이 하나도 없다** — 실행하면 실패한다.
모든 명령은 **`py -3.13`** 으로 돌린다.

- 실행: `py -3.13 main.py`
- 의존성 설치: `py -3.13 -m pip install anthropic moviepy edge-tts pillow requests numpy`
- 비용 0원 스모크 테스트:
  `py -3.13 -c "import sys; sys.path.insert(0,'.'); from src.llm_module import generate_shorts_source; from src.video_module import build_video_with_subtitles; d=generate_shorts_source('테스트', True); print('build:', build_video_with_subtitles(d, '_smoke.mp4'))"`

외부 의존: `edge-tts`(TTS 실행파일)와 `ffmpeg`(moviepy 인코딩). 자막용 `assets/fonts/font.ttf`가 없으면
영상 빌드가 즉시 실패한다. 테스트 스위트는 없다.

## Architecture

책 제목 하나로 30초 세로 쇼츠(mp4)를 만드는 3단 파이프라인. `main.py`가 대화형 컨트롤 타워로
두 모듈을 순서대로 엮는다.

1. **기획 (`src/llm_module.py` → `generate_shorts_source`)**
   `src/claude_engine.py`의 `ask_claude`에 엄격한 시스템 프롬프트를 넣어 Claude에게
   **6개 키 JSON**(`script_1..3`, `image_prompt_1..3`)을 받는다. Claude가 잡담을 섞어도
   `extract_robust_json`이 순수 JSON을 도려낸다. 이어서 각 `image_prompt`로 배경 3장을 생성한다
   (`generate_visual_image` → OpenAI `gpt-image-1` 우선, 실패/무키 시 Pollinations `sd35` 백업 →
   `enhance_image_quality`로 1080×1920 보정). 생성 전 옛 배경은 소각한다.

2. **조립 (`src/video_module.py` → `build_video_with_subtitles`)**
   `edge-tts`(ko-KR-SunHiNeural)로 전체 대본을 낭독해 mp3를 만들고, **오디오 길이를 3등분**해
   구간 타이밍을 잡는다. moviepy로 1080×1920 배경(슬로우 줌인 transform) + 상하 15% 블랙바 +
   자막을 합성하고, `assets/bgm.mp3`가 있으면 자동 믹싱해 libx264/aac로 인코딩한다.

**핵심 데이터 계약**: 위 6키 JSON dict가 두 모듈을 잇는 유일한 인터페이스다. 키 이름을 바꾸면
`extract_robust_json`(성공 판정에 `image_prompt_1`·`script_1` 존재를 검사)과 조립 단계가 함께 깨진다.

**"세트" 개념**: 하나의 쇼츠 = 같은 base 이름을 공유하는 3개 산출물 —
`outputs/videos/<base>.mp4`, `outputs/audios/<base>.mp3`, `outputs/scripts/<base>_prompts.txt`.
`main.py`는 같은 제목이 이미 있으면 `_1`, `_2`… 번호를 붙여 덮어쓰기를 피하고, 삭제(메뉴 2)는
이 3개 세트를 함께 처리한다.

**테스트 모드**: `generate_shorts_source(book, is_test_mode=True)`는 Claude/이미지 API를 건너뛰고
고정 더미 대본을 쓴다(이미지 생성은 여전히 시도). 실가동(`False`)은 과금되므로 기본은 테스트 모드.

## Secrets

API 키는 코드에 두지 않고 환경변수에서 읽는다 — `ANTHROPIC_API_KEY`(claude_engine), `OPENAI_API_KEY`(llm_module).
OpenAI 키가 비면 이미지가 자동으로 무료 백업 라인으로 우회한다. Claude 모델 ID는 `src/claude_engine.py`에서 관리한다.

## Custom skills

`.claude/skills/`에 파이프라인 전용 스킬 4종: `shorts-script`(대본 JSON 기획),
`build-short`(실제 생산), `factory-doctor`(환경 진단), `clean-warehouse`(세트 삭제).
