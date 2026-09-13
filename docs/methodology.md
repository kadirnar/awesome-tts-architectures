# Scope and methodology

[← Model list](../README.md#models)

This is a curated research snapshot of text-to-speech architectures and named model families. It covers acoustic models, complete text-to-waveform systems, speech-token and continuous language models, compact releases and selected commercial interfaces. It is not a claim to enumerate every private model, regional deployment, fine-tune or checkpoint.

## Inclusion and grouping

Each entry has a documented path from text to synthesized speech and at least one primary source. Reference-conditioned voice cloning, expressive synthesis and script-to-dialogue rendering are included. ASR, speech understanding, autonomous voice assistants, standalone vocoders and codecs are outside this catalog.

Distinct research generations have separate cards. Sizes, quantizations and closely related checkpoints remain variants. Piper denotes its trained VITS voice family, rather than counting its runtime as a new architecture. SpeechT5 and SpeechX cards cover their synthesis paths.

Groups are navigation aids, not mutually exclusive technical claims:

| Group | Organizing feature |
| --- | --- |
| Autoregressive | Sequential acoustic or waveform prediction |
| Parallel | Feed-forward acoustic generation and duration expansion |
| Flow / VAE | Normalizing flows, variational inference and related hybrids |
| Diffusion / flow | Diffusion or flow matching for speech or style generation |
| Token LM | Language modeling over discrete speech representations, including masked and diffusion token models |
| Continuous LM | Autoregressive modeling of continuous speech latents, often with a diffusion or flow output head |
| Compact | Releases centered on small models and on-device inference |
| API | Selected commercial interfaces with limited architectural disclosure |

For example, Flowtron is autoregressive but appears under normalizing flows; StyleTTS 2 diffuses style rather than every waveform sample; CosyVoice combines a token LM with flow matching. Compact and API are deployment groups. Inclusion does not establish that weights are available or that a model runs on every local device.

## Modalities and interaction

- **T:** text to be spoken, including phonemes after preprocessing and optional style descriptions.
- **S input:** reference speech, audio prefix, speaker conditioning or prosody, often optional and variant-dependent. It does not establish spoken-question understanding. Training-only audio is not an inference input.
- **S output:** synthesized speech through the documented complete pipeline. Acoustic-model entries include their accompanying vocoder or waveform reconstruction stage.
- **A:** broader generated audio where a TTS-capable model also supports non-speech sounds.
- **Generation:** speech synthesis is established; this label makes no latency claim.
- **Streaming:** the source explicitly documents incremental synthesis. Backend and checkpoint restrictions remain in the notes.

Modality sets summarize the family. They do not promise all combinations for all variants. Speaker IDs, embeddings and numeric controls are described in notes rather than added as separate modalities. Scripted multi-speaker rendering does not imply autonomous dialogue.

## Sources, dates and figures

Architecture and capability statements use linked papers, developer repositories, model cards and official documentation. Review levels distinguish abstracts, READMEs and other source types; they do not imply reproducing results or running model weights. Source dates mean first paper submissions or explicitly dated announcements, not necessarily release dates. Missing dates remain blank.

The [2025–2026 descriptions](model-descriptions.md) explain synthesis methods, voice controls and intended use in one paragraph per family. This collection includes later releases of older families, such as F5-TTS v1 Base, without changing their original paper dates. Descriptions distinguish paper proposals from released controls and avoid inferring undisclosed architecture from API behavior.

Every card has a local image. Paper or developer figures retain attribution and their original download URL in [figure credits](../assets/architectures/CREDITS.md). Multi-panel PDF excerpts preserve the technical content. Where a suitable primary-source figure is unavailable, a generated SVG explicitly summarizes documented inputs and outputs without inventing internal architecture. Third-party figures retain their own rights; see the [figure notice](../assets/architectures/FIGURE_NOTICE.md).

The catalog format and initial speech-generation entries are adapted from [Awesome Omni Architectures](https://github.com/kadirnar/awesome-omni-architectures). The TTS scope additionally includes conventional neural acoustic models and diffusion systems. The [neural speech synthesis survey](https://arxiv.org/abs/2106.15561) was used for discovery; model-level claims cite their own primary sources.

## Maintenance

[data/models.json](../data/models.json) and [data/figures.json](../data/figures.json) are the sources of truth. Run `python3 scripts/catalog.py --check` to verify the catalog offline. See [CONTRIBUTING.md](../CONTRIBUTING.md) for updates and corrections.
