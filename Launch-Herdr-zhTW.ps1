# Run isolated debug build without touching installed Herdr executable.
[CmdletBinding()]
param([string]$WorkRoot = (Join-Path $env:USERPROFILE 'Herdr-zhTW-v0.0.1'))
$ErrorActionPreference = 'Stop'
$exe = Join-Path $WorkRoot 'herdr-v0.9.3-zhTW\target\debug\herdr.exe'
if (-not (Test-Path -LiteralPath $exe -PathType Leaf)) {
    throw "找不到中文化測試版：$exe。請先執行 Build-Herdr-zhTW.ps1。"
}
# Respect independent debug paths; remove overrides inherited from existing Herdr panes.
Remove-Item Env:HERDR_SOCKET_PATH -ErrorAction SilentlyContinue
Remove-Item Env:HERDR_CLIENT_SOCKET_PATH -ErrorAction SilentlyContinue
Remove-Item Env:HERDR_SESSION -ErrorAction SilentlyContinue
# Explicit system runtime: source build is not a complete Windows distribution package.
# Remove only this line after bundling a verified app-local ConPTY runtime.
$env:HERDR_WINDOWS_CONPTY = 'system'
& $exe
exit $LASTEXITCODE
