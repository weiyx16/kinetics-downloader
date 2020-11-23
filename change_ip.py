import json
import subprocess

machine_list = [1]

for machine in machine_list:
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

