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
FTlist = "./Fail_trimmed_video_v2.txt"
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
        output_path = label_to_dir['tmp'] if trim else label_to_dir[label]
    else:
        output_path = label_to_dir['tmp'] if trim else label_to_dir['.']

    # don't download if already exists
    input_filename = os.path.join(output_path, filename + VIDEO_EXTENSION)
    input_filenameV2 = os.path.join(output_path, filename + VIDEO_EXTENSION_V2)
    start = str(time_start)
    end = str(time_end - time_start)
    output_filename = os.path.join(label_to_dir[label] if not is_test else label_to_dir['.'], filename + '_{}_{}'.format(start, end) + VIDEO_EXTENSION)

    if not os.path.exists(input_filename) and not os.path.exists(input_filenameV2):
        pass
    else:
        # Take video from tmp folder and put trimmed to final destination folder
        # better write full path to video
        if os.path.exists(output_filename):
            print('Already trimmed: ', filename)
            with open(Slist, 'a+') as f:
                lines = f.readlines()
                if (filename + '_{}_{}'.format(start, end)) not in lines:
                    f.write(filename + '_{}_{}'.format(start, end)+'\n')
                
        elif os.path.exists(input_filename):
            if use_cuda:
                command = 'ffmpeg -hwaccel cuvid -y -i "{input_filename}" ' \
                        '-ss {time_start} ' \
                        '-t {time_end} ' \
                        '-c:v h264_nvenc -c:a copy -threads 1 ' \
                        '"{output_filename}"'.format(
                            input_filename=input_filename,
                            time_start=start,
                            time_end=end,
                            output_filename=output_filename) 
            else:
                command = 'ffmpeg -i "{input_filename}" ' \
                        '-ss {time_start} ' \
                        '-t {time_end} ' \
                        '-c:v libx264 -c:a copy -threads 1 ' \
                        '"{output_filename}"'.format(
                            input_filename=input_filename,
                            time_start=start,
                            time_end=end,
                            output_filename=output_filename)
        else:
            input_filename = input_filenameV2
            if use_cuda: #'-strict -2 ' \
                command = 'ffmpeg -hwaccel cuvid -y -i "{input_filename}" ' \
                        '-ss {time_start} ' \
                        '-t {time_end} ' \
                        '-c:v h264_nvenc -c:a copy -threads 1 ' \
                        '"{output_filenameV2}" && ffmpeg -i "{output_filenameV2}" -map 0 -c copy -c:a aac "{output_filename}" && echo "123456" | sudo -S rm "{output_filenameV2}"' .format(
                            input_filename=input_filename,
                            time_start=start,
                            time_end=end,
                            output_filenameV2=os.path.join(label_to_dir[label] if not is_test else label_to_dir['.'], filename + '_{}_{}'.format(start, end) + VIDEO_EXTENSION_V2),
                            output_filename=output_filename,)
            else:
               command = 'ffmpeg -i "{input_filename}" ' \
                        '-ss {time_start} ' \
                        '-t {time_end} ' \
                        '-strict -2 ' \
                        '-c:v libx264 -c:a copy -threads 1 ' \
                        '"{output_filenameV2}" && ffmpeg -i "{output_filenameV2}" -map 0 -strict -2 -c copy -c:a aac "{output_filename}" && sudo rm "{output_filenameV2}"' .format(
                            input_filename=input_filename,
                            time_start=start,
                            time_end=end,
                            output_filenameV2=os.path.join(label_to_dir[label] if not is_test else label_to_dir['.'], filename + '_{}_{}'.format(start, end) + VIDEO_EXTENSION_V2),
                            output_filename=output_filename,)
        if not os.path.exists(output_filename):
            print('Start trimming: ', filename)
            # Construct command to trim the videos (ffmpeg required).
            try:
                subprocess.check_output(command, shell=True, stderr=subprocess.DEVNULL)
                with open(Slist, 'a') as f:
                    f.write(filename + '_{}_{}'.format(start, end)+'\n')
                print('Successful trimming: ', filename)
                try:
                    #subprocess.call("sudo rm {}".format(input_filename), shell=True)
                    subprocess.Popen("echo '123456' | sudo -S rm {} ".format(input_filename) ,shell= True, stdout= subprocess.PIPE)
                except:
                    print("ERROR: rm {}".format(input_filename))
            except: # subprocess.CalledProcessError:
                print('Error while trimming: ', filename)
                with open(FTlist, 'a+') as f:
                    lines = f.readlines()
                    if command not in lines:
                        f.write(command+'\n')
    if count % 100 == 0:
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

