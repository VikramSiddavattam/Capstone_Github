$ErrorActionPreference = 'Stop'

function Get-HookText {
    try {
        $inputJson = [Console]::In.ReadToEnd()
        if ([string]::IsNullOrWhiteSpace($inputJson)) { return '' }
        return $inputJson
    } catch {
        return ''
    }
}

function Test-NonEmptyFile($Path) {
    return (Test-Path -LiteralPath $Path -PathType Leaf) -and ((Get-Item -LiteralPath $Path).Length -gt 0)
}

function Block($Message, $Failures) {
    $output = [ordered]@{
        continue      = $false
        stopReason    = $Message
        systemMessage = "$Message $($Failures -join ' ')"
    }
    $output | ConvertTo-Json -Depth 5 -Compress
    exit 2
}

$hookText = Get-HookText
if ($hookText -notmatch '(?i)(pr agent|pull request|pre-pr|pr readiness|publish)') { exit 0 }

$failures = @()
$requiredFiles = @(
    'documentation/requirements.md',
    'documentation/architecture.md',
    'documentation/design-review.md',
    'documentation/impl-plan.md',
    'documentation/code-review.md',
    'documentation/verification-report.md',
    'documentation/pr-description.md'
)

foreach ($file in $requiredFiles) {
    if (-not (Test-NonEmptyFile $file)) { $failures += "Missing or empty: $file." }
}

if (Test-NonEmptyFile 'documentation/verification-report.md') {
    $verification = Get-Content -LiteralPath 'documentation/verification-report.md' -Raw
    $hasPassingVerdict = $verification -match '(?i)(verification verdict\s*:\s*\*\*pass\*\*|verification status\s*:\s*pass|status\s*:\s*pass|\btests?\s+passed\b)'
    $hasNonZeroFailures = $verification -match '(?i)\b([1-9][0-9]*)\s+(failures?|failed)\b|verification verdict\s*:\s*\*\*fail\*\*|\bblocked\b'
    if (-not $hasPassingVerdict -or $hasNonZeroFailures) {
        $failures += 'Verification report does not show an unambiguous passing result.'
    }
    if ($verification -notmatch '(?i)\btests?\b.*\b(pass|passed)\b') {
        $failures += 'Verification report does not include test execution evidence.'
    }
}

if (Test-NonEmptyFile 'documentation/code-review.md') {
    $review = Get-Content -LiteralPath 'documentation/code-review.md' -Raw
    if ($review -match '(?i)verdict\s*:\s*blocked|review conclusion\s*:\s*blocked') {
        $failures += 'Code review is blocked.'
    }
}

if ($failures.Count -gt 0) {
    Block 'Pre-PR readiness gate failed: PR publication prerequisites are not satisfied.' $failures
}

$output = [ordered]@{
    systemMessage = 'Pre-PR readiness gate passed: SDLC artifacts, code review, verification evidence, and PR description are available.'
}
$output | ConvertTo-Json -Depth 5 -Compress
exit 0
