# apply-auto-allow.ps1 -- add --auto-allow-devtools-connections to a Chromium checkout
#
# Patches three files (anchored on exact upstream bytes at tag 152.0.7977.84;
# anchors are chosen so they hold across nearby tags too):
#   chrome/common/chrome_switches.h
#   chrome/common/chrome_switches.cc
#   chrome/browser/devtools/chrome_devtools_manager_delegate.cc
#
# Effect: when launched with --auto-allow-devtools-connections, every incoming
# remote debugging connection is accepted without showing the consent dialog.
#
# Usage:  .\apply-auto-allow.ps1 [-SrcRoot E:\unsafe-chrome\chromium\src]
# Idempotent: files already containing the switch are skipped.

param(
    [string]$SrcRoot = "E:\unsafe-chrome\chromium\src"
)

$ErrorActionPreference = 'Stop'

$utf8NoBom = [System.Text.UTF8Encoding]::new($false)

$SwitchName = 'auto-allow-devtools-connections'
$ConstName  = 'kAutoAllowDevtoolsConnections'

# --- anchors (exact bytes as of 152.0.7977.84) ------------------------------

$AnchorSwitchesH = "extern const char kAutoOpenDevToolsForTabs[];"
$NewSwitchesH    = "extern const char $ConstName[];`n"

$AnchorSwitchesCc = "// This flag makes Chrome auto-open DevTools window for each tab. It is"
$NewSwitchesCc    = "// Automatically accepts incoming remote debugging connections without showing`n" +
                   "// the consent dialog. Local automation builds only; never send upstream.`n" +
                   "const char $ConstName[] = `"$SwitchName`";`n`n"

$AnchorDelegate = "void ChromeDevToolsManagerDelegate::AcceptDebugging(AcceptCallback callback) {"
$NewDelegate    = "`n" +
                   "  // --auto-allow-devtools-connections: skip the consent dialog, accept every`n" +
                   "  // incoming remote debugging connection. Local automation build only.`n" +
                   "  if (base::CommandLine::ForCurrentProcess()->HasSwitch(`n" +
                   "          switches::$ConstName)) {`n" +
                   "    std::move(callback).Run(`n" +
                   "        content::DevToolsManagerDelegate::AcceptConnectionResult::kAllow);`n" +
                   "    return;`n" +
                   "  }`n"

# --- helpers ----------------------------------------------------------------

function Edit-File {
    param([string]$Path, [string]$Anchor, [string]$Replacement, [string]$Label, [switch]$After)
    if (-not (Test-Path $Path)) { throw "file not found: $Path" }
    $text = [IO.File]::ReadAllText($Path)
    if ($text.Contains($ConstName)) {
        Write-Host "[skip] $Label already patched"
        return
    }
    $idx = $text.IndexOf($Anchor)
    if ($idx -lt 0) { throw "anchor not found in $Label -- upstream drifted, update anchors" }
    if ($text.IndexOf($Anchor, $idx + 1) -ge 0) { throw "anchor not unique in $Label" }
    $at = if ($After) { $idx + $Anchor.Length } else { $idx }
    $new = $text.Insert($at, $Replacement)
    [IO.File]::WriteAllText($Path, $new, $utf8NoBom)
    Write-Host "[ok]   $Label patched"
}

# --- apply ------------------------------------------------------------------

Edit-File -Path (Join-Path $SrcRoot 'chrome\common\chrome_switches.h') `
          -Anchor $AnchorSwitchesH -Replacement $NewSwitchesH `
          -Label 'chrome_switches.h'

Edit-File -Path (Join-Path $SrcRoot 'chrome\common\chrome_switches.cc') `
          -Anchor $AnchorSwitchesCc -Replacement $NewSwitchesCc `
          -Label 'chrome_switches.cc'

Edit-File -Path (Join-Path $SrcRoot 'chrome\browser\devtools\chrome_devtools_manager_delegate.cc') `
          -Anchor $AnchorDelegate -Replacement $NewDelegate -After `
          -Label 'chrome_devtools_manager_delegate.cc'

Write-Host "`nDone. Build with:`n  autoninja -C out\Release chrome"
Write-Host "Run with:`n  chrome --user-data-dir=<dir> --remote-debugging-port=9222 --auto-allow-devtools-connections"
