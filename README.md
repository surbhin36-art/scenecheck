# SceneCheck

**Open-source, local-first quality checks for AI-generated and edited videos.**

SceneCheck is an early MVP that helps creators inspect a video for:
- Abrupt scene boundaries (using OpenCV frame differences)
- On-screen text in sampled frames (using Tesseract OCR)
- Optional audio transcription (using faster-whisper)
- A basic script/transcript word-overlap report
- A downloadable JSON QA report

> SceneCheck is an assistive review tool, not an automated guarantee of quality. Its signals can be wrong and should be checked by a human.

## Current status

**Prototype / v0.1.0.** The first release focuses on a small, understandable baseline. It does not yet verify visual-semantic alignment between a script and footage, detect character consistency, or reliably identify spelling errors in every font/language.

## Requirements

- macOS, Windows, or Linux
- Python 3.10–3.12 recommended
- Tesseract OCR for on-screen text extraction
- FFmpeg is recommended for broad media compatibility and optional audio workflows

## Run on macOS

Open Terminal and run:

```bash
# 1. Install system tools
brew install python tesseract ffmpeg

# 2. Move into the downloaded/cloned project directory
cd scenecheck

# 3. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 4. Install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# 5. Launch the app
streamlit run app.py
```

Your browser should open the local SceneCheck interface.

### Optional audio transcription

Audio transcription runs locally and downloads the Whisper `tiny` model the first time it is used. It may take time and uses CPU.

```bash
pip install -r requirements-audio.txt
```

Then enable **Transcribe audio** in the app sidebar.

## How to use

1. Upload an MP4, MOV, M4V, AVI, or MKV video.
2. Optionally paste the intended narration/script.
3. Adjust scene sensitivity and OCR sampling in the sidebar.
4. Enable transcription if the optional audio dependency is installed.
5. Run the quality check.
6. Review timestamps and download the JSON report.

## How it works

- **Scene detection:** resizes frames and calculates mean absolute grayscale difference between consecutive frames. A threshold crossing is reported as a possible cut.
- **OCR:** samples frames at a configurable interval and runs Tesseract on each sample.
- **Transcription:** optionally uses faster-whisper's small-footprint `tiny` model on CPU.
- **Script comparison:** compares unique words in the expected script and transcript. This is intentionally a simple baseline, not semantic alignment.

## Known limitations

- Scene detection can flag flashes, animation, rapid motion, or camera movement.
- OCR quality depends on resolution, font, contrast, language packs, and text duration.
- OCR sampling may miss text that appears between sampled timestamps.
- The initial script comparison ignores word order, synonyms, paraphrases, and timestamps.
- The app currently processes videos locally and does not upload them to a server.
- Large files may take a while; use a short test clip first.

## Development

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
```

## Roadmap

- [ ] Scene thumbnails and a visual timeline
- [ ] Timestamped OCR confidence and language selection
- [ ] Word-level audio/script alignment
- [ ] Optional visual-to-script matching using configurable vision models
- [ ] Duplicate-shot and black-frame detection
- [ ] CSV and HTML reports
- [ ] Batch processing
- [ ] More automated tests and sample fixtures

## Contributing

Issues and pull requests are welcome. Please include:
- Operating system and Python version
- A minimal reproduction where possible
- Expected and actual behavior
- A short sample clip only if you have the right to share it

See [CONTRIBUTING.md](CONTRIBUTING.md).

## Privacy

The default analysis is local. If optional transcription is enabled, faster-whisper also runs locally. Do not upload confidential or copyrighted footage unless you have permission to process it.

## License

MIT. See [LICENSE](LICENSE).
