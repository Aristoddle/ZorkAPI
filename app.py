#!/usr/bin/python3
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
ROOT_PATH = '/home/J3lanzone'

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
    "lastSaveFile": "file path",
    "newUser": bool,
    
    "hike": ["hike save files"],
    "spell": ["spell save files"],
    "wish": ["wish save files"],
    "zork1": ["zork1 files"],
    "zork2": ["zork2 files"],
    "zork3": ["zork3 files"],

    "userEmail": "",
}

def loadSession():
    if (session.get("profiles", None)):
        with open(USER_PROFILES_FILE, 'rb') as f:
                session["profiles"] = pickle.load(f)
    else:
        session["profiles"] = {}

def dumpSession(email, title, saveFile, game):
    print(f"dumping... email: {email}, title: {title}, saveFile {saveFile}")
    if (game):
        saveGame(f"{ROOT_PATH}/{email}/{title}/AutoSave", game)
        if (f"AutoSave" not in session["profiles"][email][title]):
            session["profiles"][email][title].append(f"AutoSave")
            session["profiles"][email]["lastSaveFile"] = f"{ROOT_PATH}/{email}/{title}/AutoSave"
            if (saveFile != "AutoSave"):
                print("still entered")
                saveGame(f"{ROOT_PATH}/{email}/{title}/{saveFile}", game)
                session["profiles"][email]["lastSaveFile"] = f"{ROOT_PATH}/{email}/{title}/{saveFile}"
                if f"{saveFile}" not in session["profiles"][email][title]:
                    session["profiles"][email][title].append(f"{saveFile}")

    
    with open(USER_PROFILES_FILE, 'wb') as f:
        pickle.dump(session["profiles"], f)

@app.route("/user", methods=['GET', 'POST'])
def user():
    loadSession()
    email = request.args.get('email')

    try:
        session["profiles"][email]
    except:
        print("hit exception -- user is new")
        session["profiles"][email] = {
            "userEmail": email,
            "hike": [],
            "spell": [],
            "wish": [],
            "zork1": [],
            "zork2": [],
            "zork3": [],
            "lastSaveFile": None,
            "newUser": True
        }

        if (not os.path.isfile(f"{ROOT_PATH}/{email}")):
            os.makedirs(f"{ROOT_PATH}/{email}")
        else:
            session["profiles"][email]["newUser"] = False;
    
    dumpSession(email, None, None, None)
    return jsonify(session["profiles"][email])

    # else, set up a new acc, write it to the pickle, return the new user


@app.route("/start", methods=['GET', 'POST'])
def start():
    loadSession()

    email = request.args.get('email')
    title = request.args.get('title')
    saveFile = request.args.get('save', None)
    os.setuid(1000)

    game, title = startGame(title)

    # Grab general game data
    game.expect('Serial [n|N]umber [0-9]+')
    titleInfo = game.before.decode('utf-8')
    titleInfoEnd = game.after.decode('utf-8')
    game.expect('>')
    firstLine = game.before.decode('utf-8')

    print("before things break...")
    print(f"{titleInfo} {titleInfoEnd} oioioioi {firstLine}")

    game.sendline("look")
    game.expect('>')
    print(game.before.decode('utf-8'))

    #if this is the first time you've played this game
    if (not os.path.isfile(f"{ROOT_PATH}/{email}/{title}")):
        os.makedirs(f"{ROOT_PATH}/{email}/{title}")

    # this is @ game init, so load them back in, and give a general
    # description of their surroundings
    if (saveFile):
        if (os.path.isfile(f"{ROOT_PATH}/{email}/{title}/{saveFile}")):
            firstLine = restoreSave(f"{ROOT_PATH}/{email}/{title}/{saveFile}", game)
        else:
            dumpSession(email, title, saveFile, game)
    else:
        if (os.path.isfile(f"{ROOT_PATH}/{email}/{title}/AutoSave")):
            firstLine = restoreSave(f"{ROOT_PATH}/{email}/{title}/AutoSave", game)
        else:
            dumpSession(email, title, "AutoSave", game)
            
    returnObj = {
        "titleInfo":    titleInfo + titleInfoEnd,
        "firstLine":    firstLine,
        "userProfile":  session["profiles"][email]
    }

    return(jsonify(returnObj))
    
@app.route("/action", methods=['GET', 'POST'])
def action():
    loadSession()
    print(session["profiles"])
    email       = request.args.get('email')
    title       = request.args.get('title')
    saveFile    = request.args.get('save', None)
    action      = request.args.get('action')

    # start a game, restore the save
    game, title = startGame(title)
    if (saveFile):
        areaDesc = restoreSave(f"{ROOT_PATH}/{email}/{title}/{saveFile}", game)
        print("entered ehre")
    else:
        print("entered this one")
        areaDesc = restoreSave(session["profiles"][email]["lastSaveFile"], game)
    
    # send an actual action, clean it up
    print(f"My action: {action}")
    
    game.expect('>|pexpect.EOF')
    game.sendline(action)
    game.expect('>|pexpect.EOF')
    output = game.before.decode('utf-8')

    resObj = {
        "cmdOutput":        output,
        "lookOutput":       areaDesc,
        "userProfile":      session["profiles"][email]
    }

    # autosave & save to your slot
    dumpSession(email, title, saveFile, game)

    # return whatever the game has given you
    return(jsonify(resObj))

def saveGame(savename, game):
    game.sendline(f"save")
    game.expect(':')
    game.sendline(savename)
    if (os.path.isfile(savename)):
        game.expect('\?')
        game.sendline("yes")
    game.expect('>')


def restoreSave(saveName, game):
    game.sendline("restore")
    game.expect(':')
    trash = game.before.decode('utf-8')
    game.sendline(saveName)
    game.expect('>')
    trash = game.before.decode('utf-8')
    print("trash3" + game.before.decode('utf-8'))
    return(game.before.decode('utf-8'))

def startGame(title):
    print(f"title: {title}")
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
        print("miss")
        game = pexpect.spawn('/home/J3lanzone/frotz/dfrotz -mp /home/J3lanzone/Games/Zork1/zork1.z5')
        title = 'zork1'

    return (game, title)

if __name__ == "__main__":
    #start()
    app.run(host='0.0.0.0', port=443)
