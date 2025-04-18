import json
import subprocess


resource_group = "EAST_US"
machine_list = 'VLdownload'
machine_list = [machine_list+str(i) for i in range(4, 16)]
for machine in machine_list:
    cmd = []
    cmd.append("az vm delete")
    cmd.append("-g {}".format(resource_group))
    cmd.append("-n {}".format(machine))
    cmd.append("--yes")
    # force_delete
    # cmd.append("--force-deletion")
    # return immediately
    # cmd.append("--no-wait")
    subprocess.getoutput(" ".join(cmd))
    print("Done:", " ".join(cmd))
