# encoding utf-8

"""
# File      :wiki_process_mp
# Time      : 2023/5/16 17:08
# Author    : 郑茂宗
# version   :python 3.8
# Description:
"""
import json
import os
import sys
from pathlib2 import Path
from concurrent import futures

from wiki_loader import read_wiki_file


def read_wiki_file_wrapper(path):
    word2vec = None
    remove_preface_segment = True
    ignore_list = True
    remove_special_tokens = True
    return_as_sentences =True
    high_granularity = True
    only_letters = False
    data, section_targets, section_title, path = read_wiki_file(path,
                          word2vec=word2vec, remove_preface_segment=remove_preface_segment,
                          ignore_list=ignore_list, return_as_sentences=return_as_sentences,
                          high_granularity=high_granularity, only_letters=only_letters,
                          remove_special_tokens=remove_special_tokens)
    return {
        'content': data,
        'section_boundary': section_targets,
        'section_title': section_title,
        'id': "/".join(path.split('/')[4:])
    }


def get_files(path):
    all_objects = Path(path).glob('*/*/*/*')
    files = [str(p) for p in all_objects if p.is_file()]
    return files


def get_files_from_base(org_data):
    content = json.load(open(org_data))
    urls = [ '../../../data/' + '/'.join(l['id'].split('/')[1:]) for l in content] 
    return urls


def main():
    # base_img_list = sys.argv[1]
    input_dir = sys.argv[1]
    save_dir = sys.argv[2]
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
    textfiles = list(Path(input_dir).glob('*'))
    # textfiles = get_files_from_base(base_img_list)
    total_num = len(textfiles)
    print('load text files: {}'.format(len(textfiles)))
    cnt = 0
    save_num = 5000
    rst = []
    num_process_workers = 8  
    with futures.ProcessPoolExecutor(max_workers=num_process_workers) as executor:
        for future in executor.map(read_wiki_file_wrapper, textfiles):
            rst.append(future)
            cnt += 1
            if cnt % 2000 == 0:
                print(f'process {cnt} of {total_num}')
            if cnt % save_num == 0:
                print(f'process {cnt} of {total_num}')
                save_name = os.path.join(save_dir, str(cnt//save_num) + '.json')
                json.dump(rst, open(save_name, 'w'), indent=4, ensure_ascii=False)
                rst = []
    if len(rst) > 0:
        save_name = os.path.join(save_dir, str(cnt // save_num + 1) + '.json')
        json.dump(rst, open(save_name, 'w'), indent=4, ensure_ascii=False)


if __name__ == '__main__':
    main()

