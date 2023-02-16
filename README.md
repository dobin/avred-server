# avred - Server

Provides an HTTP interface to scan files with the installed AntiVirus software on Windows. 


## Details 

To be used with the AV Reduction (avred) project. Exposes a port, which accepts a (virus) file and runs an AV against it. 

Returns ```{"detected": true}``` if file was detected by AV, or ```{"detected": false}``` if it wasn't. 


## Setup

0. Create a (Windows) VM and install the AV of your choosing (or use pre-installed Defender)
1. install python3,  pip3 and flask 
	- Linux: ```sudo apt install python3 python3-pip && pip3 install flask```
	- Windows: download python from https://www.python.org/downloads/, include pip in installation, then open powershell: ```pip install flask```
2. check config.json
3. put the "virus_dir" (default `c:\temp\`) on the AV exclusion list
4. Disable sample submission on your AV
4. Browser to `localhost:8001/test` to check if it works


## Passive Scanning

If you have a solution which is not attached via AMSI, but will still delete the file upon detecting malware, use passive scanning by setting: 
```
"cmd" = [],
"av_timeout": 30,
```

This will be very slow. 
