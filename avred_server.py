#import argparse
from flask import Flask, request
from json import load
from os.path import isfile, join
from os import remove
from random import choice
from time import sleep
from string import ascii_letters
from subprocess import PIPE, DEVNULL, run
from sys import platform


app = Flask(__name__)
detected = "Yay"
undetected = "Nay"
cmd_file_placeholder = "VIRUS_FILE"


@app.route("/")
def index():
	return f"AV Server {app.config['engine']} is up.\n"


@app.route("/scan", methods=["POST"])
def scan():
	contents = request.get_data()

	# do timeout test if non-cli AV or run as non admin
	if app.config["cmd"] in ["", []] or not app.config["is_admin"]:
		log("ScanType: Timeout")
		return scan_timeout(contents)
	else:
		log("ScanType: CMD")
		return scan_cmd(contents)


# TODO, start timer, abort and alert after given time (AV might block write)
def save_file(data):
	log("Writing data to file...")
	with open(app.config["virus_file"], "wb") as f:
		f.write(data)


def delete_file():
	"""
	Delete virus file, or change to new file name if unable to delete.
	"""
	try:
		remove(app.config["virus_file"])
	except BaseException:
		change_virus_file_path()


def scan_cmd(contents):
	"""
	Stores file and actively scans it with AV.
	"""
	save_file(contents)

	# call sophos. Required admin!
	# sample output:
	# >>> Virus 'EICAR-AV-Test' found in file c:\Temp\eicar.com
	log("Scanning file...")
	stdout = run(
		app.config["parsed_cmd"],
		check=False,
		stdin=DEVNULL, # do not wait for user input
		stdout=PIPE).stdout
	log("Scan Result: " + str(stdout))

	delete_file()
	if b'found in file' in stdout:
		log("Detected with Scan")
		return detected
	else:
		log("Not detected with Scan")
		return undetected


def scan_timeout(contents):
	"""
	Stores file, waits some time, and then checks if file was removed by AV.
	"""
	save_file(contents)
	print("Starting timeout...")
	sleep(app.config["av_timeout"])

	if not isfile(app.config["virus_file"]):
		log("Detected with Timeout")
		return detected
	else:
		delete_file()
		log("Not detected with Timeout")
		return undetected


def build_cmd():
	"""
	Replaces file placeholder in cmd list and returns runnable command.
	"""
	return list(map(
		lambda x: app.config["virus_file"] if x == cmd_file_placeholder else x,
		app.config["cmd"]
	))


def load_config():
	with open("config.json") as f:
		data = load(f)
	
	# load config for given AV engine
	#for k, v in data["engines"][av_type].items():
	#	app.config[k] = v

	# load general config
	for k, v in data.items():
		#if k == "engines": continue
		app.config[k] = v

	app.config["virus_file"] = join(app.config["virus_dir"], "test.exe")
	app.config["parsed_cmd"] = build_cmd()


def change_virus_file_path():
	rand = "".join([choice(ascii_letters) for _ in range(5)])
	name = "test-" + rand + ".exe"
	app.config["virus_file"] = name
	app.config["parsed_cmd"] = build_cmd()


def check_admin():
	is_admin = False

	if platform == "linux":
		from os import getuid
		is_admin = getuid() == 0

	elif platform == "win32":
		from ctypes import windll
		is_admin = windll.shell32.IsUserAnAdmin()
	
	return is_admin


#TODO, make log beautifuller
def log(s):
	print(s)


def run_server():
	if not check_admin():
		log("Not an Admin, cannot actively scan with AV")
		app.config["is_admin"] = False
	load_config()
	log("Config loaded:\n" + str(app.config))

	app.run(app.config["bind_ip"], app.config["port"])


if __name__ == "__main__":
	#parser = argparse.ArgumentParser()
	#parser.add_argument("-a", "--av-type", choices=["Sophos", "Defender"], help="Choose an AV Engine to run the file agains.", default="Sophos")
	#args = parser.parse_args()

	run_server()
