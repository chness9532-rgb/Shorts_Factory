---
name: hyperframes
description: HeyGen HyperFrames로 HTML을 영상으로 렌더한다. 컴포지션·GSAP 애니메이션·자막·보이스오버·오디오 반응 비주얼·웹사이트→영상 캡처를 지원. moviepy 조립 대신 HTML 기반으로 쇼츠 비주얼을 만들 때 사용. "HTML로 영상", "hyperframes", "HeyGen 렌더" 요청에 사용.
---

# HyperFrames (HeyGen) — HTML → 영상 렌더

HyperFrames는 스킬/MCP 파일이 아니라 **npm CLI 도구**다(npm: `hyperframes`). 이 스킬은 그 CLI를
이 공장에서 쓰는 방법을 안내한다. moviepy 조립 라인의 대안으로, HTML+CSS+GSAP로 자막·보이스오버가
들어간 쇼츠 영상을 렌더할 수 있다.

## 사전 준비
- 실행: 별도 설치 없이 `npx hyperframes <명령>` (또는 `npm i -g hyperframes` 후 `hyperframes`).
- 인증: HeyGen/HyperFrames API 키가 필요하다. `npx hyperframes auth` 로 로그인/키 등록.
  키는 코드에 박지 말고 CLI 인증 흐름이나 환경변수로 둔다.

## 기본 사용
- 사용 가능한 명령 확인: `npx hyperframes --help`
- 문서: `npx hyperframes docs`, 진단: `npx hyperframes doctor`
- 렌더: HTML 컴포지션을 작성한 뒤 hyperframes로 영상(mp4)으로 렌더한다.
  (자막·보이스오버·오디오 반응 효과는 컴포지션에서 지정)

## 이 공장에서의 활용
- 세로 1080×1920 규격의 HTML 컴포지션을 만들고, 3구간 대본을 자막으로,
  edge-tts 또는 HyperFrames 보이스오버로 내레이션을 넣어 렌더한다.
- 즉, [shorts-script](../shorts-script/SKILL.md)가 뽑은 대본을 HTML 컴포지션에 얹어
  moviepy 대신 HyperFrames로 출력하는 대체 라인으로 쓸 수 있다.

## 주의
- 정확한 서브커맨드·옵션은 버전에 따라 다르니, 실제 작업 전 `npx hyperframes --help`로 확인한다.
- 렌더는 HeyGen 서비스 과금이 발생할 수 있으므로, 실제 렌더 전 사용자에게 알린다.
