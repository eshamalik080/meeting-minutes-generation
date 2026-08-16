import torch
from pyannote.audio import Pipeline
import os


def diarize_audio(audio_path: str) -> list:
    """
    Step 5: Speaker Diarization
    Identifies "who spoke when" in an audio file using pyannote.audio.
    Returns a list of (start_sec, end_sec, speaker_label) tuples.
    """
    hf_token = os.environ["HF_TOKEN"]

    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1",
        use_auth_token=hf_token
    )
    pipeline.to(torch.device("cuda"))

    diarization = pipeline(audio_path, min_speakers=1, max_speakers=8)

    segments = []
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        segments.append((turn.start, turn.end, speaker))

    return segments


if __name__ == "__main__":
    results = diarize_audio("data/processed_audio.wav")
    for start, end, speaker in results:
        print(f"start={start:.1f}s stop={end:.1f}s speaker={speaker}")
