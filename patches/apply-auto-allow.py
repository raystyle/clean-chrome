# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""apply-auto-allow.py -- unsafe-chrome anchored patcher (uv, cross-platform).

Patches four files of a Chromium checkout (anchors are exact upstream bytes
at tag 152.0.7977.84, chosen to hold across nearby tags):

  chrome/common/chrome_switches.h
  chrome/common/chrome_switches.cc
  chrome/browser/devtools/chrome_devtools_manager_delegate.cc
  chrome/browser/devtools/remote_debugging_server.cc   (two anchors)

Effect (local automation build only, never send upstream):
  1. adds switch --auto-allow-devtools-connections;
  2. with that switch, every incoming remote debugging connection is
     accepted without the consent dialog;
  3. launching without --remote-debugging-port opens the port on 9222 by
     default;
  4. the default user data dir carries no remote-debugging restriction;
  5. the "remote debugging active" infobar is never shown.

Usage:
  uv run patches/apply-auto-allow.py [--src-root C:/unsafe-chrome/chromium/src]

Idempotent: each anchor carries its own marker; patched anchors skip.
Replaces the retired apply-auto-allow.ps1 (same effect, verified equivalent).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

SWITCH_NAME = "auto-allow-devtools-connections"
CONST_NAME = "kAutoAllowDevtoolsConnections"

# --- anchors (exact bytes as of 152.0.7977.84) -------------------------------

ANCHOR_SWITCHES_H = "extern const char kAutoOpenDevToolsForTabs[];"
NEW_SWITCHES_H = f"extern const char {CONST_NAME}[];\n"
MARK_SWITCHES_H = f"extern const char {CONST_NAME}[];"

ANCHOR_SWITCHES_CC = "// This flag makes Chrome auto-open DevTools window for each tab. It is"
NEW_SWITCHES_CC = (
    "// Automatically accepts incoming remote debugging connections without showing\n"
    "// the consent dialog. Local automation builds only; never send upstream.\n"
    f"const char {CONST_NAME}[] = \"{SWITCH_NAME}\";\n\n"
)
MARK_SWITCHES_CC = f"const char {CONST_NAME}[] ="

ANCHOR_DELEGATE = "void ChromeDevToolsManagerDelegate::AcceptDebugging(AcceptCallback callback) {"
NEW_DELEGATE = (
    "\n"
    "  // --auto-allow-devtools-connections: skip the consent dialog, accept every\n"
    "  // incoming remote debugging connection. Local automation build only.\n"
    "  if (base::CommandLine::ForCurrentProcess()->HasSwitch(\n"
    f"          switches::{CONST_NAME})) {{\n"
    "    std::move(callback).Run(\n"
    "        content::DevToolsManagerDelegate::AcceptConnectionResult::kAllow);\n"
    "    return;\n"
    "  }\n"
)
MARK_DELEGATE = "  // --auto-allow-devtools-connections: skip the consent dialog"

ANCHOR_PORT = (
    "  std::string port_str =\n"
    "      command_line.GetSwitchValueASCII(::switches::kRemoteDebuggingPort);"
)
NEW_PORT = (
    "\n\n"
    "  // unsafe-chrome: open the debugging port on 9222 by default when launched\n"
    "  // without --remote-debugging-port (local automation build only).\n"
    "  if (port_str.empty()) {\n"
    "    port_str = \"9222\";\n"
    "  }"
)
MARK_PORT = "  // unsafe-chrome: open the debugging port on 9222 by default"

ANCHOR_USER_DATA = (
    "#if BUILDFLAG(GOOGLE_CHROME_BRANDING)\n"
    "  constexpr bool default_user_data_dir_check_enabled = true;\n"
    "#else\n"
    "  const bool default_user_data_dir_check_enabled =\n"
    "      g_enable_default_user_data_dir_check_for_chromium_branding_for_testing;\n"
    "#endif\n"
    "\n"
    "  if (default_user_data_dir_check_enabled &&\n"
    "      is_default_user_data_dir.value_or(true)) {\n"
    "    return base::unexpected(\n"
    "        RemoteDebuggingServer::NotStartedReason::kDisabledByDefaultUserDataDir);\n"
    "  }"
)
NEW_USER_DATA = (
    "  // unsafe-chrome: restriction removed -- the default user data dir\n"
    "  // carries no remote-debugging restriction in this local automation\n"
    "  // build. (Upstream gate block + flag definition replaced; an early\n"
    "  // return here would hit -Wunreachable-code.)"
)
MARK_USER_DATA = "  // unsafe-chrome: restriction removed -- the default user data dir"

