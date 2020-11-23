
import os
import shutil
import subprocess
from joblib import delayed
from joblib import Parallel
FTlist = "./Fail_trimmed_video_v2.txt"
tmplist = "./tmp_list.txt"
Slist = "./Success_trimmed_video.txt"
    
with open(FTlist) as f:
    lines = f.readlines()
num_jobs = 4
def run(command, count, LENGTH):
    
    input_filename = command.split('\"')[1]
    if ".mkv" in input_filename:
        output_filename = command.split('\"')[7]
    else:
        output_filename = command.split('\"')[3]
    if os.path.exists(output_filename):
        print('Already trimmed: ', output_filename)
        with open(Slist, 'a') as f:
            f.write(input_filename.split('/')[-1]+'\n')
    else:
        try:
            subprocess.check_output(command, shell=True, stderr=subprocess.DEVNULL)
            with open(Slist, 'a') as f:
                f.write(input_filename.split('/')[-1]+'\n')
            print('Successful trimming: ', input_filename.split('/')[-1])
            try:
                #subprocess.call("sudo rm {}".format(input_filename), shell=True)
                subprocess.Popen("echo '123456' | sudo -S rm {} ".format(input_filename) ,shell= True, stdout= subprocess.PIPE)
            except:
                print("ERROR: rm {}".format(input_filename))
        except: # subprocess.CalledProcessError:
            print('Error while trimming: ', input_filename.split('/')[-1])
            with open(tmplist, 'a+') as f:
                f.write(command+'\n')
    if count % 100 == 0:
        print('Processed %i out of %i' % (count + 1, LENGTH))
Parallel(n_jobs=num_jobs)(delayed(run)(line[:-1], idx, len(lines)) for idx, line in enumerate(lines))
subprocess.call(f"mv {tmplist} {FTlist}")
