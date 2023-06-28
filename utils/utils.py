#!/usr/bin/python
#****************************************************************#
# ScriptName: utils/utils.py
# Author: $SHTERM_REAL_USER@alibaba-inc.com
# Create Date: 2023-05-08 14:33
# Modify Author: $SHTERM_REAL_USER@alibaba-inc.com
# Modify Date: 2023-05-08 14:33
# Function: 
#***************************************************************#

import os
import sys
import json
import random


def random_select(name, top_k=2):
    rst = []
    with open(name) as f:
        for lines in f:
            lines = lines.strip()
            lines = json.loads(lines)
            text = lines['content'].split('Article:\n')[-1]
            label = lines['summary']
            label = "|".join(label.split('\n'))
            example = "input:" + text + "\noutput:\n" + label
            rst.append(example)
    num = len(rst)
    cnt = 0 
    few_shot_examples = []
    while cnt < top_k:
        index = random.randint(0, num-1)
        few_shot_examples.append(rst[index])
        cnt += 1
    return few_shot_examples



def select_by_length(name, top_k=30):
    rst = []
    with open(name) as f:
        for lines in f:
            lines = lines.strip()
            lines = json.loads(lines)
            text = lines['content'].split('Article:\n')[-1]
            label = lines['summary']
            label = "|".join(label.split('\n'))
            if len(label.split('|')) >=2 :
                example = "input:" + text + "\noutput:\n" + label
                rst.append(example)
    
    
    rst.sort(key=lambda x: len(x))

    return rst[:top_k]


def select_by_rule(name, top_k=2):
    # select must be as soon as much label 
    rst = []
    with open(name) as f:
        for lines in f:
            lines = lines.strip()
            lines = json.loads(lines)
            text = lines['content'].split('Article:\n')[-1]
            label = lines['summary']
            label = "|".join(label.split('\n'))
            if len(label.split('|')) >=3 :
                example = "input:" + text + "\noutput:\n" + label
                rst.append(example)
    
    
    rst.sort(key=lambda x: len(x))
    examples = []
    label_dicts = {}
    cnt = 0

    for content in rst:
        text, label = content.split('output:\n')
        labels = label.split('|')
        label_cnt = 0
        for each_label in labels:
            if each_label not in label_dicts:
                label_cnt += 1
        if label_cnt>=2:
            cnt += len(text.split(' '))
            if cnt>=700:
                return examples
            else:
                examples.append(content)
                for each_label in labels:
                    if each_label not in label_dicts:
                        label_dicts[each_label] = 1
                
    return examples
        



