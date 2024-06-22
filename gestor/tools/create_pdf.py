from django.conf import settings
from django.http import HttpRequest
from django.template.loader import render_to_string
from weasyprint import CSS


def create_pdf(
    template: str,
    context: dict,
    request: HttpRequest | None = None,
):
    """
    Generate a pdf document using a template and a context.

    Args:
        template (str): The template path.
        context (dict): The context to pass to the template.
        request (HttpRequest | None): The request to pass to the template.

    Returns:
        bytes: The pdf file.
        str: The html string.
    """
    html_string = render_to_string(template, context)
    if settings.USE_WEASYPRINT:
        from weasyprint import HTML

        boxicons = CSS(f"{settings.STATIC_ROOT}/assets/vendor/fonts/boxicons.css")
        core = CSS(f"{settings.STATIC_ROOT}/assets/vendor/css/core.css")
        theme = CSS(f"{settings.STATIC_ROOT}/assets/vendor/css/theme-default.css")
        demo = CSS(f"{settings.STATIC_ROOT}/assets/css/demo.css")
        apex_chart = CSS(
            f"{settings.STATIC_ROOT}/assets/vendor/libs/apex-charts/apex-charts.css"
        )
        editor = CSS(f"{settings.STATIC_ROOT}/libs/ckeditor/ckeditor.css")
        style = CSS(f"{settings.STATIC_ROOT}/assets/css/style.css")

        html = HTML(
            string=html_string,
            base_url=None if request is None else request.build_absolute_uri(),
        )
        main_doc = html.render(
            presentational_hints=True,
            stylesheets=[
                boxicons,
                core,
                theme,
                demo,
                apex_chart,
                editor,
                style,
            ],
        )
        return main_doc.write_pdf()
    return html_string
