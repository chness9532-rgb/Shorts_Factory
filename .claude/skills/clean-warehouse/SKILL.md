---
name: clean-warehouse
description: Shorts_Factory 창고(outputs)를 정리한다. 완제품 쇼츠 세트(영상 mp4 + 오디오 mp3 + 대본 txt)를 목록으로 보여주고 선택 삭제한다. "실패작 지워줘", "창고 정리", "영상 목록", "이 쇼츠 삭제" 요청에 사용. main.py의 2번 메뉴와 동일 동작.
---

# 창고 정리 스킬 (clean-warehouse)

`main.py`의 `delete_shorts_set_by_list()`와 동일하게, 하나의 쇼츠는
**3대 자재 세트**로 취급한다:
- `outputs/videos/<base>.mp4`
- `outputs/audios/<base>.mp3`
- `outputs/scripts/<base>_prompts.txt`

## 절차
1. `outputs/videos/`의 `.mp4` 목록을 번호와 함께 보여준다. 비어 있으면 그렇게 알린다.
2. 사용자가 삭제할 항목(들)을 고르게 한다.
3. **삭제 전 반드시 확인**한다 — 무엇이 지워지는지 3개 경로를 명시하고 동의를 받는다.
   (되돌릴 수 없는 파괴적 작업이므로, 명시적 승인 없이는 삭제하지 않는다.)
4. 선택된 base에 대해 위 3개 경로 중 **존재하는 것만** 삭제하고, 삭제된 개수를 보고한다.

## 목록 확인 명령
```powershell
Get-ChildItem outputs\videos\*.mp4 | Select-Object -ExpandProperty Name
```

## 삭제 (승인 후에만)
```powershell
$base='<base>'   # 예: 내면근력_shorts
foreach ($p in @("outputs\videos\$base.mp4","outputs\audios\$base.mp3","outputs\scripts\${base}_prompts.txt")) {
  if (Test-Path $p) { Remove-Item $p -Force; Write-Output "deleted: $p" }
}
```

## 주의
- `<base>`는 `.mp4` 확장자를 뗀 이름. 대본 파일만 접미사 `_prompts.txt`가 붙는 점에 유의.
- 여러 개를 지울 때도 각 세트를 명시하고 한 번에 승인받는다.
- 배경 이미지(`assets/backgrounds/bg1~3.jpg`)는 생산 세트가 아니라 매번 덮어써지는
  임시 자재이므로 이 스킬의 삭제 대상이 아니다.
