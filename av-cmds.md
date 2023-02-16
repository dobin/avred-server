# AV CMDs

If you dont wanna use `amsi.exe`:

 - Sophos
   - "cmd" = [ "C:\\Program Files (x86)\\Sophos\\Sophos Anti-Virus\\sav32cli.exe", "-ss", "VIRUS_FILE" ]
    - "virus_detected" = "found in file"

 - Defender
   - "cmd" = [ "%ProgramFiles%\\Windows Defender\\MpCmdRun.exe", "-Scan", "-ScanType", "3", "-File", "VIRUS_FILE"]
   - "virus_detected" = "TODO"

 - Kaspersky
   - "cmd" = [ "C:\\Program Files (x86)\\Kaspersky Lab\\Kaspersky Endpoint Security for Windows\\avp.com", "--scan-file", "VIRUS_FILE" ]
   - "virus_detected" = "TODO"

 - Avast
   - "cmd" = [ "%ProgramFiles%"\\AVAST Software\\Avast\\ashCmd.exe", "VIRUS_FILE" ]
   - "virus_detected" = "TODO"