ANCHOR_INFOBAR = (
    "  if (count == 0 && infobar_) {\n"
    "    // We need to reset the pointer to the infobar before closing it because\n"
    "    // closing the infobar deletes it.\n"
    "    auto* infobar = infobar_.get();\n"
    "    infobar_ = nullptr;\n"
    "    infobar->Close();\n"
    "  } else if (count > 0 && !infobar_) {\n"
    "    auto delegate = std::make_unique<DevToolsRemoteServerInfobarDelegate>();\n"
    "    delegate->AddObserver(this);\n"
    "    infobar_ = GlobalConfirmInfoBar::Show(std::move(delegate));\n"
    "  }"
)
NEW_INFOBAR = (
    "  // unsafe-chrome: never show the \"remote debugging active\" infobar in\n"
    "  // this local automation build. (Upstream show/close block replaced;\n"
    "  // -Wunreachable-code forbids an early return here.)"
)
MARK_INFOBAR = "  // unsafe-chrome: never show the \"remote debugging active\" infobar"

ANCHOR_STARTUP_INFOBARS = (
    "  infobars::ContentInfoBarManager* infobar_manager =\n"
    "      infobars::ContentInfoBarManager::FromWebContents(web_contents);\n"
    "\n"
    "  if (!google_apis::HasAPIKeyConfigured()) {\n"
    "    GoogleApiKeysInfoBarDelegate::Create(infobar_manager);\n"
    "  }\n"
    "\n"
    "  if (ObsoleteSystem::IsObsoleteNowOrSoon()) {\n"
    "    PrefService* local_state = g_browser_process->local_state();\n"
    "    if (!local_state ||\n"
    "        !local_state->GetBoolean(prefs::kSuppressUnsupportedOSWarning)) {\n"
    "      ObsoleteSystemInfoBarDelegate::Create(infobar_manager);\n"
    "    }\n"
    "  }"
)
NEW_STARTUP_INFOBARS = (
    "  // unsafe-chrome: no API-keys / obsolete-OS startup infobars in this\n"
    "  // local automation build (upstream block replaced; early return is\n"
    "  // forbidden by -Wunreachable-code, and later code shares this scope)."
)
MARK_STARTUP_INFOBARS = "  // unsafe-chrome: no API-keys / obsolete-OS startup infobars"

ANCHOR_OSCRYPT = "  OSCryptAsyncAvailabilityInfoBarDelegate::MaybeCreate(browser);"
NEW_OSCRYPT = (
    "  // unsafe-chrome: no OSCrypt-migration startup infobar (call replaced)."
)
MARK_OSCRYPT = "  // unsafe-chrome: no OSCrypt-migration startup infobar"

ANCHOR_STARTUP_LAUNCH = (
    "#if BUILDFLAG(IS_WIN)\n"
    "  if (auto* startup_launch_manager =\n"
    "          StartupLaunchManager::From(g_browser_process)) {\n"
    "    startup_launch_manager->SetInfoBarManager(\n"
    "        std::make_unique<StartupLaunchInfoBarManagerImpl>());\n"
    "    startup_launch_manager->MaybeShowInfoBars();\n"
    "  }\n"
    "#endif"
)
NEW_STARTUP_LAUNCH = (
    "#if BUILDFLAG(IS_WIN)\n"
    "  // unsafe-chrome: no startup-launch (default-browser / pin) infobars\n"
    "  // (block replaced).\n"
    "#endif"
)
MARK_STARTUP_LAUNCH = "  // unsafe-chrome: no startup-launch (default-browser / pin) infobars"

ANCHOR_SESSION_RESTORE = (
    "#if BUILDFLAG(IS_MAC) || BUILDFLAG(IS_WIN) || BUILDFLAG(IS_LINUX)\n"
    "  if (base::FeatureList::IsEnabled(features::kSessionRestoreInfobar)) {\n"
    "    auto* session_restore_infobar_controller =\n"
    "        session_restore_infobar::SessionRestoreInfobarController::From(browser);\n"
    "    session_restore_infobar_controller->MaybeShowInfoBar(*profile,\n"
    "                                                         is_post_crash_launch);\n"
    "  }\n"
    "#endif  // BUILDFLAG(IS_MAC) || BUILDFLAG(IS_WIN) || BUILDFLAG(IS_LINUX)"
)
NEW_SESSION_RESTORE = (
    "#if BUILDFLAG(IS_MAC) || BUILDFLAG(IS_WIN) || BUILDFLAG(IS_LINUX)\n"
    "  // unsafe-chrome: no session-restore infobar (block replaced).\n"
    "#endif  // BUILDFLAG(IS_MAC) || BUILDFLAG(IS_WIN) || BUILDFLAG(IS_LINUX)"
)
MARK_SESSION_RESTORE = "  // unsafe-chrome: no session-restore infobar (block replaced)."

