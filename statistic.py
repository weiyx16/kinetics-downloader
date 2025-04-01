import pandas as pd
import numpy as np
import os

URL_BASE = 'https://www.youtube.com/watch?v='
df = pd.read_csv('/data/home/v-yixwe/kinetics-700/kinetics700_2020/train.csv')
class_name = df['label'].unique().tolist()
print(len(class_name))
#tmp_files = os.listdir('/data/home/v-yixwe/kinetics700_new/train/tmp')
#tmp_count = 0
#with open('./files_in_train_tmp.txt', 'w') as f:
#    for tmp_file in tmp_files:
#        if '.ytdl' not in tmp_file and '.part' not in tmp_file:
#            f.write(tmp_file + './')
#            tmp_count += 1
#print(tmp_count)
f = open('./train_stat.txt', 'w')
est = 0
acc = 0
for class_ in class_name:
    #print('{} / {}'.format(len(os.listdir('/data/home/v-yixwe/kinetics700_new/train/{}'.format(class_))), np.sum(list(df['label'] == class_))))
    _est = np.sum(list(df['label'] == class_))
    files = os.listdir('/data/home/v-yixwe/kinetics700_new/train/{}'.format(class_))
    _acc = len(files)
    est += _est
    acc += _acc
    with open('./filter_last.txt', 'a+') as ff:
        est_files = df[df['label'] == class_]['youtube_id']
        for est_file in est_files:
            founded = False
            for acc_file in files:
                if est_file in acc_file:
                    founded = True
                    continue
            #if not founded:
            #    for tmp_file in tmp_files:
            #        if est_file in tmp_file:
            #            founded = True
            #            continue
            if not founded:
                ff.write(URL_BASE+est_file+'\n')
    
    print('{}: {} / {}'.format(class_, _acc, _est))
    f.write('{}: {} / {}\n'.format(class_, _acc, _est))
f.close()

print(f'{acc} / {est}')

"""
# statistic for test
df = pd.read_csv('/data/home/v-yixwe/kinetics-700/kinetics700_2020/test.csv')
video_name = df['youtube_id'].unique().tolist()
print(len(video_name))
#tmp_files = os.listdir('/data/home/v-yixwe/kinetics700_new/test/tmp')
#print(len(tmp_files))
files = os.listdir('/data/home/v-yixwe/kinetics700_new/test')
print(len(files))
#all_files = tmp_files + files
f = open('./test_stat.txt', 'w')
for vid in files:
    f.write(vid + '\n')
f.close()
"""
"""
#f = open('./video_redownload_test.txt', 'w')
for vid in video_name:
    founded = False
    for file_ in all_files:
        if file_ != 'tmp' and '.part' not in file_ and '.ytdl' not in file_:
            if vid in file_:
                founded = True
                continue
    if not founded:
        f.write(URL_BASE+vid+'\n')
f.close()
"""
