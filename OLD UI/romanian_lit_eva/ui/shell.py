from __future__ import annotations

import streamlit as st

from romanian_lit_eva import settings
from romanian_lit_eva.api.client import ApiError, PlatformApiClient
from romanian_lit_eva.services.navigation import Navigator


class AppShell:
    def __init__(self, navigator: Navigator, api_client: PlatformApiClient):
        self.navigator = navigator
        self.api_client = api_client

    def render_header(self) -> None:
        top_cols = st.columns([2, 5])
        with top_cols[0]:
            st.markdown(
                """
                <div class='brand' style='padding-top: .8rem;'>
                  <div class='brand-badge'>R</div>
                  <div>
                    <div class='brand-main'>Romanian Lit</div>
                    <div class='brand-sub'>Evaluation Platform</div>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        
        with top_cols[1]:
            st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)
            nav_cols = st.columns(len(settings.NAV_ITEMS))
            for idx, (label, page, icon) in enumerate(settings.NAV_ITEMS):
                with nav_cols[idx]:
                    is_active = self.navigator.current_page() == page
                    if st.button(label, icon=icon, key=f"nav_{page}", type="tertiary", use_container_width=True):
                        self.navigator.go(page)
                    
                    if is_active:
                        st.markdown("<div style='height:2px;background:var(--fg);margin-top:-14px;width:75%;margin-left:auto;margin-right:auto;position:relative;z-index:999;'></div>", unsafe_allow_html=True)

        st.markdown("<div style='border-bottom: 1px solid var(--line); margin-bottom: 2.5rem; margin-top: 1rem;'></div>", unsafe_allow_html=True)

    def render_footer(self) -> None:
        st.markdown(
            f"""
            <div class='foot'>
              <div>
                <div style='font-family:Cormorant Garamond, Georgia, serif;font-size:1.2rem;font-style:italic;'>Platforma CRET</div>
                <div class='kicker'>Continuous Evaluation of Romanian Editions</div>
              </div>
              <div style='display:flex;gap:1rem;font-size:10px;letter-spacing:.1em;text-transform:uppercase;align-items:center;'>
                <a href='{settings.API_BASE}/docs' target='_blank' style='text-decoration:none;color:inherit;'>Documentation</a>
                <a href='{settings.API_BASE}/export?format=csv' target='_blank' style='text-decoration:none;color:inherit;'>Export CSV</a>
                <a href='{settings.API_BASE}/export?format=json' target='_blank' style='text-decoration:none;color:inherit;'>Export JSON</a>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        c = st.columns([1, 1, 1, 1, 1, 2])
        with c[5]:
            if st.button("Run Crawler Tool", key="nav_crawler", type="tertiary", use_container_width=True):
                try:
                    self.api_client.run_crawler()
                    st.success("Crawler started.")
                except ApiError as exc:
                    st.error(f"Crawler error: {exc}")
