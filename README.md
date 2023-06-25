# avred-server

Provides an HTTP interface to scan files with the installed AntiVirus software on Windows via AMSI. 


## Details 

To be used with the AV Reduction (avred) project. Exposes a port, which accepts a (virus) file and runs an AV against it. 

Returns ```{"detected": true}``` if file was detected by AV, or ```{"detected": false}``` if it wasn't. 


## Setup

0. Create a Windows VM and install the AV of your choosing (or use pre-installed Defender)
1. install python3, pip3
2. `pip -r requirements.txt`
3. Disable sample submission on your AV
4. Browser to `localhost:8001/test` to check if it works

Note: If you get a `ImportError: DLL load failed while importing _brotli", see 
https://github.com/google/brotli/issues/782, solution is: 

install "vc_redist.x64.exe" from this link https://support.microsoft.com/en-gb/help/2977003/the-latest-supported-visual-c-downloads
