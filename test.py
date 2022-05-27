from avred_server import *


virus = b"X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"


def test_load_config():
	print("** TEST LOAD CONFIG...")
	conf = {}
	load_config(conf)

	# assert that conf["virus_file"] is the whole path 
	assert conf["virus_file"] == join(conf["virus_dir"], virus_file_initial_name)

	# assert that conf["cmd"] was not overwritten
	assert not any(virus_file_initial_name in s for s in conf["cmd"])
	assert cmd_file_placeholder in conf["cmd"]
	assert not any(conf["virus_dir"] in s for s in conf["cmd"])

	# assert that conf["parsed_cmd"] was correctly created
	assert any(virus_file_initial_name in s for s in conf["parsed_cmd"])
	assert cmd_file_placeholder not in conf["parsed_cmd"]
	assert any(conf["virus_dir"] in s for s in conf["parsed_cmd"])

	print("** TEST LOAD CONFIG passed")


def test_update_virus_file_name():
	print("** TEST UPDATE VIRUS FILE NAME...")
	conf = {}
	load_config(conf)

	change_virus_file_name(conf)
	path, name = conf["virus_file"].rsplit("\\", 1)

	# assert that path stayed same, but name changed
	assert path + "\\" == conf["virus_dir"]
	assert name != virus_file_initial_name

	print("** TEST UPDATE VIRUS FILE NAME passed")


def test_scan_cmd():
	print("** TEST SCAN CMD...")
	conf = {}
	load_config(conf)
	assert scan_cmd(virus, conf)
	assert not scan_cmd(b"Not malicous", conf)
	print("** TEST SCAN CMD passed")


def test_scan_timeout():
	print("** TEST SCAN TIMEOUT...")
	conf = {}
	load_config(conf)
	assert scan_timeout(virus, conf)
	assert not scan_timeout(b"Not malicous", conf)
	print("** TEST SCAN TIMEOUT passed")


def test_test_endpoint():
	print("** TEST TEST ENDPOINT...")
	conf = {}
	load_config(conf)
	text, status = test_server(conf)
	assert status == 200
	print("** TEST TEST ENDPOINT passed")


def test_all():
	test_load_config()
	test_update_virus_file_name()
	test_scan_cmd()
	# test_scan_timeout() # cannot scan timeout and cmd with same config!
	test_test_endpoint()


if __name__ == "__main__":
	test_scan_cmd()
