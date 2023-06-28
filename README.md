# topic-segment-chatglm

The definition of topic segmentation task involves dividing a document into coherent segments, which is typically a prerequisite for tasks such as question retrieval, new knowledge-augmented LLM knowledge and others. This github presents a generative model-based approach for addressing the topic segmentation task and releases the chatglm-6b model finetuning on the wiki727 dataset. The model has also been validated to achieve excellent performance on the low-resource cross-domain conference dataset QMSum.

# dependences

```
torch==1.3.1+cu11.6
transformers==4.27.1
datasets==2.10.0

loralib
deepspeed==0.8.0
accelerate==0.16.0
bitsandbytes
peft==0.3.0
```

# Data

download wiki727 org datasets, and put it in data/wiki_727

```
cd utils

sh wiki_process.sh
```

# Train

wiki727k: using 4xA100 80G

```
sh scripts/ds_train_finetune.sh
```

qmsum train

using lora, using 1xA100 80G

```
sh scripts/train_lora.sh
```

# Test

wiki727k:

```
sh scripts/evaluate_finetune.sh
```

qmsum:

sh scripts/evaluate_lora.sh

wiki727k:

performance compare with other methods, chatglm+finetune models can be found in huggingface.co


|                         | Pk    |
| ------------------------- | ------- |
| CATS                    | 15.95 |
| StructuredSummarizaiton | 15.0  |
| chatglm+finetune(ours)  | 14.0  |

qmsum:

performance compare with other methods


|                         | Pk   |
| ------------------------- | ------ |
| DialogLM                | 38.0 |
| StructuredSummarizaiton | 32.8 |
| chatglm(wiki)-no train  | 37.7 |
| chatglm-lora            | 36.0 |
| chatglm(wiki)-lora      | 32.3 |

# Reference

code: https://github.com/THUDM/ChatGLM-6B

Inan, Hakan, Rashi Rungta, and Yashar Mehdad. "Structured Summarization: Unified Text Segmentation and Segment Labeling as a Generation Task." *arXiv preprint arXiv:2209.13759* (2022).
