---
name: build-short
description: Shorts_Factory 생산 라인을 실제로 가동해 완제품 쇼츠(mp4)를 출하한다. 책 제목을 받아 대본·이미지·성우 TTS·자막 합성까지 돌린다. 테스트 모드(비용 0원)와 실가동 모드를 구분한다. "영상 만들어줘", "쇼츠 뽑아줘", "공장 가동", "생산 라인 돌려줘" 요청에 사용.
---

# 쇼츠 완제품 생산 스킬 (build-short)

`main.py`의 1번 라인(생산)과 동일한 결과를 낸다. main.py는 `input()` 대화형이라
자동 구동이 어렵기 때문에, 이 스킬은 모듈 함수를 **비대화형으로 직접 호출**한다.

## 사전 점검
먼저 `factory-doctor` 스킬 수준의 최소 확인만 한다:
- `assets/fonts/font.ttf` 존재 여부(없으면 영상 빌드가 즉시 실패한다).
- 실가동 모드면 API 키가 유효한지(무효 시 이미지는 Pollinations 백업으로 우회됨).

## 사용자에게 확인할 것
1. **책 제목** (필수).
2. **모드**: 테스트(`is_test_mode=True`, 비용 0원·가짜 대본) / 실가동(`False`, 클로드+이미지 API 과금).
3. 같은 제목 완제품이 이미 `outputs/videos/`에 있으면 덮어쓰지 말고
   `<제목>_shorts_1`, `_2` … 처럼 번호를 붙인다(main.py와 동일 규칙).

## 실행 방법 (비대화형 드라이버)
⚠️ **인터프리터 주의**: 이 PC의 기본 `python`은 3.14(패키지 없음)다. 의존성과 키는
**Python 3.13**(`py -3.13`)에만 있으니 반드시 `py -3.13`으로 실행한다.

아래처럼 파이프라인 함수를 직접 호출한다. `<제목>`과 `<TEST>`만 채워 실행:

```powershell
py -3.13 -c "import sys; sys.path.insert(0,'.'); from src.llm_module import generate_shorts_source; from src.video_module import build_video_with_subtitles; book='<제목>'; base=book+'_shorts'; out=generate_shorts_source(book, <TEST>); ok = build_video_with_subtitles(out, base+'.mp4') if out else False; print('DONE' if ok else 'FAILED')"
```
- `<TEST>` = `True`(테스트) 또는 `False`(실가동).
- 실가동일 때 대본 txt도 남기려면, `generate_shorts_source` 반환 dict를
  `outputs/scripts/<제목>_shorts_prompts.txt`에 main.py의 저장 포맷대로 기록한다.

## 파이프라인이 하는 일 (참고)
1. `generate_shorts_source`: 클로드가 3구간 대본+영문 이미지 프롬프트 JSON 생성 →
   `generate_visual_image`로 `assets/backgrounds/bg1~3.jpg` 3장 생성
   (gpt-image-1 우선, 실패/무키 시 Pollinations sd35 백업). 기존 bg 파편은 먼저 소각됨.
2. `build_video_with_subtitles`: `edge-tts`(ko-KR-SunHiNeural, rate -8%)로 성우 낭독 mp3 →
   1080×1920 FHD, 상하 15% 블랙바, 자막(폰트 56), 10% 슬로우 줌인 →
   `assets/bgm.mp3`가 있으면 자동 믹싱 → libx264/aac, fps 24로 인코딩.

## 출력
- 영상: `outputs/videos/<base>.mp4`
- 오디오: `outputs/audios/<base>.mp3`
- 대본: `outputs/scripts/<base>_prompts.txt` (실가동 시)

## 실패 대응
- `edge-tts`/`moviepy`/`ffmpeg`/`PIL` 미설치 → `factory-doctor` 스킬로 넘긴다.
- 폰트 없음 → `assets/fonts/font.ttf` 확인.
- 이미지 API 오류 → 자동으로 무료 백업 라인이 돈다(치명적 아님).
- 완료 후 `outputs/videos/`에 파일이 실제로 생겼는지 확인하고 사용자에게 경로를 보고한다.
