#!/usr/bin/env python3
import errno
import os
import posix
import socket
import subprocess
from string import Template
from subprocess import PIPE, Popen

import pexpect
from flask import Flask, request, session
from flask_session import Session
from redis import Redis, RedisError

SESSION_TYPE = 'filesystem'

# Connect to Redis 
# redis = Redis(host="redis", db=0, socket_connect_timeout=2, socket_timeout=2)
app = Flask(__name__)
app.config.from_object(__name__)
Session(app)

@app.route("/start", methods=['GET', 'POST'])
def start():
    game = request.args.get('game')
    os.setuid(1000)

    try:
        session.get("gameThread", None).close()
    
    except:
        pass

    if (game == 'hike'):
        session["gameThread"] = pexpect.spawn('/home/J3lanzone/frotz/dfrotz -mp /home/J3lanzone/Games/HitchHikers/hhgg.z3')
        game = "The Hitchiker\'s Guide to the Galaxy"
    
    elif (game == 'spell'):
        session["gameThread"] = pexpect.spawn('/home/J3lanzone/frotz/dfrotz -mp /home/J3lanzone/Games/Spellbreaker/spellbre.dat') 
        game = "Spellbreaker"

    elif (game == 'wish'):
        session["gameThread"] = pexpect.spawn('/home/J3lanzone/frotz/dfrotz -mp /home/J3lanzone/Games/Wishbringer/wishbrin.dat')
        game = "Wishbringer"

    elif (game == 'zork1'):
        session["gameThread"] = pexpect.spawn('/home/J3lanzone/frotz/dfrotz -mp /home/J3lanzone/Games/Zork1/zork1.z5')
        game = "Zork One"

    elif (game == 'zork2'):
        session["gameThread"] = pexpect.spawn('/home/J3lanzone/frotz/dfrotz -mp /home/J3lanzone/Games/Zork2/zork2.dat')
        game = "Zork Two"

    elif (game == 'zork3'):
        session["gameThread"] = pexpect.spawn('/home/J3lanzone/frotz/dfrotz -mp /home/J3lanzone/Games/Zork3/ZORK3.DAT')
        game = "Zork Three"

    else:
         session["gameThread"] = pexpect.spawn('/home/J3lanzone/frotz/dfrotz -mp /home/J3lanzone/Games/Zork1/zork1.z5')

    session.get("gameThread", None).expect('Serial [n|N]umber [0-9]+')
    firstLine = session.get("gameThread", None).before.decode('utf-8')
    after = session.get("gameThread", None).after.decode('utf-8')

    return(f"{firstLine} {after}")

@app.route("/check", methods=['GET', 'POST'])
def check():
    session.get("gameThread", None).expect('>')
    return(session.get("gameThread", None).before.decode('utf-8'))
    
@app.route("/action", methods=['GET', 'POST'])
def action():
    command = request.args.get('cmd') 
    session.get("gameThread", None).sendline(command)
    session.get("gameThread", None).expect('>')
    output = session.get("gameThread", None).before.decode('utf-8')
    output = output.replace(command,"",1)
    return(output)

if __name__ == "__main__":
    #start()
    app.run(host='0.0.0.0', port=443)
