# encoding utf-8

"""
# File      :eval_metrics
# Time      : 2023/5/22 15:30
# Author    : 郑茂宗
# version   :python 3.8
# Description: 计算文档分割任务的pk, rouge 分
"""
import json
import os
import sys
import jieba
from rouge_chinese import Rouge
import segeval as seg
from nltk.translate.bleu_score import  sentence_bleu, SmoothingFunction
import numpy as np


def get_boundary_and_label(content):
    base_split = [v.split(':') for v in content.split('|')]
    base_split = [v for v in base_split if len(v)>=2]
    seg_boundary = [int(i[0]) for i in base_split]
    seg_label = ' '.join([i[1] for i in base_split])
    return seg_boundary, seg_label


def pk_func(h, gold, window_size=-1):
    """
    :param gold: gold segmentation (item in the list contains the number of words in segment)
    :param h: hypothesis segmentation  (each item in the list contains the number of words in segment)
    :param window_size: optional
    :return: accuracy
    """
    if window_size != -1:
        false_seg_count, total_count = seg.pk(h, gold, window_size=window_size, return_parts=True)
    else:
        false_seg_count, total_count = seg.pk(h, gold, return_parts=True)

    if total_count == 0:
        # TODO: Check when happens
        false_prob = -1
    else:
        false_prob = float(false_seg_count) / float(total_count)

    return false_prob, total_count


def calcu_metric(preds, labels, window_size=-1, use_pk_weight=False):

    score_dict = {
        'rouge-1': [],
        'rouge-2': [],
        'rouge-l': [],
        'bleu-4': [],
        'pk': []
    }

    for pred, label in zip(preds, labels):
        if pred == '-1 : unknown' or label == '-1 : unknown': continue
        if len(pred) == 0: continue
        print(f' pred: {pred}, label: {label}')

        pred_boundary, pred_str = get_boundary_and_label(pred)
        label_boundary, label_str = get_boundary_and_label(label)
        print('------process---------')
        print('pred boundary', pred_boundary)
        print('label boundary', label_boundary)
        print('pred string', pred_str)
        print('label string', label_str)
        if len(label_str)==0 or len(pred_str) ==0: continue

        # caclue rouge:
        hypothesis = list(jieba.cut(pred_str))
        reference = list(jieba.cut(label_str))
        rouge = Rouge()
        scores = rouge.get_scores(' '.join(hypothesis), ' '.join(reference))
        result = scores[0]
        for k, v in result.items():
            score_dict[k].append(round(v["f"] * 100, 4))
        bleu_score = sentence_bleu([list(label_str)], list(pred_str), smoothing_function=SmoothingFunction().method3)
        score_dict["bleu-4"].append(round(bleu_score * 100, 4))

        # last sentence must be equal
        if pred_boundary[-1] < label_boundary[-1]:
            pred_boundary[-1] = label_boundary[-1]
        else:
            label_boundary[-1] = pred_boundary[-1]
        pred_boundary.insert(0, -1)
        pred_boundary = [pred_boundary[i] - pred_boundary[i - 1] for i in range(1, len(pred_boundary))]
        label_boundary.insert(0, -1)
        label_boundary = [label_boundary[i] - label_boundary[i-1] for i in range(1, len(label_boundary))]
        pk, total_count = pk_func(pred_boundary, label_boundary, window_size)
        if not use_pk_weight:
            score_dict['pk'].append(pk)
        else:
            score_dict['pk'].append([pk, total_count])

    for k, v in score_dict.items():
        if k != 'pk':
            score_dict[k] = float(np.mean(v))
        else:
            if not use_pk_weight:
                score_dict[k] = float(np.mean(v))
            else:
                score_dict[k] = sum([pw[0] * pw[1] for pw in v]) / sum([pw[1] for pw in v])

    return score_dict


# 需要合并数据，
# 删除为-1: unknown;
# 删除每次预测/label 最后一个
# 建立label 信息那?
def load_data(name):
    preds, labels = [], []
    with open(name, 'r') as f:
        for lines in f:
            content = json.loads(lines.strip())
            preds.append(content['predict'])
            labels.append(content['labels'])
    return preds, labels


def merge_list(value):
    if len(value) == 1:
        return value[0]
    rst = ""
    num = len(value)
    last_index = 0
    for ind, v in enumerate(value):
        if '-1 :' in v: continue
        if ind != num-1:
            del_last_v = "|".join(v.split('|')[:-1])
            print('del last v', del_last_v)
            if len(del_last_v)==0: continue
            del_less_v = [each_seg for each_seg in del_last_v.split('|') if  len(each_seg.split(':'))>=2 and int(each_seg.split(':')[0]) > last_index]
            print('del less v', del_less_v)
            if len(del_less_v) == 0: continue
            last_index = int(del_less_v[-1].split(":")[0])
            rst = rst + "|".join(del_less_v)
            rst = rst + '| '
        else:
            print('each predict label,', v)
            del_less_v = "|".join(
                    [each_seg for each_seg in v.split('|') if  len(each_seg.split(':'))>=2 and int(each_seg.split(':')[0]) > last_index])
            rst = rst + del_less_v
    if rst[-2:] == "| ":
        rst = rst[:-2]
    return rst


def load_rst_merge(name):
    preds_rst = {}
    labels_rst = {}

    with open(name, 'r') as f:
        for lines in f:
            content = json.loads(lines.strip())
            predict = content['predict']
            labels = content['labels']
            idx = content['idx']
            if idx not in preds_rst:
                preds_rst[idx] = [predict]
            else:
                preds_rst[idx].append(predict)

            if idx not in labels_rst:
                labels_rst[idx] = [labels]
            else:
                labels_rst[idx].append(labels)
    # merge result
    preds = [merge_list(v) for k, v in preds_rst.items()]
    labels = [merge_list(v) for k, v in labels_rst.items()]
    return preds, labels



def main():
    print('main preprocess')
    name = sys.argv[1]
    datasets_name= sys.argv[2]
    window_size = -1
    if datasets_name=='wiki727':
        window_size = 7 
    preds, labels = load_rst_merge(name)
    print('labels', labels[0])
    print('preds', preds[0])
    scores = calcu_metric(preds, labels, window_size)
    print(scores)


if __name__ == '__main__':
    main()



