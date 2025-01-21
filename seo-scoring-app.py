import streamlit as st
import pandas as pd
import numpy as np
import json
from datetime import datetime
from io import BytesIO

class SEOScorer:
    def __init__(self):
        self.weights = {
            'content_seo': 0.3,
            'technical_seo': 0.3,
            'user_experience': 0.2,
            'off_page_seo': 0.2
        }

    def analyze_content_seo(self, df):
        scores = {}

        # Meta Title Analysis
        if 'Title 1' in df.columns and 'Title 1 Length' in df.columns:
            valid_titles = df['Title 1'].notna()
            good_length = (df['Title 1 Length'] >= 30) & (df['Title 1 Length'] <= 60)
            scores['meta_title'] = round((valid_titles & good_length).mean() * 100)
        else:
            scores['meta_title'] = 0

        # Meta Description Analysis
        if 'Meta Description 1' in df.columns and 'Meta Description 1 Length' in df.columns:
            valid_desc = df['Meta Description 1'].notna()
            good_length = (df['Meta Description 1 Length'] >= 120) & (df['Meta Description 1 Length'] <= 160)
            scores['meta_description'] = round((valid_desc & good_length).mean() * 100)
        else:
            scores['meta_description'] = 0

        # H1 Tags
        if 'H1-1' in df.columns:
            scores['h1_tags'] = round(df['H1-1'].notna().mean() * 100)
        else:
            scores['h1_tags'] = 0

        # Internal Linking
        if 'Inlinks' in df.columns:
            scores['internal_linking'] = round((df['Inlinks'] > 0).mean() * 100)
        else:
            scores['internal_linking'] = 0

        return round(np.mean(list(scores.values()))), scores

    def analyze_technical_seo(self, df):
        scores = {}

        # Indexability
        if 'Indexability' in df.columns:
            scores['indexability'] = round((df['Indexability'] == 'Indexable').mean() * 100)
        else:
            scores['indexability'] = 0

        # Response Time
        if 'Response Time' in df.columns:
            scores['response_time'] = round((df['Response Time'] <= 1.0).mean() * 100)
        else:
            scores['response_time'] = 0

        return round(np.mean(list(scores.values()))), scores

    def analyze_user_experience(self, df):
        scores = {}

        # Mobile Friendly
        if 'Mobile Alternate Link' in df.columns:
            scores['mobile_friendly'] = round(df['Mobile Alternate Link'].notna().mean() * 100)
        else:
            scores['mobile_friendly'] = 0

        # Largest Contentful Paint (LCP)
        if 'Largest Contentful Paint Time (ms)' in df.columns:
            scores['largest_contentful_paint'] = round((df['Largest Contentful Paint Time (ms)'] <= 2500).mean() * 100)
        else:
            scores['largest_contentful_paint'] = 0

        # Cumulative Layout Shift (CLS)
        if 'Cumulative Layout Shift' in df.columns:
            scores['cumulative_layout_shift'] = round((df['Cumulative Layout Shift'] <= 0.1).mean() * 100)
        else:
            scores['cumulative_layout_shift'] = 0

        return round(np.mean(list(scores.values()))), scores

    def calculate_overall_score(self, content_score, technical_score, ux_score):
        content_score = content_score / 100
        technical_score = technical_score / 100
        ux_score = ux_score / 100

        weighted_scores = {
            'Content SEO': content_score * self.weights['content_seo'],
            'Technical SEO': technical_score * self.weights['technical_seo'],
            'User Experience': ux_score * self.weights['user_experience']
        }

        return round(sum(weighted_scores.values()) / sum(self.weights.values()) * 100)

def main():
    st.set_page_config(page_title="SEO Readiness Scorer", layout="wide")
    st.title("SEO Readiness Score Calculator")
    st.write("Upload your Screaming Frog exports to analyze SEO readiness")

    uploaded_file = st.file_uploader("Upload Internal HTML Report (CSV or XLSX)", type=['csv', 'xlsx'])

    if uploaded_file:
        try:
            # Load file
            df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)

            # Initialize scorer
            scorer = SEOScorer()

            # Calculate scores
            content_score, content_details = scorer.analyze_content_seo(df)
            technical_score, technical_details = scorer.analyze_technical_seo(df)
            ux_score, ux_details = scorer.analyze_user_experience(df)

            overall_score = scorer.calculate_overall_score(content_score, technical_score, ux_score)

            # Display results
            st.header("SEO Readiness Scores")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Content SEO Score", f"{content_score}/100")
                st.subheader("Content Details")
                for metric, score in content_details.items():
                    st.write(f"{metric.replace('_', ' ').title()}: {score}/100")

            with col2:
                st.metric("Technical SEO Score", f"{technical_score}/100")
                st.subheader("Technical Details")
                for metric, score in technical_details.items():
                    st.write(f"{metric.replace('_', ' ').title()}: {score}/100")

            with col3:
                st.metric("User Experience Score", f"{ux_score}/100")
                st.subheader("UX Details")
                for metric, score in ux_details.items():
                    st.write(f"{metric.replace('_', ' ').title()}: {score}/100")

            st.header("Overall SEO Readiness Score")
            st.metric("Final Score", f"{overall_score}/100")

        except Exception as e:
            st.error(f"Error processing file: {str(e)}")

if __name__ == "__main__":
    main()
