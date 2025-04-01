from joblib import delayed
from joblib import Parallel
import json
import urllib
import time
import os
import subprocess
import multiprocessing

URL_BASE = 'https://www.youtube.com/watch?v='
# vid.info.json

with open('./vid_list_tiny.txt') as f:
    vid_list = f.readlines()

global_count = len(vid_list)
def download_json(count, vid):
    data_root = '.'
    cmd = f"/usr/local/bin/youtube-dl {URL_BASE+vid} --write-info-json --skip-download --output {data_root}/infos/{vid}"
    output = subprocess.getoutput(cmd)
    # if os.path.isfile(f"{data_root}/infos/{vid}.info.json"):
    #     infos = json.load(open(f"{data_root}/infos/{vid}.info.json"))
    if count % 100 == 0:
        print(f"{count} / {global_count}")

def get_one_url(count, vid):
    data_root = '.'
    url_BASE = 'https://www.youtube.com/watch?v='
    url = url_BASE + vid
    t = time.time()
    import IPython
    IPython.embed()
    response = urllib.request.urlopen(url)
    r = response.read().decode('utf-8')
    r = r.split('\n')[19]
    part1 = r.split('"microformat":{"playerMicroformatRenderer":')[1].split('},"trackingParams')[0]
    part1 = json.loads(part1.replace('\n', ' '))
    title = part1['title']
    des = part1['description']
    cate = part1['category']
    uploadDate = part1['uploadDate']

    part2 = '[' + r.split('keywords":[')[1].split(']')[0] + ']'
    keywords = json.loads(part2.replace('\n', ' '))

    part3 = '[' + r.split('adaptiveFormats":[')[1].split(']')[0] + ']'
    part3 = json.loads(part3.replace('\n', ' '))
    width = 0
    height = 0
    for ele in part3:
        if 'width' in ele.keys():
            width = max(width, int(ele['width']))
            height = max(height, int(ele['height']))
    size = (width, height)

    pid = multiprocessing.current_process().pid
    with open(data_root + '/all_info/' + str(pid), 'a+') as f:
        json.dump([vid, title, des, cate, uploadDate, keywords, size], f)

    print(time.time() - t)

Parallel(n_jobs=1)(delayed(get_one_url)(count, vid[:-1]) for count, vid in enumerate(vid_list))