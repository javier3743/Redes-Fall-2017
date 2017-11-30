#!/usr/bin/python3

import requests
import json
import subprocess
import datetime
#
# Monitoring Upload
#

who = requests.get('http://localhost:5000/who')
os = requests.get('http://localhost:5000/os/kernel')
swap = requests.get('http://localhost:5000/swap/so')
mem = requests.get('http://localhost:5000/mem/free')
cpu = requests.get('http://localhost:5000/cpu/sy')
disk = requests.get ('http://localhost:5000/partition')
uploadtime = {'uploadtime' :'{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())}
dicSwap = swap.json()
dicWho = who.json()
dicOs = os.json()
dicMem = mem.json()
dicCpu = cpu.json()
dicDisk = disk.json()
payload = {**dicWho, **dicOs, **dicSwap, **dicMem, **dicCpu, **dicDisk, **uploadtime}
postdisk = requests.post('https://manage-remote.herokuapp.com/monitoring', json = payload)
print (postdisk.status_code)

#
# Transmission Magnetlinks requests
#

urls = requests.get('https://manage-remote.herokuapp.com/get-requests')
dicUrls = urls.json()
values = dicUrls.values()
for magnet in values:
    subprocess.check_output(["transmission-remote", "-a", magnet])

#
# Transmission Magnetlinks status
#

keys = ['ID', 'progress', 'downloaded', 'size' ,'ETA', 'speedup', 'speeddown', 'ratio', 'status-1', 'name']
keysN = ['ID', 'progress', 'downloaded' ,'ETA', 'speedup', 'speeddown', 'ratio', 'status-1', 'name']
keysA = ['ID', 'progress', 'downloaded', 'size', 'ETA', 'speedup', 'speeddown', 'ratio', 'status-1', 'status-2', 'status-3', 'name']
def list (value):
    transmission = subprocess.Popen(['transmission-remote' , '-l'],stdout = subprocess.PIPE)
    tail = subprocess.Popen(['tail', '-n' , '+2'], stdin = transmission.stdout,stdout = subprocess.PIPE)
    tr = subprocess.Popen(['tr', '-s' , ' '], stdin = tail.stdout, stdout = subprocess.PIPE)
    output = subprocess.check_output(['cut' , '-d', '\n', '-f', str(value)], stdin = tr.stdout).decode('utf-8').strip()
    return output



def generate():
    x = 1
    uploadtime = {'uploadtime' :'{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())}
    payload = []
    while True:
        aux = list(x)
        if ((aux.find("Sum:")) != -1)  :
            break
        else:
            x += 1
        data = {**uploadtime}
        if ((aux.find("Up & Down")) != -1):
            values = aux.split(" ")
            for i in range (0 , 11):
                data[keysA[i]] = values[i]
        elif ((aux.find("None")) != -1):
            values = aux.split(" ")
            for j in range (0, 9):
                data[keysN[j]] = values[j]
        else:
            values = aux.split(" ")
            for j in range (0, 10):
                data[keys[j]] = values[j]
        payload.append(data)
    return payload


post = requests.post('https://manage-remote.herokuapp.com/status', json = generate())
print (post.status_code)
