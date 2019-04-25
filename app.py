#!/usr/bin/python3
import errno
import os
import os.path
import pickle
import socket
import subprocess 
from string import Template
from subprocess import PIPE, Popen

import pexpect
from flask import Flask, jsonify, request
from redis import Redis, RedisError

import platform

USER_PROFILES_FILE = './profiles.pickle'
profiles_TYPE = 'filesystem'
# ROOT_PATH = '/home/J3lanzone/LinuxSaves' if (platform.system() == "Linux") else "C:\\Users\\J3lan\\OneDrive\\Documents\\Code\\ZorkAPI\\WindowsSaves"

# Connect to Redis 
# redis = Redis(host="redis", db=0, socket_connect_timeout=2, socket_timeout=2)
app = Flask(__name__)
app.config.from_object(__name__)


# define response object to say: 
# person has some save files 
# here's what they are
# here's how many there are?

profileObjectExample = {
    "hike": ["hike save files"],
    "spell": ["spell save files"],
    "wish": ["wish save files"],
    "zork1": ["zork1 files"],
    "zork2": ["zork2 files"],
    "zork3": ["zork3 files"],
    "email": "User Email",
    "lastGame": [None or "last_game_played"]
}

def loadProfiles():
    try:
        with open(USER_PROFILES_FILE, 'rb') as f:
            profiles = pickle.load(f)
    except:
        profiles = {}
    return profiles

def dumpProfiles(profiles, email, title, game, saveFile="AutoSave"):
    print(f"dumping... email: {email}, title: {title}, savefile: {saveFile}")
    if (title):
        profiles[email]["lastGame"] = title   
        
        if (not saveFile in profiles[email][title]):
            print(f"saveFile not found... adding")
            profiles[email][title].append(saveFile)
        else:
            print(f"saveFile found.. {saveFile} in {profiles[email][title]}")
    print(f"new profiles: {profiles}")
    with open(USER_PROFILES_FILE, 'wb') as f:
        pickle.dump(profiles, f)

def saveGame(profiles, saveFile, game):
    print(f"\n\n SAVEGAME CALLED:  {saveFile}\n\n")
    game.sendline(f"save")
    game.expect(':')
    prompt = game.before.decode('utf-8')
    game.sendline(saveFile)
    entries = saveFile.split(".")
    if (entries[2] in profiles[entries[0]][entries[1]]):
        game.expect(['\?', pexpect.EOF, pexpect.TIMEOUT], timeout=5)
        game.sendline("yes")
    game.expect(['>', pexpect.EOF, pexpect.TIMEOUT], timeout=.2)
    response = game.before.decode('utf-8')

def restoreSave(saveFile, game):
    print(f"\n\n\nRESTORE SAVE CALLED\n {saveFile}\n\n\n")
    titleInfo, firstLine = getFirstLines(game)
    game.sendline("restore")
    game.expect(':')
    trash = game.before.decode('utf-8')
    game.sendline(saveFile)
    game.expect(['>', pexpect.EOF, pexpect.TIMEOUT], timeout=.2)
    trash = game.before.decode('utf-8')
    outputs = {
        "titleInfo": titleInfo,
        "firstLine": firstLine
    }
    return(outputs)

def getFirstLines(game):
    print(f"\n\n\nGET FIRST LINE CALLED\n {game}\n\n\n")
    game.expect('Serial [n|N]umber [0-9]+')
    titleInfo = game.before.decode('utf-8')
    titleInfo += game.after.decode('utf-8')
    game.expect(['>', pexpect.EOF, pexpect.TIMEOUT], timeout=.2)
    firstLine = game.before.decode('utf-8')
    return (titleInfo, firstLine)

def startGame(title):
    print(f"\n\n\nSPAWN GAME CALLED\n {title}\n\n\n")
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

@app.route("/user", methods=['GET', 'POST'])
def user():
    profiles = loadProfiles()
    responseObj = {}

    print(f"\n\n\nUSER CALLED\n\n\n")
    print(f"profiles: {profiles}")
    email = request.args.get('email')

    if (not profiles.get(email, None)):
        print(f"Profile not found: {email}")
        profiles[email] = {
            "email": email,
            "hike": [],
            "spell": [],
            "wish": [],
            "zork1": [],
            "zork2": [],
            "zork3": []
        }
        responseObj["newUser"] = True
    else:
        print(f"Profile  found: {email}")
        print(f"Profile: {profiles[email]}")
        responseObj["newUser"] = False
        
    dumpProfiles(profiles, email, None, None)
    responseObj["profile"] = profiles[email]

    return jsonify(responseObj)

