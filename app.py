#!/usr/bin/env python3
# Minimal version of Duino-Coin PC Miner, useful for developing own apps. Created by revox 2020-2021
# Modified by Alicia426 to run ina docker container and be able to be started with a URL
# Addign multiprocessing to start and stop the mining thread
import socket
import hashlib
import urllib.request
import time
import os
import babylog
import sys  # Only python3 included libraries
import multiprocessing

from flask import Flask, request

babylog.start()

app = Flask(__name__)


class Miner:

    def __init__(self, username, UseLowerDiff):
        self.username = username
        self.UseLowerDiff = UseLowerDiff
        self.soc = socket.socket()
        self.soc.settimeout(15)

    def mine(self):
        current_buffer = ''
        if self.UseLowerDiff:
            self.soc.send(
                bytes("JOB," + str(self.username) + ",MEDIUM", encoding="utf8")
            )  # Send job request for lower difficulty
        else:
            self.soc.send(
                bytes("JOB," + str(self.username), encoding="utf8")
            )  # Send job request
        job = self.soc.recv(1024).decode()  # Get work from pool
        # Split received data to job (job and difficulty)
        job = job.split(",")
        difficulty = job[2]

        # Calculate hash with difficulty
        for result in range(100 * int(difficulty) + 1):
            ducos1 = hashlib.sha1(
                str(job[0] + str(result)).encode("utf-8")
            ).hexdigest()  # Generate hash
            if job[1] == ducos1:  # If result is even with job
                self.soc.send(
                    bytes(str(result) + ",,Minimal_PC_Miner", encoding="utf8")
                )  # Send result of hashing algorithm to pool
                # Get feedback about the result
                feedback = self.soc.recv(1024).decode()
                if feedback == "GOOD":  # If result was good
                    current_buffer = "Accepted share: " + \
                        str(result)+' '+"Difficulty: "+str(difficulty)
                    break
                elif feedback == "BAD":  # If result was bad
                    current_buffer = "Rejected share: " + \
                        str(result)+' '+"Difficulty: "+str(difficulty)
                    break
        return current_buffer

    def requestAndMine(self):
        while True:
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
                self.soc.connect((str(pool_address), int(pool_port)))
                server_version = self.soc.recv(
                    3).decode()  # Get server version
                babylog.status("Server is on version: "+str(server_version))
                # Mining section
                while True:
                    buff = self.mine()
                    if 'Accepted' in buff:
                        babylog.status(buff)
                    elif 'Rejected' in buff:
                        babylog.warn(buff)
                    else:
                        babylog.warn('Empty buffer, likely error')

            except Exception as e:
                babylog.error("Error occured: " + str(e) +
                              ", restarting in 5s.")
                time.sleep(5)
                try:
                    self.soc.close()
                except Exception as e:
                    babylog.warn(str(e))

    def start_mining(self):
        """Starts mining as a process"""
        try:
            self.proc.terminate()  # pylint: disable=access-member-before-definition
        except Exception:
            babylog.status('No previously running threads, OK!')
        finally:
            self.proc = multiprocessing.Process(  # pylint: disable=attribute-defined-outside-init
                target=self.requestAndMine, args=())
            self.proc.start()

    def stop_mining(self):
        """Stops mining as a process"""
        try:
            self.proc.terminate()  # pylint: disable=access-member-before-definition
        except Exception as e:
            babylog.error(str(e))


# Global mining object

miners = []


@app.route('/mine/<username>/<UseLowerDiff>')
def mining(username, UseLowerDiff):
    if UseLowerDiff == 'False':
        boolUseLowerDiff = False
    else:
        boolUseLowerDiff = True
    # Fetches the username and difficulty
    babylog.status('Mining for '+username)
    babylog.status('Using Lower Mining Difficulty: '+UseLowerDiff)
    cpus = os.cpu_count()
    for i in range(cpus):
        m = Miner(username, boolUseLowerDiff)
        m.start_mining()
        babylog.status('Mining Started on Thread {}!'.format(i))
        miners.append(m)
    return 'Wooohooo! Mining started! You can close this tab or window.'


@app.route('/stop')
def stop():
    try:
        for m in miners:
            m.stop_mining()
            babylog.status('Stopped Mining on thread!')
        return '3 ,2, 1 aaand Done! Mining stopped! You can close this tab or window.'
    except NameError:
        babylog.warn('Tried to stop a non existent miner')
        return 'The miner has not started yet.'


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
