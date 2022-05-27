import logging
from time import sleep, time
from os.path import isfile, join
from os import remove
from subprocess import PIPE, DEVNULL, run, TimeoutExpired
from random import choice
from string import ascii_letters

cmd_file_placeholder = "VIRUS_FILE"


def scan(contents, conf):
	# do timeout test if non-cli AV
	if conf["cmd"] in ["", []]:
		return scan_timeout(contents, conf)
	else:
		return scan_cmd(contents, conf)


def save_file(data, filename):
	try:
		logging.info(f"Writing data to file: {filename}")
		with open(filename, "wb") as f:
			f.write(data)
		return True
	except BaseException as e:
		logging.info(f"Could not save virus file! Exception: {str(e)}")
		return False


def delete_file(filename):
	try:
		remove(filename)
	except BaseException:
		logging.info("Could not delete virus file, it's probably held by some process.")


def scan_cmd(contents, conf):
	filename = join(conf["virus_dir"], getRandomFilename())
	if not save_file(contents, filename):
		err = "Virus file could not be saved!"
		logging.info(err)
		raise Exception(err)

	logging.info(f"Scanning file: {filename}")
	try:
		cmd = list(map(lambda x: x.replace(cmd_file_placeholder, filename), conf["cmd"]))
		stdout = run(
			cmd,
			check=False,
			stdin=DEVNULL, # do not wait for user input
			stdout=PIPE,
			timeout=conf["av_timeout"]
		).stdout
	except TimeoutExpired:
		err = "Did not finish scan within timeout window!"
		logging.info(err)
		raise Exception(err)

	logging.info("Scan Result: " + str(stdout))

	# AV detected and removed the file, add AV exception for path
	if not isfile(filename):
		err = f"File was removed before or at scan time! Add {conf['virus_dir']} to AV whitelist."
		logging.info(err)
		raise Exception(err)

	delete_file(filename)
	if conf["virus_detected"].encode() in stdout:
		logging.info("Virus detected with Scan")
		return True
	else:
		logging.info("No Virus detected with Scan")
		return False


def scan_timeout(contents, conf):
	save_file(contents, conf)
	logging.info("Starting timeout...")
	sleep(conf["av_timeout"])

	if not isfile(conf["virus_file"]):
		logging.info("Virus detected with Timeout")
		return True
	else:
		delete_file(conf)
		logging.info("No Virus detected with Timeout")
		return False


def getRandomFilename(origFilename="test.exe"):
	name, ext = origFilename.rsplit(".", 1)
	rand = "".join([choice(ascii_letters) for _ in range(5)])
	new_name = f"{name}-{rand}.{ext}"
	return new_name
