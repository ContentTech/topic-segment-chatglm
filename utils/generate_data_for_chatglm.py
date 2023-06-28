# encoding utf-8

"""
# File      :generate_data_for_chatglm
# Time      : 2023/5/17 11:30
# Author    : 郑茂宗
# version   :python 3.8
# Description:
"""
import glob
import os
import sys
import json
from concurrent import futures

prompt = "please divide text delimited by triple backticks into multi coherent sections \
and describe each section with a brief text summary. \
Output format:  end sentence's index of each section and summary, seperated by |.\n"

max_token_num = 900


def get_total_num(sections):
    return sum([len(sent.split(' ')) for sent in sections])


def generate_data(elem):
    sections, sections_boundary, sections_title, id = elem['content'], elem['section_boundary'], elem['section_title'], elem['id']
    print(id)
    print(sections_boundary)
    print(sections_title)
    print('total section sentence', len(sections))
    total_words_num = get_total_num(sections)
    sections_index = [str(i) + " " + sent for i, sent in enumerate(sections)]
    if total_words_num < max_token_num:
        content = ' '.join(sections_index)
        labels = ' | '.join([str(b) + ' : ' + t for b, t in zip(sections_boundary, sections_title)])
        # print(content)
        # print(labels)
        return [{
            "content": f"{prompt}```{content}```",
            "summary": labels,
            "id": id
        }]
    else:
        rst = []
        # sections_index = [str(i)+" "+sent for i, sent in enumerate(sections)]
        sections_num_token = [len(sent.split(' ')) for sent in sections_index]
        start_index = 0
        end_index = 0
        total_index = len(sections_num_token)
        while end_index < total_index:
            # find last index
            cnt_token = 0
            while end_index < total_index and cnt_token < max_token_num:
                cnt_token += sections_num_token[end_index]
                end_index += 1
            # boundary
            split_section_boundary = [b  for b, t in zip(sections_boundary, sections_title) if b>=start_index and b<end_index]
            split_section_title = [ t for b, t in zip(sections_boundary, sections_title) if b>=start_index and b<end_index]
            split_section_boundary_ind = [ind_b for ind_b, b in enumerate(sections_boundary) if b>=start_index and b<end_index]
            # print(f'start index {start_index}, end index {end_index}')
            if len(split_section_boundary) == 0:
                content = ' '.join(sections_index[start_index:end_index])
                labels = '-1 : unknown'
                rst.append(
                    {
                        "content": f"{prompt}```{content}```",
                        "summary": labels,
                        "id": id
                    }
                )
                start_index = end_index
                end_index = start_index
            elif split_section_boundary[-1] != (end_index-1):
                print('boundary index, ', split_section_boundary_ind[-1])
                split_section_boundary.append(end_index-1)
                split_section_title.append(sections_title[split_section_boundary_ind[-1]+1])
                content = ' '.join(sections_index[start_index:end_index])
                labels = ' | '.join(str(b)+' : ' + t for b, t in zip(split_section_boundary, split_section_title))
                rst.append(
                    {
                        "content": f"{prompt}```{content}```",
                        "summary": labels,
                        "id": id
                    }
                )
                # update index
                start_index = split_section_boundary[-2] + 1
                end_index = start_index
            else:
                content = ' '.join(sections_index[start_index:end_index])
                labels = ' | '.join(str(b) + ' : ' + t for b, t in zip(split_section_boundary, split_section_title))
                rst.append(
                    {
                        "content": f"{prompt}```{content}```",
                        "summary": labels,
                        "id": id
                    }
                )
                start_index = split_section_boundary[-1] + 1
                end_index = start_index
        return rst


def load_org_data(input_name):
    if os.path.isdir(input_name):
        input_file = glob.glob(os.path.join(input_name + '*.json'))
        print('load input file number: {}'.format(len(input_file)))
        org_data = []
        for name in input_file:
            org_data.extend(json.load(open(name, 'r')))
        return org_data
    elif os.path.isfile(input_name):
        org_data = json.load(open(input_name, 'r'))
        return org_data


def main():
    input_dir = sys.argv[1]
    save_dir = sys.argv[2]
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)

    org_data = load_org_data(input_dir)
    # org_data= org_data
    total_num = len(org_data)
    print('load org data number:', len(org_data))

    cnt = 0
    save_num = 100000
    rst = []
    num_process_workers = 1
    with futures.ProcessPoolExecutor(max_workers=num_process_workers) as executor:
        for future in executor.map(generate_data, org_data):
            rst.extend(future)
            cnt += 1
            if cnt % 2000 == 0:
                print(f'process {cnt} of {total_num}')
            if cnt % save_num == 0:
                print(f'process {cnt} of {total_num}')
                save_name = os.path.join(save_dir, str(cnt//save_num) + '.json')
                with open(save_name, 'w') as f:
                    for elem in rst:
                        f.writelines(json.dumps(elem, ensure_ascii=False) + '\n')
                rst = []
    if len(rst) > 0:
        save_name = os.path.join(save_dir, str(cnt//save_num +1 ) + '.json')
        with open(save_name, 'w') as f:
            for elem in rst:
                f.writelines(json.dumps(elem, ensure_ascii=False) + '\n')


if __name__ == '__main__':
    main()










