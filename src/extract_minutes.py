import ollama
import json
import torch

# Lazy-loaded, module-level cache so the fine-tuned model is only loaded once
_finetuned_model = None
_finetuned_tokenizer = None

BASE_MODEL_NAME = "Qwen/Qwen2.5-7B-Instruct"
ADAPTER_PATH = "outputs/qwen2.5-7b-lora-minutes"


def _build_prompt(transcript: str) -> str:
    return f"""You are an assistant that converts meeting transcripts into structured minutes.
Transcript:
\"\"\"{transcript}\"\"\"
Return ONLY valid JSON with this exact structure, no other text before or after:
{{
  "summary": "2-3 sentence summary of the meeting",
  "key_topics": ["topic1", "topic2"],
  "decisions": ["decision1"],
  "action_items": [{{"task": "description", "owner": "unknown", "deadline": "unknown"}}]
}}
"""


def _parse_json_output(raw_output: str) -> dict:
    raw_output = raw_output.strip()
    if raw_output.startswith("```"):
        raw_output = raw_output.split("```")[1]
        if raw_output.startswith("json"):
            raw_output = raw_output[4:]
        raw_output = raw_output.strip()
    try:
        return json.loads(raw_output)
    except json.JSONDecodeError:
        print("Warning: model did not return valid JSON. Raw output:")
        print(raw_output)
        return {"error": "invalid_json", "raw_output": raw_output}


def _load_finetuned_model():
    global _finetuned_model, _finetuned_tokenizer
    if _finetuned_model is not None:
        return _finetuned_model, _finetuned_tokenizer

    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    from peft import PeftModel

    print("Loading base model + LoRA adapter (first call only)...")
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
    )
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_NAME)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    base_model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL_NAME,
        quantization_config=bnb_config,
        device_map="auto",
        torch_dtype=torch.bfloat16,
    )
    model = PeftModel.from_pretrained(base_model, ADAPTER_PATH)
    model.eval()

    _finetuned_model = model
    _finetuned_tokenizer = tokenizer
    return model, tokenizer


def _extract_minutes_finetuned(transcript: str) -> dict:
    model, tokenizer = _load_finetuned_model()
    prompt = _build_prompt(transcript)
    messages = [{"role": "user", "content": prompt}]
    inputs = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        return_tensors="pt",
        return_dict=True,
    ).to(model.device)
    with torch.no_grad():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=512,
            temperature=0.3,
            do_sample=True,
            pad_token_id=tokenizer.pad_token_id,
        )
    generated_ids = output_ids[0][inputs["input_ids"].shape[1]:]
    raw_output = tokenizer.decode(generated_ids, skip_special_tokens=True)
    return _parse_json_output(raw_output)


def extract_minutes(transcript: str, model_name: str = "qwen2.5") -> dict:
    """
    Step 6: LLM-based Information Extraction
    Takes a speaker-labeled transcript, returns structured meeting minutes.
    """
    if model_name == "qwen2.5-finetuned":
        return _extract_minutes_finetuned(transcript)

    prompt = _build_prompt(transcript)
    response = ollama.chat(
        model=model_name,
        messages=[{"role": "user", "content": prompt}]
    )
    raw_output = response["message"]["content"]
    return _parse_json_output(raw_output)


if __name__ == "__main__":
    from clean_ner import merge_transcript_with_speakers
    import whisper
    from diarize import diarize_audio
    model = whisper.load_model("base", device="cuda")
    whisper_result = model.transcribe("data/sample_audio.flac", word_timestamps=True)
    diarization_segments = diarize_audio("data/processed_audio.wav")
    labeled_transcript = merge_transcript_with_speakers(whisper_result, diarization_segments)
    print("=== Transcript fed to LLM ===")
    print(labeled_transcript)
    minutes = extract_minutes(labeled_transcript, model_name="qwen2.5-finetuned")
    print("\n=== Extracted Minutes (fine-tuned) ===")
    print(json.dumps(minutes, indent=2))
    with open("outputs/final_minutes.json", "w") as f:
        json.dump(minutes, f, indent=2)
    print("\nSaved to outputs/final_minutes.json")
