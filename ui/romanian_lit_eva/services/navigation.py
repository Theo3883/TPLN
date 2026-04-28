from __future__ import annotations

import streamlit as st

from romanian_lit_eva import settings


class Navigator:
    _KEY_PAGE = "page"
    _KEY_SELECTED_EDITION = "selected_edition"

    def ensure(self) -> None:
        if self._KEY_PAGE not in st.session_state:
            st.session_state[self._KEY_PAGE] = settings.PAGE_HOME
        if self._KEY_SELECTED_EDITION not in st.session_state:
            st.session_state[self._KEY_SELECTED_EDITION] = None

    def current_page(self) -> str:
        return st.session_state[self._KEY_PAGE]

    def selected_edition(self) -> int | None:
        value = st.session_state.get(self._KEY_SELECTED_EDITION)
        return int(value) if value else None

    def go(self, page: str) -> None:
        st.session_state[self._KEY_PAGE] = page
        st.rerun()

    def go_edition(self, edition_id: int) -> None:
        st.session_state[self._KEY_SELECTED_EDITION] = edition_id
        st.session_state[self._KEY_PAGE] = settings.PAGE_EDITION
        st.rerun()
