Const MinimizeWindow = 7

Set objArgs = WScript.Arguments
Set objShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
Dim jlinks()

' Read jlink path from registry
jlink_path = objShell.RegRead("HKCU\Software\SEGGER\J-Link\InstallPath") + "JLink.exe"

sdk_root = fso.GetAbsolutePathName(fso.GetParentFolderName(WScript.ScriptFullName) + "\..\..\..") + "\"

' Add quotes in case of spaces in path
if InStr(jlink_path, " ") then
  jlink_path = """" + jlink_path + """"
end if

' Id not passed find any connected JLink
if objArgs.length >= 1 then
    Do While i < objArgs.Count
      Select Case objArgs(i)
        Case "--jlink_path"
          jlink_path = """" + objArgs(i + 1) + "\JLink.exe" + """"
          i = i + 2
        Case Else
          id = objArgs(i)
          i = i + 1
      End Select
    Loop
End If

if IsEmpty(id) then
  ' Ask JLink about connected debuggers
  'J-Link[0]: Connection: USB, Serial number: 480065842, ProductName: J-Link-OB-SAM3U128
  'J-Link[1]: Connection: USB, Serial number: 483000272, ProductName: J-Link-OB-SAM3U128
  set resn = new regexp
  set resn2 = new regexp
  ' pattern to search for is Serial number
  resn.Pattern = "Serial number: *\d*"
  resn2.Pattern = "Serial number: *"

  'use existing script to list all debuggers
  cmd = jlink_path + " -CommandFile " + """" + sdk_root + "utilities\scripts\qspi\jlink_showemulist.script" + """"

  num = 0
  set result = objShell.exec(cmd)
  Do While result.stdOut.AtEndOfStream <> True
    line = result.StdOut.ReadLine()
    'if line contais Serial number patter, get it
    If resn.execute(line).count > 0 Then
      ReDim preserve jlinks(num + 1)
      id = resn2.Replace(resn.execute(line).Item(0), "")
      jlinks(num) = id
      num = num + 1
    end if
  Loop
End If

Dim name

cmd = jlink_path + " -if SWD -device Cortex-M0 -speed auto -SelectEmuBySN " + id + " -CommandFile " + """" + sdk_root + "utilities\scripts\qspi\reboot.script" + """"
objShell.run cmd, MinimizeWindow
