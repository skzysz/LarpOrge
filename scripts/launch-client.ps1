$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
Push-Location $projectRoot
try {
    $localJdk = Get-ChildItem "$projectRoot/.local/java" -Directory -Filter 'jdk-21*' -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($localJdk) { $env:JAVA_HOME = $localJdk.FullName }
    $env:GRADLE_USER_HOME = "$projectRoot/.local/gradle"
    python "$PSScriptRoot/brand-loader.py"
    if ($LASTEXITCODE -ne 0) { throw 'Failed to prepare MeowForge loading screen.' }
    python "$PSScriptRoot/forge_compat.py" "$projectRoot/projects/neoforge/run/client/mods" --strict --report "$projectRoot/.local/compatibility-report.json"
    if ($LASTEXITCODE -ne 0) { throw 'Mod preflight failed. See .local/compatibility-report.json for unsupported Forge APIs or Minecraft versions.' }
    $gradle = "$projectRoot/.local/tools/gradle-9.8.1/bin/gradle.bat"
    if (-not (Test-Path -LiteralPath $gradle)) { $gradle = "$projectRoot/gradlew.bat" }
    # Setup must finish before compilation: it extracts the patched Minecraft sources.
    & $gradle :neoforge:setup --console=plain
    if ($LASTEXITCODE -ne 0) { throw "Minecraft source setup failed: $LASTEXITCODE" }
    & $gradle :neoforge:runClient --console=plain
    if ($LASTEXITCODE -ne 0) { throw "Client launch failed: $LASTEXITCODE" }
} finally {
    Pop-Location
}
