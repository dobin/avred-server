from flask import Flask, request
from json import load
from avred_server import run_server
from multiprocessing import Process


app = Flask(__name__)
running_servers = {}
with open("config.json") as f:
	engines = load(f)["engines"].keys()


@app.route("/")
def index():
	return "Master Server is up."


@app.route("/start")
def start_server():
	av_type = request.args.get("type")
	if av_type not in engines:
		return "Unknown AV Type", 400
	p = Process(target=run_server, args=(av_type,))
	p.start()
	running_servers[av_type] = p
	return "Started AV Server.\n"


@app.route("/stop")
def stop_server():
	av_type = request.args.get("type")
	if av_type not in running_servers:
		return "Unknown AV Type", 400
	p = running_servers[av_type]
	p.terminate()
	p.join()
	return "Stopped AV Server.\n"


if __name__ == "__main__":
	app.run("10.10.10.107", 9000)
