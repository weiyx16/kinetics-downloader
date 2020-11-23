import json
import subprocess
import paramiko
import base64
import json


username = "t-zhuyao"
resource_group = "EAST_US"
machine_list = [7,8,9,10,11,12,13,14,15,16]

ip_json = json.load(open('./ip.json'))


for machine in machine_list:
    machine = 'VLdownload' + str(machine)
    password = "_" + machine
    cmd = []
    cmd.append("az vm create")
    cmd.append("-g {}".format(resource_group))
    cmd.append("-n {}".format(machine))
    cmd.append("--authentication-type password")
    cmd.append("--admin-username {}".format(username))
    cmd.append("--admin-password {}".format(password))
    cmd.append("--image Canonical:UbuntuServer:16.04-LTS:latest")
    cmd.append("--public-ip-address-allocation dynamic")
    cmd.append("--size Standard_A2m_v2")
    # return immediately
    # cmd.append("--no-wait")
    output = json.loads(subprocess.getoutput(" ".join(cmd)))
    ip = output['publicIpAddress']
    ip_json[machine] = ip
    print(output)

# update ip_list 
with open('./ip.json', 'w') as json_file:
    json.dump(ip_json, json_file)

# get new ssh rsa-key
key_json = json.load(open('./key.json'))
class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return str(obj, encoding='utf-8')
        return json.JSONEncoder.default(self, obj)

for machine in machine_list:
    machine = 'VLdownload' + str(machine)
    server = ip_json[machine]
    password = '_' + machine
    test_key = b'AAAAB3NzaC1yc2EAAAADAQABAAABAQDS4BkM8zhY+QBI8qch3LcoEc/YwKpdhAqxOJGV4/z6p6yoK8siyBc1gzSfXrBmCO5c4r7ujbhbB8RD7ECPRrvOPiDeJodequoSQzoxXs0KHBd41ehBlxSBoBIwnWZvOZB6ZigamYdq79Bb+f5giRYyWXHqyCEtphdh2ZNQgQl+Rf6wJQSL80SQe2EEgiUnnzsEcx2on1P59tC5swt6NOnSRCM+yf70qzmDkoacMexQVJc7ofmrZZkFhvYdPC9nFX1GHySL0CimeF1BByrPZzfPdewmK47m6a7WYFQCMOdfuznzYYNEk5uW6OlQGYnVapINr/rJ5hG7IZ4+JIIPAjB1'
    ssh = paramiko.SSHClient()
    key = paramiko.RSAKey(data=base64.b64decode(test_key))
    ssh.get_host_keys().add(server, 'ssh-rsa', key)
    try:
        ssh.connect(server, username=username, password=password)
    except paramiko.BadHostKeyException as e:
        new_rsa = e.key.get_base64()
        print("Fetch {} RSA: {}".format(machine, e.key.get_base64()))
    key_json[machine] = new_rsa

with open('./key.json', 'w') as json_file:
    json.dump(key_json, json_file, cls=MyEncoder)

# config new machine
for machine in machine_list:
    machine = 'VLdownload' + str(machine)
    server = ip_json[machine]
    password = '_' + machine

    ssh = paramiko.SSHClient()
    key = paramiko.RSAKey(data=base64.b64decode(key_json[machine]))
    ssh.get_host_keys().add(server, 'ssh-rsa', key)
    ssh.connect(server, username=username, password=password)

    # transfer file first
    ftp_client = ssh.open_sftp()
    ftp_client.put('./prepare.sh', '/home/t-zhuyao/prepare.sh')
    ftp_client.close()

    cmd = "mkdir /home/t-zhuyao/kinetics ;"
    cmd += "chmod +x /home/t-zhuyao/prepare.sh ;"
    cmd += "./prepare.sh ;"
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd)
    print(' machine : {}, error msg:'.format(machine))
    for line in ssh_stderr:
        print('... ' + line.strip('\n'))
    
    # tranfer new files
    ftp_client = ssh.open_sftp()
    ftp_client.put('./download_only.py', '/home/t-zhuyao/kinetics/download_only.py')
    ftp_client.put('./update.py', '/home/t-zhuyao/kinetics/update.py')
    # TODO: KINETICS CERTAIN
    machine_split = int(machine[len('VLdownload'):])
    split_file = f'/data/home/v-yixwe/kinetics-700/kinetics700_2020/train_split_{machine_split-1}.txt'
    ftp_client.put(split_file, '/home/t-zhuyao/kinetics/Fail_download_video.txt')
    ftp_client.close()

    cmd = "chmod 755 /home/t-zhuyao/kinetics/* ;"
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd)
    ssh.close()