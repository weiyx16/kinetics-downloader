import pandas as pd
import time
import argparse
import os
import shutil
import subprocess
from urllib.parse import quote
# import pytube
from joblib import delayed
from joblib import Parallel

REQUIRED_COLUMNS_TRAINVAL = ['label', 'youtube_id', 'time_start', 'time_end', 'split']
REQUIRED_COLUMNS_TEST = ['youtube_id', 'time_start', 'time_end', 'split']
TRIM_FORMAT = '%06d'
URL_BASE = 'https://www.youtube.com/watch?v='

VIDEO_EXTENSION = '.mp4'
VIDEO_EXTENSION_V2 = '.mkv'
VIDEO_FORMAT = 'mp4'
TOTAL_VIDEOS = 0
Flist = "./Fail_download_video.txt"
FTlist = "./Fail_trimmed_video.txt"
Slist = "./Success_trimmed_video.txt"

def create_file_structure(path, folders_names):
    """
    Creates folders in specified path.
    :return: dict
        Mapping from label to absolute path folder, with videos of this label
    """
    mapping = {}
    if not os.path.exists(path):
        os.mkdir(path)
    for name in folders_names:
        dir_ = os.path.join(path, name)
        if not os.path.exists(dir_):
            os.mkdir(dir_)
        mapping[name] = dir_
    return mapping


def download_clip(row, label_to_dir, trim, count, proxy=None, is_test=False, use_cuda=False):
    """
    Download clip from youtube.
    row: dict-like objects with keys: ['label', 'youtube_id', 'time_start', 'time_end']
    'time_start' and 'time_end' matter if trim is True
    trim: bool, trim video to action ot not
    """

    if not is_test:
        label = row['label']
    filename = row['youtube_id']
    time_start = row['time_start']
    time_end = row['time_end']

    # if trim, save full video to tmp folder
    if not is_test:
        output_path = label_to_dir[label]
    else:
        output_path = label_to_dir['.']

    # don't download if already exists
    input_filename = os.path.join(output_path, filename + VIDEO_EXTENSION)
    input_filenameV2 = os.path.join(output_path, filename + VIDEO_EXTENSION_V2)
    start = str(time_start)
    end = str(time_end - time_start)
    output_filename = os.path.join(label_to_dir[label] if not is_test else label_to_dir['.'], filename + '_{}_{}'.format(start, end) + VIDEO_EXTENSION)

    if not os.path.exists(input_filename) and not os.path.exists(input_filenameV2):
        print('Start downloading: ', filename)
        #try:
            # pytube.YouTube(URL_BASE + filename).\
            #     streams.filter(subtype=VIDEO_FORMAT).first().\
            #     download(output_path, filename)
                    # , "--proxy", proxy
            # 'bestvideo[height<=480]+bestaudio/best[height<=480]'
            # https://l1ving.github.io/youtube-dl/#format-selection-examples
        output = subprocess.getoutput("youtube-dl {} --quiet -f best --output {} --no-continue".format(URL_BASE + filename, os.path.join(output_path, filename + VIDEO_EXTENSION)))
            #subprocess.check_output(
            #["youtube-dl", URL, "--quiet", "-f",
            #"bestvideo[ext={}]+bestaudio/best".format(VIDEO_FORMAT), "--output", os.path.join(output_path, filename + VIDEO_EXTENSION), "--no-continue"], stderr=subprocess.DEVNULL)
        if "YouTube said: Unable to extract video data" in output:
            print(' Warning Private Video: ', filename)
        else:
            if len(output) < 5:
                print('Success downloading: ', filename)
            else:
                with open(Flist, 'a+') as f:
                    lines = f.readlines()
                    if (URL_BASE + filename) not in lines:
                        f.write(URL_BASE + filename+'\n')
                # TOOOOO MANY Request
                print('Failed: Unavailable video: ', filename)
                if 'HTTP Error 429: Too Many Requests' in output:
                    print('429 occured!')
                    time.sleep(120)
    else:
        print('Already downloaded: ', filename)
    
    time.sleep(5)
    print('Processed %i out of %i' % (count + 1, TOTAL_VIDEOS))


def main(input_csv, output_dir, trim, num_jobs, proxy, cuda):
    global TOTAL_VIDEOS

    assert input_csv[-4:] == '.csv', 'Provided input is not a .csv file'
    links_df = pd.read_csv(input_csv)
    assert all(elem in REQUIRED_COLUMNS_TEST if 'test' in input_csv else REQUIRED_COLUMNS_TRAINVAL for elem in links_df.columns.values),\
        'Input csv doesn\'t contain required columns.'

    # Creates folders where videos will be saved later
    # Also create 'tmp' directory for temporary files
    if 'test' not in input_csv:
        folders_names = links_df['label'].unique().tolist() + ['tmp']
    else:
        folders_names = ['tmp', '.']
    label_to_dir = create_file_structure(path=output_dir,
                                         folders_names=folders_names)

    TOTAL_VIDEOS = links_df.shape[0]
    # Download files by links from dataframe
    Parallel(n_jobs=num_jobs)(delayed(download_clip)(
            row, label_to_dir, trim, count, proxy, use_cuda=cuda, is_test=True if 'test' in input_csv else False) for count, row in links_df.iterrows())

    # Clean tmp directory
    # shutil.rmtree(label_to_dir['tmp'])

if __name__ == '__main__':
    description = 'Script for downloading and trimming videos from Kinetics dataset.' \
                  'Supports Kinetics-400 as well as Kinetics-600 and Kinetics-700-2020.'
    p = argparse.ArgumentParser(description=description)
    p.add_argument('--input_csv', type=str,
                   help=('Path to csv file, containing links to youtube videos.\n'
                         'Should contain following columns:\n'
                         'label, youtube_id, time_start, time_end, split, is_cc'))
    p.add_argument('--output_dir', type=str,
                   help='Output directory where videos will be saved.\n'
                        'It will be created if doesn\'t exist')
    p.add_argument('--trim', action='store_true', dest='trim', default=False,
                   help='If specified, trims downloaded video, using values, provided in input_csv.\n'
                        'Requires "ffmpeg" installed and added to environment PATH')
    p.add_argument('--cuda', action='store_true', dest='cuda', default=False,
                   help='If specified, use cuda based ffmpeg to do the trim')
    p.add_argument('--num-jobs', type=int, default=1,
                   help='Number of parallel processes for downloading and trimming.')
    p.add_argument('--proxy', type=str, default="socks5://127.0.0.1:10808",
                   help='Use the specified HTTP/HTTPS/SOCKS proxy. \n'
                        'To enable SOCKS proxy, specify a proper scheme.\n'
                        'For example socks5://127.0.0.1:1080/. \n'
                        'Pass in an empty string (--proxy "") for direct connection.')
    main(**vars(p.parse_args()))
