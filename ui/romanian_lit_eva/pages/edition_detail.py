from __future__ import annotations

from datetime import datetime

import streamlit as st

from romanian_lit_eva import settings
from romanian_lit_eva.api.client import ApiError, PlatformApiClient
from romanian_lit_eva.pages.base import Page
from romanian_lit_eva.services.mappers import to_edition_card, to_review_item
from romanian_lit_eva.services.navigation import Navigator
from romanian_lit_eva.ui.components import cover_markup, safe


class EditionDetailPage(Page):
    def __init__(self, navigator: Navigator, api_client: PlatformApiClient):
        self.navigator = navigator
        self.api_client = api_client

    def render(self) -> None:
        edition_id = self.navigator.selected_edition()
        if not edition_id:
            st.info("No edition selected.")
            if st.button("Back to catalog"):
                self.navigator.go(settings.PAGE_CATALOG)
            return

        try:
            edition = to_edition_card(self.api_client.get_edition(edition_id))
            reviews = [to_review_item(raw) for raw in self.api_client.get_edition_reviews(edition_id)]
        except ApiError as exc:
            st.error(f"Edition detail error: {exc}")
            if st.button("Back to catalog"):
                self.navigator.go(settings.PAGE_CATALOG)
            return

        if st.button("Back to catalog"):
            self.navigator.go(settings.PAGE_CATALOG)

        left, right = st.columns([1, 1.5], gap="large")
        with left:
            st.markdown(cover_markup(edition.title[:1]), unsafe_allow_html=True)
        with right:
            st.markdown(f"<h1 class='section-title' style='margin-bottom:.2rem;'>{safe(edition.title)}</h1>", unsafe_allow_html=True)
            st.markdown(
                f"<div style='font-family:Cormorant Garamond, Georgia, serif;font-size:1.6rem;font-style:italic;opacity:.7;margin-bottom:1rem;'>{safe(edition.authors)}</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"""
                <div class='card' style='border-radius:16px;'>
                  <div style='display:grid;grid-template-columns:1fr 1fr;gap:.8rem;'>
                    <div><div class='kicker'>Publisher</div><div>{safe(edition.publisher)}</div></div>
                    <div><div class='kicker'>Year</div><div class='mono'>{safe(edition.year)}</div></div>
                    <div><div class='kicker'>ISBN</div><div class='mono'>{safe(edition.isbn)}</div></div>
                    <div><div class='kicker'>Reviews</div><div>{edition.review_count}</div></div>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown(
                f"""
                <div class='card' style='margin-top:.8rem;background:#1a1a1a;color:white;'>
                  <div class='kicker' style='color:rgba(255,255,255,.8);'>Bayesian confidence score</div>
                  <div class='mono' style='font-size:1.8rem;margin-top:.2rem;'>{edition.score:.2f}</div>
                  <div style='font-size:.82rem;color:rgba(255,255,255,.75);'>confidence index {edition.confidence:.2f}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height:.9rem;'></div>", unsafe_allow_html=True)
        st.markdown("<h3 style='font-family:Cormorant Garamond, Georgia, serif;font-size:2rem;font-weight:500;margin-bottom:.45rem;'>Evaluate Edition</h3>", unsafe_allow_html=True)
        with st.form("review_form", clear_on_submit=True):
            rating = st.slider("Rating (1-5)", min_value=1.0, max_value=5.0, value=3.0, step=0.5)
            content = st.text_area("Review text", placeholder="Share your detailed analysis...")
            reviewer = st.text_input("Reviewer identifier", value="anonymous")
            submitted = st.form_submit_button("Submit")
            if submitted:
                try:
                    self.api_client.create_review(
                        edition_id=edition.id,
                        content=content,
                        rating=rating,
                        reviewer_identifier=reviewer or "anonymous",
                    )
                    st.success("Evaluation submitted. It is now in moderation queue.")
                    st.rerun()
                except ApiError as exc:
                    st.error(f"Submit failed: {exc}")

        st.markdown("<h3 style='font-family:Cormorant Garamond, Georgia, serif;font-size:2rem;font-weight:500;margin:1.2rem 0 .45rem 0;'>Public Reviews</h3>", unsafe_allow_html=True)
        approved = [review for review in reviews if review.status == "approved"]
        if not approved:
            st.markdown(
                "<div class='card' style='text-align:center;'><div style='font-family:Cormorant Garamond, Georgia, serif;font-style:italic;opacity:.6;'>No approved reviews yet.</div></div>",
                unsafe_allow_html=True,
            )
            return

        for review in approved:
            st.markdown(
                f"""
                <div class='card' style='margin-top:.6rem;'>
                  <div style='display:flex;justify-content:space-between;gap:.8rem;align-items:flex-start;'>
                    <div>
                      <div class='mono muted' style='font-size:.72rem;'>{safe(self._format_date(review.created_at))}</div>
                      <div style='font-size:.96rem;'>{safe(review.content)}</div>
                    </div>
                    <div class='mono'>{review.rating}/5</div>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    @staticmethod
    def _format_date(raw: str) -> str:
        try:
            return datetime.fromisoformat(raw.replace("Z", "+00:00")).strftime("%Y-%m-%d")
        except Exception:
            return raw
