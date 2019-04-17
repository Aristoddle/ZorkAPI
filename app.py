#!/usr/bin/env python3
import errno
import os
import posix
import socket
import subprocess
from string import Template
from subprocess import PIPE, Popen

import pexpect
from flask import Flask, request
from redis import Redis, RedisError

global child

# Connect to Redis 
#redis = Redis(host="redis", db=0, socket_connect_timeout=2, socket_timeout=2)
app = Flask(__name__)

@app.route("/start", methods=['GET', 'POST'])
def start():
    global child
    game = request.args.get('game')
    os.setuid(1000)

    try:
        child.close()
    
    except:
        pass

    if (game == 'hike'):
        child = pexpect.spawn('/home/J3lanzone/frotz/dfrotz -mp /home/J3lanzone/Games/HitchHikers/hhgg.z3')
        game = "The Hitchiker\'s Guide to the Galaxy"
    
    elif (game == 'spell'):
        child = pexpect.spawn('/home/J3lanzone/frotz/dfrotz -mp /home/J3lanzone/Games/Spellbreaker/spellbre.dat') 
        game = "Spellbreaker"

    elif (game == 'wish'):
        child = pexpect.spawn('/home/J3lanzone/frotz/dfrotz -mp /home/J3lanzone/Games/Wishbringer/wishbrin.dat')
        game = "Wishbringer"

    elif (game == 'zork1'):
        child = pexpect.spawn('/home/J3lanzone/frotz/dfrotz -mp /home/J3lanzone/Games/Zork1/zork1.z5')
        game = "Zork One"

    elif (game == 'zork2'):
        child = pexpect.spawn('/home/J3lanzone/frotz/dfrotz -mp /home/J3lanzone/Games/Zork2/zork2.dat')
        game = "Zork Two"

    elif (game == 'zork3'):
        child = pexpect.spawn('/home/J3lanzone/frotz/dfrotz -mp /home/J3lanzone/Games/Zork3/ZORK3.DAT')
        game = "Zork Three"

    else:
         child = pexpect.spawn('/home/J3lanzone/frotz/dfrotz -mp /home/J3lanzone/Zork3/zork1.z5')

    child.expect('Serial [n|N]umber [0-9]+')
    firstLine = child.before.decode('utf-8')
    after = child.after.decode('utf-8')

    return(f"Loaded {game}.\n Before: {firstLine} {after}")

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
    global child
