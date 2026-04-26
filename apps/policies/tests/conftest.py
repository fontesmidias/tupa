"""Workaround: Python 3.14 quebra Context.__copy__ do Django; o signal
`template_rendered` instrumentado pelo test runner invoca `copy(context)` e
explode com AttributeError. Desligamos esse signal para testes de policies
(que renderizam templates com contexto richo como o modal)."""

from __future__ import annotations

import pytest
from django.template import base as template_base


@pytest.fixture(autouse=True)
def _restore_template_render():
    """Reverte o instrumented_test_render do setup_test_environment do Django,
    que dispara o signal template_rendered e quebra no Python 3.14."""
    original = getattr(template_base.Template, "_render", None)
    patched = getattr(template_base.Template, "_render", None)

    def plain_render(self, context):
        return self.nodelist.render(context)

    template_base.Template._render = plain_render
    try:
        yield
    finally:
        template_base.Template._render = patched
