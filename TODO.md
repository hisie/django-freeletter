# TODO

Internal notes on things not built yet. Not a promise or a roadmap; delete an
entry when it ships (and move it to `CHANGELOG.md`).

## Language per subscriber

**Why**: the package is meant to be reusable, and a site with more than one
language needs each subscriber to get the confirmation, unsubscribe and issue
emails in their own language. Raised from the urbanplants project (Spanish
only), which does *not* need it; kept here because it is a package feature.

**State today** (checked in the code, 0.2.0): `Subscriber` has no language
field. Emails are rendered in whichever language is active when they are built
— the request's language for the confirmation email, the project's
`LANGUAGE_CODE` for `send_freeletter_issues` (a management command, so no
request). The package already ships a Spanish catalogue (`locale/es`) and an
empty English one (`locale/en`).

**Sketch** (not decided):
- `Subscriber.language` (a language code) + migration, defaulting to a new
  setting (e.g. `FREELETTER_DEFAULT_LANGUAGE`, falling back to
  `LANGUAGE_CODE`). Existing rows get the default.
- Optional language choice on `SubscribeForm`; the host project can hide it.
- Render each email under `translation.override(subscriber.language)`:
  `send_confirmation_email` and, per recipient, `send_issue_email`.
- Open question: issue *content* (`Issue.title`, `IssueBlock.html`) is stored
  in one language. Per-subscriber rendering only translates the package's own
  text (links, "Unsubscribe"…) unless issues themselves get a language or
  translations.
- Tests for each email in two languages; document in the README.

**Related**: `django-oscar-freeletter/TODO.md` (dashboard side).
