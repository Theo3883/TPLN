from __future__ import annotations

import streamlit as st

from romanian_lit_eva import settings
from romanian_lit_eva.api.client import ApiError, PlatformApiClient
from romanian_lit_eva.pages.base import Page
from romanian_lit_eva.services.navigation import Navigator
from romanian_lit_eva.ui.components import cover_markup, safe


class HomePage(Page):
    def __init__(self, navigator: Navigator, api_client: PlatformApiClient):
        self.navigator = navigator
        self.api_client = api_client

    def render(self) -> None:
        left, right = st.columns([1.2, 1], gap="large")
        with left:
            st.markdown(
                """
                <div class='hero-kicker'><span class='hero-line'></span>Continuous Evaluation</div>
                <h1 class='hero-title'>Preserving <br /><em>Romanian Literature</em></h1>
                <p class='hero-copy'>A comprehensive web platform for data ingestion, user reviews, and transparent ranking of Romanian literature editions.</p>
                """,
                unsafe_allow_html=True,
            )

            st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
            c1, c2 = st.columns([1, 1])
            with c1:
                if st.button("Browse Catalog ➔", key="home_catalog", type="primary", use_container_width=True):
                    self.navigator.go(settings.PAGE_CATALOG)
            with c2:
                if st.button("Search Database", key="home_search", type="secondary", use_container_width=True):
                    self.navigator.go(settings.PAGE_SEARCH)

        with right:
            total = "140+"
            try:
                editions = self.api_client.list_editions(limit=100)
                if editions:
                    total = f"{len(editions)}+"
            except ApiError:
                total = "140+"

            st.markdown(
                f"""
                <div class='arch-container'>
                    <div class='edition-badge'>
                        <div style='font-family:Cormorant Garamond, Georgia, serif;font-size:2rem;font-style:italic;'>{safe(total)}</div>
                        <div class='kicker' style='color:rgba(255,255,255,.8);'>Editions</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height:2.7rem;'></div>", unsafe_allow_html=True)
        st.markdown("<h2 class='section-title' style='text-align:center;'>Platform Architecture</h2>", unsafe_allow_html=True)

        features = [
            ("Data Ingestion", "Automated collection of metadata using crawlers for Romanian bookstores."),
            ("Meilisearch", "Blazing-fast full-text lookup with typo tolerance and instant filtering."),
            ("Bayesian Ranking", "Fair score model with shrinkage to prevent unstable top rankings."),
            ("Governance", "Moderation queue, audit trail, and review accountability controls."),
        ]
        cols = st.columns(4)
        for idx, col in enumerate(cols):
            title, desc = features[idx]
            with col:
                st.markdown(
                    f"""
                    <div class='feature-card'>
                      <div class='kicker'>Feature</div>
                      <div class='feature-title'>{safe(title)}</div>
                      <div class='muted' style='font-size:.9rem;line-height:1.5;'>{safe(desc)}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
