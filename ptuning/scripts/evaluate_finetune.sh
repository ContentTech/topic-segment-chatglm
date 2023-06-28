CHECKPOINT=wiki727-chatglm-6b-ft-1e-5
STEP=20000

CUDA_VISIBLE_DEVICES=0 python3 main.py \
    --do_predict \
    --tokenizer_flag \
    --validation_file /mnt/zhengmaozong.zmz/data/wiki_727_extractor_chatglm_900/dev/1.json  \
    --test_file /mnt/zhengmaozong.zmz/data/wiki_727_extractor_chatglm_900/test/1.json  \
    --max_eval_samples 496 \
    --overwrite_cache \
    --prompt_column content \
    --response_column summary \
    --preprocessing_num_workers 8 \
    --model_name_or_path ./output/$CHECKPOINT/checkpoint-$STEP  \
    --output_dir ./output/$CHECKPOINT \
    --overwrite_output_dir \
    --max_source_length 1024 \
    --max_target_length 128 \
    --per_device_eval_batch_size 16 \
    --predict_with_generate \
    --fp16_full_eval
