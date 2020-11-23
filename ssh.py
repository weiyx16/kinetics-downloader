import paramiko
import base64
import json
import subprocess

machine_need_change_list = []
machine_need_run_list = [6]
is_run = True

ip_json = json.load(open('./ip.json'))

for idx, machine in enumerate(machine_need_change_list):
    machine = 'VLdownload' + str(machine)
    out = json.loads(subprocess.getoutput("az vm nic list -g EAST_US --vm-name {}".format(machine)))
    nic = out[0]['id'].split('/')[-1]

    out = json.loads(subprocess.getoutput("az vm nic show -g EAST_US --vm-name {} --nic {}".format(machine, nic)))
    cfg = out['ipConfigurations'][0]['id'].split('/')[-1]
    pre_ip = out['ipConfigurations'][0]['publicIpAddress']['id'].split('/')[-1]

    subprocess.getoutput("az network public-ip update -g EAST_US -n {} --allocation-method Static".format(pre_ip))

    new_ip = machine + 'ip0'
    if pre_ip == new_ip:
        new_ip = pre_ip + 'du'
    subprocess.getoutput("az network public-ip create -g EAST_US -n {} --allocation-method Dynamic --version IPv4".format(new_ip))
    subprocess.getoutput("az network nic ip-config update --name {} --nic-name {} --resource-group EAST_US --public-ip-address {}".format(cfg, nic, new_ip))
    subprocess.getoutput("az network public-ip delete -g EAST_US -n {}".format(pre_ip))

    out = json.loads(subprocess.getoutput("az vm list-ip-addresses --resource-group EAST_US --name {}".format(machine)))
    print('Machine {} new IP: {}'.format(machine, out[0]['virtualMachine']['network']['publicIpAddresses'][0]['ipAddress']))
    ip_list[machine] = out[0]['virtualMachine']['network']['publicIpAddresses'][0]['ipAddress']

# update ip_list 
with open('./ip.json', 'w') as json_file:
    json.dump(ip_json, json_file)

key_json = json.load(open('./key.json'))
for machine in machine_need_run_list:
    machine = 'VLdownload' + str(machine)
    server = ip_json[machine]
    username = 't-zhuyao'
    password = '_' + machine
    ssh = paramiko.SSHClient()
    key = paramiko.RSAKey(data=base64.b64decode(key_json[machine]))
    ssh.get_host_keys().add(server, 'ssh-rsa', key)
    ssh.connect(server, username=username, password=password)
    ## run from list and save to dataset_split/tmp
    if is_run:
        cmd = "tmux kill-session -t 0 ;"
        cmd += "cd /home/t-zhuyao/kinetics ;"
        cmd += "python update.py ;"
        # https://janakiev.com/blog/python-background/
        # https://stackoverflow.com/questions/2975624/how-to-run-a-python-script-in-the-background-even-after-i-logout-ssh
        #cmd += "sudo rm /home/t-zhuyao/kinetics/output.log ;"
        #cmd += "nohup python3 -u /home/t-zhuyao/kinetics/download_only.py --input_file /home/t-zhuyao/kinetics/Fail_download_video.txt --output_dir /home/t-zhuyao/mycontainer/train/ --num-jobs 2 > /home/t-zhuyao/kinetics/output.log &"
        cmd += "tmux new-session -d -s 0 'python3 /home/t-zhuyao/kinetics/download_only.py --input_file /home/t-zhuyao/kinetics/Fail_download_video.txt --output_dir /home/t-zhuyao/mycontainer/train/ --num-jobs 2' ;"
    
    ## run from csv and save to certain_subdir
    #cmd = TODO, needed in yt8m
    else:
        ## monitor the status
        cmd = "cat /home/t-zhuyao/kinetics/my_tmp.txt | wc -l"
    
    ## used when reboot the machine during downloading Fail_download_list
    #cmd = "cd /home/t-zhuyao/kinetics & python update.py"
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd)
    if not is_run:
        for line in ssh_stdout:
            print('... ' + line.strip('\n'))
    print(' machine : {}, error msg:'.format(machine))
    for line in ssh_stderr:
        print('... ' + line.strip('\n'))
    ssh.close()
