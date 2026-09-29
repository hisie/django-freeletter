# django-freeletter

A small Django newsletter engine: subscribers with double opt-in, issues
made of ordered content blocks, a web-viewable archive, and a plain
management-command send queue. No e-commerce framework, no CMS, no
particular project's assumptions baked in — just Django.

## What this package does, and doesn't, do

- `Subscriber`: email + optional name, double opt-in (confirm via a
  tokenized email link before ever receiving a send), a separate
  unsubscribe token.
- `Issue`: a draft → queued → sent newsletter, made of ordered
  `IssueBlock`s.
- **One built-in block type**: `"html"` — free-form content (rich text +
  an optional image). That's the only content type this package itself
  knows about.
- A **pluggable block-type registry** (`freeletter.blocks`) — anything
  else (a blog post teaser, a product card, whatever a host project
  wants to feature in an issue) is registered by a *different* package or
  the host project itself, pointing at its own template and its own
  model, via a generic `(content_type, object_id)` pointer. freeletter
  never imports or knows about that other model — see "Registering a
  block type" below.
- A public archive (`freeletter/`) of sent issues, subscribe/confirm/
  unsubscribe views, and a `send_freeletter_issues` management command
  meant to run off a plain cron/systemd timer, not a task queue.
- It does **not** ship any dashboard/admin UI beyond Django's own
  `admin.py` registration, any e-commerce integration, or any CTA
  placement — all host-project scope.

## Installation

```
uv add django-freeletter
```

```python
INSTALLED_APPS = [
    ...,
    "django.contrib.contenttypes",  # required by IssueBlock's generic FK
    "freeletter",
]

FREELETTER_FROM_EMAIL = "newsletter@example.com"  # defaults to DEFAULT_FROM_EMAIL
FREELETTER_BASE_URL = "https://example.com"  # required for links in emails sent outside a request (the send command)
```

```python
# urls.py
urlpatterns = [
    path("newsletter/", include("freeletter.urls")),
]
```

Run `manage.py migrate`.

## Registering a block type

```python
# yourapp/apps.py
from django.apps import AppConfig

class YourAppConfig(AppConfig):
    def ready(self):
        from freeletter.blocks import BlockType, register_block_type

        register_block_type(
            BlockType(
                slug="product",
                label="Product",
                template_name="yourapp/freeletter_blocks/product.html",
            )
        )
```

```html
{# yourapp/freeletter_blocks/product.html — `object` is the resolved content_object #}
<a href="{{ object.get_absolute_url }}">{{ object.title }} — {{ object.price }}</a>
```

An editor then creates an `IssueBlock` with `block_type="product"` and
`content_object=<some product instance>` (e.g. via Django admin, or a
host project's own dashboard) — freeletter resolves and renders it
without ever importing the product model.

## Sending

```
manage.py send_freeletter_issues
```

Sends every `Issue` with `status="queued"` to every active (`is_confirmed
and not unsubscribed_at`) subscriber, then marks it `sent`. A single
recipient's send failure is logged and skipped, not fatal to the run.
Point a systemd timer or cron entry at this command — there's no daemon
or task queue involved by design, matching the "prepare for sending in an
agnostic way" requirement this package was built for: swapping the mail
transport later (a different SMTP relay, an ESP used as an SMTP backend)
only ever means changing `EMAIL_BACKEND`, nothing here.

Optional batching, if a mail relay needs it:

```python
FREELETTER_BATCH_SIZE = 50
FREELETTER_BATCH_DELAY = 2  # seconds, after every FREELETTER_BATCH_SIZE sends
```

## Development

```
uv sync
uv run pytest
```
