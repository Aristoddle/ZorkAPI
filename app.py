#!/usr/bin/env python3
import errno
import os
import os.path
import posix
import socket
import subprocess
from string import Template
from subprocess import PIPE, Popen

import pexpect
from flask import Flask, request, session, jsonify
from flask_session import Session
from redis import Redis, RedisError

import pickle

USER_PROFILES_FILE = 'profiles.pickle'
SESSION_TYPE = 'filesystem'

# Connect to Redis 
# redis = Redis(host="redis", db=0, socket_connect_timeout=2, socket_timeout=2)
app = Flask(__name__)
app.config.from_object(__name__)
Session(app)


# define response object to say: 
# person has some save files
# here's what they are
# here's how many there are?

profileObjectExample = {
    "userEmail": "",

    "savesZork1": [],
    "savesZork2": [],
    "savesZork3": [],
    "savesHitchHikers": [],
    "savesWishbringer": [],
    "savesSpellbreaker": [],

    "lastSaveFile": ""
}


@app.route("/user", methods=['GET', 'POST'])
def user():
    email = request.args.get('email')
    saveFilesList = []
    
    # open profiles pickle, load to the cache
    with open(USER_PROFILES_FILE, 'rb') as f:
        try:
            session["profiles"] = pickle.load(f)
        except:
            session["profiles"] = {}

    # if the email is in the system, return their data
    if (session["profiles"] and
        session["profiles"][email]):
        session["profiles"][email]["newUser"] = False
        print("Not new user")
        #todo may break
        return jsonify(session["profiles"][email])

    # else, set up a new acc, write it to the pickle, return the new user
    else:
        print("new user")
        session["profiles"][email] = {
            "userEmail": email,
            "savesZork1": [],
            "savesZork2": [],
            "savesZork3": [],
            "savesHitchHikers": [],
            "savesWishbringer": [],
            "savesSpellbreaker": [],
            "lastSaveFile": "",
            "newUser": True
        }
        #dump session info w extra new user
        with open(USER_PROFILES_FILE, 'wb') as f:
            pickle.dump(session["profiles"], f)
        
        return jsonify(session["profiles"][email])


@app.route("/start", methods=['GET', 'POST'])
def start():
    email = request.args.get('email')
    title = request.args.get('game')
    saveFile = None
    
    try:
        saveFile = request.args.get('save')
    except:
        pass

    os.setuid(1000)

    game, title = startGame(title)

    # Grab general game data
    game.expect('Serial [n|N]umber [0-9]+')
    titleInfo = game.before.decode('utf-8')
    titleInfoEnd = game.after.decode('utf-8')
    game.expect('>')
    firstLine = game.after.decode('utf-8')

    print("before things break...")
    print(f"{titleInfo} {titleInfoEnd} oioioioi {firstLine}")

    game.sendLine("look")
    game.expect('>')
    print(game.before.decode('utf-8'))

    # this is @ game init, so load them back in, and give a general
    # description of their surroundings
    if (saveFile):
        return restoreSave(saveFile, game)
    else:
        autoSave(f"{email}_AutoSave", game)
        with open(USER_PROFILES_FILE, 'wb') as f:
            pickle.dump(session["profiles"], f)

        return(f"{titleInfo} {titleInfoEnd} oioioioi {firstLine}")
    
@app.route("/action", methods=['GET', 'POST'])
def action():

    email       = request.args.get('email')
    title       = request.args.get('game')
    save        = request.args.get('save')
    command     = request.args.get('cmd')

    # start a game, restore the save
    game, title = startGame(title)
    areaDesc = restoreSave(save, game)

    # send an actual command, clean it up
    game.sendline(command)
    game.expect('>')
    output = game.before.decode('utf-8')
    output = output.replace(command,"",1)

    # autosave & save to your slot
    autoSave(f"{email}_AutoSave", game)
    autoSave("save", game)

    # return whatever the game has given you
    return(output)

def autoSave(savename, game):
    game.sendLine(f"save")
    game.expect(':')
    game.sendLine(savename)
    if (os.path.isfile(savename)):
        game.expect('?')
        game.sendLine("yes")
    game.expect('>')

def restoreSave(saveName, game):
    game.sendLine("restore")
    game.expect(':')
    game.sendLine(saveName)
    game.sendLine("look")
    game.expect('>')
    return(game.before.decode('utf-8'))

def startGame(title):

    if (title == 'hike'):
        game = pexpect.spawn('/home/J3lanzone/frotz/dfrotz -mp /home/J3lanzone/Games/HitchHikers/hhgg.z3')
    elif (title == 'spell'):
        game = pexpect.spawn('/home/J3lanzone/frotz/dfrotz -mp /home/J3lanzone/Games/Spellbreaker/spellbre.dat')
    elif (title == 'wish'):
        game = pexpect.spawn('/home/J3lanzone/frotz/dfrotz -mp /home/J3lanzone/Games/Wishbringer/wishbrin.dat')
    elif (title == 'zork1'):
        game = pexpect.spawn('/home/J3lanzone/frotz/dfrotz -mp /home/J3lanzone/Games/Zork1/zork1.z5')
    elif (title == 'zork2'):
        game = pexpect.spawn('/home/J3lanzone/frotz/dfrotz -mp /home/J3lanzone/Games/Zork2/zork2.dat')
    elif (title == 'zork3'):
        game = pexpect.spawn('/home/J3lanzone/frotz/dfrotz -mp /home/J3lanzone/Games/Zork3/ZORK3.DAT')
    else:
         game = pexpect.spawn('/home/J3lanzone/frotz/dfrotz -mp /home/J3lanzone/Games/Zork1/zork1.z5')
         title = 'zork1'

    return (game, title)

if __name__ == "__main__":
    #start()
    app.run(host='0.0.0.0', port=443)
