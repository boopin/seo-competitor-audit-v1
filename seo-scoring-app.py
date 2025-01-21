import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

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
        weaknesses = []

        # Meta Title Analysis
        if 'Title 1' in df.columns and 'Title 1 Length' in df.columns:
            valid_titles = df['Title 1'].notna()
            good_length = (df['Title 1 Length'] >= 30) & (df['Title 1 Length'] <= 60)
            title_score = ((valid_titles & good_length).mean() * 100)
            if title_score < 50:
                weaknesses.append("Meta titles are not optimized.")
        else:
            title_score = 0
        scores['meta_title'] = round(title_score)

        # Meta Description Analysis
        if 'Meta Description 1' in df.columns and 'Meta Description 1 Length' in df.columns:
            valid_desc = df['Meta Description 1'].notna()
            good_length = (df['Meta Description 1 Length'] >= 120) & (df['Meta Description 1 Length'] <= 160)
            desc_score = ((valid_desc & good_length).mean() * 100)
            if desc_score < 50:
                weaknesses.append("Meta descriptions are missing or too short.")
        else:
            desc_score = 0
        scores['meta_description'] = round(desc_score)

        # H1 Tags
        if 'H1-1' in df.columns:
            h1_score = df['H1-1'].notna().mean() * 100
            if h1_score < 50:
                weaknesses.append("Missing or poorly optimized H1 tags.")
        else:
            h1_score = 0
        scores['h1_tags'] = round(h1_score)

        return round(np.mean(list(scores.values()))), scores, weaknesses

    def analyze_technical_seo(self, df):
        scores = {}
        weaknesses = []

        # Indexability
        if 'Indexability' in df.columns:
            indexable = df['Indexability'] == 'Indexable'
            index_score = indexable.mean() * 100
            if index_score < 70:
                weaknesses.append("Pages are not indexable.")
        else:
            index_score = 0
        scores['indexability'] = round(index_score)

        return round(np.mean(list(scores.values()))), scores, weaknesses

    def analyze_user_experience(self, df):
        scores = {}
        weaknesses = []

        # Mobile Friendliness
        if 'Mobile Alternate Link' in df.columns:
            mobile_score = df['Mobile Alternate Link'].notna().mean() * 100
            if mobile_score < 50:
                weaknesses.append("Pages are not mobile-friendly.")
        else:
            mobile_score = 0
        scores['mobile_friendly'] = round(mobile_score)

        # Largest Contentful Paint
        if 'Largest Contentful Paint Time (ms)' in df.columns:
            lcp_score = (df['Largest Contentful Paint Time (ms)'] <= 2500).mean() * 100
            if lcp_score < 50:
                weaknesses.append("Slow loading speed (LCP).")
        else:
            lcp_score = 0
        scores['largest_contentful_paint'] = round(lcp_score)

        return round(np.mean(list(scores.values()))), scores, weaknesses

    def calculate_overall_score(self, content_score, technical_score, ux_score):
        weighted_scores = {
            'Content SEO': content_score / 100 * self.weights['content_seo'],
            'Technical SEO': technical_score / 100 * self.weights['technical_seo'],
            'User Experience': ux_score / 100 * self.weights['user_experience']
        }
        overall_score = round(sum(weighted_scores.values()) / sum(self.weights.values()) * 100)
        category = "Good" if overall_score >= 90 else "Medium" if overall_score >= 50 else "Bad"
        return overall_score, category

def main():
    st.set_page_config(page_title="SEO Readiness Analysis", layout="wide")
    st.title("SEO Readiness Analysis Tool")
    uploaded_file = st.file_uploader("Upload Screaming Frog Export (CSV or XLSX)", type=['csv', 'xlsx'])

    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
            scorer = SEOScorer()

            content_score, content_details, content_weaknesses = scorer.analyze_content_seo(df)
            technical_score, technical_details, technical_weaknesses = scorer.analyze_technical_seo(df)
            ux_score, ux_details, ux_weaknesses = scorer.analyze_user_experience(df)
            overall_score, category = scorer.calculate_overall_score(content_score, technical_score, ux_score)

            # Display scores
            st.metric("Content SEO", f"{content_score}/100")
            st.metric("Technical SEO", f"{technical_score}/100")
            st.metric("User Experience", f"{ux_score}/100")
            st.metric("Overall Score", f"{overall_score}/100 - {category}")

            # Display weaknesses
            st.subheader("Identified Weaknesses")
            for weakness in content_weaknesses + technical_weaknesses + ux_weaknesses:
                st.write(f"- {weakness}")

        except Exception as e:
            st.error(f"Error processing file: {str(e)}")

if __name__ == "__main__":
    main()
