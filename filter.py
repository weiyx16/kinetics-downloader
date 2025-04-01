import pandas as pd
import numpy as np
import re
import os
import subprocess
from joblib import delayed
from joblib import Parallel

URL_BASE = 'https://www.youtube.com/watch?v='
if os.path.exists('./filter_last.txt'):
    with open('./filter_last.txt') as f:
        LAST_FILTERED = f.readlines()
    print(len(LAST_FILTERED))
else:
    LAST_FILTERED = None
df = pd.read_csv('/data/home/v-yixwe/kinetics-700/kinetics700_2020/train.csv')
class_name = df['label'].unique().tolist()
save_txt = './tmp_filter.txt'
save_txt_v2 = './filter_train_duration.txt'
print(len(class_name))
def stat_class(class_):
    print(class_)
    files = os.listdir('/data/home/v-yixwe/kinetics700_new/train/{}'.format(class_))
    for f in files:
        filepath = '/data/home/v-yixwe/kinetics700_new/train/{}/{}'.format(class_, f)
        file_tmp = filepath
        video_id = file_tmp.split('/')[-1]
        idxxx = [m.start() for m in re.finditer('_', video_id)]
        video_id = video_id[:idxxx[-2]]
        if LAST_FILTERED is not None and not (URL_BASE+video_id+'\n') in LAST_FILTERED:
            continue
        size = os.path.getsize(filepath)
        if size < 1024:
            subprocess.Popen(f"echo '123456' | sudo -S rm '{filepath}'", shell= True, stdout= subprocess.PIPE)
            with open(save_txt, 'a') as f:
                f.write(URL_BASE + video_id + '\n')
                #f.write(filepath+'\n')    
        continue
        Duration = subprocess.getoutput(f'ffmpeg -i "{filepath}" 2>&1 | grep "Duration"')
        Duration = Duration.split(',')[0]
        Duration = Duration.split(':')[-1]
        try:
            Duration = float(Duration)
        except:
            print(filepath)
            subprocess.Popen(f"echo '123456' | sudo -S rm '{filepath}'", shell= True, stdout= subprocess.PIPE)
            with open(save_txt, 'a') as f:
                f.write(URL_BASE + video_id + '\n')
                #f.write(filepath+'\n')
        else:
            if abs(Duration - 10.0) > 1:
                #subprocess.Popen(f"echo '123456' | sudo -S rm '{filepath}'", shell= True, stdout= subprocess.PIPE)
                with open(save_txt_v2, 'a') as f:
                    #f.write(URL_BASE + video_id + '\n')
                    f.write(filepath+'\n')
Parallel(n_jobs=8)(delayed(stat_class)(class_) for class_ in class_name)
os.system(f'mv /data/home/v-yixwe/kinetics-700/simple-downloader/{save_txt} /data/home/v-yixwe/kinetics-700/simple-downloader/filter_last.txt')

# statistic for test
#df = pd.read_csv('/data/home/v-yixwe/kinetics-700/kinetics700_2020/test.csv')
#video_name = df['youtube_id'].unique().tolist()
#print(len(video_name))
#files = os.listdir('/data/home/v-yixwe/kinetics700_new/test/tmp')
#print(len(files))
#f = open('./test_stat.txt', 'w')
#for file_ in files:
#    if 'tmp' not in file_:
#        f.write(file_+'\n')
#f.close()
