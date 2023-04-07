import json
import shlex
import socket
import subprocess

from flask import Flask, request, Response

app = Flask(__name__)
traceroute_bin = "/usr/bin/traceroute"


def find_remote_addr(req):
    """Determine the correct IP address of the requester."""
    for header in ["CF-Connecting-IP", "X-Forwarded-For"]:
        if req.headers.get(header):
            return req.headers.get(header)
    return req.remote_addr


def validate_ip(remote_addr):
    """Verify the IP address is valid before running traceroute."""
    try:
        socket.inet_pton(socket.AF_INET, remote_addr)
        return True
    except socket.error:
        pass

    try:
        socket.inet_pton(socket.AF_INET6, remote_addr)
        return True
    except socket.error:
        pass

    return False


def run_traceroute(remote_addr):
    """Run traceroute and return the results."""
    tracecmd = shlex.split(f"{traceroute_bin} -q 1 -f 1 -w 1 {remote_addr}")
    result = subprocess.run(tracecmd, capture_output=True, text=True)
    return result.stdout.strip()


@app.route("/")
@app.route("/<target>")
def handler(target=None):
    """Run traceroute and return the output."""
    remote_addr = find_remote_addr(request)

    if not validate_ip(remote_addr):
        return Response("Invalid IP", status=406)

    if target is None:
        target = remote_addr
    elif not validate_ip(target):
        return Response("Invalid target address", status=406)

    traceroute_output = run_traceroute(target)

    return Response(traceroute_output + "\n", mimetype="text/plain")
