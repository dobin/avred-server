# AV Reduction Server

## Use Case
To be used with the AV Reduction (avred) project. Exposes a port, which accepts a (virus) file and runs an AV against it. Returns ```{"detected": true}``` if file was detected by AV, or ```{"detected": false}``` if it wasn't. The avred adapts the file until it's no longer detected by the AV engine.


## Setup
0. Create a (Windows) VM and install the AV of your choosing (or use pre-installed Defender)
1. install python3,  pip3 and flask 
	- Linux: ```sudo apt install python3 python3-pip && pip3 install flask```
	- Windows: download python from https://www.python.org/downloads/, include pip in installation, then open powershell: ```pip install flask```
2. check config.json
3. put the "virus_dir" (default `c:\temp\`) on the AV exclusion list
4. Browser to `localhost:8001/test` to check if it works


#### Active Scanning, i.e. CLI Scanning
The cmd should point to your AV executable, the virus file name and handling should work automagically. The virus_dir should be whitelisted in your AV (except when for timebase / passive scanning).
Examples for active scanning for different AV's and their CLI command:

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


#### Passive Scanning, i.e. Timeout Scanning
This is a backup solution, if your AV does not support CLI scanning, or you run into other problems. Active Scanning should be preferred! To activate passive scanning, set the cmd to "" or [] and adapt the timeout if the /test is not passing.



## Disclaimer
For research, pentesting and red teaming purposes only.
