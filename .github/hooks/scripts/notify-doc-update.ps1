# PostToolUse hook: after a file-editing tool runs, check whether any touched
# path affects project intelligence and remind the agent to sync documentation.
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
$editTools = @('editFiles', 'createFile', 'create_file', 'replace_string_in_file', 'multi_replace_string_in_file', 'insert_edit_into_file', 'apply_patch')
if ($data.tool_name -and ($editTools -notcontains $data.tool_name)) {
    exit 0
}

# Serialize tool_input to text and scan it for major project path references.
# This sidesteps PowerShell's array-unwrapping quirks that plague recursive collectors.
$toolInputText = $data.tool_input | ConvertTo-Json -Compress
if (-not $toolInputText) { exit 0 }

$normalizedToolInput = $toolInputText.Replace('\\', '/')
$majorPathMarkers = @(
    'app.py',
    'README.md',
    'documentation/',
    'locator_lense/',
    'templates/',
    'tests/',
    '.github/',
    '.vscode/',
    'rag/project-intelligence.md'
)

$isRelevantChange = $false
foreach ($marker in $majorPathMarkers) {
    if ($normalizedToolInput.Contains($marker)) {
        $isRelevantChange = $true
        break
    }
}

if (-not $isRelevantChange) { exit 0 }

$output = [ordered]@{
    hookSpecificOutput = [ordered]@{
        hookEventName      = 'PostToolUse'
        additionalContext  = "Project intelligence-relevant files changed. Review and refresh documentation/*.md and rag/project-intelligence.md when behavior, architecture, features, quality gates, or developer workflow changed. Keep rag/project-intelligence.md concise, factual, and optimized for AI retrieval."
    }
}

$output | ConvertTo-Json -Depth 10 -Compress
exit 0
