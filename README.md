# DuinoCoin Minimal Dockerized Miner

This miner is for people who want to mine DUCO and want to use docker. 
Credit for the miner goes to revox, I only moved things around a little bit, to make it 
work with my flask app setup.

I used flask here to be able to trigger it from only a URL. 

*Please note this uses the minimal miner which is single thread only*

If this has enough support I will start work on the multithreaded miner.

## Installation and Usage:

0. Make sure you have [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/) installed on your system.

1. Clone this repository with `git clone https://github.com/Alicia426/Dockerized_DUCO_Miner_minimal.git`

2. Go into the repository's directory.
   
3. Run `docker-compose up`. `Crrl + C` Cancels it.

4. To test, first go to `http://localhost:6969/` on your browser, you should see this: `//\(oo)/\\ Congrats, the server is working! //\(oo)/\\`. This server will be exposed on your local network, so you can also access it from other computers, `http://<server_ip_here>:6969/`.

5. To mine, call the URL `http://localhost:6969/<username>/<LowDifficulty>`, username is your DUCO account user, LowDifficulty is either `True` or `False`, set to True it will mine on a lower difficulty.
Examples:
    ```
    http://localhost:6969/mine/Alicia426/True
    http://localhost:6969/mine/Alicia426/False
    ```
    Please note that no web page will be loaded, you can close your tab right after you get a loading icon. 

6. If needed, you can check the logs either through `http://localhost:6969/logs` or in the local `miner.log file`
7. To mine with your container in the background use `docker-compose up -d`, this will start the container on detached mode.

**Note: you may have to run docker-compose with sudo**

## Upcoming features:

If this gets enough traction, I will make a docker friendly version of the multithreaded miner. 

**Feature requests are welcome, justping me on the discord or send me a message here.**

## How tf does this whole thing work: 

Basically, I use flask to process http requests, which can then trigger in this case the miner function. I made a tiny module called `babylog` just to not clutter the code. 
This module creates the logfile which can then be read with another URL. 

Normally one would deploy Flask ina WSGI server, however, flask has its own WSGI testing server, and since we are not running a large web app and the userbase will be of 1 per container, I see no issue with doing it the quick way.

Flask normally is exposed on port 5000, however to avoid conflicts with other flask apps i am working on, it was assigned to the doubly nice 6969 port. This setting is on the `docker-compose.yml` file and can be changed to any non reserved port.


This is hacky, not super stylish, I did it in my spare time today and I will update as needed.
I know it's janky.

### License:

MIT License, same as most of DuinoCoin.



**If you made it this far, thank you.**
