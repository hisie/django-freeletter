# Changelog

All notable changes to this project are documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

## [0.1.1] - 2026-10-02

Docs-only — this `CHANGELOG.md` itself didn't exist until after 0.1.0
was published; bumping so PyPI's project page reflects it (PyPI freezes
the README/description at publish time, so it would otherwise stay
stale relative to what's in git).

## [0.1.0] - 2026-09-29

### Added

- `Subscriber`: double opt-in via a tokenized confirmation email link,
  a separate unsubscribe token, `is_active` = confirmed and not
  unsubscribed.
- `Issue` + `IssueBlock`: draft → queued → sent, made of ordered content
  blocks.
- A pluggable block-type registry (`freeletter.blocks`) — the only
  built-in type is `"html"` (free content + optional image); any other
  type (a blog post, a product) is registered by a separate package via
  a generic `(content_type, object_id)` pointer, with freeletter never
  importing that model.
- A public archive of sent issues, subscribe/confirm/unsubscribe views.
- `send_freeletter_issues` management command, meant to run off a plain
  cron/systemd timer rather than a task queue — continues past a single
  recipient's send failure instead of aborting the run.
- 17 tests, 96% coverage.

[Unreleased]: https://github.com/hisie/django-freeletter/compare/0.1.1...HEAD
[0.1.1]: https://github.com/hisie/django-freeletter/compare/0.1.0...0.1.1
[0.1.0]: https://github.com/hisie/django-freeletter/releases/tag/0.1.0
