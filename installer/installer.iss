; Inno Setup script for Ayen-Ode desktop installer.
;
; Build with:   ISCC.exe /DAyenOdeVersion=0.3.2 installer\installer.iss
; (or use scripts\build_exe.ps1 -Installer which wires this up automatically)
;
; Per-user install (no admin required). The EXE lives in
; %LOCALAPPDATA%\Programs\Ayen-Ode, and the user's saved state lives separately
; in %APPDATA%\Ayen-Ode\ so uninstalling never deletes their worlds.

#ifndef AyenOdeVersion
  #define AyenOdeVersion "0.3.2"
#endif

#define AppName        "Ayen-Ode"
#define AppPublisher   "Ayen-Ode"
#define AppURL         "https://github.com/SnowyAyser/Ayen-Ode-0.3"
#define AppExeName     "Ayen-Ode.exe"

[Setup]
AppId={{B9C73B12-0F4E-4EAD-A24E-A8C8E5BD6E61}}
AppName={#AppName}
AppVersion={#AyenOdeVersion}
AppVerName={#AppName} {#AyenOdeVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}
DefaultDirName={localappdata}\Programs\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
OutputDir=..\dist
OutputBaseFilename=Ayen-Ode-Setup-{#AyenOdeVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayName={#AppName}
UninstallDisplayIcon={app}\{#AppExeName}
; SetupIconFile=..\static\favicon.ico    ; uncomment once we ship an icon

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Ship the entire PyInstaller onedir folder.
Source: "..\dist\Ayen-Ode\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{group}\{cm:UninstallProgram,{#AppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Run]
; Offer to launch after install. Unchecked-by-default would feel awkward for a
; "click run" desktop app, so we leave it checked.
Filename: "{app}\{#AppExeName}"; Description: "{cm:LaunchProgram,{#AppName}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Don't touch %APPDATA%\Ayen-Ode\ — the user's worlds live there. Only clean
; up the install dir itself (Inno does this automatically; entry kept for
; clarity).
Type: filesandordirs; Name: "{app}"

; ---------------------------------------------------------------------------
; WebView2 runtime detection. Edge WebView2 ships with Windows 11 and is on
; most Win10 boxes via Edge updates, but a small fraction of Win10 machines
; don't have it. We probe two registry keys and run the official bootstrapper
; if absent. The bootstrapper itself is ~2 MB and downloads the rest online;
; if you prefer an offline install, replace it with the standalone installer
; from https://developer.microsoft.com/microsoft-edge/webview2/.
; ---------------------------------------------------------------------------

[Code]
function WebView2Installed(): Boolean;
var
  HKLMKey, HKCUKey: string;
  version: string;
begin
  Result := False;
  HKLMKey := 'SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}';
  HKCUKey := 'Software\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}';
  if RegQueryStringValue(HKLM, HKLMKey, 'pv', version) then
    if (version <> '') and (version <> '0.0.0.0') then Result := True;
  if not Result then
    if RegQueryStringValue(HKCU, HKCUKey, 'pv', version) then
      if (version <> '') and (version <> '0.0.0.0') then Result := True;
end;

procedure InitializeWizard();
begin
  // Placeholder for future custom pages (welcome blurb, prerequisite check, …)
end;

function ShouldDownloadWebView2(): Boolean;
begin
  Result := not WebView2Installed();
end;
