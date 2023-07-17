#!/usr/bin/env python3
import argparse
import logging
import logging
from flask import Flask, request, jsonify
from json import load
import brotli

from amsiscan import AMSIScanner


app = Flask(__name__)
conf = {}
EICAR = b"X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"


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
	
	if request.args.get('brotli', "False") == "True":
		contents = brotli.decompress(contents)

	if 'filename' in request.args:
		filename = request.args['filename']

	try:
		return jsonify({
			"detected": scan(contents)
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
	
	try:
		logging.info("Test malicous...")
		mal_det = scan(EICAR)
		logging.info("Test benign...")
		benign_det = scan(b"Not malicous")

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


def run_server(conf):
	load_config(conf)
	app.run(conf["bind_ip"], conf["port"])


def scan(contents):
	with AMSIScanner() as amsiScanner:
		res = amsiScanner.scan(contents)

		r = str(res)
		if 'AMSI_RESULT_DETECTED' in r or 'AMSI_RESULT_BLOCKED' in r:
			return True
		elif 'AMSI_RESULT_CLEAN' in r or 'AMSI_RESULT_NOT_DETECTED' in r:
			return False
		else:
			raise Exception("Scanner error: {}".format(r))


if __name__ == "__main__":
	run_server(conf)
