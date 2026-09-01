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
if ($hookText -notmatch '(?i)(verification agent|pre-verification|verify|verification)') { exit 0 }

$failures = @()
$requiredFiles = @(
    'documentation/requirements.md',
    'documentation/architecture.md',
    'documentation/design-review.md',
    'documentation/impl-plan.md',
    'documentation/code-review.md',
    'app.py',
    'requirements.txt'
)

foreach ($file in $requiredFiles) {
    if (-not (Test-NonEmptyFile $file)) { $failures += "Missing or empty: $file." }
}

if (-not (Test-Path -LiteralPath 'locator_lense' -PathType Container)) { $failures += 'Missing implementation package: locator_lense/.' }
if (-not (Test-Path -LiteralPath 'tests' -PathType Container)) { $failures += 'Missing automated tests directory: tests/.' }

if (Test-NonEmptyFile 'documentation/code-review.md') {
    $review = Get-Content -LiteralPath 'documentation/code-review.md' -Raw
    if ($review -match '(?i)verdict\s*:\s*blocked|review conclusion\s*:\s*blocked') {
        $failures += 'Code review is blocked.'
    }
    if ($review -match '(?im)^\s*(critical|high)\b' -and $review -notmatch '(?i)no\s+(critical|high)') {
        $failures += 'Code review contains Critical or High findings; resolve or explicitly document acceptance before verification.'
    }
}

if ($failures.Count -gt 0) {
    Block 'Pre-verification gate failed: verification prerequisites are not satisfied.' $failures
}

$output = [ordered]@{
    systemMessage = 'Pre-verification gate passed: review artifact, implementation artifacts, and tests are available with no detected blocking review verdict.'
}
$output | ConvertTo-Json -Depth 5 -Compress
exit 0
