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
            border-radius: 16px;
            margin-bottom: 1.5rem;
            border: 1px solid rgba(148, 163, 184, 0.25);
        }
        .ami-hero-labs {
            background: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #0c4a6e 100%);
        }
        .ami-hero h1 {
            color: #f8fafc !important;
            font-size: 2.1rem !important;
            font-weight: 700 !important;
            margin: 0 0 0.75rem 0 !important;
            line-height: 1.2 !important;
        }
        .ami-hero .ami-tagline {
            font-size: 1.2rem;
            line-height: 1.5;
            color: #e2e8f0;
            margin: 0 0 0.75rem 0;
            font-weight: 500;
        }
        .ami-hero .ami-purpose {
            font-size: 0.95rem;
            color: #94a3b8;
            border-top: 1px solid rgba(148, 163, 184, 0.3);
            padding-top: 1rem;
            margin: 0;
            line-height: 1.55;
        }
        .ami-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 14px;
            padding: 1.35rem 1.45rem;
            height: 100%;
            box-shadow: 0 1px 3px rgba(15, 23, 42, 0.06);
            transition: box-shadow 0.2s ease, border-color 0.2s ease, transform 0.2s ease;
        }
        .ami-card:hover {
            border-color: #0ea5e9;
            box-shadow: 0 6px 16px rgba(14, 165, 233, 0.14);
            transform: translateY(-2px);
        }
        .ami-card-accent { border-left: 4px solid #0ea5e9; }
        .ami-card-theme { border-left: 4px solid #6366f1; }
        .ami-card-domain { border-left: 4px solid #059669; }
        .ami-card-portfolio { border-left: 4px solid #d97706; }
        .ami-card-lab {
            border-left: 4px solid #8b5cf6;
            text-align: left;
        }
        .ami-card-lab .ami-lab-icon {
            font-size: 1.75rem;
            display: block;
            margin-bottom: 0.5rem;
        }
        .ami-lab-header {
            display: flex;
            align-items: center;
            gap: 1rem;
            margin-bottom: 1.25rem;
        }
        .ami-lab-icon-lg {
            font-size: 2.5rem;
            line-height: 1;
        }
        .ami-card h4 {
            margin: 0 0 0.4rem 0;
            font-size: 1.08rem;
            color: #0f172a;
        }
        .ami-card .ami-badge {
            display: inline-block;
            font-size: 0.68rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #0369a1;
            background: #e0f2fe;
            padding: 0.22rem 0.55rem;
            border-radius: 5px;
            margin-bottom: 0.55rem;
        }
        .ami-card-lab .ami-badge {
            color: #5b21b6;
            background: #ede9fe;
        }
        .ami-card p {
            margin: 0;
            font-size: 0.88rem;
            line-height: 1.55;
            color: #475569;
        }
        .ami-section-title {
            font-size: 1.4rem;
            font-weight: 650;
            color: #0f172a;
            margin: 2.25rem 0 0.35rem 0;
        }
        .ami-section-sub {
            color: #64748b;
            font-size: 0.92rem;
            margin: 0 0 1.25rem 0;
            line-height: 1.5;
        }
        .ami-stat-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.85rem;
            margin: 1.25rem 0 1.5rem 0;
        }
        .ami-stat {
            flex: 1;
            min-width: 120px;
            background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 1.1rem 1rem;
            text-align: center;
        }
        .ami-stat .ami-stat-num {
            font-size: 1.85rem;
            font-weight: 700;
            color: #0ea5e9;
            line-height: 1.15;
        }
        .ami-stat .ami-stat-label {
            font-size: 0.78rem;
            color: #64748b;
            margin-top: 0.3rem;
            line-height: 1.3;
        }
        .ami-summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 0.85rem;
            margin: 1rem 0 1.25rem 0;
        }
        .ami-summary-card {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 1rem 1.15rem;
        }
        .ami-summary-label {
            font-size: 0.72rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            color: #0ea5e9;
            margin-bottom: 0.4rem;
        }
        .ami-summary-text {
            font-size: 0.88rem;
            color: #334155;
            line-height: 1.5;
        }
        .ami-value-box {
            background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
            border: 1px solid #e2e8f0;
            border-radius: 14px;
            padding: 1.5rem 1.75rem;
            margin: 1rem 0;
        }
        .ami-nav-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 0.85rem;
            margin: 0.5rem 0 1.5rem 0;
        }
        .ami-nav-tile {
            background: #fff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 1.15rem;
            text-align: center;
        }
        .ami-nav-tile .ami-nav-icon {
            font-size: 1.5rem;
            margin-bottom: 0.35rem;
        }
        .ami-nav-tile h5 {
            margin: 0 0 0.25rem 0;
            color: #0f172a;
            font-size: 0.95rem;
        }
        .ami-nav-tile p {
            margin: 0;
            font-size: 0.8rem;
            color: #64748b;
            line-height: 1.4;
        }
        .ami-step {
            display: flex;
            gap: 1rem;
            margin-bottom: 0.85rem;
            align-items: flex-start;
            padding: 0.85rem 1rem;
            background: #fafafa;
            border-radius: 10px;
            border: 1px solid #f1f5f9;
        }
        .ami-step-num {
            flex-shrink: 0;
            width: 2rem;
            height: 2rem;
            background: linear-gradient(135deg, #0ea5e9, #0284c7);
            color: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 0.9rem;
        }
        .ami-step-body h5 {
            margin: 0 0 0.2rem 0;
            color: #0f172a;
            font-size: 0.98rem;
        }
        .ami-hero-action {
            background: linear-gradient(135deg, #0c4a6e 0%, #1e40af 45%, #312e81 100%);
        }
        .ami-hero-ref {
            background: linear-gradient(135deg, #334155 0%, #1e293b 55%, #0f172a 100%);
        }
        .ami-action-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 16px;
            padding: 1.75rem 1.5rem;
            height: 100%;
            text-align: center;
            box-shadow: 0 2px 8px rgba(15, 23, 42, 0.06);
            transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
        }
        .ami-action-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 12px 28px rgba(14, 165, 233, 0.15);
            border-color: #0ea5e9;
        }
        .ami-action-icon {
            font-size: 2.75rem;
            line-height: 1;
            margin-bottom: 0.75rem;
        }
        .ami-action-label {
            display: inline-block;
            font-size: 0.72rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: #0369a1;
            background: #e0f2fe;
            padding: 0.3rem 0.65rem;
            border-radius: 999px;
            margin-bottom: 0.65rem;
        }
        .ami-action-card h3 {
            margin: 0 0 0.5rem 0;
            font-size: 1.05rem;
            color: #0f172a;
            line-height: 1.3;
        }
        .ami-action-card p {
            margin: 0;
            font-size: 0.88rem;
            color: #64748b;
            line-height: 1.5;
        }
        .ami-action-tools {
            margin-top: 0.75rem;
            font-size: 0.75rem;
            color: #94a3b8;
            line-height: 1.4;
        }
        .ami-step-body p {
            margin: 0;
            color: #475569;
            font-size: 0.88rem;
            line-height: 1.5;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
