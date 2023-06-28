LR=6e-4
base_model=../models/chatglm-6b-topic-segment

CUDA_VISIBLE_DEVICES=0 python3 main_lora.py \
    --do_train \
    --train_file ..//data/QMSum_chatglm_900/train/1.json \
    --do_eval \
    --validation_file ../data/QMSum_chatglm_900/dev/1.json \
    --tokenizer_flag \
    --test_file ../data/QMSum_chatglm_900/test/1.json \
    --prompt_column content \
    --response_column summary \
    --overwrite_cache \
    --model_name_or_path $base_model \
    --output_dir output/qmsum-chatglm-6b-lora-$LR-r16 \
    --overwrite_output_dir \
    --max_source_length 1024 \
    --max_target_length 128 \
    --per_device_train_batch_size 8 \
    --per_device_eval_batch_size 4 \
    --gradient_accumulation_steps 1 \
    --predict_with_generate \
    --max_steps 600 \
    --logging_steps 10 \
    --save_steps 100 \
    --learning_rate $LR

