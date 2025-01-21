import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

class SEOScorer:
    def __init__(self):
        self.weights = {
            'content_seo': 0.4,  # Adjusted weight after removing off-page SEO
            'technical_seo': 0.4,
            'user_experience': 0.2
        }

    def analyze_content_seo(self, df):
        scores = {}
        weaknesses = []

        # Meta Title Analysis
        if 'Title 1' in df.columns and 'Title 1 Length' in df.columns:
            valid_titles = df['Title 1'].notna()
            good_length = (df['Title 1 Length'] >= 30) & (df['Title 1 Length'] <= 60)
            title_score = ((valid_titles & good_length).mean() * 100)
            scores['meta_title'] = round(title_score)
            if title_score < 50:
                weaknesses.append("Short or missing meta titles.")
        else:
            scores['meta_title'] = 0

        # Meta Description Analysis
        if 'Meta Description 1' in df.columns and 'Meta Description 1 Length' in df.columns:
            valid_desc = df['Meta Description 1'].notna()
            good_length = (df['Meta Description 1 Length'] >= 120) & (df['Meta Description 1 Length'] <= 160)
            desc_score = ((valid_desc & good_length).mean() * 100)
            scores['meta_description'] = round(desc_score)
            if desc_score < 50:
                weaknesses.append("Short or missing meta descriptions.")
        else:
            scores['meta_description'] = 0

        # H1 Tags
        if 'H1-1' in df.columns:
            h1_score = df['H1-1'].notna().mean() * 100
            scores['h1_tags'] = round(h1_score)
            if h1_score < 50:
                weaknesses.append("Missing or poorly optimized H1 tags.")
        else:
            scores['h1_tags'] = 0

        # Internal Linking
        if 'Inlinks' in df.columns:
            internal_linking_score = (df['Inlinks'] > 0).mean() * 100
            scores['internal_linking'] = round(internal_linking_score)
            if internal_linking_score < 50:
                weaknesses.append("Insufficient internal linking.")
        else:
            scores['internal_linking'] = 0

        return round(np.mean(list(scores.values()))), scores, weaknesses

    def analyze_technical_seo(self, df):
        scores = {}
        weaknesses = []

        # Response Time
        if 'Response Time' in df.columns:
            response_time_score = (df['Response Time'] <= 1.0).mean() * 100
            scores['response_time'] = round(response_time_score)
            if response_time_score < 50:
                weaknesses.append("Slow response times.")
        else:
            scores['response_time'] = 0

        # Indexability
        if 'Indexability' in df.columns:
            indexability_score = (df['Indexability'] == 'Indexable').mean() * 100
            scores['indexability'] = round(indexability_score)
            if indexability_score < 70:
                weaknesses.append("Pages not indexable.")
        else:
            scores['indexability'] = 0

        return round(np.mean(list(scores.values()))), scores, weaknesses

    def analyze_user_experience(self, df):
        scores = {}
        weaknesses = []

        # Mobile Friendly
        if 'Mobile Alternate Link' in df.columns:
            mobile_friendly_score = df['Mobile Alternate Link'].notna().mean() * 100
            scores['mobile_friendly'] = round(mobile_friendly_score)
            if mobile_friendly_score < 50:
                weaknesses.append("Pages not mobile-friendly.")
        else:
            scores['mobile_friendly'] = 0

        # Largest Contentful Paint (LCP)
        if 'Largest Contentful Paint Time (ms)' in df.columns:
            lcp_score = (df['Largest Contentful Paint Time (ms)'] <= 2500).mean() * 100
            scores['largest_contentful_paint'] = round(lcp_score)
            if lcp_score < 50:
                weaknesses.append("Slow LCP times.")
        else:
            scores['largest_contentful_paint'] = 0

        # Cumulative Layout Shift (CLS)
        if 'Cumulative Layout Shift' in df.columns:
            cls_score = (df['Cumulative Layout Shift'] <= 0.1).mean() * 100
            scores['cumulative_layout_shift'] = round(cls_score)
            if cls_score < 50:
                weaknesses.append("High CLS values.")
        else:
            scores['cumulative_layout_shift'] = 0

        return round(np.mean(list(scores.values()))), scores, weaknesses

    def calculate_overall_score(self, content_score, technical_score, ux_score):
        content_score = content_score / 100
        technical_score = technical_score / 100
        ux_score = ux_score / 100

        weighted_scores = {
            'Content SEO': content_score * self.weights['content_seo'],
            'Technical SEO': technical_score * self.weights['technical_seo'],
            'User Experience': ux_score * self.weights['user_experience']
        }

        return round(sum(weighted_scores.values()) * 100)

    def summarize_category(self, weaknesses):
        if weaknesses:
            return "\n".join([f"- {issue}" for issue in weaknesses])
        else:
            return "No major issues detected."

def main():
    st.set_page_config(page_title="SEO Readiness Scorer", layout="wide")
    st.title("SEO Readiness Score Calculator")
    st.write("Upload your Screaming Frog exports to analyze SEO readiness")

    uploaded_file = st.file_uploader("Upload Internal HTML Report (CSV or XLSX)", type=['csv', 'xlsx'])

    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
            scorer = SEOScorer()

            # Analyze scores
            content_score, content_details, content_weaknesses = scorer.analyze_content_seo(df)
            technical_score, technical_details, technical_weaknesses = scorer.analyze_technical_seo(df)
            ux_score, ux_details, ux_weaknesses = scorer.analyze_user_experience(df)
            overall_score = scorer.calculate_overall_score(content_score, technical_score, ux_score)

            # Display results
            st.header("SEO Readiness Scores")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Content SEO Score", f"{content_score}/100")
                st.subheader("Content SEO Summary")
                st.text(scorer.summarize_category(content_weaknesses))

            with col2:
                st.metric("Technical SEO Score", f"{technical_score}/100")
                st.subheader("Technical SEO Summary")
                st.text(scorer.summarize_category(technical_weaknesses))

            with col3:
                st.metric("User Experience Score", f"{ux_score}/100")
                st.subheader("User Experience Summary")
                st.text(scorer.summarize_category(ux_weaknesses))

            st.header("Overall SEO Readiness Score")
            st.metric("Final Score", f"{overall_score}/100")

        except Exception as e:
            st.error(f"Error processing file: {str(e)}")

if __name__ == "__main__":
    main()
