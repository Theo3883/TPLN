import streamlit as st


def inject_theme() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400;1,500&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

        :root {
            --bg: #f5f2ed;
            --fg: #1a1a1a;
            --muted: rgba(26,26,26,.62);
            --line: rgba(26,26,26,.12);
            --card: #ffffff;
            --accent: #1a1a1a;
            --soft: #e8e4dc;
        }

        .stApp {
            background: var(--bg);
            color: var(--fg);
            font-family: Inter, ui-sans-serif, system-ui, sans-serif;
        }

        .block-container {
            max-width: 100%;
            padding-left: 3rem;
            padding-right: 3rem;
            padding-top: 1.4rem;
            padding-bottom: 3rem;
        }

        .shell-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 1px solid var(--line);
            padding-bottom: 1rem;
            margin-bottom: 1.2rem;
        }

        .brand {
            display: flex;
            align-items: center;
            gap: .75rem;
        }

        .brand-badge {
            width: 40px;
            height: 40px;
            border-radius: 999px;
            border: 1px solid var(--fg);
            background: var(--fg);
            color: #fff;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: Cormorant Garamond, Georgia, serif;
            font-style: italic;
            font-weight: 700;
        }

        .brand-main {
            font-family: Cormorant Garamond, Georgia, serif;
            font-size: 1.42rem;
            line-height: 1;
        }

        .brand-sub {
            margin-top: 2px;
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: .2em;
            color: var(--muted);
        }

        .hero-kicker {
            display: inline-flex;
            align-items: center;
            gap: .7rem;
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: .2em;
            color: var(--muted);
            font-weight: 600;
        }

        .hero-line {
            width: 30px;
            height: 1px;
            background: var(--fg);
        }

        .hero-title {
            font-family: Cormorant Garamond, Georgia, serif;
            font-size: clamp(2.2rem, 7vw, 4.9rem);
            line-height: 1.08;
            font-weight: 300;
            margin: .85rem 0 .45rem 0;
        }

        .hero-copy {
            font-family: Cormorant Garamond, Georgia, serif;
            font-size: 1.2rem;
            line-height: 1.55;
            max-width: 560px;
            color: var(--muted);
        }

        .section-title {
            font-family: Cormorant Garamond, Georgia, serif;
            font-size: clamp(2rem, 5vw, 3.3rem);
            line-height: 1.1;
            font-weight: 300;
            margin: 0;
        }

        .section-sub {
            margin-top: .45rem;
            color: var(--muted);
            font-size: .92rem;
        }

        .card {
            background: var(--card);
            border: 1px solid var(--line);
            border-radius: 24px;
            padding: 1.08rem;
        }

        .feature-card {
            min-height: 170px;
            border-radius: 20px;
            border: 1px solid var(--line);
            background: var(--card);
            padding: 1.2rem;
        }

        .feature-title {
            margin-top: .4rem;
            margin-bottom: .35rem;
            font-family: Cormorant Garamond, Georgia, serif;
            font-size: 1.34rem;
        }

        .cover {
            width: 100%;
            aspect-ratio: 3 / 4;
            border: 1px solid rgba(26,26,26,.08);
            border-radius: 16px;
            background: linear-gradient(180deg, #eee9e0 0%, #d9d4ca 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: rgba(26,26,26,.33);
            font-family: Cormorant Garamond, Georgia, serif;
            font-size: 2rem;
            text-transform: uppercase;
        }

        .mono {
            font-family: JetBrains Mono, ui-monospace, SFMono-Regular, Menlo, monospace;
        }

        .kicker {
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: .16em;
            color: var(--muted);
        }

        .muted {
            color: var(--muted);
        }

        .metric-wrap {
            display: flex;
            align-items: center;
            gap: .6rem;
            margin-top: .35rem;
        }

        .metric-bar {
            width: 92px;
            height: 6px;
            border-radius: 999px;
            overflow: hidden;
            background: rgba(26,26,26,.1);
        }

        .metric-bar span {
            display: block;
            height: 100%;
            background: var(--accent);
        }

        .foot {
            border-top: 1px solid var(--line);
            padding-top: 1.3rem;
            margin-top: 2.8rem;
            display: flex;
            justify-content: space-between;
            gap: 1rem;
            flex-wrap: wrap;
            color: var(--muted);
        }

        @media (max-width: 900px) {
            .hero-copy {
                font-size: 1.05rem;
            }
            .block-container {
                padding-left: 1.2rem;
                padding-right: 1.2rem;
            }
        }

        @media (max-width: 768px) {
            .brand {
                justify-content: center;
                margin-bottom: 1rem;
            }
            
            .hero-title {
                font-size: 3rem;
                text-align: center;
            }
            .hero-copy {
                text-align: center;
                margin: 0 auto;
            }
            .hero-kicker {
                display: flex;
                justify-content: center;
                margin: 0 auto 1rem auto;
            }
            
            .arch-container {
                margin-top: 2.5rem;
                border-top-left-radius: 200px;
                border-top-right-radius: 200px;
                max-height: 500px;
            }

            .edition-badge {
                left: 10px;
                bottom: -20px;
                width: 100px;
                height: 100px;
            }
            
            .edition-badge div:first-child {
                font-size: 1.4rem !important;
            }

            /* Make navigation horizontally scrollable on mobile */
            div[data-testid="stHorizontalBlock"]:nth-of-type(1) > div[data-testid="column"]:nth-of-type(2) > div[data-testid="stVerticalBlock"] > div > div[data-testid="stHorizontalBlock"] {
                flex-direction: row !important;
                flex-wrap: nowrap !important;
                overflow-x: auto !important;
                justify-content: flex-start;
                padding-bottom: 10px;
                scrollbar-width: none;
            }
            div[data-testid="stHorizontalBlock"]:nth-of-type(1) > div[data-testid="column"]:nth-of-type(2) > div[data-testid="stVerticalBlock"] > div > div[data-testid="stHorizontalBlock"]::-webkit-scrollbar {
                display: none;
            }
            div[data-testid="stHorizontalBlock"]:nth-of-type(1) > div[data-testid="column"]:nth-of-type(2) > div[data-testid="stVerticalBlock"] > div > div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
                width: auto !important;
                min-width: max-content !important;
                flex: 0 0 auto !important;
                padding-right: 0.5rem;
            }
        }
        
        /* Primary Button - Dark Pill */
        div[data-testid="stButton"] > button[kind="primary"] {
            background: var(--accent);
            color: #ffffff;
            border: 1px solid var(--accent);
            border-radius: 999px;
            font-family: Inter, ui-sans-serif, system-ui, sans-serif;
            font-weight: 500;
            padding: 0.5rem 1.5rem;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            font-size: 0.8rem;
        }

        /* Secondary Button - Outlined Pill */
        div[data-testid="stButton"] > button[kind="secondary"] {
            background: transparent;
            color: var(--accent);
            border: 1px solid rgba(26,26,26,.2);
            border-radius: 999px;
            font-family: Inter, ui-sans-serif, system-ui, sans-serif;
            font-weight: 600;
            padding: 0.5rem 1.5rem;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            font-size: 0.8rem;
        }

        /* Tertiary Button - Navigation Text */
        div[data-testid="stButton"] > button[kind="tertiary"] {
            background: transparent;
            color: var(--muted);
            border: none;
            font-family: Inter, ui-sans-serif, system-ui, sans-serif;
            font-weight: 600;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            font-size: 0.8rem;
            padding: 0.2rem 0.5rem;
        }
        div[data-testid="stButton"] > button[kind="tertiary"]:hover {
            color: var(--accent);
            background: transparent;
        }

        /* Form and Link Buttons (fallback to generic rounded) */
        div[data-testid="stFormSubmitButton"] > button,
        div[data-testid="stLinkButton"] > a {
            background: var(--accent);
            color: #ffffff;
            border: 1px solid var(--accent);
            border-radius: 8px;
            font-family: Inter, ui-sans-serif, system-ui, sans-serif;
            font-weight: 500;
        }

        /* Arch Cover Styles */
        .arch-container {
            position: relative;
            width: 100%;
            aspect-ratio: 3.5 / 4;
            max-height: 800px;
            border-top-left-radius: 500px;
            border-top-right-radius: 500px;
            background-image: url('https://images.unsplash.com/photo-1495446815901-a7297e633e8d?q=80&w=2070&auto=format&fit=crop');
            background-size: cover;
            background-position: center;
        }

        .edition-badge {
            position: absolute;
            bottom: -30px;
            left: -30px;
            width: 140px;
            height: 140px;
            background: #1a1a1a;
            border-radius: 50%;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            color: white;
            z-index: 10;
        }
        
        /* Hide top padding of Streamlit */
        .stAppHeader {
            display: none;
        }
        .block-container {
            padding-top: 2rem !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
