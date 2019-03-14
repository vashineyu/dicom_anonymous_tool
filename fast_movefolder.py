"""
Version date: 20190314
"""
import argparse
import glob
import os
import shutil

args = argparse.ArgumentParser(description="anonymization program - fast copy")
args.add_argument("--dicomdir_path", help="full path to DICOMDIR")
args = args.parse_args()
print(args)

with open(os.path.join(args.dicomdir_path, "anonymous_mapping.csv"), "r") as f:
    d = f.readlines()

convert_folder = os.path.join(args.dicomdir_path, "convert")
try:
    os.makedirs(convert_folder)
except:
    pass

for line in d[1:]:
    parse_line = line.split(",")
    selected = parse_line[0]
    patient_id = parse_line[1]
    dir_id = parse_line[2]
    if selected != '0':
        try:
            source_dir = glob.glob(os.path.join(args.dicomdir_path, "anonymous", patient_id, "dir{}*".format(dir_id) ))[0]
        except:
            continue
        target_dir = os.path.join(convert_folder, patient_id, os.path.basename(source_dir))
        # move it
        try:
            shutil.move(source_dir, target_dir)
            print("Move folder from {} to {}".format(source_dir, target_dir))
        except:
            print("Folder {} not found, check if it moved".format(source_dir))
            
print("All done")