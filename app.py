#!/usr/bin/env python3
from flask import Flask
from redis import Redis, RedisError
import os
import socket
import subprocess
from subprocess import Popen, PIPE
from string import Template
import errno
import posix
from flask import request
import pexpect

# Connect to Redis 
#redis = Redis(host="redis", db=0, socket_connect_timeout=2, socket_timeout=2)
app = Flask(__name__)


global child
@app.route("/start", methods=['GET', 'POST'])
def start():
    global child
    game = request.args.get('game')
    os.setuid(1000)
    
    if (game == 'zork'):
        child = pexpect.spawn('/home/J3lanzone/frotz/dfrotz /home/J3lanzone/Zork1/zork1.z5')
    elif (game == 'hike'):
        child = pexpect.spawn('/home/J3lanzone/frotz/dfrotz /home/J3lanzone/HitchHikers/hhgg.z3')
    else:
         child = pexpect.spawn('/home/J3lanzone/frotz/dfrotz /home/J3lanzone/Zork1/zork1.z5')

    return(f"loaded {game}")

@app.route("/check", methods=['GET', 'POST'])
def check():
    global child
    child.expect('>')
    return(child.before.decode('utf-8'))
    
@app.route("/action", methods=['GET', 'POST'])
def action():
    global child
    command = request.args.get('cmd') 
    child.sendline(command)
    child.expect('>')
    output = child.before.decode('utf-8')
    output = output.replace(command,"",1)
    return(output)

if __name__ == "__main__":
    #start()
    app.run(host='0.0.0.0', port=443)


