; PodexLang — Inno Setup 6 installer
; Builds Setup-PodexLang-x.x.x.exe with .pdx icons + context menu

#define MyAppName      "PodexLang"
#define MyAppVersion   "0.2.2"
#define MyAppPublisher "Markazuk"
#define MyAppURL       "https://github.com/markabrazuk336-maker/PodexLang"
#define MyAppExeName   "PodexStudio.vbs"

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
InfoBeforeFile=
OutputDir=..\dist
OutputBaseFilename=PodexLang-Setup-{#MyAppVersion}
SetupIconFile=icons\podex.ico
UninstallDisplayIcon={app}\icons\podex.ico
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ChangesAssociations=yes
ArchitecturesInstallIn64BitMode=x64compatible
DisableProgramGroupPage=no
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription=PodexLang compiler and Podex Studio IDE
VersionInfoCopyright=Copyright (C) 2026 Markazuk
VersionInfoProductName={#MyAppName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "fileassoc"; Description: "Associate .pdx files with Podex Studio (custom icon)"; GroupDescription: "File associations:"; Flags: checkedonce
Name: "contextmenu"; Description: "Add ""Open with Podex Studio"" to .pdx context menu"; GroupDescription: "File associations:"; Flags: checkedonce

[Files]
; Launcher
Source: "..\PodexStudio.vbs"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\PodexStudio.cmd"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\PodexStudio.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\CMakeLists.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\compile.bat"; DestDir: "{app}"; Flags: ignoreversion

; Icons
Source: "icons\podex.ico"; DestDir: "{app}\icons"; Flags: ignoreversion
Source: "icons\pdx.ico"; DestDir: "{app}\icons"; Flags: ignoreversion
Source: "icons\podex.png"; DestDir: "{app}\icons"; Flags: ignoreversion skipifsourcedoesntexist
Source: "icons\pdx.png"; DestDir: "{app}\icons"; Flags: ignoreversion skipifsourcedoesntexist

; Studio (Python IDE)
Source: "..\studio\*"; DestDir: "{app}\studio"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: "__pycache__\*,*.pyc"
; Compiler sources + stdlib + examples
Source: "..\compiler\*"; DestDir: "{app}\compiler"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\stdlib\*"; DestDir: "{app}\stdlib"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\examples\*"; DestDir: "{app}\examples"; Flags: ignoreversion recursesubdirs createallsubdirs

; Prebuilt compiler binary
Source: "..\build\podexc.exe"; DestDir: "{app}\bin"; Flags: ignoreversion
Source: "..\build\podexc.exe"; DestDir: "{app}\build"; Flags: ignoreversion

[Icons]
Name: "{group}\Podex Studio"; Filename: "{sys}\wscript.exe"; Parameters: """{app}\PodexStudio.vbs"""; WorkingDir: "{app}"; IconFilename: "{app}\icons\podex.ico"; Comment: "PodexLang IDE"
Name: "{group}\Examples"; Filename: "{app}\examples"; Comment: "PodexLang example programs"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Podex Studio"; Filename: "{sys}\wscript.exe"; Parameters: """{app}\PodexStudio.vbs"""; WorkingDir: "{app}"; IconFilename: "{app}\icons\podex.ico"; Tasks: desktopicon

[Registry]
; ---- ProgID + default icon for .pdx ----
Root: HKCR; Subkey: "PodexLang.pdx"; ValueType: string; ValueName: ""; ValueData: "PodexLang Source File"; Flags: uninsdeletekey; Tasks: fileassoc
Root: HKCR; Subkey: "PodexLang.pdx\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\icons\pdx.ico,0"; Tasks: fileassoc
Root: HKCR; Subkey: "PodexLang.pdx\shell"; ValueType: string; ValueName: ""; ValueData: "open"; Tasks: fileassoc
Root: HKCR; Subkey: "PodexLang.pdx\shell\open"; ValueType: string; ValueName: ""; ValueData: "Open with Podex Studio"; Tasks: fileassoc
Root: HKCR; Subkey: "PodexLang.pdx\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{sys}\wscript.exe"" ""{app}\PodexStudio.vbs"" ""%1"""; Tasks: fileassoc

; Extension -> ProgID
Root: HKCR; Subkey: ".pdx"; ValueType: string; ValueName: ""; ValueData: "PodexLang.pdx"; Flags: uninsdeletevalue; Tasks: fileassoc
Root: HKCR; Subkey: ".pdx\OpenWithProgids"; ValueType: string; ValueName: "PodexLang.pdx"; ValueData: ""; Flags: uninsdeletevalue; Tasks: fileassoc
Root: HKCR; Subkey: ".pdx\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\icons\pdx.ico,0"; Tasks: fileassoc

; Explicit context-menu verb (ПКМ)
Root: HKCR; Subkey: "PodexLang.pdx\shell\PodexStudio"; ValueType: string; ValueName: ""; ValueData: "Edit with Podex Studio"; Flags: uninsdeletekey; Tasks: contextmenu
Root: HKCR; Subkey: "PodexLang.pdx\shell\PodexStudio\command"; ValueType: string; ValueName: ""; ValueData: """{sys}\wscript.exe"" ""{app}\PodexStudio.vbs"" ""%1"""; Tasks: contextmenu

; Also register under SystemFileAssociations for stubborn Explorer caches
Root: HKCR; Subkey: "SystemFileAssociations\.pdx\shell\PodexStudio"; ValueType: string; ValueName: ""; ValueData: "Open with Podex Studio"; Flags: uninsdeletekey; Tasks: contextmenu
Root: HKCR; Subkey: "SystemFileAssociations\.pdx\shell\PodexStudio\command"; ValueType: string; ValueName: ""; ValueData: """{sys}\wscript.exe"" ""{app}\PodexStudio.vbs"" ""%1"""; Tasks: contextmenu

; App Paths (optional helpers)
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\App Paths\PodexStudio.exe"; ValueType: string; ValueName: ""; ValueData: "{app}\PodexStudio.vbs"; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\App Paths\PodexStudio.exe"; ValueType: string; ValueName: "Path"; ValueData: "{app}\bin;{app}"
Root: HKLM; Subkey: "Software\PodexLang"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\PodexLang"; ValueType: string; ValueName: "Version"; ValueData: "{#MyAppVersion}"

[Run]
Filename: "{sys}\wscript.exe"; Parameters: """{app}\PodexStudio.vbs"" ""{app}\examples\hello.pdx"""; Description: "Launch Podex Studio"; Flags: nowait postinstall skipifsilent
Filename: "{sys}\ie4uinit.exe"; Parameters: "-show"; Flags: runhidden skipifdoesntexist; Tasks: fileassoc
