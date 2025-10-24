from django import forms
from django.utils.safestring import mark_safe
from django.conf import settings
from markdown import markdown


class MarkdownEditorWidget(forms.Textarea):
    class Media:
        css = {
            'all': ('https://cdn.jsdelivr.net/simplemde/latest/simplemde.min.css',)
        }
        js = ('https://cdn.jsdelivr.net/simplemde/latest/simplemde.min.js',)

    def render(self, name, value, attrs=None, renderer=None):
        rendered = super().render(name, value, attrs)
        return rendered + mark_safe(
            f'<script>var simplemde = new SimpleMDE({{element: document.getElementById("id_{name}"),}});</script>'
        )
