#!/usr/bin/python
#****************************************************************#
# ScriptName: tokenizer_data.py
# Author: $SHTERM_REAL_USER@alibaba-inc.com
# Create Date: 2023-05-19 11:38
# Modify Author: $SHTERM_REAL_USER@alibaba-inc.com
# Modify Date: 2023-05-19 11:38
# Function: 
#***************************************************************#
import os
import sys

from transformers import AutoTokenizer
from datasets import load_dataset

dataset_name = sys.argv[1]
save_dir = sys.argv[2]
data_files = f'../../../data/wiki_727_extractor_chatglm_900/{dataset_name}/*.json'

max_source_length = 1024
max_target_length = 128

dataset = load_dataset('json', data_files=data_files)
print(dataset)

train_dataset = dataset['train']
samples = train_dataset.shuffle(seed=42).select(range(20))
print(samples[0])

# add length
def computer_length_batch(example):
    return {'summary_length': [ len(i.split(' ')) for i in example['summary']],
        'content_length': [ len(i.split(' ')) for i in example['content']] }

dataset = dataset.map(computer_length_batch, batched=True)


column_names = train_dataset.column_names
prompt_column  = "content"
response_column = "summary"
history_column = None
prefix = ""

# filter long length text
train_dataset = dataset['train']
total_num = len(train_dataset)
print('total number: ', total_num)
filter_train_dataset = train_dataset.filter(lambda x: x['summary_length'] < max_target_length and x['content_length'] < max_source_length)
low_num = len(filter_train_dataset)
print('ratio {}, {}/{}'.format(low_num/total_num, low_num, total_num))

model_name = '../../chatglm-6b/'
tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)


def preprocess_function_train(examples):
    max_seq_length = max_source_length + max_target_length

    model_inputs = {
        "input_ids": [],
        "labels": [],
    }
    for i in range(len(examples[prompt_column])):
        if examples[prompt_column][i] and examples[response_column][i]:
            query, answer = examples[prompt_column][i], examples[response_column][i]

            if history_column is None:
                prompt = query
            else:
                prompt = ""
                history = examples[history_column][i]
                for turn_idx, (old_query, response) in enumerate(history):
                    prompt += "[Round {}]\n问：{}\n答：{}\n".format(turn_idx, old_query, response)
                prompt += "[Round {}]\n问：{}\n答：".format(len(history), query)

            prompt = prefix + prompt
            a_ids = tokenizer.encode(text=prompt, add_special_tokens=False)
            b_ids = tokenizer.encode(text=answer, add_special_tokens=False)

            if len(a_ids) > max_source_length - 1:
                a_ids = a_ids[: max_source_length - 1]

            if len(b_ids) > max_target_length - 2:
                b_ids = b_ids[: max_target_length - 2]

            input_ids = tokenizer.build_inputs_with_special_tokens(a_ids, b_ids)

            context_length = input_ids.index(tokenizer.bos_token_id)
            mask_position = context_length - 1
            labels = [-100] * context_length + input_ids[mask_position+1:]
            
            pad_len = max_seq_length - len(input_ids)
            input_ids = input_ids + [tokenizer.pad_token_id] * pad_len
            labels = labels + [tokenizer.pad_token_id] * pad_len
            if True:
                labels = [(l if l != tokenizer.pad_token_id else -100) for l in labels]

            model_inputs["input_ids"].append(input_ids)
            model_inputs["labels"].append(labels)

    return model_inputs


tokenizer_datasets = filter_train_dataset.map(
               preprocess_function_train,
               batched=True,
               num_proc=8,
               remove_columns=column_names,
               )

def print_dataset_example(example):
    print("input_ids",example["input_ids"])
    print("inputs", tokenizer.decode(example["input_ids"]))
    print("label_ids", example["labels"])
    print("labels", tokenizer.decode(example["labels"]))
print_dataset_example(tokenizer_datasets[0])

tokenizer_datasets.save_to_disk(save_dir + '/' + dataset_name)
