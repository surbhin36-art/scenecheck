import os
import json
import tempfile
from pathlib import Path

import streamlit as st

from scenecheck.analyzer import analyze_video

st.set_page_config(page_title="SceneCheck", page_icon="🎬", layout="wide")
st.title("🎬 SceneCheck")
st.caption("Open-source quality checks for AI-generated and edited videos.")

with st.sidebar:
    st.header("Analysis settings")
    scene_threshold = st.slider("Scene-change sensitivity", 5, 60, 25,
                                help="Lower values detect more scene changes.")
    sample_every = st.slider("OCR sampling interval (seconds)", 1, 10, 3)
    max_frames = st.slider("Maximum OCR frames", 5, 100, 30)
    run_transcription = st.checkbox("Transcribe audio (requires faster-whisper)", value=False)

st.markdown(
    "Upload a video and optionally paste the intended narration/script. "
    "SceneCheck will identify scene boundaries, inspect sampled on-screen text, "
    "and (optionally) compare a transcript with your script."
)

uploaded = st.file_uploader("Choose a video", type=["mp4", "mov", "m4v", "avi", "mkv"])
script = st.text_area("Expected script / narration (optional)", height=160,
                      placeholder="Paste the narration or script here…")

if uploaded and st.button("Run quality check", type="primary"):
    suffix = Path(uploaded.name).suffix or ".mp4"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded.getbuffer())
        video_path = tmp.name

    try:
        with st.spinner("Inspecting video… Larger files may take a little while."):
            result = analyze_video(
                video_path,
                script=script,
                scene_threshold=scene_threshold,
                sample_every_seconds=sample_every,
                max_ocr_frames=max_frames,
                transcribe=run_transcription,
            )

        st.success("Analysis complete.")
        m1, m2, m3 = st.columns(3)
        m1.metric("Duration", f"{result['video']['duration_seconds']:.1f} sec")
        m2.metric("Detected scenes", len(result["scenes"]))
        m3.metric("OCR samples", len(result["ocr_samples"]))

        st.subheader("Scene boundaries")
        if result["scenes"]:
            st.dataframe(result["scenes"], use_container_width=True, hide_index=True)
        else:
            st.info("No scene boundaries detected. The video may be very short or visually static.")

        st.subheader("On-screen text")
        if result["ocr_samples"]:
            st.dataframe(result["ocr_samples"], use_container_width=True, hide_index=True)
        else:
            st.info("No readable text was found in the sampled frames, or Tesseract is not installed.")

        if result.get("transcription"):
            st.subheader("Audio transcript")
            st.write(result["transcription"]["text"] or "No speech detected.")
            if script.strip():
                st.subheader("Script comparison")
                st.write(result["script_comparison"])

        st.subheader("Review notes")
        for note in result["review_notes"]:
            st.write(f"- {note}")
        if not result["review_notes"]:
            st.write("No automatic review flags were raised. This is not a guarantee that the video is error-free.")

        st.download_button(
            "Download full JSON report",
            data=json.dumps(result, indent=2, ensure_ascii=False),
            file_name="scenecheck-report.json",
            mime="application/json",
        )
    except Exception as exc:
        st.error(f"Analysis failed: {exc}")
        st.exception(exc)
    finally:
        try:
            os.unlink(video_path)
        except OSError:
            pass

st.divider()
st.caption("SceneCheck is an assistive QA tool. Always review flagged moments manually; automated checks can miss errors.")
