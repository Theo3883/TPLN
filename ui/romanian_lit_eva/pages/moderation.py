from __future__ import annotations

import streamlit as st

from romanian_lit_eva.api.client import ApiError, PlatformApiClient
from romanian_lit_eva.pages.base import Page
from romanian_lit_eva.services.mappers import to_review_item
from romanian_lit_eva.services.navigation import Navigator
from romanian_lit_eva.ui.components import safe, section_header_markup


class ModerationPage(Page):
    def __init__(self, navigator: Navigator, api_client: PlatformApiClient):
        self.navigator = navigator
        self.api_client = api_client

    def render(self) -> None:
        try:
            pending = [to_review_item(raw) for raw in self.api_client.get_pending_reviews()]
        except ApiError as exc:
            st.error(f"Moderation error: {exc}")
            return

        st.markdown(
            section_header_markup("Moderation Workspace", "Review pending evaluations for platform integrity."),
            unsafe_allow_html=True,
        )
        st.markdown(f"<div class='card mono' style='max-width:240px;margin-top:.8rem;'>Queue Size: {len(pending)}</div>", unsafe_allow_html=True)

        if not pending:
            st.markdown(
                """
                <div class='card' style='text-align:center;padding:2.8rem 1rem;margin-top:1rem;'>
                  <div style='font-family:Cormorant Garamond, Georgia, serif;font-size:1.5rem;font-style:italic;opacity:.56;'>Queue is empty</div>
                  <div class='muted'>All pending evaluations have been processed.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            return

        for review in pending:
            st.markdown(
                f"""
                <div class='card' style='margin-top:.8rem;'>
                  <div class='kicker'>Review #{review.id} - edition_id={review.edition_id}</div>
                  <div style='font-family:Cormorant Garamond, Georgia, serif;font-size:1.16rem;line-height:1.45;margin-top:.35rem;'>{safe(review.content)}</div>
                  <div class='muted' style='font-size:.82rem;margin-top:.26rem;'>Rating: {review.rating} | Status: {safe(review.status)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            c1, c2 = st.columns(2)
            with c1:
                if st.button("Approve", key=f"approve_{review.id}", use_container_width=True):
                    try:
                        self.api_client.approve_review(review.id)
                        st.success("Review approved.")
                        st.rerun()
                    except ApiError as exc:
                        st.error(f"Approve failed: {exc}")
            with c2:
                if st.button("Reject", key=f"reject_{review.id}", use_container_width=True):
                    try:
                        self.api_client.reject_review(review.id)
                        st.warning("Review rejected.")
                        st.rerun()
                    except ApiError as exc:
                        st.error(f"Reject failed: {exc}")
