import torch
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
)
from peft import LoraConfig, prepare_model_for_kbit_training, get_peft_model
from trl import SFTTrainer, SFTConfig
import mlflow

MODEL_NAME = "Qwen/Qwen2.5-7B-Instruct"
DATASET_PATH = "data/finetune_dataset.jsonl"
OUTPUT_DIR = "outputs/qwen2.5-7b-lora-minutes"
MAX_SEQ_LENGTH = 2048  # transcripts truncated to fit; matches evaluate.py's 4000-char cap roughly

def main():
    # 4-bit quantization config (QLoRA)
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
    )

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        quantization_config=bnb_config,
        device_map="auto",
        torch_dtype=torch.bfloat16,
    )
    model = prepare_model_for_kbit_training(model)

    lora_config = LoraConfig(
        r=16,
        lora_alpha=32,
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=[
            "q_proj", "k_proj", "v_proj", "o_proj",
            "gate_proj", "up_proj", "down_proj",
        ],
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    # Load dataset (50 examples, "messages" chat format) and split
    dataset = load_dataset("json", data_files=DATASET_PATH, split="train")
    split = dataset.train_test_split(test_size=0.1, seed=42)  # 45 train / 5 eval
    train_dataset = split["train"]
    eval_dataset = split["test"]

    mlflow.set_experiment("meeting-minutes-llm-comparison")

    training_args = SFTConfig(
        output_dir=OUTPUT_DIR,
        num_train_epochs=2,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=8,
        gradient_checkpointing=True,
        optim="paged_adamw_8bit",
        learning_rate=2e-4,
        lr_scheduler_type="cosine",
	warmup_steps=2,
        logging_steps=1,
        eval_strategy="epoch",
        save_strategy="epoch",
        bf16=True,
        max_length=MAX_SEQ_LENGTH,
        packing=False,
        report_to="mlflow",
        run_name="qwen2.5-7b-qlora-finetune",
    )

    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        processing_class=tokenizer,
    )

    trainer.train()

    trainer.save_model(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)
    print(f"\nDone. LoRA adapter saved to {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
