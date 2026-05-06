from __future__ import annotations

import streamlit as st

from romanian_lit_eva import settings
from romanian_lit_eva.api.client import ApiError, PlatformApiClient
from romanian_lit_eva.pages.base import Page
from romanian_lit_eva.services.mappers import to_edition_card
from romanian_lit_eva.services.navigation import Navigator
from romanian_lit_eva.ui.components import confidence_markup, cover_markup, safe, section_header_markup


class CatalogPage(Page):
    def __init__(self, navigator: Navigator, api_client: PlatformApiClient):
        self.navigator = navigator
        self.api_client = api_client

    def render(self) -> None:
        st.markdown(
            section_header_markup("Literary Catalog", "Browse, review, and evaluate Romanian editions."),
            unsafe_allow_html=True,
        )



        try:
            editions = [to_edition_card(raw) for raw in self.api_client.list_editions(limit=90)]
        except ApiError as exc:
            st.error(f"Catalog error: {exc}")
            return

        if not editions:
            st.info("Catalogul este gol. Rulează crawlerul pentru a adăuga titluri.")
            return

        cols = st.columns(3)
        for idx, item in enumerate(editions):
            with cols[idx % 3]:
                st.markdown(
                    f"""
                    <div class='card'>
                      {cover_markup(item.title[:1])}
                      <div style='display:flex;justify-content:space-between;gap:.8rem;margin-top:1rem;align-items:flex-start;'>
                        <div style='font-family:Cormorant Garamond, Georgia, serif;font-size:1.4rem;line-height:1.15;'>{safe(item.title)}</div>
                        <div class='mono' style='font-size:.68rem;background:rgba(26,26,26,.06);padding:.22rem .45rem;border-radius:4px;'>{safe(item.year)}</div>
                      </div>
                      <div class='muted' style='font-size:.88rem;margin-top:.25rem;'>{safe(item.authors)}</div>
                      <div style='border-top:1px solid rgba(26,26,26,.1);margin-top:.95rem;padding-top:.8rem;display:flex;justify-content:space-between;'>
                        <div>
                          <div class='kicker'>Bayesian score</div>
                          <div class='mono' style='font-size:1.05rem;'>{item.score:.2f}</div>
                        </div>
                        <div style='text-align:right;'>
                          <div class='kicker'>Reviews</div>
                          <div style='font-family:Cormorant Garamond, Georgia, serif;font-style:italic;font-size:1.1rem;'>{item.review_count}</div>
                        </div>
                      </div>
                      {confidence_markup(item.confidence)}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button("View details", key=f"catalog_open_{item.id}", use_container_width=True):
                    self.navigator.go_edition(item.id)
