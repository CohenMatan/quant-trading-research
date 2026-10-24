# Pilot assessment (C001–C024), written before the main pass

- **Workflow:** sound.
  - All 24 images are legible: candles, volume, MA50 and MA200 are distinguishable.
  - The decision bar is visibly the last candle, followed by a blank margin.
  - No text, axis value or date appears.
- **Leakage:** none seen. The render script also confirms in code that the last drawn bar equals the decision date for all 299 charts. A synthetic test confirms that later bars never change an image.
- **Vocabulary:** usable without changes, so it was not extended.
  - Fresh up gaps with no hold yet are tagged `GAP_AND_HOLD` with a note.
  - Trend-then-plateau charts are tagged `RANGE_BOUND`.
- **Early impression, recorded so that later counts can be checked against it:**
  - Charts split roughly into clean persistent uptrends at or near highs, volatile gap-driven sideways charts, and post-decline recoveries or bases.
  - No pattern is proposed yet.
- **Decision:** continue to C299 in id order.
