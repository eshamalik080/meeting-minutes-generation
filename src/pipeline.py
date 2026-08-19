from preprocess import extract_and_normalize_audio
from transcribe import transcribe_audio
from diarize import diarize_audio
from clean_ner import merge_transcript_with_speakers, extract_entities
from extract_minutes import extract_minutes
from export import export_all_formats


def generate_minutes(audio_path: str, llm_model: str = "qwen2.5-finetuned") -> dict:
    """
    Single entry point for the full ML pipeline.
    Input: path to raw audio/video file
    Output: structured dict with transcript, summary, decisions, action items,
            plus paths to exported JSON/HTML/PDF files.
    """
    # Stage 2+3: Preprocess
    clean_audio_path = extract_and_normalize_audio(audio_path)

    # Stage 4: ASR
    whisper_result = transcribe_audio(clean_audio_path)

    # Stage 5: Diarization
    diarization_segments = diarize_audio(clean_audio_path)

    # Stage 6: Merge + NER
    labeled_transcript = merge_transcript_with_speakers(whisper_result, diarization_segments)
    entities = extract_entities(whisper_result["text"])

    # Stage 7: LLM extraction
    minutes = extract_minutes(labeled_transcript, model_name=llm_model)
    minutes["transcript"] = labeled_transcript
    minutes["entities"] = entities

    # Stage 8: Export
    export_paths = export_all_formats(minutes)
    minutes["export_paths"] = export_paths

    return minutes


if __name__ == "__main__":
    import json
    import sys
    audio_path = sys.argv[1] if len(sys.argv) > 1 else "data/sample_audio.flac"
    result = generate_minutes(audio_path)
    print(json.dumps(result, indent=2))
