import spacy

nlp = spacy.load("en_core_web_sm")


def merge_transcript_with_speakers(whisper_result: dict, diarization_segments: list) -> str:
    """
    Merges Whisper's word-level transcript with pyannote's speaker segments.
    Returns a labeled transcript like:
        Speaker SPEAKER_00: text spoken by this speaker...
        Speaker SPEAKER_01: text spoken by this speaker...
    """
    labeled_lines = []

    for segment in whisper_result["segments"]:
        seg_start = segment["start"]
        seg_end = segment["end"]
        seg_mid = (seg_start + seg_end) / 2

        # Find which speaker was talking at this segment's midpoint
        speaker = "UNKNOWN"
        for start, end, spk in diarization_segments:
            if start <= seg_mid <= end:
                speaker = spk
                break

        labeled_lines.append(f"Speaker {speaker}: {segment['text'].strip()}")

    return "\n".join(labeled_lines)


def extract_entities(text: str) -> dict:
    """
    Runs NER on the transcript, tags people, dates, organizations.
    """
    doc = nlp(text)
    entities = {"PERSON": [], "DATE": [], "ORG": [], "GPE": []}

    for ent in doc.ents:
        if ent.label_ in entities:
            entities[ent.label_].append(ent.text)

    # dedupe while preserving order
    for key in entities:
        entities[key] = list(dict.fromkeys(entities[key]))

    return entities


if __name__ == "__main__":
    import whisper
    from diarize import diarize_audio

    model = whisper.load_model("base", device="cuda")
    whisper_result = model.transcribe("data/sample_audio.flac", word_timestamps=True)

    diarization_segments = diarize_audio("data/processed_audio.wav")

    labeled_transcript = merge_transcript_with_speakers(whisper_result, diarization_segments)
    print("=== Labeled Transcript ===")
    print(labeled_transcript)

    entities = extract_entities(whisper_result["text"])
    print("\n=== Extracted Entities ===")
    print(entities)
