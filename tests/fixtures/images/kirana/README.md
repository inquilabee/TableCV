# Kirana Invoice Fixtures

These invoice images come from the Hugging Face dataset [`build-small-hackathon/kirana-invoice-train-data`](https://huggingface.co/datasets/build-small-hackathon/kirana-invoice-train-data).

The dataset contains programmatically generated invoice images for OCR and document-understanding tests. It is released under CC0 1.0 Universal, so these fixture images can be used without attribution requirements. The generation scripts are MIT licensed.

Default tests use injected OCR results against these images. Real OCR checks remain integration-only so the default suite stays deterministic and does not download OCR models.
