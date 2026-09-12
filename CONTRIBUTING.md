# Contributing

Add a named TTS model or a distinct architecture release with a paper, official repository, model card or developer documentation. Keep checkpoint sizes, quantizations and voice packs under the same family unless the architecture changes substantially.

1. Edit [data/models.json](data/models.json). Use a stable ID, one short architecture sentence, concise notes and primary-source metadata. Follow an existing record for the complete schema.
2. Add a matching record to [data/figures.json](data/figures.json). Prefer a relevant figure from the primary source; record its exact image origin, figure number and SHA-256 checksum. Use a labeled `io-diagram` when no suitable diagram is available.
3. Regenerate and validate with Python 3.10 or newer:

   ```bash
   python3 scripts/catalog.py
   python3 scripts/catalog.py --check
   ```

The generator uses only the Python standard library. It checks metadata, duplicate entries, dates, asset checksums, local links, anchors and generated-file consistency. Inspect new figures and rendered Markdown before sharing changes.

Do not infer architecture from a product name, equate reference conditioning with conversational understanding, or claim an acoustic model alone emits a waveform. Undated sources can remain undated. Repository timestamps are not release dates.

See the [methodology](docs/methodology.md) and [figure notice](assets/architectures/FIGURE_NOTICE.md) for scope and attribution. Submit corrections with the model ID and supporting source; attribution or removal requests should identify the affected asset.
