import os

input_file = './Fail_download_video.txt'

with open(input_file, 'r') as f:
    lines = f.readlines()

tmplist = 'my_tmp.txt'
with open(tmplist, 'r') as f:
    LOADED = f.readlines()
with open(input_file, 'w') as f:
    for line in lines:
        if line not in LOADED:
            f.write(line)
os.system('rm {}'.format(tmplist))