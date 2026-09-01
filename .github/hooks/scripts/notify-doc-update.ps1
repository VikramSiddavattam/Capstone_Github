# PostToolUse hook: after a file-editing tool runs, check whether any touched
# path is under locator_lense/ and, if so, remind the agent to sync documentation/*.md.
$ErrorActionPreference = 'Stop'

try {
    $inputJson = [Console]::In.ReadToEnd()
    if ([string]::IsNullOrWhiteSpace($inputJson)) { exit 0 }
    $data = $inputJson | ConvertFrom-Json
} catch {
    # Malformed/absent input must never block the agent session.
    exit 0
}

# Only react to tools that create or modify files.
$editTools = @('editFiles', 'createFile', 'create_file', 'replace_string_in_file', 'multi_replace_string_in_file', 'insert_edit_into_file')
if ($data.tool_name -and ($editTools -notcontains $data.tool_name)) {
    exit 0
}

# Serialize tool_input to text and scan it for locator_lense/*.py path references.
# This sidesteps PowerShell's array-unwrapping quirks that plague recursive collectors.
$toolInputText = $data.tool_input | ConvertTo-Json -Compress
if (-not $toolInputText) { exit 0 }

$matches = [regex]::Matches($toolInputText, '"([^"]*locator_lense[^"]*\.py)"')
if ($matches.Count -eq 0) { exit 0 }

$changedSource = $matches | ForEach-Object { $_.Groups[1].Value -replace '\\\\', '\' } | Select-Object -Unique
$fileList = $changedSource -join ', '

$output = [ordered]@{
    hookSpecificOutput = [ordered]@{
        hookEventName      = 'PostToolUse'
        additionalContext  = "Source code under locator_lense/ changed ($fileList). Review the Markdown files in documentation/ (architecture.md, design-review.md, impl-plan.md, requirements.md) and update any sections describing the changed module(s) so the docs stay in sync with the code."
    }
}

$output | ConvertTo-Json -Depth 10 -Compress
exit 0
