# encoding utf-8

"""
# File      :wiki_utils.py
# Time      : 2023/5/16 16:09
# Author    : 郑茂宗
# version   :python 3.8
# Description: 参考 https://github.com/koomri/text-segmentation
"""

segment_seperator = "========"


def get_segment_seperator(level,name):
    return segment_seperator + "," + str(level) + "," +name


def get_seperator_foramt(levels = None):
    level_format = '\d' if levels == None else '['+ str(levels[0]) + '-' + str(levels[1]) + ']'
    seperator_fromat = segment_seperator + ',' + level_format + ",.*?\."
    return seperator_fromat


def is_seperator_line(line):
    return line.startswith(segment_seperator)


def get_segment_level(seperator_line):
    return int(seperator_line.split(',')[1])


def get_segment_name(seperator_line):
    return seperator_line.split(',')[2]


def get_list_token():
    return "***LIST***"


def get_formula_token():
    return "***formula***"


def get_codesnipet_token():
    return "***codice***"


def get_special_tokens():
    special_tokens = []
    special_tokens.append(get_list_token())
    special_tokens.append(get_formula_token())
    special_tokens.append(get_codesnipet_token())
    return special_tokens


