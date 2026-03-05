from urllib.parse import urljoin

import httpx
import streamlit as st

API_BASE = "http://localhost:8000"


def get_client():
    return httpx.Client(base_url=API_BASE, timeout=30)


def main():
    st.set_page_config(
        page_title="Platformă Evaluare Literatură Română",
        page_icon="📚",
        layout="wide",
    )
    st.title("Platformă Evaluare Literatură Română")

    sidebar = st.sidebar
    page = sidebar.radio(
        "Navigare",
        ["Catalog", "Căutare", "Ranking", "Moderare", "Export"],
    )
    sidebar.divider()
    if sidebar.button("Rulează crawlerul"):
        with get_client() as client:
            r = client.post("/ingest/run-crawler")
            if r.status_code == 200:
                sidebar.success("Crawler pornit!")
            else:
                sidebar.error("Eroare")

    if page == "Catalog":
        if "selected_edition" in st.session_state:
            eid = st.session_state["selected_edition"]
            with get_client() as client:
                r = client.get(f"/editions/{eid}")
                if r.status_code == 200:
                    e = r.json()
                    st.subheader(e.get("book", {}).get("title", "N/A"))
                    st.write(f"**Autori:** {', '.join(a.get('name', '') for a in e.get('authors', []))}")
                    st.write(f"**ISBN:** {e.get('isbn') or '-'} | **Editura:** {e.get('publisher') or '-'} | **An:** {e.get('year') or '-'}")
                    st.write(f"**Scor:** {e.get('score') or '-'} | **Încredere:** {e.get('confidence') or '-'} | **Recenzii:** {e.get('review_count', 0)}")
                    if st.button("Înapoi"):
                        del st.session_state["selected_edition"]
                        st.rerun()
                    st.divider()
                    st.write("**Recenzii:**")
                    rev_r = client.get(f"/editions/{eid}/reviews")
                    if rev_r.status_code == 200:
                        for rev in rev_r.json():
                            st.write(f"- {rev.get('content', '')[:200]}... (rating: {rev.get('rating')})")
                    st.write("**Audit trail:**")
                    audit_r = client.get(f"/audit/editions/{eid}")
                    if audit_r.status_code == 200:
                        for ev in audit_r.json():
                            st.write(f"- {ev.get('old_score')} → {ev.get('new_score')} ({ev.get('reason')})")
                else:
                    del st.session_state["selected_edition"]
                    st.rerun()
            return

        with get_client() as client:
            r = client.get("/editions", params={"limit": 50})
            if r.status_code != 200:
                st.error("Eroare la încărcarea catalogului")
                return
            editions = r.json()

        if not editions:
            st.info("Catalogul este gol. Rulează crawlerul pentru a adăuga titluri.")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Rulează crawlerul"):
                    with get_client() as client:
                        r = client.post("/ingest/run-crawler")
                        if r.status_code == 200:
                            st.success("Crawler pornit! Așteaptă câteva secunde, apoi apasă Reîmprospătează.")
                        else:
                            st.error("Eroare: " + r.text)
            with col2:
                if st.button("Reîmprospătează"):
                    st.rerun()
            return

        for e in editions:
            authors_str = ", ".join(a.get("name", "") for a in e.get("authors", []))
            with st.expander(f"{e.get('book', {}).get('title', 'N/A')} - {authors_str}"):
                st.write(f"**ISBN:** {e.get('isbn') or '-'} | **Editura:** {e.get('publisher') or '-'} | **An:** {e.get('year') or '-'}")
                st.write(f"**Scor:** {e.get('score') or '-'} | **Încredere:** {e.get('confidence') or '-'} | **Recenzii:** {e.get('review_count', 0)}")
                if st.button(f"Vezi detalii", key=f"view_{e['id']}"):
                    st.session_state["selected_edition"] = e["id"]
                    st.rerun()

    elif page == "Căutare":
        q = st.text_input("Caută titluri, autori, ISBN...")
        if q:
            with get_client() as client:
                r = client.get("/search/editions", params={"q": q})
                if r.status_code == 200:
                    results = r.json()
                    for e in results:
                        with st.container():
                            st.write(f"**{e.get('book', {}).get('title', 'N/A')}** - {', '.join(a.get('name', '') for a in e.get('authors', []))}")
                            st.write(f"Scor: {e.get('score') or '-'} | Recenzii: {e.get('review_count', 0)}")
                            if st.button(f"Adaugă recenzie", key=f"review_{e['id']}"):
                                st.session_state["review_edition"] = e["id"]
                                st.session_state["review_edition_title"] = e.get("book", {}).get("title", "")
                                st.rerun()

    elif page == "Ranking":
        with get_client() as client:
            r = client.get("/rankings", params={"limit": 50})
            if r.status_code != 200:
                st.error("Eroare la încărcarea ranking-ului")
                return
            items = r.json()

        if not items:
            st.info("Nu există încă ranking.")
            return

        st.dataframe(
            [
                {
                    "Titlu": i["title"],
                    "Autori": ", ".join(i["authors"]),
                    "Scor": i["score"],
                    "Încredere": i["confidence"],
                    "Recenzii": i["review_count"],
                }
                for i in items
            ],
            use_container_width=True,
        )

    elif page == "Moderare":
        with get_client() as client:
            r = client.get("/moderation/pending")
            if r.status_code != 200:
                st.error("Eroare la încărcarea recenziilor")
                return
            pending = r.json()

        if not pending:
            st.info("Nu există recenzii în așteptare.")
            return

        for rev in pending:
            with st.container():
                st.write(f"**Recenzie #{rev['id']}** (edition_id={rev['edition_id']})")
                st.write(rev["content"])
                st.write(f"Rating: {rev.get('rating')}")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Aprobă", key=f"approve_{rev['id']}"):
                        with get_client() as c:
                            c.post(f"/moderation/{rev['id']}/approve")
                        st.rerun()
                with col2:
                    if st.button("Respinge", key=f"reject_{rev['id']}"):
                        with get_client() as c:
                            c.post(f"/moderation/{rev['id']}/reject")
                        st.rerun()

    if page == "Export":
        st.subheader("Export date")
        st.write(f"[Export CSV]({API_BASE}/export?format=csv)")
        st.write(f"[Export JSON]({API_BASE}/export?format=json)")
        st.write(f"[Documentație API]({API_BASE}/docs)")
        return

    if "review_edition" in st.session_state:
        st.divider()
        st.subheader(f"Adaugă recenzie: {st.session_state.get('review_edition_title', '')}")
        with st.form("review_form"):
            content = st.text_area("Conținut recenzie")
            rating = st.slider("Rating (1-5)", 1.0, 5.0, 3.0, 0.5)
            if st.form_submit_button("Trimite"):
                with get_client() as client:
                    r = client.post(
                        "/reviews",
                        json={
                            "edition_id": st.session_state["review_edition"],
                            "content": content,
                            "rating": rating,
                            "reviewer_identifier": "anonymous",
                        },
                    )
                    if r.status_code == 200:
                        st.success("Recenzie adăugată!")
                        del st.session_state["review_edition"]
                        del st.session_state["review_edition_title"]
                    else:
                        st.error("Eroare: " + r.text)
                st.rerun()


if __name__ == "__main__":
    main()
