#import argparse
import logging

from flask import Flask, request, jsonify
from json import load
from sys import platform
from scanner import scan
from os import remove
from os.path import join


app = Flask(__name__)
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
		logging.info("Test malicous...")
		mal_det = scan(virus, conf)
		logging.info("Test benign...")
		benign_det = scan(b"Not malicous", conf)

	except BaseException as e:
		logging.info("Tests failed, please check config and log above.")
		return jsonify({
			"exception": str(e)
		}), 500

	if not mal_det or benign_det:
		logging.info("Tests failed, malicous should be detected, and benign not detected.")
		logging.info("Please check your config and the log above.")
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



def load_config(conf):
	with open("config.json") as f:
		data = load(f)

	# load general config
	for k, v in data.items():
		conf[k] = v


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
		logging.info(f"Path {virus_path} must be writable and readable! Exception: {str(e)}")
		logging.info("May need to clean up test file manually.")
		return False
	except BaseException:
		logging.info(f"Unknown exception when testing {virus_path}! Exception: {str(e)}")
		logging.info("May need to clean up test file manually.")
		return False


def check_admin():
	is_admin = False

	if platform in ["linux", "darwin"]:
		from os import getuid
		is_admin = getuid() == 0

	elif platform == "win32":
		from ctypes import windll
		is_admin = windll.shell32.IsUserAnAdmin()
	
	return is_admin


def run_server(conf):
	if check_admin():
		logging.info("AV server started as Admin")
	else:
		logging.info("AV server started as User")
	
	load_config(conf)
	if not check_is_path_writable(conf["virus_dir"]):
		raise Exception("Virus Dir is non writable, use different path or make it writable")

	app.run(conf["bind_ip"], conf["port"])


if __name__ == "__main__":
	run_server(conf)
