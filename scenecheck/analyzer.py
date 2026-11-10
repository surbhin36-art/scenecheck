from __future__ import annotations

from pathlib import Path
from typing import Any

import cv2


def _metadata(cap: cv2.VideoCapture) -> dict[str, float | int]:
    fps = cap.get(cv2.CAP_PROP_FPS) or 0.0
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    duration = frame_count / fps if fps > 0 else 0.0
    return {
        "fps": round(float(fps), 3),
        "frame_count": frame_count,
        "duration_seconds": round(duration, 3),
        "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0),
        "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0),
    }


def detect_scenes(cap: cv2.VideoCapture, fps: float, threshold: float = 25.0) -> list[dict[str, Any]]:
    """Detect abrupt cuts using mean absolute grayscale frame difference."""
    if fps <= 0:
        return []
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    previous = None
    scenes: list[dict[str, Any]] = []
    frame_index = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        small = cv2.resize(frame, (160, 90), interpolation=cv2.INTER_AREA)
        gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
        if previous is not None:
            score = float(cv2.absdiff(previous, gray).mean())
            if score >= threshold:
                scenes.append({
                    "timestamp_seconds": round(frame_index / fps, 2),
                    "frame": frame_index,
                    "change_score": round(score, 2),
                })
        previous = gray
        frame_index += 1
    return scenes


def extract_ocr(cap: cv2.VideoCapture, fps: float, duration: float,
                interval: int = 3, max_frames: int = 30) -> list[dict[str, Any]]:
    """Sample frames and OCR them with the local Tesseract executable, if available."""
    try:
        import pytesseract
        # Check executable availability before scanning all frames.
        pytesseract.get_tesseract_version()
    except Exception:
        return []

    samples: list[dict[str, Any]] = []
    timestamps = list(range(0, max(1, int(duration) + 1), max(1, interval)))[:max_frames]
    for seconds in timestamps:
        cap.set(cv2.CAP_PROP_POS_MSEC, seconds * 1000)
        ok, frame = cap.read()
        if not ok:
            continue
        text = pytesseract.image_to_string(frame).strip()
        if text:
            samples.append({"timestamp_seconds": seconds, "text": text[:2000]})
    return samples


def transcribe_audio(video_path: str) -> dict[str, str]:
    """Optional local transcription using faster-whisper; downloads a model on first use."""
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise RuntimeError(
            "Audio transcription needs the optional package. Install it with "
            "`pip install -r requirements-audio.txt`."
        ) from exc

    model = WhisperModel("tiny", device="cpu", compute_type="int8")
    segments, info = model.transcribe(video_path, beam_size=1)
    pieces = []
    for segment in segments:
        pieces.append(segment.text.strip())
    return {"text": " ".join(pieces), "language": str(info.language)}


def compare_script(script: str, transcript: str) -> dict[str, Any]:
    """A transparent baseline comparison; not semantic fact-checking."""
    import re
    words = lambda value: re.findall(r"\b[\w']+\b", value.lower())
    expected = words(script)
    spoken = words(transcript)
    expected_set, spoken_set = set(expected), set(spoken)
    missing = sorted(expected_set - spoken_set)
    extra = sorted(spoken_set - expected_set)
    overlap = len(expected_set & spoken_set) / max(1, len(expected_set))
    return {
        "unique_word_overlap": round(overlap * 100, 1),
        "words_in_script_not_heard": missing[:100],
        "words_heard_not_in_script": extra[:100],
        "method_note": "Simple unique-word overlap only; it does not account for paraphrases, word order, or transcription errors.",
    }


def analyze_video(video_path: str, script: str = "", scene_threshold: float = 25.0,
                  sample_every_seconds: int = 3, max_ocr_frames: int = 30,
                  transcribe: bool = False) -> dict[str, Any]:
    path = Path(video_path)
    if not path.exists():
        raise FileNotFoundError(video_path)

    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise ValueError("Could not open this video. Try an MP4 or MOV file.")

    try:
        metadata = _metadata(cap)
        if metadata["frame_count"] <= 0:
            raise ValueError("The video appears to contain no readable frames.")

        scenes = detect_scenes(cap, float(metadata["fps"]), scene_threshold)
        ocr_samples = extract_ocr(
            cap, float(metadata["fps"]), float(metadata["duration_seconds"]),
            sample_every_seconds, max_ocr_frames
        )
    finally:
        cap.release()

    result: dict[str, Any] = {
        "tool": "SceneCheck",
        "version": "0.1.0",
        "video": {"filename": path.name, **metadata},
        "scenes": scenes,
        "ocr_samples": ocr_samples,
        "review_notes": [],
    }

    if not ocr_samples:
        result["review_notes"].append(
            "No OCR text extracted. Install Tesseract and check that sampled frames contain legible text."
        )
    if len(scenes) == 0:
        result["review_notes"].append(
            "No abrupt scene changes detected. Confirm this is expected for the video."
        )
    if transcribe:
        transcript = transcribe_audio(str(path))
        result["transcription"] = transcript
        if script.strip():
            result["script_comparison"] = compare_script(script, transcript["text"])
    elif script.strip():
        result["review_notes"].append(
            "A script was provided, but audio transcription was not enabled; no script comparison was run."
        )

    result["review_notes"].append(
        "Scene boundaries use visual frame differences and may flag flashes, animations, or camera movement as cuts."
    )
    result["review_notes"].append(
        "OCR and script checks are best-effort signals, not proof of correctness. Review flagged timestamps manually."
    )
    return result
