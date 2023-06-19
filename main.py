from flask import Flask, render_template, request, redirect, url_for, session
import os
from pathlib import Path
import base64
import json
import logging
import sendKey
app = Flask(__name__)


managedPubkeyFile = 'data/managed_pubkey.json'

@app.route('/', methods=['GET'])
def index():
    if request.method == 'POST':
        print(request.form)
    elif request.method == 'GET':
        with open(managedPubkeyFile, 'r') as f:
            fr = f.read()
            if os.path.getsize(managedPubkeyFile) != 0:
                try:
                    ipkeyData = json.loads(fr)
                    lines = []

                    for key in ipkeyData.keys():
                        lines.append(key + ':' + ','.join(ipkeyData[key]))

                    return render_template('index.html', lines = lines)
                except json.decoder.JSONDecodeError:
                    return render_template('index.html', message = 'something error occured on json file loading', lines = '')
            else:
                return render_template('index.html', lines = '')


@app.route('/send', methods=['POST'])
def send():
    if request.method == 'POST':
        hostname = request.form['hostname']
        pubkey = request.form['pubkey']
        ipkeyData = {}
        keyList = []

        with open(managedPubkeyFile, 'r') as f:
            fr = f.read()
            if fr != '' and fr != '\n':
                ipkeyData = json.loads(fr)


        with open(managedPubkeyFile, 'w') as f:
            if hostname in ipkeyData.keys():
                keyList = ipkeyData[hostname]


            keyList.append(pubkey)
            ipkeyData[hostname] = keyList
            ipkeyDataJson = json.dumps(ipkeyData, indent=4)
            f.write(ipkeyDataJson)

            sendAgent = sendKey.SendKeyAgent(hostname, pubkey)
            sendAgent.sendToHost()

        return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