ANCHOR_NTP_DEFAULT = (
    "  registry->RegisterStringPref(prefs::kNewTabPageLocationOverride,\n"
    "                               std::string());"
)
NEW_NTP_DEFAULT = (
    "  // unsafe-chrome: NTP goes to about:blank by default (policy-pref\n"
    "  // default value changed; startup tab, new tab and ctrl+t all follow).\n"
    "  registry->RegisterStringPref(prefs::kNewTabPageLocationOverride,\n"
    "                               \"about:blank\");"
)
MARK_NTP_DEFAULT = "  // unsafe-chrome: NTP goes to about:blank by default"

ANCHOR_SEARCH_DEFAULT = (
    "  registry->RegisterBooleanPref(prefs::kDefaultSearchProviderEnabled, true);"
)
NEW_SEARCH_DEFAULT = (
    "  // unsafe-chrome: omnibox does not fall back to Google search by\n"
    "  // default (existing profiles keep their persisted value).\n"
    "  registry->RegisterBooleanPref(prefs::kDefaultSearchProviderEnabled, false);"
)
MARK_SEARCH_DEFAULT = "  // unsafe-chrome: omnibox does not fall back to Google search"

ANCHOR_NEWTAB_RESOLVE = (
    "  const GURL resolved_url =\n"
    "      url.is_empty() ? browser->GetBrowserForMigrationOnly()->GetNewTabURL()\n"
    "                     : url;"
)
NEW_NEWTAB_RESOLVE = (
    "  // unsafe-chrome: any implicitly-created tab (startup, new-tab button,\n"
    "  // ctrl+t) opens about:blank instead of the new tab page.\n"
    "  const GURL resolved_url = url.is_empty() ? GURL(\"about:blank\") : url;"
)
MARK_NEWTAB_RESOLVE = "  // unsafe-chrome: any implicitly-created tab"

ANCHOR_CRASH_BUBBLE = (
    "  // Web apps should not display the session restore bubble (crbug.com/40800614)\n"
    "  const bool should_display_bubble =\n"
    "      !is_web_app && HasPendingUncleanExit(browser->GetProfile());\n"
    "  base::UmaHistogramBoolean(\"Startup.CrashBubbleShown\", should_display_bubble);\n"
    "  if (should_display_bubble) {\n"
    "    SessionCrashedBubble::ShowIfNotOffTheRecordProfile(\n"
    "        browser,\n"
    "        /*skip_tab_checking=*/false);\n"
    "  }"
)
NEW_CRASH_BUBBLE = (
    "  // unsafe-chrome: never show the \"restore pages?\" crash bubble in this\n"
    "  // local automation build (block replaced; HasPendingUncleanExit stays\n"
    "  // defined elsewhere so no unused-function fallout)."
)
MARK_CRASH_BUBBLE = "  // unsafe-chrome: never show the \"restore pages?\" crash bubble"

ANCHOR_NTP_FACTORY = (
    "const GURL& ChromeUINewTabURLAsGURL() {\n"
    "  static base::NoDestructor<GURL> instance(kChromeUINewTabURL);\n"
    "  return *instance;\n"
    "}"
)
NEW_NTP_FACTORY = (
    "const GURL& ChromeUINewTabURLAsGURL() {\n"
    "  // unsafe-chrome: chrome://newtab resolves to about:blank everywhere\n"
    "  // (startup tab, first-run, NTP provider tabs) in this local build.\n"
    "  static base::NoDestructor<GURL> instance(GURL(\"about:blank\"));\n"
    "  return *instance;\n"
    "}"
)
MARK_NTP_FACTORY = "  // unsafe-chrome: chrome://newtab resolves to about:blank everywhere"

