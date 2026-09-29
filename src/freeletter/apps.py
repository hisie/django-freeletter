from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class FreeletterConfig(AppConfig):
    name = "freeletter"
    label = "freeletter"
    verbose_name = "Freeletter"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self) -> None:
        from freeletter.blocks import BlockType, register_block_type

        register_block_type(
            BlockType(
                slug="html",
                label=str(_("Free content")),
                template_name="freeletter/blocks/html.html",
                requires_object=False,
            )
        )
