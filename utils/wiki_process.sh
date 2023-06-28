
python wiki_process_mp.py ./data/wiki_727/train ./data/wiki_727_extractor/train
python generate_data_for_chatglm.py ./data/wiki_727_extractor/train ./data/wiki_727_extractor_chatglm_900/train
python tokenizer_data.py train ./data/wiki727chatglm900/train

python wiki_process_mp.py ./data/wiki_727/dev ./data/wiki_727_extractor/dev
python generate_data_for_chatglm.py ./data/wiki_727_extractor/dev ./data/wiki727chatglm900//dev


python wiki_process_mp.py ./data/wiki_727/test ./data/wiki_727_extractor/test
python generate_data_for_chatglm.py ./data/wiki_727_extractor/test ./data/wiki727chatglm900/test
