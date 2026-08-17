from pydub import AudioSegment
import webrtcvad
import wave
import os


def extract_and_normalize_audio(input_path: str, output_path: str = None) -> str:
    """
    Step 2: Audio Extraction & Preprocessing
    Converts any input format to a clean 16kHz mono WAV (Whisper's preferred format).
    If output_path isn't given, saves alongside the input file as '<name>_processed.wav'.
    """
    if output_path is None:
        base, _ = os.path.splitext(input_path)
        output_path = f"{base}_processed.wav"

    audio = AudioSegment.from_file(input_path)
    audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
    audio.export(output_path, format="wav")
    return output_path


def apply_vad(wav_path: str, aggressiveness: int = 2) -> list:
    """
    Step 3: Voice Activity Detection
    Removes silence, returns list of (start_ms, end_ms) speech segments.
    """
    vad = webrtcvad.Vad(aggressiveness)
    with wave.open(wav_path, "rb") as wf:
        sample_rate = wf.getframerate()
        pcm_data = wf.readframes(wf.getnframes())
    frame_duration_ms = 30
    frame_size = int(sample_rate * frame_duration_ms / 1000) * 2
    speech_segments = []
    current_start = None
    timestamp_ms = 0
    for i in range(0, len(pcm_data) - frame_size, frame_size):
        frame = pcm_data[i:i + frame_size]
        is_speech = vad.is_speech(frame, sample_rate)
        if is_speech and current_start is None:
            current_start = timestamp_ms
        elif not is_speech and current_start is not None:
            speech_segments.append((current_start, timestamp_ms))
            current_start = None
        timestamp_ms += frame_duration_ms
    if current_start is not None:
        speech_segments.append((current_start, timestamp_ms))
    return speech_segments


if __name__ == "__main__":
    clean_audio = extract_and_normalize_audio("data/sample_audio.flac")
    print(f"Preprocessed audio saved: {clean_audio}")
    segments = apply_vad(clean_audio)
    print(f"Detected {len(segments)} speech segments:")
    for start, end in segments:
        print(f"  {start}ms - {end}ms")
