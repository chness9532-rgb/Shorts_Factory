# Shorts_Factory 가드레일 — 셸 명령(PreToolUse: Bash|PowerShell) 검사
# stdin으로 훅 JSON을 받아 위험/실수 패턴이면 permissionDecision=deny 를 출력한다.
# 문제 없으면 아무것도 출력하지 않고 종료(=허용).
$ErrorActionPreference = 'Stop'

function Deny([string]$reason) {
    $obj = @{
        hookSpecificOutput = @{
            hookEventName            = 'PreToolUse'
            permissionDecision       = 'deny'
            permissionDecisionReason = $reason
        }
    }
    ($obj | ConvertTo-Json -Depth 6 -Compress)
    exit 0
}

try {
    $raw = [Console]::In.ReadToEnd()
    if (-not $raw) { exit 0 }
    $j = $raw | ConvertFrom-Json
    $cmd = ''
    if ($j.tool_input -and $j.tool_input.command) { $cmd = [string]$j.tool_input.command }
} catch { exit 0 }  # 파싱 실패 시 안전하게 허용(가드레일이 정상 작업을 막지 않도록)

if (-not $cmd) { exit 0 }

# ── 규칙 3: 위험한 재귀/강제 삭제 ────────────────────────────────
if ($cmd -match '(?i)Remove-Item[^\r\n]*(-Recurse[^\r\n]*-Force|-Force[^\r\n]*-Recurse)' `
    -or $cmd -match '(?i)(^|[\s;&|])rm\s+-[a-z]*r[a-z]*f' `
    -or $cmd -match '(?i)(^|[\s;&|])rm\s+-[a-z]*f[a-z]*r' `
    -or $cmd -match '(?i)\brmdir\s+/s') {
    Deny('[가드레일] 위험한 재귀/강제 삭제가 감지됐습니다. 무엇을 지우는지 대상 경로를 명시하고 사용자 승인을 받은 뒤 진행하세요. outputs/ 정리는 clean-warehouse 스킬을 쓰세요.')
}

# ── 규칙 1: py -3.13 강제 (기본 python은 3.14, 의존성 없음) ──────
# 명령에 'py -3.13'이 이미 있으면 통과(그래야 `py -3.13 -m pip ...`이 안 막힘).
$usesPy313 = ($cmd -match '(?i)\bpy\s+-3\.13\b')
if (-not $usesPy313) {
    if ($cmd -match '(?i)(^|[\s;&|])(python3?|pip3?)(\.exe)?($|[\s;&|])') {
        Deny('[가드레일] 이 공장은 반드시 py -3.13 을 써야 합니다(기본 python은 3.14=의존성 없음). `python ...`→`py -3.13 ...`, `pip ...`→`py -3.13 -m pip ...` 로 바꿔 실행하세요.')
    }
}

# ── 규칙 4: 실가동(과금) 보호 ────────────────────────────────────
if ($cmd -match '(?i)is_test_mode\s*=\s*False' `
    -or $cmd -match '(?i)generate_shorts_source\s*\([^)]*,\s*False\s*\)') {
    Deny('[가드레일] 실가동(is_test_mode=False)은 Claude/이미지 API 과금이 발생합니다. 사용자의 명시적 승인 없이 실가동하지 마세요. 확인 전에는 테스트 모드(True)로 실행하세요.')
}

exit 0
