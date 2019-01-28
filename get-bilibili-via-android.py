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
import commands
import copy


def replace_slash(input_str):
    output_str = ""
    for i in input_str:
        if i == "/":
            i = ""
        output_str = output_str + i
    return output_str


def video_process(video_path, video_output):
    """page data, one episode, one episode consist of several snapvideo"""
    print("start page_data: {}".format(video_path), file=sys.stderr)
    
    with open(os.path.join(video_path, 'entry.json')) as fh:
        entry = json.load(fh)
    title = replace_slash(entry['title'].encode('utf-8'))
    cover_url = entry['cover']
    page_data = entry['page_data']
    part = replace_slash(page_data['part'].encode('utf-8'))

    print("title: {}\tpart: {}".format(title, part), file=sys.stderr)

    img_name = "{}-{}.jpg".format(title, part)
    img_file = os.path.join(video_output, img_name)
    print("begin download cover_img: {}".format(cover_url), file=sys.stderr)
    urllib.urlretrieve(cover_url, img_file)

    # src folder
    video_src_folder_ = [os.path.join(video_path, x) for x in os.listdir(video_path) if os.path.isdir(os.path.join(video_path, x))][0]
    video_src_folder = copy.deepcopy(video_src_folder_)
    # dst folder
    video_dst_folder_temp = os.path.join(os.path.split(os.path.realpath(__file__))[0], "cache")
    if os.path.exists(video_dst_folder_temp):
        shutil.rmtree(video_dst_folder_temp)
    os.makedirs(video_dst_folder_temp)
    # dst video_name
    video_dst_name_final = "{}-{}.avi".format(title, part)
    video_dst_name_temp = "temp"
    # rename and copy sub_video to dst_folder
    video_sub_files = os.listdir(video_src_folder)
    video_sub_videos = [v for v in video_sub_files if v.endswith('.blv') ]
    for video_src_sub_name in video_sub_videos:
        video_src_sub_file = os.path.join(video_src_folder, video_src_sub_name)
        video_sub_idx = video_src_sub_name.split('.')[0]
        video_dst_sub_name = "{}-{}.flv".format(video_dst_name_temp, video_sub_idx)
        video_dst_sub_file = os.path.join(video_dst_folder_temp, video_dst_sub_name)
        print("begin copy file, dst: {}".format(video_dst_sub_name), file=sys.stderr)
        shutil.copyfile(video_src_sub_file, video_dst_sub_file)
    trans_and_concat(video_dst_folder_temp, video_dst_name_final, video_output)


def trans_and_concat(input_dir, new_name, output_dir):
    """snapvideo in input_dir -> concat -> output_dir"""
    # trans flv -> avi
    for snap_video in os.listdir(input_dir):
        if not snap_video.endswith(".flv"):
            continue
        snap_video_input = os.path.join(input_dir, snap_video)
        snap_video_output = snap_video_input[:-4] + ".avi"
        snap_video_input = snap_video_input.replace(" ", "\ ")
        snap_video_output = snap_video_output.replace(" ", "\ ")
        cmd_line = "ffmpeg -i {input} {output}".format(
            input=snap_video_input,
            output=snap_video_output
        )
        print("trans format: {}".format(new_name), file=sys.stderr)
        print(cmd_line, file=sys.stderr)
        commands.getstatusoutput(cmd_line)
    # concat
    snap_video_list = os.listdir(input_dir)
    snap_video_list = [os.path.join(input_dir, i) for i in snap_video_list if i.endswith(".avi")]
    snap_video_list.sort()
    if len(snap_video_list) == 1:
        shutil.move(os.path.join(input_dir, snap_video_list[0], os.path.join(input_dir, 'output.avi')))
        print("concat: {}".format(new_name), file=sys.stderr)
    else:
        inputs = "|".join(snap_video_list)
        outputs = os.path.join(input_dir, "output.avi")
        cmd_line = 'ffmpeg -i "concat:{input}" -c copy {output}'.format(
            input=inputs,
            output=outputs
        )
        print("concat: {}".format(new_name), file=sys.stderr)
        commands.getstatusoutput(cmd_line)
    shutil.move(os.path.join(input_dir, "output.avi"), os.path.join(output_dir, new_name))
    print("completed: {}".format(new_name), file=sys.stderr)


def main(video_input, video_output):
    video_folders = os.listdir(video_input)
    for video_folder in video_folders:
        if video_folder == ".DS_Store":
            continue
        # one episode: one episode consist of several snapvideo
        video_path = os.path.join(video_input, video_folder)
        video_process(video_path, video_output)
        # clear
        shutil.rmtree(os.path.join(os.path.split(os.path.realpath(__file__))[0], "cache"))


if __name__ == "__main__":
    root_input = sys.argv[1]
    root_output = sys.argv[2]
    for video_source in os.listdir(root_input):
        # one video: a video folder include several episodes
        video_input = os.path.join(root_input, video_source)
        if not os.path.isdir(video_input):
            continue
        main(video_input, root_output)