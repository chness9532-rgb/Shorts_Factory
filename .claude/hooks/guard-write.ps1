# Shorts_Factory 가드레일 — 파일 쓰기(PreToolUse: Write|Edit) 검사
# 소스에 API 키 리터럴(sk-ant-/sk-proj-)을 다시 박으려 하면 차단한다.
# 문서/설명의 짧은 플레이스홀더(sk-ant-...)는 통과하도록 긴 실제 키만 탐지한다.
$ErrorActionPreference = 'Stop'

try {
    $raw = [Console]::In.ReadToEnd()
    if (-not $raw) { exit 0 }
    $j = $raw | ConvertFrom-Json
    $ti = $j.tool_input
    $content = ''
    if ($ti.content)    { $content += [string]$ti.content }
    if ($ti.new_string) { $content += "`n" + [string]$ti.new_string }
} catch { exit 0 }

if (-not $content) { exit 0 }

if ($content -match 'sk-ant-[A-Za-z0-9_\-]{20,}' -or $content -match 'sk-proj-[A-Za-z0-9_\-]{20,}') {
    $obj = @{
        hookSpecificOutput = @{
            hookEventName            = 'PreToolUse'
            permissionDecision       = 'deny'
            permissionDecisionReason = '[가드레일] 소스에 API 키 리터럴(sk-ant-/sk-proj-)을 넣으려 합니다. 키는 하드코딩하지 말고 os.environ["ANTHROPIC_API_KEY"] / os.environ["OPENAI_API_KEY"] 로 읽으세요.'
        }
    }
    ($obj | ConvertTo-Json -Depth 6 -Compress)
    exit 0
}

exit 0
