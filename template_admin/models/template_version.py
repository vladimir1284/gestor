from django.db import models

from template_admin.models.template_content_version import TemplateContentVersion
from template_admin.tools.templates_tools import TT_TEXT


class TemplateVersion(models.Model):
    module = models.CharField(max_length=100)
    template = models.CharField(max_length=100)
    language = models.CharField(max_length=50)
    tmp_type = models.CharField(max_length=20, default=TT_TEXT)

    @property
    def last_version(self) -> int:
        last = self.version()
        if last is None:
            return 0
        return last.version

    @property
    def versions_list(self) -> list[int]:
        versions = [v.version for v in self.versions.all()]
        return versions

    @property
    def versions_list_date(self) -> list[int]:
        versions = [
            {
                "version": v.version,
                "date": v.created_date,
            }
            for v in self.versions.all()
        ]
        return versions

    def new_version(self, content: str = "") -> TemplateContentVersion:
        new_version = TemplateContentVersion(
            template=self,
            version=self.last_version + 1,
            content=content,
        )
        new_version.save()
        return new_version

    def version(self, version: int | None = None) -> TemplateContentVersion | None:
        if version is None:
            return self.versions.order_by("-version").first()
        return self.versions.filter(version=version).first()

    def render_template(
        self,
        ctx,
        version: int | None = None,
        replaces: dict | None = None,
    ) -> str:
        version = self.version(version)
        if version is None:
            return None
        return version.render_template(ctx, replaces)