ANCHOR_STARTUP_LAST = (
    "#if BUILDFLAG(IS_WIN) || BUILDFLAG(IS_LINUX) || BUILDFLAG(IS_MAC)\n"
    "  if (features::kSetDefaultToContinueSession.Get()) {\n"
    "    return SessionStartupPref::LAST;\n"
    "  }\n"
    "#endif"
)
NEW_STARTUP_LAST = (
    "#if BUILDFLAG(IS_WIN) || BUILDFLAG(IS_LINUX) || BUILDFLAG(IS_MAC)\n"
    "  // unsafe-chrome: default startup type stays DEFAULT (about:blank via\n"
    "  // the NTP factory), never \"continue where you left off\".\n"
    "#endif"
)
MARK_STARTUP_LAST = "  // unsafe-chrome: default startup type stays DEFAULT"

ANCHOR_AIM = "BASE_FEATURE(kAimEnabled, base::FEATURE_ENABLED_BY_DEFAULT);"
NEW_AIM = (
    "// unsafe-chrome: omnibox AI Mode off by default (local automation build).\n"
    "BASE_FEATURE(kAimEnabled, base::FEATURE_DISABLED_BY_DEFAULT);"
)
MARK_AIM = "// unsafe-chrome: omnibox AI Mode off by default"

ANCHOR_SR_BUBBLE_2 = (
    "      // If 'browser' is not null, show the crash bubble in the current browser\n"
    "      // instance.\n"
    "      SessionCrashedBubble::ShowIfNotOffTheRecordProfile(\n"
    "          browser, /*skip_tab_checking=*/true);\n"
    "      ProfileLaunchObserver::AddLaunched(profile());"
)
NEW_SR_BUBBLE_2 = (
    "      // unsafe-chrome: no crash-restore bubble from the session-service\n"
    "      // path either (second call site besides startup infobar_utils).\n"
    "      ProfileLaunchObserver::AddLaunched(profile());"
)
MARK_SR_BUBBLE_2 = "  // unsafe-chrome: no crash-restore bubble from the session-service"

ANCHOR_PDF_INFOBAR = "BASE_FEATURE(kPdfInfoBar, base::FEATURE_ENABLED_BY_DEFAULT);"
NEW_PDF_INFOBAR = (
    "// unsafe-chrome: never offer to become the default PDF viewer\n"
    "// (local automation build).\n"
    "BASE_FEATURE(kPdfInfoBar, base::FEATURE_DISABLED_BY_DEFAULT);"
)
MARK_PDF_INFOBAR = "// unsafe-chrome: never offer to become the default PDF viewer"

# --- engine -------------------------------------------------------------------

def edit_file(path: Path, anchor: str, new: str, marker: str, label: str,
              *, mode: str = "before") -> None:
    """mode: 'before' | 'after' (insert around anchor) | 'replace'."""
    if not path.is_file():
        raise SystemExit(f"file not found: {path}")
    text = path.read_text(encoding="utf-8")
    if marker in text:
        print(f"[skip] {label} already patched")
        return
    idx = text.find(anchor)
    if idx < 0:
        raise SystemExit(f"anchor not found in {label} -- upstream drifted, update anchors")
    if text.find(anchor, idx + 1) >= 0:
        raise SystemExit(f"anchor not unique in {label}")
    if mode == "replace":
        path.write_text(text[:idx] + new + text[idx + len(anchor):],
                        encoding="utf-8", newline="")
    else:
        at = idx + len(anchor) if mode == "after" else idx
        path.write_text(text[:at] + new + text[at:], encoding="utf-8", newline="")
    print(f"[ok]   {label} patched")


