from datasets import load_dataset
import json
import os


def build_training_dataset(n_samples: int = 50, output_path: str = "data/finetune_dataset.jsonl"):
    """
    Builds a training dataset for fine-tuning Qwen on transcript -> summary.
    Format: JSONL, one training example per line, in instruction-tuning format.
    """
    dataset = load_dataset("huuuyeah/meetingbank", split="train")
    samples = dataset.select(range(min(n_samples, len(dataset))))

    os.makedirs("data", exist_ok=True)

    with open(output_path, "w") as f:
        for sample in samples:
            transcript = sample["transcript"][:3000]
            summary = sample["summary"]

            example = {
                "messages": [
                    {"role": "system", "content": "You summarize meeting transcripts concisely."},
                    {"role": "user", "content": f"Summarize this meeting transcript:\n\n{transcript}"},
                    {"role": "assistant", "content": summary}
                ]
            }
            f.write(json.dumps(example) + "\n")

    print(f"Wrote {n_samples} training examples to {output_path}")
    return output_path


if __name__ == "__main__":
    build_training_dataset(n_samples=50)
