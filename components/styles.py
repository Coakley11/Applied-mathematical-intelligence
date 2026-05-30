"""Global styling for a polished platform feel."""

import streamlit as st


def inject_platform_styles() -> None:
    st.markdown(
        """
        <style>
        .ami-hero {
            background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 55%, #0c4a6e 100%);
            color: #f8fafc;
            padding: 2.5rem 2rem;
            border-radius: 14px;
            margin-bottom: 1.5rem;
            border: 1px solid rgba(148, 163, 184, 0.25);
        }
        .ami-hero h1 {
            color: #f8fafc !important;
            font-size: 2rem !important;
            font-weight: 700 !important;
            margin: 0 0 0.75rem 0 !important;
            line-height: 1.2 !important;
        }
        .ami-hero .ami-tagline {
            font-size: 1.15rem;
            line-height: 1.55;
            color: #e2e8f0;
            margin: 0 0 1rem 0;
        }
        .ami-hero .ami-purpose {
            font-size: 0.95rem;
            color: #94a3b8;
            border-top: 1px solid rgba(148, 163, 184, 0.3);
            padding-top: 1rem;
            margin: 0;
        }
        .ami-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 1.25rem 1.35rem;
            height: 100%;
            box-shadow: 0 1px 3px rgba(15, 23, 42, 0.06);
            transition: box-shadow 0.15s ease, border-color 0.15s ease;
        }
        .ami-card:hover {
            border-color: #0ea5e9;
            box-shadow: 0 4px 12px rgba(14, 165, 233, 0.12);
        }
        .ami-card-accent {
            border-left: 4px solid #0ea5e9;
        }
        .ami-card-theme {
            border-left: 4px solid #6366f1;
        }
        .ami-card-domain {
            border-left: 4px solid #059669;
        }
        .ami-card-portfolio {
            border-left: 4px solid #d97706;
        }
        .ami-card h4 {
            margin: 0 0 0.35rem 0;
            font-size: 1.05rem;
            color: #0f172a;
        }
        .ami-card .ami-badge {
            display: inline-block;
            font-size: 0.7rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            color: #0369a1;
            background: #e0f2fe;
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            margin-bottom: 0.5rem;
        }
        .ami-card p {
            margin: 0;
            font-size: 0.88rem;
            line-height: 1.5;
            color: #475569;
        }
        .ami-section-title {
            font-size: 1.35rem;
            font-weight: 600;
            color: #0f172a;
            margin: 2rem 0 0.25rem 0;
        }
        .ami-section-sub {
            color: #64748b;
            font-size: 0.9rem;
            margin: 0 0 1rem 0;
        }
        .ami-stat-row {
            display: flex;
            flex-wrap: wrap;
            gap: 1rem;
            margin: 1rem 0 1.5rem 0;
        }
        .ami-stat {
            flex: 1;
            min-width: 140px;
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            padding: 1rem 1.25rem;
            text-align: center;
        }
        .ami-stat .ami-stat-num {
            font-size: 1.75rem;
            font-weight: 700;
            color: #0ea5e9;
            line-height: 1.2;
        }
        .ami-stat .ami-stat-label {
            font-size: 0.8rem;
            color: #64748b;
            margin-top: 0.25rem;
        }
        .ami-value-box {
            background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 1.5rem 1.75rem;
            margin: 1rem 0;
        }
        .ami-step {
            display: flex;
            gap: 1rem;
            margin-bottom: 1rem;
            align-items: flex-start;
        }
        .ami-step-num {
            flex-shrink: 0;
            width: 2rem;
            height: 2rem;
            background: #0ea5e9;
            color: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 0.9rem;
        }
        .ami-step-body h5 {
            margin: 0 0 0.25rem 0;
            color: #0f172a;
            font-size: 1rem;
        }
        .ami-step-body p {
            margin: 0;
            color: #475569;
            font-size: 0.9rem;
            line-height: 1.5;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
