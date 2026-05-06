from __future__ import annotations

from datetime import datetime

import streamlit as st

from romanian_lit_eva.api.client import ApiError, PlatformApiClient
from romanian_lit_eva.pages.base import Page
from romanian_lit_eva.services.mappers import to_audit_item, to_ranking_item
from romanian_lit_eva.services.navigation import Navigator
from romanian_lit_eva.ui.components import safe, section_header_markup


class RankingsPage(Page):
    def __init__(self, navigator: Navigator, api_client: PlatformApiClient):
        self.navigator = navigator
        self.api_client = api_client

    def render(self) -> None:
        st.markdown(
            section_header_markup("Global Rankings", "Scores are calculated using a Bayesian shrinkage model to ensure fair and stable ranking positions."),
            unsafe_allow_html=True,
        )

        try:
            rankings = [to_ranking_item(raw) for raw in self.api_client.list_rankings(limit=60)]
        except ApiError as exc:
            st.error(f"Ranking error: {exc}")
            return

        if not rankings:
            st.info("No ranking entries yet.")
            return

        show_audit = st.toggle("View audit trail", value=False)
        if show_audit:
            self._render_audit(rankings)
            return

        st.markdown("<div class='card' style='padding:0;'>", unsafe_allow_html=True)
        st.markdown(
            """
            <div style='display:grid;grid-template-columns:70px 1.7fr 120px 140px 130px;gap:.5rem;padding:.9rem;border-bottom:1px solid rgba(26,26,26,.08);background:rgba(26,26,26,.04);'>
              <div class='kicker' style='text-align:center;'>Rank</div>
              <div class='kicker'>Edition</div>
              <div class='kicker' style='text-align:center;'>Reviews</div>
              <div class='kicker' style='text-align:center;'>Confidence</div>
              <div class='kicker' style='text-align:right;'>Score</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        for idx, item in enumerate(rankings, start=1):
            width = max(0, min(100, int(item.confidence * 100)))
            st.markdown(
                f"""
                <div style='display:grid;grid-template-columns:70px 1.7fr 120px 140px 130px;gap:.5rem;padding:.9rem;border-bottom:1px solid rgba(26,26,26,.06);align-items:center;'>
                  <div class='mono' style='text-align:center;opacity:.75;'>{idx}</div>
                  <div>
                    <div style='font-family:Cormorant Garamond, Georgia, serif;font-size:1.24rem;line-height:1;'>{safe(item.title)}</div>
                    <div class='muted' style='font-size:.84rem;margin-top:.16rem;'>{safe(item.authors)}</div>
                  </div>
                  <div style='text-align:center;font-family:Cormorant Garamond, Georgia, serif;font-style:italic;'>{item.review_count}</div>
                  <div style='display:flex;align-items:center;gap:.45rem;justify-content:center;'>
                    <div class='metric-bar'><span style='width:{width}%'></span></div>
                    <div class='mono muted' style='font-size:.65rem;'>{item.confidence:.2f}</div>
                  </div>
                  <div class='mono' style='text-align:right;font-size:1.2rem;'>{item.score:.1f}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Open edition", key=f"rank_open_{item.edition_id}"):
                self.navigator.go_edition(item.edition_id)

        st.markdown("</div>", unsafe_allow_html=True)

    def _render_audit(self, rankings: list) -> None:
        options = {f"#{r.edition_id} - {r.title}": r.edition_id for r in rankings}
        selected_label = st.selectbox("Select edition for audit", list(options.keys()))
        edition_id = options[selected_label]

        try:
            events = [to_audit_item(raw) for raw in self.api_client.get_audit(edition_id)]
        except ApiError as exc:
            st.error(f"Audit error: {exc}")
            return

        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<h2 style='font-family:Cormorant Garamond, Georgia, serif;font-size:2rem;margin:0 0 .8rem 0;'>Score Audit Trail</h2>", unsafe_allow_html=True)
        if not events:
            st.markdown("<div class='muted'>No score events found for this edition.</div>", unsafe_allow_html=True)
        for event in events:
            dt = self._format_date(event.created_at)
            old_value = "-" if event.old_score is None else f"{event.old_score:.2f}"
            new_value = "-" if event.new_score is None else f"{event.new_score:.2f}"
            st.markdown(
                f"""
                <div style='padding:.75rem 0;border-top:1px solid rgba(26,26,26,.08);'>
                  <div class='kicker'>{safe(dt)} - {safe(event.reason)}</div>
                  <div class='mono' style='margin-top:.2rem;'>{old_value} -> {new_value}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

    @staticmethod
    def _format_date(raw: str) -> str:
        try:
            return datetime.fromisoformat(raw.replace("Z", "+00:00")).strftime("%Y-%m-%d")
        except Exception:
            return raw
