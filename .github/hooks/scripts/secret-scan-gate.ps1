$ErrorActionPreference = 'Stop'

try {
    $inputJson = [Console]::In.ReadToEnd()
    if ([string]::IsNullOrWhiteSpace($inputJson)) { exit 0 }
    $data = $inputJson | ConvertFrom-Json
} catch {
    exit 0
}

$editTools = @('editFiles', 'createFile', 'create_file', 'replace_string_in_file', 'multi_replace_string_in_file', 'insert_edit_into_file', 'apply_patch')
if ($data.tool_name -and ($editTools -notcontains $data.tool_name)) { exit 0 }

$toolInputText = $data.tool_input | ConvertTo-Json -Compress -Depth 100
if (-not $toolInputText) { exit 0 }

$patterns = @(
    'ghp_[A-Za-z0-9_]{30,}',
    'github_pat_[A-Za-z0-9_]{30,}',
    'AKIA[0-9A-Z]{16}',
    '-----BEGIN [A-Z ]*PRIVATE KEY-----',
    '(?i)Authorization\s*[:=]\s*Bearer\s+(?!\$\{(?:env|input):)[A-Za-z0-9._~+/-]{24,}'
)

$detectedPatterns = @()
foreach ($pattern in $patterns) {
    if ($toolInputText -match $pattern) { $detectedPatterns += $pattern }
}

if ($detectedPatterns.Count -gt 0) {
    $output = [ordered]@{
        hookSpecificOutput = [ordered]@{
            hookEventName              = 'PreToolUse'
            permissionDecision         = 'deny'
            permissionDecisionReason   = 'Secret-scan gate blocked this edit because it appears to include credential material. Use environment variables, VS Code secure inputs, or an approved secret manager instead.'
        }
    }
    $output | ConvertTo-Json -Depth 10 -Compress
    exit 2
}

exit 0