# else, set up a new acc, write it to the pickle, return the new user
@app.route("/newGame", methods=['GET', 'POST'])
def newGame():
    profiles = loadProfiles()
    
    print("\n\n New Game Called\n\n")
    print(f"profiles: {profiles}")
    email       = request.args.get('email')
    title       = request.args.get('title')
    game, title = startGame(title)
    if ("AutoSave" in profiles[email][title]):
        os.remove(f"./{email}.{title}.AutoSave")
        profiles[email][title].remove("AutoSave")

    try:
        titleInfo, firstLine = getFirstLines(game)
        saveGame(profiles, f"{email}.{title}.AutoSave", game)
    except:
        print ("import broke somehow...")
    
    userProfile = profiles[email]
    print(f"titleInfo: {titleInfo}, firstLine: {firstLine}, userProfile: {userProfile}")

    returnObj = {
        "titleInfo":    titleInfo,
        "firstLine":    firstLine,
        "userProfile":  profiles[email]
    }
    dumpProfiles(profiles, email, title, game)
    game.terminate()
    return (jsonify(returnObj))

# So start should get AutoSave, or the name of some SaveFile
@app.route("/start", methods=['GET', 'POST'])
def start():
    profiles = loadProfiles()

    print("\n\nStart Called\n\n")
    email = request.args.get('email')
    title = request.args.get('title')
    saveFile  = request.args.get('save')
    game, title = startGame(title)
        
    try: 
        restoreObj = restoreSave(f"{email}.{title}.{saveFile}", game)
    except:
        print ("import broke somehow...")

    print(f"restoreObj: {restoreObj}")

    titleInfo   =    restoreObj["titleInfo"]
    firstLine   =    restoreObj["firstLine"]
    userProfile =    profiles[email]
    print(f"titleInfo: {titleInfo}, firstLine: {firstLine}, userProfile: {userProfile}")
    returnObj = {
        "titleInfo":    restoreObj["titleInfo"],
        "firstLine":    restoreObj["firstLine"],
        "userProfile":  profiles[email]
    }
    dumpProfiles(profiles, email, title, game)
    game.terminate()
    return(jsonify(returnObj))

@app.route("/action", methods=['GET', 'POST'])
def action():
    profiles = loadProfiles()

    print("\n\nAction Called\n\n")
    print(profiles)
    email       = request.args.get('email')
    title       = request.args.get('title')
    action      = request.args.get('action')

    # start a game, restore the save
    game, title = startGame(title)
    
    areaDesc = restoreSave(f"{email}.{title}.AutoSave", game)
    
    print("about to sendline")
    game.sendline(action)
    game.expect(['>', pexpect.EOF, pexpect.TIMEOUT], timeout=.2)
    output = game.before.decode('utf-8')
    saveGame(profiles, f"{email}.{title}.AutoSave", game)
    print("sent line, saved")

    resObj = {
        "cmdOutput":        output,
        "lookOutput":       areaDesc,
        "userProfile":      profiles[email]
    }

    print(f"action response item: {resObj}")

    # autosave & save to your slot
    dumpProfiles(profiles, email, title, game)
    game.terminate()
    # return whatever the game has given you
    return(jsonify(resObj))



@app.route("/save", methods=['GET', 'POST'])
def save():
    profiles = loadProfiles()

    print("\n\nSave API Called\n\n")
    email       = request.args.get('email')
    title       = request.args.get('title')
    saveFile    = request.args.get('save')
    # start a game, restore the save
    game, title = startGame(title)
    areaDesc = restoreSave(f"{email}.{title}.AutoSave", game)
    saveGame(profiles, f"{email}.{title}.{saveFile}", game)
    dumpProfiles(profiles, email, title, game, saveFile)
    game.terminate()
    return (jsonify(profiles[email]))

if __name__ == "__main__":
    #start()
    app.run(host='0.0.0.0', port=443)
