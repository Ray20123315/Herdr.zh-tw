# Herdr 0.9.3 zh-TW independent DEVELOPMENT build.
# Does NOT replace or modify your existing installed Herdr.
[CmdletBinding()]
param([string]$WorkRoot = (Join-Path $env:USERPROFILE 'Herdr-zhTW-v0.0.1'))
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$ExpectedSha = '7b116c05bfda646af39d2524c54e70c751f57ee8'
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Repo = Join-Path $WorkRoot 'herdr-v0.9.3-zhTW'
function Require([string]$Name) {
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) { throw "缺少必要工具 $Name。請先安裝並加入 PATH。" }
}
Require 'git'
Require 'cargo'
Require 'zig'
$Py = Get-Command 'py' -ErrorAction SilentlyContinue
if ($Py) { $PythonCommand = 'py'; $PythonPrefix = @('-3') }
else { Require 'python'; $PythonCommand = 'python'; $PythonPrefix = @() }
$ZigVersion = & zig version 2>$null
if ($LASTEXITCODE -ne 0 -or $ZigVersion.Trim() -ne '0.16.0') {
    throw "需要 Zig 0.16.0；目前版本：$ZigVersion。請先從官方安裝，並確認 'zig version' 輸出 0.16.0。"
}
if (Test-Path -LiteralPath $Repo) {
    throw "目標目錄已存在：$Repo。為避免覆蓋或套用重複補丁，請另選 WorkRoot。"
}
New-Item -ItemType Directory -Force -Path $WorkRoot | Out-Null
Write-Host '[1/6] Clone pinned v0.9.3 source into an isolated directory...'
& git clone --branch v0.9.3 --depth 1 https://github.com/herdrdev/herdr.git $Repo
if ($LASTEXITCODE -ne 0) { throw 'Git clone 失敗' }
Push-Location $Repo
try {
    $ActualSha = (& git rev-parse HEAD).Trim()
    if ($ActualSha -ne $ExpectedSha) { throw "Git commit 不符：$ActualSha" }
    Write-Host '[2/6] Validate and apply zh-TW patch...'
    $Arguments = @($PythonPrefix) + @((Join-Path $ScriptDir 'apply_zh_tw.py'), '--source', $Repo, '--report', (Join-Path $WorkRoot 'translation-report.json'))
    & $PythonCommand @Arguments
    if ($LASTEXITCODE -ne 0) { throw '翻譯補丁套用失敗' }
    Write-Host '[3/6] Format patched Rust sources and verify...'
    & cargo fmt --all
    if ($LASTEXITCODE -ne 0) { throw 'cargo fmt 失敗' }
    & cargo fmt --all -- --check
    if ($LASTEXITCODE -ne 0) { throw 'cargo fmt 檢查失敗' }
    Write-Host '[4/6] Compile check (development profile)...'
    & cargo check --locked
    if ($LASTEXITCODE -ne 0) { throw 'cargo check 編譯檢查失敗' }
    Write-Host '[5/6] Build separate debug executable...'
    & cargo build --locked
    if ($LASTEXITCODE -ne 0) { throw 'cargo build 失敗' }
    $Binary = Join-Path $Repo 'target\debug\herdr.exe'
    if (-not (Test-Path -LiteralPath $Binary)) { throw '找不到建置輸出 exe' }
    Write-Host '[6/6] Verify version...'
    & $Binary --version
    if ($LASTEXITCODE -ne 0) { throw '新執行檔版本檢查失敗' }
    Write-Host "已產生測試版（不覆蓋正式安裝）：$Binary"
    Write-Host '此為 development build，使用獨立 herdr-dev 設定／Server，不代表完整翻譯或 Windows UI 測試已通過。'
} finally { Pop-Location }
