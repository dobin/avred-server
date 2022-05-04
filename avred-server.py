from flask import Flask, request
from hashlib import sha256
from time import sleep
from subprocess import PIPE, DEVNULL
import subprocess

app = Flask(__name__)
detected = "Yay"
undetected = "Nay"


@app.route("/")
def index():
	return "Server is Up.\n"


@app.route("/scan", methods=["POST"])
def scan():
	method = request.args.get("method")
	to_scan = request.get_data()

	if method == "run":
		return run_scanner(to_scan)
	if method == "store":
		return store_file(to_scan)
	return "Unsupported method!\n", 400


# TODO
def run_scanner(to_scan):
	# write file
	# need to be excluded from AV?
	print("Writing file")
	f = open("c:\\temp\\test.exe", "wb")
	f.write(to_scan)
	f.close()

	# call sophos. Required admin!
	# output:
	# >>> Virus 'EICAR-AV-Test' found in file c:\Temp\eicar.com
	print("Scanning file")
	stdout = subprocess.run(
		['C:\\Program Files (x86)\\Sophos\\Sophos Anti-Virus\\sav32cli.exe', '-ss', 'c:\\temp\\test.exe'],
		check=False,
		stdin=DEVNULL, # do not wait for user input
		stdout=PIPE).stdout
	print("Result: " + str(stdout))
	if b'found in file' in stdout:
		print ("Detected")
		return detected
	else:
		print("Not detected")
		return undetected


# TODO
def store_file(to_scan):
	sleep(5)
	if False:
		return detected + ":threat-name"
	return undetected


if __name__ == "__main__":
	app.run("10.10.10.107", 9001)