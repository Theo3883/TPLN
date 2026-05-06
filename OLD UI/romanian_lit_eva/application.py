from __future__ import annotations

import streamlit as st

from romanian_lit_eva import settings
from romanian_lit_eva.api.client import PlatformApiClient
from romanian_lit_eva.pages import (
    CatalogPage,
    EditionDetailPage,
    HomePage,
    ModerationPage,
    RankingsPage,
    SearchPage,
)
from romanian_lit_eva.services.navigation import Navigator
from romanian_lit_eva.ui.shell import AppShell
from romanian_lit_eva.ui.theme import inject_theme


class RomanianLitEvaApp:
    def __init__(self) -> None:
        self.navigator = Navigator()
        self.api_client = PlatformApiClient(base_url=settings.API_BASE)
        self.shell = AppShell(navigator=self.navigator, api_client=self.api_client)

        self.pages = {
            settings.PAGE_HOME: HomePage(self.navigator, self.api_client),
            settings.PAGE_CATALOG: CatalogPage(self.navigator, self.api_client),
            settings.PAGE_SEARCH: SearchPage(self.navigator, self.api_client),
            settings.PAGE_RANKINGS: RankingsPage(self.navigator, self.api_client),
            settings.PAGE_MODERATION: ModerationPage(self.navigator, self.api_client),
            settings.PAGE_EDITION: EditionDetailPage(self.navigator, self.api_client),
        }

    def run(self) -> None:
        st.set_page_config(
            page_title="Platformă Evaluare Literatură Română",
            page_icon="📚",
            layout="wide",
        )
        self.navigator.ensure()
        inject_theme()

        self.shell.render_header()
        page_name = self.navigator.current_page()
        page = self.pages.get(page_name, self.pages[settings.PAGE_HOME])
        page.render()
        self.shell.render_footer()
