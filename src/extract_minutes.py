import ollama
import json


def extract_minutes(transcript: str, model_name: str = "qwen2.5") -> dict:
    """
    Step 6: LLM-based Information Extraction
    Takes a speaker-labeled transcript, returns structured meeting minutes.
    """
    prompt = f"""You are an assistant that converts meeting transcripts into structured minutes.

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

    response = ollama.chat(
        model=model_name,
        messages=[{"role": "user", "content": prompt}]
    )

    raw_output = response["message"]["content"].strip()

    if raw_output.startswith("```"):
        raw_output = raw_output.split("```")[1]
        if raw_output.startswith("json"):
            raw_output = raw_output[4:]
        raw_output = raw_output.strip()

    try:
        minutes = json.loads(raw_output)
    except json.JSONDecodeError:
        print("Warning: model did not return valid JSON. Raw output:")
        print(raw_output)
        minutes = {"error": "invalid_json", "raw_output": raw_output}

    return minutes


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

    minutes = extract_minutes(labeled_transcript, model_name="qwen2.5")

    print("\n=== Extracted Minutes ===")
    print(json.dumps(minutes, indent=2))
