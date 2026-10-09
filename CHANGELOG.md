# Changelog

All notable changes to this project are documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

## [0.2.1] - 2026-10-09

### Fixed

- Issue emails now carry absolute `src`/`href` URLs in the block content
  (images, product/post links). They were root-relative (`/media/...`), which
  an email client cannot resolve. Built from the request, or from
  `FREELETTER_BASE_URL` when sent from the management command.
- The English source catalogue (`locale/en`, added in 0.2.0) lacked one
  string, "Queue selected issues for sending". Empty `msgstr`s anyway, so no
  behaviour change.

## [0.2.0] - 2026-10-07

### Added

- Spanish translation (`freeletter/locale/es`, `.po` and compiled `.mo`
  both committed and shipped in the wheel): models, admin, subscribe /
  confirm / unsubscribe pages, the confirmation email and the issue email.
- The admin action "Queue selected issues for sending" is translatable.
- `freeletter/locale/en`: the English source catalogue (empty `msgstr`s, `.po`
  and `.mo`), the same reference template Django and Oscar ship. No
  behaviour change: the `msgid` is the English text.

### Changed

- The package's standalone HTML pages now set `<html lang>` from the active
  language instead of leaving it unset.

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

[Unreleased]: https://github.com/hisie/django-freeletter/compare/0.2.1...HEAD
[0.2.1]: https://github.com/hisie/django-freeletter/compare/0.2.0...0.2.1
[0.2.0]: https://github.com/hisie/django-freeletter/compare/0.1.1...0.2.0
[0.1.1]: https://github.com/hisie/django-freeletter/compare/0.1.0...0.1.1
[0.1.0]: https://github.com/hisie/django-freeletter/releases/tag/0.1.0
