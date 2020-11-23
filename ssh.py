import paramiko
import base64
import json
import subprocess

machine_need_change_list = []
machine_need_run_list = [1,2,3,4]
is_run = False

ip_list = []
with open('./ip_list', 'r') as f:
    ips = f.readlines()
    for ip in ips:
        ip_list.append(ip[:-1])

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
    ip_list[idx] = out[0]['virtualMachine']['network']['publicIpAddresses'][0]['ipAddress']

# update ip_list 
with open('./ip_list', 'w') as f:
    for ip in ip_list:
        f.write(ip+'\n')

key_list = [b'AAAAB3NzaC1yc2EAAAADAQABAAABAQDA1wHTaqvnTWef3uwlTtbhF7IljfXsDp+IiwzJ55OiRWyeybpY35XYgVwNSE50N7WbLT13r8DIEqlmnMWC1jaCrgmkxQxVSe6DtPtr1uiFZCkrZFFSCNaOeMA/e6k9sPYyt/UDYa3H8BL1e/iZOqnFV1iZyBkdPw7q/RMiaKibaLBi9opmVdGAE65kRy7XUkWrMpNfBEOQZvyeZBV3Wfixb9g9TVLQzMThH3TE9trdxriGSiBP81F/qQ/xhqe+F4nemiuvV1GVtja9zcwne/1RsX4lEK76TQm9hXlTOTdb4OnYLSaCOioK7Sb4iU7xuzycZqINSlyN04svzJYinIUZ',
b'AAAAB3NzaC1yc2EAAAADAQABAAABAQDWbb0W0/eDBe5jq28Qy2jNUpIu2EgJ4bF3owrEIBGztlxCFv5V9DCovA1UVT9ld6KSjVaXsHW8tl1yU37/P9F5xbSwpPy7pd4RqB+akLldZ7Pcto/urdYkNu82XmYJI1o57rroiMk6RA6eYGzX/ENwdDybQb8YkQu6Kusy4fMM+S2seMOWlPTvch7aMVvJak3LQiJotYxh8qf37c8E5sd3zRRk+PD2Ctr6CmrM1rMI6O9afn2JNxPNR0HpFFDqzHPDJvB8Pkrgcopxz4WT1v6KlY/a9nvD6wI+b33xE10XLiqQpbwibdzdAuGzr473Ko0yWeUAZ1XIdDi/SlCPo1l3',
b'AAAAB3NzaC1yc2EAAAADAQABAAABAQCexJEXaSr0OEVdTE4UUQco0654zZKq5LO84CzgOGtVh4d9bVvN8CzP7mXXOaVAeULqoWjN2AJPLa42Dvl8TRFb4fSL7zbIo4ANHdqq789fyqE4zQdL2KdgRvanIaFMWw2XT4Ee80cvRh6xYbsAax8FUBkbQrfzTCmvixrX10apF993L5Bj48t0q644Ya7M3CHXP8o8TX1L3m4eJfTMD/P99CFSqy3eNRpHrmFH7IKl3Uxk0NTriKQ5+p4QJ3iQiYnCveT4T5NKwy6HnuwFn8Rmce2VQ2pqB0vevSzKUOGBkg5FWw8QasMm/wN1S9fG1ssXjjC30Upde+VRlPRcGyNX',
b'AAAAB3NzaC1yc2EAAAADAQABAAABAQDS4BkM8zhY+QBI8qch3LcoEc/YwKpdhAqxOJGV4/z6p6yoK8siyBc1gzSfXrBmCO5c4r7ujbhbB8RD7ECPRrvOPiDeJodequoSQzoxXs0KHBd41ehBlxSBoBIwnWZvOZB6ZigamYdq79Bb+f5giRYyWXHqyCEtphdh2ZNQgQl+Rf6wJQSL80SQe2EEgiUnnzsEcx2on1P59tC5swt6NOnSRCM+yf70qzmDkoacMexQVJc7ofmrZZkFhvYdPC9nFX1GHySL0CimeF1BByrPZzfPdewmK47m6a7WYFQCMOdfuznzYYNEk5uW6OlQGYnVapINr/rJ5hG7IZ4+JIIPAjB1',
]
for machine in machine_need_run_list:
    server = ip_list[machine-1]
    username = 't-zhuyao'
    password = '_VLdownload'+str(machine)
    ssh = paramiko.SSHClient()
    key = paramiko.RSAKey(data=base64.b64decode(key_list[machine-1]))
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
