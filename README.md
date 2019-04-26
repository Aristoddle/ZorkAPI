# ZorkAPI
This is the codebase for the flask-based server that serves ZorkBot.

## Running/Testing the Code:
* [Python3.6+](https://www.python.org/downloads/) (unique string modificaiton is done that was intruduced in Python 6)
* [Flask](http://flask.pocoo.org/)
* [Pexpect](https://pexpect.readthedocs.io/en/stable/)
* [frotz for Unix](https://gitlab.com/DavidGriffith/frotz), --specifically its *dfrotz* module, from which the process will (manually jump around permisions levels to) can call the dfrotz command
* [An Azure Virtual Machine](https://azure.microsoft.com/en-us/services/virtual-machines/), or any other unix-based host to serve the application from

## Getting the System Online:
Once you have the app running on a Linux host, you should be able to follow [this guide](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-18-04) to establish and deploy the application using [Gunicorn](https://gunicorn.org/) and [nginx](https://www.nginx.com/)

## Core Profile Object:
Each time we hit the endpoint an object of the following form is loaded into the Flask server from a pickly files named `profiles.pickle`. It is a general representation of user state, holding a list of save files for the 6 games emulated, a secondary reference to the email which is used as a key to find this object, and a record of the last game that the user was playing.  This object is returned by most endpoints (along with secondary payloads depending on the endpoint's function), and is used to ensure consistency between the client and the server.*

```python
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
```

## Core API Endpoints:

### /user

> ### General Description:
 
> This endpoint is called when a user first pings the server.   If a user with the same email, or who has provided the same unique identifier, has already hit the system and begun to play games, this will return an object representing the set of (I decided to forgo formal security)

> ### Example Call:

/user?email=user_email`

> ### Return Object:

```python
returnObject = { 
    'newUser': bool, #representing whether the user was already in the system 
    'profile': Object, #the core profile object described in the above section
}
```
 
> ### Arguments:

>  **email**: the email of the given user, will either be pulled directly from device that the user uses to access the API, or will be provided by the user after a short dialogue.  Used to organize persistent save files for a user, and allows them to user the system statelesslessly

### /start

> ### General Description:
 
> This endpoint is called when a user tries to load a game other than the 'New Game' placeholder.  This will allow the user to write to from that save file forward  in later `/action` calls.

> ### Example Call:

`/start?email=user_email&title=game_title&save=safeFile`

> ### Return Object:

```python
returnObject = { 
    'titleInfo': String, # Represents the first few lines of the game, up until the licensing information, etc 
    'firstLine': String, # Represents the first actual line of gameplay Information.  THe text between the end of the title info, and the first `>` input prompt
    'profile': Object,   # The core profile object described in the above section
}
```

> ### Arguments:

> **email**: the email of the given user, will either be pulled directly from device that the user uses to access the API, or will be provided by the user after a short dialogue.  Used to organize persistent save files for a user, and allows them to user the system statelesslessly
 
> **title**: The title of the game that the user is playing.  Needed so that dfrotz can be used to spin up an instance of the right game for the user to play

> **save**: The name of the specific saveFile that the user is trying to load.  After each turn in-game, the state is saved, the model object is updated, the game is closed, and the response is sent back to the user.  Normally, that most-recent save is stored at a  location called `AutoSave`, but through an explicit save dialog (see below), they can also set fixed save points within the story.  With the `/save` command, it is possible to load these older saves directly.

### /newGame

> ### General Description:
 
> This endpoint is called when a user tries to load a game titled with the'New Game' placeholder.  The server will init that game, delete any potential AutoSaves for the game, and move the AutoSave head to the first state in the game (move 0).  This will allow the user to write to from that save file forward  in later `/action` calls.

> ### Example Call

> `/newGame?email=user_email&title=game_title`

> ### Return Object:

```python
returnObject = { 
    'titleInfo': String,    # Represents the first few lines of the game, up until the licensing information, etc 
    'firstLine': String,    # Represents the first actual line of gameplay Information.  THe text between the end of the title info, and the first `>` input prompt
    'profile': Object,      # The core profile object described in the above section
}
```
 
> ### Arguments:

> **email**: the email of the given user, will either be pulled directly from device that the user uses to access the API, or will be provided by the user after a short dialogue.  Used to organize persistent save files for a user, and allows them to user the system statelesslessly
 
> **title**: The title of the game that the user is playing.  Needed so that dfrotz can be used to spin up an instance of the right game for the user to play

### /action

> ### General Description:

> This call sits are the heart of the core gameplay loop for the server.  This is called after `/start` or `/newGame` have initialized a game state and set the position for the AutoSave.  It will load the AutoSave into the system, execute the given action, update the AutoSave, and then save the game before returning.  

> ### Example Call

`/newGame?email=user_email&title=game_title`

> ### Return Object:

```python
returnObject = {
        "cmdOutput":        String,     # The game's response to the input user command
        "lookOutput":       String,     # The line returned upon loading the save to the user's expected state; unused, but may be of future value
        "userProfile":      Object,     # The core profile object described in the above section
    }
```

> ### Arguments: 

> **email**: the email of the given user, will either be pulled directly from device that the user uses to access the API, or will be provided by the user after a short dialogue.  Used to organize persistent save files for a user, and allows them to user the system statelesslessly
 
> **title**: The title of the game that the user is playing.  Needed so that dfrotz can be used to spin up an instance of the right game for the user to play
