import time
import argparse
import os
import shutil
import subprocess
from urllib.parse import quote
# import pytube
from joblib import delayed
from joblib import Parallel

URL_BASE = 'https://www.youtube.com/watch?v='

VIDEO_EXTENSION = '.mp4'
VIDEO_EXTENSION_V2 = '.mkv'
VIDEO_FORMAT = 'mp4'
TOTAL_VIDEOS = 0
LOADED = []

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


def download_clip(row, label_to_dir, count, proxy=None):
    """
    Download full video from youtube.
    """
    URL = row[:-1] if row[-1:] == '\n' else row
    filename = URL[len(URL_BASE):]
    output_path = label_to_dir['tmp']

    # don't download if already exists
    input_filename = os.path.join(output_path, filename + VIDEO_EXTENSION)
    input_filenameV2 = os.path.join(output_path, filename + VIDEO_EXTENSION_V2)

    if not os.path.exists(input_filename) and not os.path.exists(input_filenameV2):
        print('Start downloading: ', filename)
        try:
            # pytube.YouTube(URL_BASE + filename).\
            #     streams.filter(subtype=VIDEO_FORMAT).first().\
            #     download(output_path, filename)
                    # , "--proxy", proxy
            # 'bestvideo[height<=480]+bestaudio/best[height<=480]'
            # https://l1ving.github.io/youtube-dl/#format-selection-examples
            subprocess.check_output(
            ["youtube-dl", URL, "--quiet", "-f",
            "bestvideo[ext={}]+bestaudio/best".format(VIDEO_FORMAT), "--output", os.path.join(output_path, filename + VIDEO_EXTENSION), "--no-continue"], stderr=subprocess.DEVNULL)
            print('Success downloading: ', filename)
            LOADED.append(URL)
        except: # subprocess.CalledProcessError:
            # with open(Flist, 'a+') as f:
            #     lines = f.readlines()
            #     if (URL_BASE + filename) not in lines:
            #         f.write(URL_BASE + filename+'\n')
            print('Failed: Unavailable video: ', filename)

    else:
        print('Already downloaded: ', filename)
    
    time.sleep(2)
    print('Processed %i out of %i' % (count + 1, TOTAL_VIDEOS))


def main(input_file, output_dir, num_jobs, proxy):
    global TOTAL_VIDEOS
    global LOADED

    with open(input_file, 'r') as f:
        lines = f.readlines()

    folders_names = ['tmp']
    label_to_dir = create_file_structure(path=output_dir,
                                         folders_names=folders_names)

    TOTAL_VIDEOS = (len(lines))
    # Download files by links from dataframe
    Parallel(n_jobs=num_jobs)(delayed(download_clip)(
            row, label_to_dir, count, proxy) for count, row in enumerate(lines))

    # Clean tmp directory
    # shutil.rmtree(label_to_dir['tmp'])

    with open(input_file, 'w') as f:
        for line in lines:
            if line not in LOADED:
                f.write(line+'\n')
    

if __name__ == '__main__':
    description = 'Script for downloading youtube link'
    p = argparse.ArgumentParser(description=description)
    p.add_argument('--input_file', type=str,
                   help=('Path to link file, containing links to youtube videos.\n'))
    p.add_argument('--output_dir', type=str,
                   help='Output directory where videos will be saved.\n'
                        'It will be created if doesn\'t exist')
    p.add_argument('--num-jobs', type=int, default=1,
                   help='Number of parallel processes for downloading and trimming.')
    p.add_argument('--proxy', type=str, default="socks5://127.0.0.1:10808",
                   help='Use the specified HTTP/HTTPS/SOCKS proxy. \n'
                        'To enable SOCKS proxy, specify a proper scheme.\n'
                        'For example socks5://127.0.0.1:1080/. \n'
                        'Pass in an empty string (--proxy "") for direct connection.')
    main(**vars(p.parse_args()))
