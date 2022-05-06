#import argparse
from flask import Flask, request, jsonify
from json import load
from os.path import isfile, join
from os import remove
from random import choice
from time import sleep, time
from string import ascii_letters
from subprocess import PIPE, DEVNULL, run, TimeoutExpired
from sys import platform


app = Flask(__name__)
cmd_file_placeholder = "VIRUS_FILE"
virus_file_initial_name = "test.exe"
conf = {}


@app.route("/")
def index():
	return jsonify({
		"msg": f"AV Server {conf['engine']} is up.",
		"api": {
			"GET /": "this screen",
			"GET /test": "test if config works",
			"POST /scan": "scan a file, body=virus_bytes"
		}
	})


@app.route("/scan", methods=["POST"])
def scan_route():
	contents = request.get_data()
	try:
		return jsonify({
			"detected": scan(contents, conf)
		})
	except BaseException as e: # handle exceptions at client side too!
		return jsonify({
			"exception": str(e)
		}), 500


@app.route("/test")
def test_server(conf=conf):
	"""
	Tests if config is working correctly, returns 500 otherwise
	"""
	virus = b"X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"
	
	try:
		log("Test malicous...")
		mal_det = scan(virus, conf)
		log("Test benign...")
		benign_det = scan(b"Not malicous", conf)

	except BaseException as e:
		log("Tests failed, please check config and log above.")
		return jsonify({
			"exception": str(e)
		}), 500

	if not mal_det or benign_det:
		log("Tests failed, malicous should be detected, and benign not detected.")
		log("Please check your config and the log above.")
		return jsonify({
			"malicous detected": mal_det, 
			"benign detected": benign_det,
			"msg": "bugs, check your server log"
		}), 500

	return jsonify({
		"malicous detected": mal_det, 
		"benign detected": benign_det,
		"msg": "working as intended"
	})


def scan(contents, conf):
	# do timeout test if non-cli AV
	if conf["cmd"] in ["", []]:
		log("ScanType: Timeout")
		return scan_timeout(contents, conf)
	else:
		log("ScanType: CMD")
		return scan_cmd(contents, conf)


def save_file(data, conf):
	try:
		log("Writing data to file...")
		with open(conf["virus_file"], "wb") as f:
			f.write(data)
		return True
	except BaseException as e:
		log(f"Could not save virus file! Exception: {str(e)}")
		return False


def delete_file(conf):
	"""
	Delete virus file, or change to new file name if unable to delete.
	"""
	try:
		remove(conf["virus_file"])
	except BaseException:
		change_virus_file_name(conf)
		log("Could not delete virus file, it's probably held by some process.")
		log(f"New virus file name: {conf['virus_file']}")


def scan_cmd(contents, conf):
	"""
	Stores a file and actively scans it with AV.
	"""
	if not save_file(contents, conf):
		err = "Virus file could not be safed!"
		log(err)
		raise Exception(err)

	# call AV, admin rights required with Sophos
	log("Scanning file...")
	try:
		stdout = run(
			conf["parsed_cmd"],
			check=False,
			stdin=DEVNULL, # do not wait for user input
			stdout=PIPE,
			timeout=conf["av_timeout"]
		).stdout
	except TimeoutExpired:
		err = "Did not finish scan within timeout window!"
		log(err)
		raise Exception(err)

	log("Scan Result: " + str(stdout))

	# AV detected and removed the file, add AV exception for path
	if not isfile(conf["virus_file"]):
		err = f"File was removed before or at scan time! Add {conf['virus_dir']} to AV whitelist."
		log(err)
		raise Exception(err)

	delete_file(conf)
	if conf["virus_detected"].encode() in stdout:
		log("Virus detected with Scan")
		return True
	else:
		log("No Virus detected with Scan")
		return False


def scan_timeout(contents, conf):
	"""
	Stores a file, waits some time, and then checks if file was removed by AV.
	"""
	save_file(contents, conf)
	log("Starting timeout...")
	sleep(conf["av_timeout"])

	if not isfile(conf["virus_file"]):
		log("Virus detected with Timeout")
		return True
	else:
		delete_file(conf)
		log("No Virus detected with Timeout")
		return False


def update_virus_file_path(conf, new_name):
	# adapt virus file name
	conf["virus_file"] = join(conf["virus_dir"], new_name)

	# replaces file placeholder in cmd list and returns runnable command
	conf["parsed_cmd"] = list(map(
		lambda x: conf["virus_file"] if x == cmd_file_placeholder else x,
		conf["cmd"]
	))


def check_is_path_writable(virus_path):
	dummy_path = join(virus_path, "test_path_writable.txt")
	try:
		with open(dummy_path, "w"):
			pass
		with open(dummy_path, "r"):
			pass
		remove(dummy_path)
		return True
	except IOError as e:
		log(f"Path {virus_path} must be writable and readable! Exception: {str(e)}")
		log("May need to clean up test file manually.")
		return False
	except BaseException:
		log(f"Unknown exception when testing {virus_path}! Exception: {str(e)}")
		log("May need to clean up test file manually.")
		return False


def load_config(conf):
	with open("config.json") as f:
		data = load(f)

	# load general config
	for k, v in data.items():
		conf[k] = v

	# load & adapt paths
	update_virus_file_path(conf, virus_file_initial_name)

	if not check_is_path_writable(conf["virus_dir"]):
		raise Exception("Virus Dir is non writable, use different path or make it writable")


def change_virus_file_name(conf):
	name, ext = virus_file_initial_name.rsplit(".", 1)
	rand = "".join([choice(ascii_letters) for _ in range(5)])
	new_name = f"{name}-{rand}.{ext}"
	update_virus_file_path(conf, new_name)


def check_admin():
	is_admin = False

	if platform in ["linux", "darwin"]:
		from os import getuid
		is_admin = getuid() == 0

	elif platform == "win32":
		from ctypes import windll
		is_admin = windll.shell32.IsUserAnAdmin()
	
	return is_admin


#TODO, make log beautifuller
def log(s):
	print(s)


def run_server(conf):
	if check_admin():
		log("AV server started as Admin")
	else:
		log("AV server started as User")
	
	load_config(conf)
	log("Config loaded:\n" + str(conf))

	app.run(conf["bind_ip"], conf["port"])


if __name__ == "__main__":
	run_server(conf)
