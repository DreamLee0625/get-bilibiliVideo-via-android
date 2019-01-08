# coding:utf-8
"""
based on python2
"""
from __future__ import print_function
import sys
import os
import json
import urllib
import shutil
import cmd
import copy


OUTPUT_PATH = ""


def replace_slash(input_str):
    """
    replace all slash in string
    """
    output_str = ""
    for i in input_str:
        if i == "/":
            i = ""
        output_str = output_str + i
    return output_str


def video_process(video_path):
    # page data
    print("start page_data: {}".format(video_path), file=sys.stderr)
    
    with open(os.path.join(video_path, 'entry.json')) as fh:
        entry = json.load(fh)
    title = replace_slash(entry['title'].encode('utf-8'))
    cover_url = entry['cover']
    page_data = entry['page_data']
    part = replace_slash(page_data['part'].encode('utf-8'))

    print("title: {}\tpart: {}".format(title, part), file=sys.stderr)

    output_folder = os.path.join(OUTPUT_PATH, title)
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)

    img_name = "{}-{}.jpg".format(title, part)
    img_file = os.path.join(output_folder, img_name)
    print("begin download cover_img: {}".format(cover_url), file=sys.stderr)
    urllib.urlretrieve(cover_url, img_file)

    # src folder
    video_src_folder_ = [os.path.join(video_path, x) for x in os.listdir(video_path) if os.path.isdir(os.path.join(video_path, x))][0]
    video_src_folder = copy.deepcopy(video_src_folder_)
    # dst folder
    video_dst_folder_temp = os.path.join(output_folder, "{}-{}".format(title, part))
    if not os.path.exists(video_dst_folder_temp):
        os.makedirs(video_dst_folder_temp)
    # dst video_name
    video_dst_name = "{}-{}".format(title, part)
    # rename and copy sub_video to dst_folder
    video_sub_files = os.listdir(video_src_folder)
    video_sub_videos = [v for v in video_sub_files if v.endswith('.blv') ]
    for video_src_sub_name in video_sub_videos:
        video_src_sub_file = os.path.join(video_src_folder, video_src_sub_name)
        video_sub_idx = video_src_sub_name.split('.')[0]
        video_dst_sub_name = "{}-{}.flv".format(video_dst_name, video_sub_idx)
        video_dst_sub_file = os.path.join(video_dst_folder_temp, video_dst_sub_name)
        print("begin copy file, dst: {}".format(video_dst_sub_name), file=sys.stderr)
        shutil.copyfile(video_src_sub_file, video_dst_sub_file)


def main(root_path):
    video_folders = os.listdir(root_path)
    for video_folder in video_folders:
        if video_folder == ".DS_Store":
            continue
        video_path = os.path.join(root_path, video_folder)
        video_process(video_path)


if __name__ == "__main__":
    try:
        root_path = sys.argv[1]
    except:
        print("Please select a folder")
    if not OUTPUT_PATH:
        OUTPUT_PATH = root_path.rsplit('/', 1)[0]
    main(root_path)
