# CHANGELOG

## v0.2.0

### Changed

- Modernized package metadata to PEP 621 and `uv`.
- Moved PaddleOCR support behind the optional `tablecv[paddle]` extra.
- Replaced token-based publishing with PyPI Trusted Publishing from pushes to `main`.
- Rewrote README documentation for package users.

### Fixed

- Importing `tablecv` no longer requires PaddleOCR.
- Empty OCR results now return an empty `DataFrame`.
- Duplicate OCR boxes preserve text order within the output cell.
- Zero-width boxes no longer crash overlap calculations.
