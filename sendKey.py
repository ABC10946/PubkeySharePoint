import paramiko
import os
import sys


def checkHostExist(hostname, configText):
    lines = configText.split('\n')
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue

        if line.startswith('Host '):
            currentHost = line[5:]
            if currentHost == hostname:
                return True

    return False


class SendKeyAgent:
    def __init__(self, hostname, pubkeyList):
        self.hostname = hostname
        self.pubkeyList = pubkeyList
        configFile = os.path.expanduser('~/.ssh/config')
        with open(configFile) as f:
            configText = f.read()
            if not checkHostExist(self.hostname, configText):
                raise ValueError("Host not in ssh config file")



    def sendToHost(self):
        configFile = os.path.expanduser('~/.ssh/config')

        sshConfig = paramiko.SSHConfig()
        sshConfig.parse(open(configFile))

        config = sshConfig.lookup(self.hostname)

        with paramiko.SSHClient() as ssh:
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(
                    config['hostname'],
                    username=config['user'],
                    key_filename=config['identityfile'],
                    port=config['port']
            )
            command = "echo " + self.pubkeyList + ">> $HOME/.ssh/authorized_keys"
            ssh.exec_command(command)

