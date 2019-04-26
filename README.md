# ZorkAPI
This is the codebase for the flask-based server that serves ZorkBot.

## Running/Testing the Code:
* [Python3.6+](https://www.python.org/downloads/) (unique string modificaiton is done that was intruduced in Python 6)
* [Flask](http://flask.pocoo.org/)
* [Pexpect](https://pexpect.readthedocs.io/en/stable/)
* [frotz for Unix](https://gitlab.com/DavidGriffith/frotz), --specifically its *dfrotz* module, from which the process will (manually jump around permisions levels to) can call the dfrotz command
* [An Azure Virtual Machine](https://azure.microsoft.com/en-us/services/virtual-machines/), or any other unix-based host to serve the application from

## Getting the app online:
Once you have the app running on a Linux host, you should be able to follow [this guide](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-18-04) to establish and deploy the application using [Gunicorn](https://gunicorn.org/) and [nginx](https://www.nginx.com/)

## Core API Endpoints:
### `/user?email=user_email`
 ***General Description:***
 
This endpoint is called when a user first pings the server.   If a user with the same email, or who has provided the same unique identifier, has already hit the system and begun to play games, this will return an object representing the set of (I decided to forgo formal security)
 
 ***Arguments:***
* **email (Required)**: the email of the given user, will either be pulled directly from device that the user uses to access the API, or will be provided by the user after a short dialogue.  Used to organize persistent save files for a user.

### `/newGame?email=user_email&title=game_title`
* **email (Required)**: the email of the given user, will either be pulled directly from device that the user uses to access the API, or will be provided by the user after a short dialogue.  Used to organize persistent save files for a user.
* **title (Required)**: the title of the game that the user is playing.  This will be used to 


## Player Profile Object Model:
*Each time an endpoint is pinged, an object of the following form is loaded into the Flask server.
It is a general representation of user state, holding a list of save files for the 6 games emulated, a secondary reference to the email which is used as a key to find this object, and a record of the last game that the user was playing.  This object is returned by most endpoints (along with secondary payloads depending on the endpoint's function), and is used to ensure consistency between the client and the server.*

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
