from datasets import load_dataset
from rouge_score import rouge_scorer
import sys
import os
import json
import mlflow

sys.path.append(os.path.dirname(__file__))
from extract_minutes import extract_minutes


def load_meetingbank_sample(n_samples: int = 3):
    dataset = load_dataset("huuuyeah/meetingbank", split="test")
    return dataset.select(range(n_samples))


def compute_rouge(generated_summary: str, reference_summary: str) -> dict:
    scorer = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=True)
    scores = scorer.score(reference_summary, generated_summary)
    return {
        "rouge1": round(scores["rouge1"].fmeasure, 4),
        "rouge2": round(scores["rouge2"].fmeasure, 4),
        "rougeL": round(scores["rougeL"].fmeasure, 4),
    }


def evaluate_pipeline(n_samples: int = 3, model_name: str = "qwen2.5"):
    mlflow.set_experiment("meeting-minutes-llm-comparison")

    with mlflow.start_run(run_name=f"{model_name}_n{n_samples}"):
        mlflow.log_param("llm_model", model_name)
        mlflow.log_param("n_samples", n_samples)
        mlflow.log_param("dataset", "MeetingBank")

        samples = load_meetingbank_sample(n_samples)
        results = []

        for i, sample in enumerate(samples):
            transcript = sample["transcript"]
            reference_summary = sample["summary"]
            transcript_for_llm = transcript[:4000]

            minutes = extract_minutes(transcript_for_llm, model_name=model_name)
            generated_summary = minutes.get("summary", "")

            scores = compute_rouge(generated_summary, reference_summary)

            results.append({
                "sample_id": i,
                "generated_summary": generated_summary,
                "reference_summary": reference_summary,
                "rouge_scores": scores
            })

            print(f"\n=== Sample {i} ===")
            print(f"Generated: {generated_summary}")
            print(f"Reference: {reference_summary}")
            print(f"ROUGE: {scores}")

        avg_rouge1 = sum(r["rouge_scores"]["rouge1"] for r in results) / len(results)
        avg_rouge2 = sum(r["rouge_scores"]["rouge2"] for r in results) / len(results)
        avg_rougeL = sum(r["rouge_scores"]["rougeL"] for r in results) / len(results)

        mlflow.log_metric("avg_rouge1", avg_rouge1)
        mlflow.log_metric("avg_rouge2", avg_rouge2)
        mlflow.log_metric("avg_rougeL", avg_rougeL)

        print(f"\n=== Average ROUGE across {n_samples} samples ({model_name}) ===")
        print(f"ROUGE-1: {avg_rouge1:.4f}")
        print(f"ROUGE-2: {avg_rouge2:.4f}")
        print(f"ROUGE-L: {avg_rougeL:.4f}")

        output_path = f"outputs/evaluation_{model_name}.json"
        with open(output_path, "w") as f:
            json.dump({
                "model": model_name,
                "n_samples": n_samples,
                "avg_rouge1": avg_rouge1,
                "avg_rouge2": avg_rouge2,
                "avg_rougeL": avg_rougeL,
                "per_sample": results
            }, f, indent=2)

        mlflow.log_artifact(output_path)

    return results


if __name__ == "__main__":
    evaluate_pipeline(n_samples=3, model_name="qwen2.5")
