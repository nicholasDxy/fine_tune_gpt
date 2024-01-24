import json
import os
import sys
import math
import torch
import argparse
import textwrap
import transformers
from peft import PeftModel
from transformers import GenerationConfig, TextStreamer, BitsAndBytesConfig
from llama_attn_replace import replace_llama_attn

PROMPT_DICT = {
    "prompt_no_input": (
        "Below is an instruction that describes a task. "
        "Write a response that appropriately completes the request.\n\n"
        "### Instruction:\n{instruction}\n\n### Response:"
    ),
    "prompt_no_input_llama2": (
        "<s>[INST] <<SYS>>\n"
        "You are a helpful, respectful and honest assistant. Always answer as helpfully as possible, while being safe.  Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature.\n\n"
        "If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information.\n"
        "<</SYS>> \n\n {instruction} [/INST]"
    ),
     "prompt_llama2": "<s><<SYS>>\n{sys}<</SYS>>\n[INST]{instruction}[/INST]"
}

def parse_config():
    parser = argparse.ArgumentParser(description='arg parser')
    parser.add_argument('--material', type=str, default="")
    parser.add_argument('--question', type=str, default="")
    parser.add_argument('--base_model', type=str, default="/data1/pretrained-models/llama-7b-hf")
    parser.add_argument('--cache_dir', type=str, default="./cache")
    parser.add_argument('--context_size', type=int, default=-1, help='context size during fine-tuning')
    parser.add_argument('--flash_attn', type=bool, default=False, help='')
    parser.add_argument('--temperature', type=float, default=0.6, help='')
    parser.add_argument('--top_p', type=float, default=0.9, help='')
    parser.add_argument('--max_gen_len', type=int, default=512, help='')
    parser.add_argument('--peft_model', type=str, default='/home/ec2-user/SageMaker/LongLoRA/checkpoints', help='')
    args = parser.parse_args()
    return args


def main(args):
    if args.flash_attn:
        replace_llama_attn(inference=True)

    # Set RoPE scaling factor
    config = transformers.AutoConfig.from_pretrained(
        args.base_model,
        token = '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',
        cache_dir=args.cache_dir,
    )

    orig_ctx_len = getattr(config, "max_position_embeddings", None)
    if orig_ctx_len and args.context_size > orig_ctx_len:
        scaling_factor = float(math.ceil(args.context_size / orig_ctx_len))
        config.rope_scaling = {"type": "linear", "factor": scaling_factor}

    # Load model and tokenizer
    model = transformers.AutoModelForCausalLM.from_pretrained(
        args.base_model,
        token = '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',
        config=config,
        cache_dir=args.cache_dir,
        torch_dtype=torch.float16,
        device_map="auto",
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16
        )
    )
    model.resize_token_embeddings(32001,8)
    model = PeftModel.from_pretrained(
        model,
        args.peft_model,
        device_map="auto",
        torch_dtype=torch.float16,
    )
    

    tokenizer = transformers.AutoTokenizer.from_pretrained(
        args.base_model,
        token = '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',
        cache_dir=args.cache_dir,
        model_max_length=args.context_size if args.context_size > orig_ctx_len else orig_ctx_len,
        padding_side="right",
        use_fast=False,
    )

    model.eval()
    if torch.__version__ >= "2" and sys.platform != "win32":
        model = torch.compile(model)
#     respond = build_generator(model, tokenizer, temperature=args.temperature, top_p=args.top_p,
#                               max_gen_len=args.max_gen_len, use_cache=True)

    # material = read_txt_file(args.material)
    prompt_no_input = PROMPT_DICT["prompt_llama2"]
    with open('/home/ec2-user/SageMaker/LongLoRA/human_valid_output.json', 'r', encoding='utf-8') as read_file:
        json_data = json.load(read_file)
    prompt = prompt_no_input.format_map(json_data[0])
#     prompt = prompt_no_input.format_map({"instruction": "\n%s"%args.question})
    print(prompt)
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
#     inputs = tokenizer('What is the capital of France?', return_tensors="pt").to(model.device)

#     output = respond(prompt=prompt)
    

    with torch.no_grad():
        output = model.generate(**inputs, temperature=0.6, top_p=0.9, max_new_tokens=args.max_gen_len)
#     output = model.generate(**inputs, temperature=0.6, top_p=0.9, max_new_tokens=500)
    output= tokenizer.decode(output[0], skip_special_tokens=True)
#     print(output)
    return output

if __name__ == "__main__":
    args = parse_config()
    output = main(args)
    print(output)