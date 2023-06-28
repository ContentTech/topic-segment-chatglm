
LR=1e-5

MASTER_PORT=$(shuf -n 1 -i 10000-65535)

deepspeed --num_gpus=4 --master_port $MASTER_PORT main.py \
    --deepspeed  deepspeed.json \
    --do_train \
    --train_dir ../data/wiki727chatglm900/train \
    --validation_dir ../data/wiki727chatglm900/dev \
    --prompt_column content \
    --response_column summary \
    --overwrite_cache \
    --model_name_or_path ../models/chatglm-6b \
    --output_dir ./output/wiki727-chatglm-6b-ft-$LR-bk \
    --overwrite_output_dir \
    --max_source_length 1024 \
    --max_target_length 128 \
    --per_device_train_batch_size 8 \
    --per_device_eval_batch_size 2 \
    --gradient_accumulation_steps 2 \
    --predict_with_generate \
    --max_steps 40000 \
    --logging_steps 100 \
    --save_steps 30000 \
    --learning_rate $LR \
    --fp16