def main() -> int:
    ap = argparse.ArgumentParser(description="unsafe-chrome anchored patcher")
    ap.add_argument("--src-root", default="C:/unsafe-chrome/chromium/src",
                    help="chromium src root (default: C:/unsafe-chrome/chromium/src)")
    args = ap.parse_args()
    root = Path(args.src_root)

    # Order matters: switches first (defines), delegate second (uses), then the
    # port / user-data-dir gates, then the infobar suppressor.
    edit_file(root / "chrome/common/chrome_switches.h",
              ANCHOR_SWITCHES_H, NEW_SWITCHES_H, MARK_SWITCHES_H, "chrome_switches.h")
    edit_file(root / "chrome/common/chrome_switches.cc",
              ANCHOR_SWITCHES_CC, NEW_SWITCHES_CC, MARK_SWITCHES_CC, "chrome_switches.cc")
    edit_file(root / "chrome/browser/devtools/chrome_devtools_manager_delegate.cc",
              ANCHOR_DELEGATE, NEW_DELEGATE, MARK_DELEGATE,
              "chrome_devtools_manager_delegate.cc (accept all)", mode="after")
    edit_file(root / "chrome/browser/devtools/remote_debugging_server.cc",
              ANCHOR_PORT, NEW_PORT, MARK_PORT,
              "remote_debugging_server.cc (default port 9222)", mode="after")
    edit_file(root / "chrome/browser/devtools/remote_debugging_server.cc",
              ANCHOR_USER_DATA, NEW_USER_DATA, MARK_USER_DATA,
              "remote_debugging_server.cc (no user-data-dir gate)", mode="replace")
    edit_file(root / "chrome/browser/devtools/chrome_devtools_manager_delegate.cc",
              ANCHOR_INFOBAR, NEW_INFOBAR, MARK_INFOBAR,
              "chrome_devtools_manager_delegate.cc (no infobar)", mode="replace")
    edit_file(root / "chrome/browser/ui/startup/infobar_utils.cc",
              ANCHOR_STARTUP_INFOBARS, NEW_STARTUP_INFOBARS, MARK_STARTUP_INFOBARS,
              "infobar_utils.cc (no API-keys/obsolete-OS infobars)", mode="replace")
    edit_file(root / "chrome/browser/ui/startup/infobar_utils.cc",
              ANCHOR_OSCRYPT, NEW_OSCRYPT, MARK_OSCRYPT,
              "infobar_utils.cc (no OSCrypt infobar)", mode="replace")
    edit_file(root / "chrome/browser/ui/startup/infobar_utils.cc",
              ANCHOR_STARTUP_LAUNCH, NEW_STARTUP_LAUNCH, MARK_STARTUP_LAUNCH,
              "infobar_utils.cc (no startup-launch infobars)", mode="replace")
    edit_file(root / "chrome/browser/ui/startup/infobar_utils.cc",
              ANCHOR_SESSION_RESTORE, NEW_SESSION_RESTORE, MARK_SESSION_RESTORE,
              "infobar_utils.cc (no session-restore infobar)", mode="replace")
    edit_file(root / "chrome/browser/profiles/profile_impl.cc",
              ANCHOR_NTP_DEFAULT, NEW_NTP_DEFAULT, MARK_NTP_DEFAULT,
              "profile_impl.cc (NTP -> about:blank default)", mode="replace")
    edit_file(root / "components/search_engines/template_url_service.cc",
              ANCHOR_SEARCH_DEFAULT, NEW_SEARCH_DEFAULT, MARK_SEARCH_DEFAULT,
              "template_url_service.cc (default search off)", mode="replace")
    edit_file(root / "chrome/browser/ui/browser_tabstrip.cc",
              ANCHOR_NEWTAB_RESOLVE, NEW_NEWTAB_RESOLVE, MARK_NEWTAB_RESOLVE,
              "browser_tabstrip.cc (implicit tabs -> about:blank)", mode="replace")
    edit_file(root / "chrome/browser/ui/startup/infobar_utils.cc",
              ANCHOR_CRASH_BUBBLE, NEW_CRASH_BUBBLE, MARK_CRASH_BUBBLE,
              "infobar_utils.cc (no crash-restore bubble)", mode="replace")
    edit_file(root / "chrome/common/webui_url_constants.cc",
              ANCHOR_NTP_FACTORY, NEW_NTP_FACTORY, MARK_NTP_FACTORY,
              "webui_url_constants.cc (newtab factory -> about:blank)", mode="replace")
    edit_file(root / "chrome/browser/prefs/session_startup_pref.cc",
              ANCHOR_STARTUP_LAST, NEW_STARTUP_LAST, MARK_STARTUP_LAST,
              "session_startup_pref.cc (startup default stays DEFAULT)", mode="replace")
    edit_file(root / "components/omnibox/browser/aim_eligibility_service_features.cc",
              ANCHOR_AIM, NEW_AIM, MARK_AIM,
              "aim_eligibility_service_features.cc (AI Mode off)", mode="replace")
    edit_file(root / "chrome/browser/sessions/session_service.cc",
              ANCHOR_SR_BUBBLE_2, NEW_SR_BUBBLE_2, MARK_SR_BUBBLE_2,
              "session_service.cc (no crash bubble, 2nd call site)", mode="replace")
    edit_file(root / "chrome/browser/ui/ui_features.cc",
              ANCHOR_PDF_INFOBAR, NEW_PDF_INFOBAR, MARK_PDF_INFOBAR,
              "ui_features.cc (no default-PDF-viewer infobar)", mode="replace")

    print("\nDone. Build with:\n  autoninja -C out\\Dev chrome   (incremental: minutes)")
    print("Run with: no arguments needed -- port 9222 opens by default, no prompts.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
