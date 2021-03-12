#!/usr/bin/env python3
# Minimal version of Duino-Coin PC Miner, useful for developing own apps. Created by revox 2020-2021
# Modified by Alicia426 to run ina docker container and be able to be started with a URL
import socket
import hashlib
import urllib.request
import time
import os
import babylog
import sys  # Only python3 included libraries

from flask import Flask, request

babylog.start()

app = Flask(__name__)

soc = socket.socket()
soc.settimeout(10)


def mine(username, UseLowerDiff):
    current_buffer = ''
    if UseLowerDiff:
        soc.send(
            bytes("JOB," + str(username) + ",MEDIUM", encoding="utf8")
        )  # Send job request for lower difficulty
    else:
        soc.send(
            bytes("JOB," + str(username), encoding="utf8")
        )  # Send job request
    job = soc.recv(1024).decode()  # Get work from pool
    # Split received data to job (job and difficulty)
    job = job.split(",")
    difficulty = job[2]

    # Calculate hash with difficulty
    for result in range(100 * int(difficulty) + 1):
        ducos1 = hashlib.sha1(
            str(job[0] + str(result)).encode("utf-8")
        ).hexdigest()  # Generate hash
        if job[1] == ducos1:  # If result is even with job
            soc.send(
                bytes(str(result) + ",,Minimal_PC_Miner", encoding="utf8")
            )  # Send result of hashing algorithm to pool
            # Get feedback about the result
            feedback = soc.recv(1024).decode()
            if feedback == "GOOD":  # If result was good
                current_buffer = "Accepted share: " + \
                    str(result)+' '+"Difficulty: "+str(difficulty)
                break
            elif feedback == "BAD":  # If result was bad
                current_buffer = "Rejected share: " + \
                    str(result)+' '+"Difficulty: "+str(difficulty)
                break
    return current_buffer


def requestAndMine(username, UseLowerDiff):
    try:
        # This sections grabs pool adress and port from Duino-Coin GitHub file
        serverip = "https://raw.githubusercontent.com/revoxhere/duino-coin/gh-pages/serverip.txt"  # Serverip file
        with urllib.request.urlopen(serverip) as content:
            content = (
                content.read().decode().splitlines()
            )  # Read content and split into lines
        pool_address = content[0]  # Line 1 = pool address
        pool_port = content[1]  # Line 2 = pool port

        # This section connects and logs user to the server
        # Connect to the server
        soc.connect((str(pool_address), int(pool_port)))
        server_version = soc.recv(3).decode()  # Get server version
        print("Server is on version", server_version)
        # Mining section
        while True:
            buff = mine(username, UseLowerDiff)
            if 'Accepted' in buff:
                babylog.status(buff)
            elif 'Rejected' in buff:
                babylog.warn(buff)
            else:
                babylog.warn('Empty buffer, likely error')

    except Exception as e:
        babylog.error("Error occured: " + str(e) + ", restarting in 5s.")
        time.sleep(5)
        requestAndMine(username, UseLowerDiff)


@app.route('/mine/<username>/<UseLowerDiff>')
def mining(username, UseLowerDiff):
    if UseLowerDiff == 'False':
        boolUseLowerDiff = False
    else:
        boolUseLowerDiff = True
    # Fetches the username and difficulty
    babylog.status('Mining for '+username)
    babylog.status('Using Lower Mining Difficulty: '+UseLowerDiff)
    requestAndMine(username, boolUseLowerDiff)


@app.route('/')
def home():
    text = r"//\(oo)/\\ Congrats, the server is working! //\(oo)/\\"
    babylog.status('Server test succesful.')
    return text


@app.route('/logs')
def checkLogs():
    babylog.status('Checking logs...')
    with open('miner.log') as l:
        text = l.read()
    head = """
     <!DOCTYPE html>
<html>
<body>
<pre> 
    """
    tail = """</pre>
</body>
</html>
    """
    return head+text+tail


if __name__ == "__main__":
    app.run(debug=True)
