; Script generated for Inno Setup 6
; Valve Workshop Management System Desktop Installer
; Zero-loss architecture preserving user data and backups across updates and uninstallation.

#define MyAppName "Valve Workshop Management System"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Valve Workshop Enterprise"
#define MyAppExeName "ValveWorkshop.exe"

[Setup]
AppId={{E68A8692-7E59-4F5B-9C08-F365A548E12A}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\ValveWorkshop
DefaultGroupName={#MyAppName}
OutputDir=dist_installer
OutputBaseFilename=ValveWorkshop_Setup_v1.0.0
SetupIconFile=app_icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayIcon={app}\{#MyAppExeName}
CloseApplications=yes
RestartApplications=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Dist folder containing PyInstaller compiled standalone executable and dependencies
Source: "dist\ValveWorkshop\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "app_icon.ico"; DestDir: "{app}"; Flags: ignoreversion
; Microsoft Edge WebView2 Bootstrapper for Windows 10 compatibility
Source: "MicrosoftEdgeWebview2Setup.exe"; DestDir: "{tmp}"; Flags: ignoreversion deleteafterinstall; Check: IsWebView2RuntimeNeeded

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\app_icon.ico"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\app_icon.ico"; Tasks: desktopicon

[Run]
; Auto-install WebView2 Runtime on Windows 10 if missing
Filename: "{tmp}\MicrosoftEdgeWebview2Setup.exe"; Parameters: "/silent /install"; StatusMsg: "Configuring Microsoft Edge Chromium Engine..."; Flags: waituntilterminated; Check: IsWebView2RuntimeNeeded
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent

[Code]
// Check if Microsoft Edge WebView2 Evergreen Runtime is installed on the machine
function IsWebView2RuntimeNeeded(): Boolean;
var
  Version: string;
begin
  Result := True;
  if RegQueryStringValue(HKEY_LOCAL_MACHINE, 'SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}', 'pv', Version) or
     RegQueryStringValue(HKEY_LOCAL_MACHINE, 'SOFTWARE\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}', 'pv', Version) or
     RegQueryStringValue(HKEY_CURRENT_USER, 'SOFTWARE\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}', 'pv', Version) then
  begin
    if (Version <> '') and (Version <> '0.0.0.0') then
    begin
      Log('WebView2 Runtime detected: ' + Version);
      Result := False;
    end;
  end;
end;

// Zero-loss uninstallation handler: Prompts the user before touching %APPDATA%\ValveWorkshop
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  DataDir: string;
  UserChoice: Integer;
begin
  if CurUninstallStep = usUninstall then
  begin
    DataDir := ExpandConstant('{userappdata}\ValveWorkshop');
    if DirExists(DataDir) then
    begin
      UserChoice := MsgBox(
        'Do you wish to delete your database, valve media uploads, and backup snapshots located in:' + #13#10 +
        DataDir + '?' + #13#10#13#10 +
        '(Recommended: Click NO to preserve all your databases and backups for future use or re-installation.)',
        mbConfirmation, MB_YESNO or MB_DEFBUTTON2
      );

      if UserChoice = idYes then
      begin
        Log('User consented to removing data directory: ' + DataDir);
        DelTree(DataDir, True, True, True);
      end
      else
      begin
        Log('Preserving user database and backups in: ' + DataDir);
      end;
    end;
  end;
end;

