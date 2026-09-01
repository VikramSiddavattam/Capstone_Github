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

function Block($Message, $Missing) {
    $output = [ordered]@{
        continue      = $false
        stopReason    = $Message
        systemMessage = "$Message Missing or empty: $($Missing -join ', ')."
    }
    $output | ConvertTo-Json -Depth 5 -Compress
    exit 2
}

$hookText = Get-HookText
if ($hookText -notmatch '(?i)(code review agent|code-review agent|pre-review|code review)') { exit 0 }

$requiredFiles = @(
    'documentation/requirements.md',
    'documentation/architecture.md',
    'documentation/design-review.md',
    'documentation/impl-plan.md',
    'app.py',
    'requirements.txt'
)

$missing = @($requiredFiles | Where-Object { -not (Test-NonEmptyFile $_) })
if (-not (Test-Path -LiteralPath 'locator_lense' -PathType Container)) { $missing += 'locator_lense/' }
if (-not (Test-Path -LiteralPath 'tests' -PathType Container)) { $missing += 'tests/' }

if ($missing.Count -gt 0) {
    Block 'Pre-review gate failed: review cannot start until SDLC and implementation prerequisites exist.' $missing
}

$output = [ordered]@{
    systemMessage = 'Pre-review gate passed: requirements, architecture, design review, implementation plan, source, dependencies, and tests are present.'
}
$output | ConvertTo-Json -Depth 5 -Compress
exit 0
