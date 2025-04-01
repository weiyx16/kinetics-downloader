import os
import re

f = open('./filter_last.txt')
lines = f.readlines()
f.close()
for line in lines:
    file_tmp = line[:-1]
    video_id = file_tmp.split('/')[-1]
    idxxx = [m.start() for m in re.finditer('_', video_id)]
    video_id_ = video_id[:idxxx[-2]]
    tmp_ = video_id[idxxx[-2]+1:].split('.')[0]
    begin_ = int(tmp_.split('_')[0])
    end_ = int(tmp_.split('_')[1])
    command = f'ffmpeg -y -i -q"/data/home/v-yixwe/kinetics700_new/validate/tmp/{video_id_}.mp4" -ss {begin_} -t {end_} -strict -2 -c:v libx264 -c:a copy -threads 1 "{line[:-1]}"'
    os.system(command)
