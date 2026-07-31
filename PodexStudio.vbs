' Podex Studio silent launcher (no console window)
' Used by .pdx file association and Start Menu shortcut
Option Explicit
Dim sh, fso, root, py, args, i, cmd
Set sh = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
root = fso.GetParentFolderName(WScript.ScriptFullName)

py = FindPythonw()
If py = "" Then
  MsgBox "Podex Studio: Python not found." & vbCrLf & _
         "Install Python 3 and enable Add to PATH.", vbCritical, "Podex Studio"
  WScript.Quit 1
End If

args = ""
For i = 0 To WScript.Arguments.Count - 1
  args = args & " """ & WScript.Arguments(i) & """"
Next

' Prefer bin\podexc on PATH for Studio builds
sh.Environment("PROCESS")("PATH") = root & "\bin;" & root & "\build;" & sh.Environment("PROCESS")("PATH")
sh.Environment("PROCESS")("PODEX_ROOT") = root

cmd = """" & py & """ """ & root & "\studio\app.py""" & args
sh.Run cmd, 0, False
WScript.Quit 0

Function FindPythonw()
  Dim c, p, outFile, ts, line
  FindPythonw = ""

  ' PATH
  On Error Resume Next
  Set c = sh.Exec("cmd /c where pythonw 2>nul")
  Do While c.Status = 0
    WScript.Sleep 50
  Loop
  line = Trim(c.StdOut.ReadLine)
  On Error GoTo 0
  If line <> "" And fso.FileExists(line) Then
    FindPythonw = line
    Exit Function
  End If

  ' Common paths
  Dim candidates
  candidates = Array( _
    sh.ExpandEnvironmentStrings("%LocalAppData%\Programs\Python\Python313\pythonw.exe"), _
    sh.ExpandEnvironmentStrings("%LocalAppData%\Programs\Python\Python312\pythonw.exe"), _
    sh.ExpandEnvironmentStrings("%LocalAppData%\Programs\Python\Python311\pythonw.exe"), _
    sh.ExpandEnvironmentStrings("%LocalAppData%\Programs\Python\Python310\pythonw.exe"), _
    "C:\Python311\pythonw.exe", _
    "C:\Python312\pythonw.exe" _
  )
  For Each p In candidates
    If fso.FileExists(p) Then
      FindPythonw = p
      Exit Function
    End If
  Next
End Function
