base_model=../models/chatglm-6b-topic-segment
lora_weight=output/qmsum-chatglm-6b-lora-6e-4-r16/checkpoint-400/pytorch_model.bin
output_dir=output/qmsum-chatglm-6b-lora-6e-4-r16/

CUDA_VISIBLE_DEVICES=0 python3 main_lora.py \
    --validation_file ../data/QMSum_chatglm_900/dev/1.json \
    --do_predict \
    --tokenizer_flag \
    --test_file ..//data/QMSum_chatglm_900/test/1.json \
    --prompt_column content \
    --response_column summary \
    --overwrite_cache \
    --model_name_or_path  $base_model \
    --finetuning_lora_weight $lora_weight \
    --output_dir $output_dir \
    --overwrite_output_dir \
    --max_source_length 1024 \
    --max_target_length 128 \
    --per_device_eval_batch_size 8 \
    --gradient_accumulation_steps 1 \
    --predict_with_generate \
    --max_steps 300 \
    --logging_steps 10 \
    --save_steps 100

