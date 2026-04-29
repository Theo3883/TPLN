from __future__ import annotations

import streamlit as st

from romanian_lit_eva.api.client import ApiError, PlatformApiClient
from romanian_lit_eva.pages.base import Page
from romanian_lit_eva.services.mappers import to_edition_card
from romanian_lit_eva.services.navigation import Navigator
from romanian_lit_eva.ui.components import safe, section_header_markup


class SearchPage(Page):
    def __init__(self, navigator: Navigator, api_client: PlatformApiClient):
        self.navigator = navigator
        self.api_client = api_client

    def render(self) -> None:
        st.markdown(
            section_header_markup(
                "Full-Text Lookup",
                "Fast, typo-tolerant search powered by Meilisearch indexing schema.",
            ),
            unsafe_allow_html=True,
        )

        query = st.text_input(
            "Search by title, author, isbn or themes",
            placeholder="Search by title, author, isbn or themes...",
        )

        with st.expander("Advanced filters", expanded=False):
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                year_min = st.number_input(
                    "Year min",
                    min_value=0,
                    max_value=2100,
                    value=0,
                    step=1,
                )

            with col2:
                year_max = st.number_input(
                    "Year max",
                    min_value=0,
                    max_value=2100,
                    value=0,
                    step=1,
                )

            with col3:
                score_min = st.slider(
                    "Minimum score",
                    min_value=0.0,
                    max_value=5.0,
                    value=0.0,
                    step=0.1,
                )

            with col4:
                confidence_min = st.slider(
                    "Minimum confidence",
                    min_value=0.0,
                    max_value=1.0,
                    value=0.0,
                    step=0.05,
                )

            sort = st.selectbox(
                "Sort results",
                options=[
                    "relevance",
                    "score_desc",
                    "year_desc",
                    "confidence_desc",
                    "reviews_desc",
                ],
                format_func=lambda value: {
                    "relevance": "Relevance",
                    "score_desc": "Score descending",
                    "year_desc": "Year descending",
                    "confidence_desc": "Confidence descending",
                    "reviews_desc": "Most reviewed",
                }[value],
            )

        if not query.strip():
            st.markdown(
                """
                <div style='text-align:center;opacity:.32;padding:3.6rem 0;'>
                  <div style='font-size:2.3rem;'>⌕</div>
                  <div style='font-family:Cormorant Garamond, Georgia, serif;font-size:1.5rem;font-style:italic;'>Ready to search...</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            return

        try:
            results = [
                to_edition_card(raw)
                for raw in self.api_client.search_editions(
                    query,
                    year_min=year_min if year_min else None,
                    year_max=year_max if year_max else None,
                    score_min=score_min if score_min > 0 else None,
                    confidence_min=confidence_min if confidence_min > 0 else None,
                    sort=sort,
                )
            ]
        except ApiError as exc:
            st.error(f"Search error: {exc}")
            return

        st.caption(f"{len(results)} results found")

        if not results:
            st.markdown(
                """
                <div style='text-align:center;padding:3.2rem 0;'>
                  <div style='font-family:Cormorant Garamond, Georgia, serif;font-size:1.5rem;font-style:italic;opacity:.58;'>No editions found</div>
                  <div class='muted'>Try adjusting your search terms or checking for typos.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            return

        for item in results:
            row = st.columns([6, 1])
            with row[0]:
                st.markdown(
                    f"""
                    <div class='card' style='border-radius:16px;margin-bottom:.5rem;'>
                      <div style='display:flex;justify-content:space-between;align-items:flex-start;gap:1rem;'>
                        <div>
                          <div style='font-family:Cormorant Garamond, Georgia, serif;font-size:1.45rem;line-height:1.1;'>{safe(item.title)}</div>
                          <div class='muted' style='font-size:.9rem;margin-top:.25rem;'>{safe(item.authors)} - {safe(item.publisher)}</div>
                        </div>
                        <div class='mono' style='font-size:.72rem;padding:.2rem .45rem;border-radius:4px;background:rgba(26,26,26,.05);'>{safe(item.year)}</div>
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with row[1]:
                st.markdown(
                    f"<div class='mono' style='font-size:1.35rem;text-align:center;padding-top:.8rem;'>{item.score:.1f}</div>",
                    unsafe_allow_html=True,
                )
                if st.button("Open", key=f"search_open_{item.id}", use_container_width=True):
                    self.navigator.go_edition(item.id)