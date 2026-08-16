"""
A single, internally-consistent fake meeting used by every mock stage in
this package. All mock functions ignore the actual contents of the input
audio and return slices of this fixture, so the transcript, speaker labels,
and extracted minutes always agree with each other regardless of which
stage you call in isolation.

Timestamps are in seconds, matching Whisper's segment format.
"""

MOCK_TRANSCRIPT_SEGMENTS = [
    {"start": 0.0, "end": 4.2, "text": "Alright everyone, thanks for joining. Let's kick off the Q3 planning sync."},
    {"start": 4.2, "end": 9.8, "text": "Sure. I think the top priority this quarter should be finishing the onboarding redesign."},
    {"start": 9.8, "end": 15.0, "text": "Agreed. Sarah, can you own that and have a first draft ready by the 20th?"},
    {"start": 15.0, "end": 18.5, "text": "Yes, I can do that."},
    {"start": 18.5, "end": 25.0, "text": "On the marketing side, we've decided to increase the ad spend budget by 15% starting next month."},
    {"start": 25.0, "end": 30.0, "text": "Sounds good. Let's also make sure we follow up with the vendor about the contract renewal before Friday."},
    {"start": 30.0, "end": 33.0, "text": "I'll send that email today."},
    {"start": 33.0, "end": 37.5, "text": "Great, thanks everyone. Let's reconvene next week."},
]

# (start_sec, end_sec, speaker_label) — same shape pyannote.audio's
# itertracks(yield_label=True) produces in src/diarize.py. Boundaries are
# aligned with MOCK_TRANSCRIPT_SEGMENTS above so the demo transcript reads
# cleanly; real diarization output won't line up this neatly.
MOCK_SPEAKER_SEGMENTS = [
    (0.0, 4.2, "SPEAKER_00"),
    (4.2, 9.8, "SPEAKER_01"),
    (9.8, 15.0, "SPEAKER_00"),
    (15.0, 18.5, "SPEAKER_01"),
    (18.5, 25.0, "SPEAKER_02"),
    (25.0, 30.0, "SPEAKER_00"),
    (30.0, 33.0, "SPEAKER_02"),
    (33.0, 37.5, "SPEAKER_00"),
]

MOCK_MINUTES = {
    "summary": (
        "The team held a Q3 planning sync covering onboarding redesign priorities, "
        "a 15% increase to the marketing ad spend budget, and vendor contract renewal "
        "follow-up. SPEAKER_01 will own the onboarding redesign draft, and the team "
        "will reconvene next week."
    ),
    "key_topics": [
        "Q3 planning",
        "Onboarding redesign",
        "Marketing budget",
        "Vendor contract renewal",
    ],
    "decisions": [
        "Increase marketing ad spend budget by 15% starting next month.",
        "Reconvene next week for a follow-up sync.",
    ],
    "action_items": [
        {"task": "Prepare first draft of onboarding redesign", "owner": "SPEAKER_01", "deadline": "the 20th"},
        {"task": "Follow up with vendor about contract renewal", "owner": "SPEAKER_00", "deadline": "Friday"},
        {"task": "Send email to vendor about contract renewal", "owner": "SPEAKER_02", "deadline": "today"},
    ],
}
