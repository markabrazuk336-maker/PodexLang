; PodexLang — Inno Setup 6 installer
; .pdx icons, context menu, PATH (podex / PodexCLI)

#define MyAppName      "PodexLang"
#define MyAppVersion   "0.2.4"
#define MyAppPublisher "Markazuk"
#define MyAppURL       "https://github.com/markabrazuk336-maker/PodexLang"

[Setup]
AppId={{A7C3E91F-2B4D-4F18-9E6A-7C1D8B2E4F60}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=..\LICENSE
OutputDir=..\dist
OutputBaseFilename=PodexLang-Setup-{#MyAppVersion}
SetupIconFile=icons\podex.ico
UninstallDisplayIcon={app}\icons\podex.ico
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ChangesAssociations=yes
ChangesEnvironment=yes
CloseApplications=force
RestartApplications=no
ArchitecturesInstallIn64BitMode=x64compatible
DisableProgramGroupPage=no
UsePreviousAppDir=yes
UsePreviousTasks=yes
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription=PodexLang compiler, PodexCLI and Podex Studio IDE
VersionInfoCopyright=Copyright (C) 2026 Markazuk
VersionInfoProductName={#MyAppName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkedonce
Name: "addpath"; Description: "Add PodexCLI (podex) to PATH for cmd / PowerShell"; GroupDescription: "Command line:"; Flags: checkedonce
Name: "fileassoc"; Description: "Associate .pdx files with Podex Studio (custom icon)"; GroupDescription: "File associations:"; Flags: checkedonce
Name: "contextmenu"; Description: "Add ""Open with Podex Studio"" to .pdx context menu"; GroupDescription: "File associations:"; Flags: checkedonce

[Files]
Source: "..\PodexStudio.vbs"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\PodexStudio.cmd"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\PodexStudio.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\podex.cmd"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\CMakeLists.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\compile.bat"; DestDir: "{app}"; Flags: ignoreversion

Source: "icons\podex.ico"; DestDir: "{app}\icons"; Flags: ignoreversion
Source: "icons\pdx.ico"; DestDir: "{app}\icons"; Flags: ignoreversion
Source: "icons\podex.png"; DestDir: "{app}\icons"; Flags: ignoreversion skipifsourcedoesntexist
Source: "icons\pdx.png"; DestDir: "{app}\icons"; Flags: ignoreversion skipifsourcedoesntexist

Source: "..\studio\*"; DestDir: "{app}\studio"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: "__pycache__\*,*.pyc"
Source: "..\compiler\*"; DestDir: "{app}\compiler"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\examples\*"; DestDir: "{app}\examples"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\stdlib\*"; DestDir: "{app}\stdlib"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\third_party\raylib\*"; DestDir: "{app}\third_party\raylib"; Flags: ignoreversion recursesubdirs createallsubdirs

; CLI + compiler on PATH
Source: "..\bin\podex.cmd"; DestDir: "{app}\bin"; Flags: ignoreversion
Source: "..\bin\PodexCLI.cmd"; DestDir: "{app}\bin"; Flags: ignoreversion
Source: "..\build\podexc.exe"; DestDir: "{app}\bin"; Flags: ignoreversion
Source: "..\build\podexc.exe"; DestDir: "{app}\build"; Flags: ignoreversion

[Icons]
Name: "{group}\Podex Studio"; Filename: "{sys}\wscript.exe"; Parameters: """{app}\PodexStudio.vbs"""; WorkingDir: "{app}"; IconFilename: "{app}\icons\podex.ico"; Comment: "PodexLang IDE"
Name: "{group}\PodexCLI Help"; Filename: "{cmd}"; Parameters: "/K ""{app}\bin\podex.cmd"" version"; WorkingDir: "{app}"; IconFilename: "{app}\icons\podex.ico"; Comment: "Show PodexCLI version"
Name: "{group}\Examples"; Filename: "{app}\examples"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
; Always refresh desktop shortcut on upgrade (points at current {app})
Name: "{autodesktop}\Podex Studio"; Filename: "{sys}\wscript.exe"; Parameters: """{app}\PodexStudio.vbs"""; WorkingDir: "{app}"; IconFilename: "{app}\icons\podex.ico"; Tasks: desktopicon

[Registry]
Root: HKCR; Subkey: "PodexLang.pdx"; ValueType: string; ValueName: ""; ValueData: "PodexLang Source File"; Flags: uninsdeletekey; Tasks: fileassoc
Root: HKCR; Subkey: "PodexLang.pdx\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\icons\pdx.ico,0"; Tasks: fileassoc
Root: HKCR; Subkey: "PodexLang.pdx\shell"; ValueType: string; ValueName: ""; ValueData: "open"; Tasks: fileassoc
Root: HKCR; Subkey: "PodexLang.pdx\shell\open"; ValueType: string; ValueName: ""; ValueData: "Open with Podex Studio"; Tasks: fileassoc
Root: HKCR; Subkey: "PodexLang.pdx\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{sys}\wscript.exe"" ""{app}\PodexStudio.vbs"" ""%1"""; Tasks: fileassoc

Root: HKCR; Subkey: ".pdx"; ValueType: string; ValueName: ""; ValueData: "PodexLang.pdx"; Flags: uninsdeletevalue; Tasks: fileassoc
Root: HKCR; Subkey: ".pdx\OpenWithProgids"; ValueType: string; ValueName: "PodexLang.pdx"; ValueData: ""; Flags: uninsdeletevalue; Tasks: fileassoc
Root: HKCR; Subkey: ".pdx\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\icons\pdx.ico,0"; Tasks: fileassoc

Root: HKCR; Subkey: "PodexLang.pdx\shell\PodexStudio"; ValueType: string; ValueName: ""; ValueData: "Edit with Podex Studio"; Flags: uninsdeletekey; Tasks: contextmenu
Root: HKCR; Subkey: "PodexLang.pdx\shell\PodexStudio\command"; ValueType: string; ValueName: ""; ValueData: """{sys}\wscript.exe"" ""{app}\PodexStudio.vbs"" ""%1"""; Tasks: contextmenu
Root: HKCR; Subkey: "SystemFileAssociations\.pdx\shell\PodexStudio"; ValueType: string; ValueName: ""; ValueData: "Open with Podex Studio"; Flags: uninsdeletekey; Tasks: contextmenu
Root: HKCR; Subkey: "SystemFileAssociations\.pdx\shell\PodexStudio\command"; ValueType: string; ValueName: ""; ValueData: """{sys}\wscript.exe"" ""{app}\PodexStudio.vbs"" ""%1"""; Tasks: contextmenu

Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\App Paths\podex.exe"; ValueType: string; ValueName: ""; ValueData: "{app}\bin\podex.cmd"; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\App Paths\podex.exe"; ValueType: string; ValueName: "Path"; ValueData: "{app}\bin"
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\App Paths\PodexCLI.exe"; ValueType: string; ValueName: ""; ValueData: "{app}\bin\PodexCLI.cmd"; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\App Paths\PodexStudio.exe"; ValueType: string; ValueName: ""; ValueData: "{app}\PodexStudio.vbs"; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\App Paths\PodexStudio.exe"; ValueType: string; ValueName: "Path"; ValueData: "{app}\bin;{app}"
Root: HKLM; Subkey: "Software\PodexLang"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\PodexLang"; ValueType: string; ValueName: "Version"; ValueData: "{#MyAppVersion}"

[Run]
Filename: "{sys}\wscript.exe"; Parameters: """{app}\PodexStudio.vbs"""; Description: "Launch Podex Studio"; Flags: nowait postinstall skipifsilent
Filename: "{sys}\ie4uinit.exe"; Parameters: "-show"; Flags: runhidden skipifdoesntexist; Tasks: fileassoc

[Code]
const
  EnvironmentKey = 'SYSTEM\CurrentControlSet\Control\Session Manager\Environment';

function NeedsAddPath(Param: string): Boolean;
var
  OrigPath: String;
begin
  if not RegQueryStringValue(HKEY_LOCAL_MACHINE, EnvironmentKey, 'Path', OrigPath) then
  begin
    Result := True;
    exit;
  end;
  { Look for exact path segment (case-insensitive) }
  Result := Pos(';' + UpperCase(Param) + ';', ';' + UpperCase(OrigPath) + ';') = 0;
end;

procedure EnvAddPath(Path: string);
var
  OrigPath: String;
begin
  if not NeedsAddPath(Path) then
    exit;
  if not RegQueryStringValue(HKEY_LOCAL_MACHINE, EnvironmentKey, 'Path', OrigPath) then
    OrigPath := '';
  if OrigPath <> '' then
    Path := OrigPath + ';' + Path;
  RegWriteExpandStringValue(HKEY_LOCAL_MACHINE, EnvironmentKey, 'Path', Path);
end;

procedure EnvRemovePath(Path: string);
var
  OrigPath, UpperPath, P: String;
  Index: Integer;
begin
  if not RegQueryStringValue(HKEY_LOCAL_MACHINE, EnvironmentKey, 'Path', OrigPath) then
    exit;
  UpperPath := ';' + UpperCase(OrigPath) + ';';
  P := ';' + UpperCase(Path) + ';';
  Index := Pos(P, UpperPath);
  if Index = 0 then
    exit;
  Delete(OrigPath, Index, Length(Path) + 1);
  { Clean double semicolons / edges }
  while Pos(';;', OrigPath) > 0 do
    StringChangeEx(OrigPath, ';;', ';', True);
  if (Length(OrigPath) > 0) and (OrigPath[1] = ';') then
    Delete(OrigPath, 1, 1);
  if (Length(OrigPath) > 0) and (OrigPath[Length(OrigPath)] = ';') then
    Delete(OrigPath, Length(OrigPath), 1);
  RegWriteExpandStringValue(HKEY_LOCAL_MACHINE, EnvironmentKey, 'Path', OrigPath);
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if (CurStep = ssPostInstall) and WizardIsTaskSelected('addpath') then
    EnvAddPath(ExpandConstant('{app}\bin'));
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usPostUninstall then
    EnvRemovePath(ExpandConstant('{app}\bin'));
end;
