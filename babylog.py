# Super small logging utility, maintains a log file.

from datetime import datetime as dt 

def tstamp():
    return str(dt.now()).split('.')[0]


def log2file(timestamp,flag,message):
    with open('miner.log','a') as f:
        sep='\t'
        print(timestamp,sep,flag,sep,message,file=f)
    

def start():
    with open('miner.log','a') as f:
        print('\n',r'    //\(oo)/\\       //\(oo)/\\          //\(oo)/\\',file=f)
    log2file(tstamp(),'BOOT','Started Dockerized mini miner')

def status(msg):
    log2file(tstamp(),'STAT',msg)

def warn(msg):
    log2file(tstamp(),'WARN',msg)

def error(msg):
    log2file(tstamp(),'ERR_',msg)

def fubar(msg):
    log2file(tstamp(),'FUCK',msg)

def stop(msg):
    log2file(tstamp(),'STOP',msg)




if __name__ == "__main__":
    start()