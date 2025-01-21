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
        title_score = 0
        if 'Title 1' in df.columns and 'Title 1 Length' in df.columns:
            valid_titles = df['Title 1'].notna()
            good_length = (df['Title 1 Length'] >= 30) & (df['Title 1 Length'] <= 60)
            title_score = ((valid_titles & good_length).mean() * 100)
        scores['meta_title'] = round(title_score)

        # Meta Description Analysis
        desc_score = 0
        if 'Meta Description 1' in df.columns and 'Meta Description 1 Length' in df.columns:
            valid_desc = df['Meta Description 1'].notna()
            good_length = (df['Meta Description 1 Length'] >= 120) & (df['Meta Description 1 Length'] <= 160)
            desc_score = ((valid_desc & good_length).mean() * 100)
        scores['meta_description'] = round(desc_score)

        # Heading Structure
        h1_score = 0
        if 'H1-1' in df.columns:
            h1_score = df['H1-1'].notna().mean() * 100
        scores['h1_tags'] = round(h1_score)

        # Internal Linking
        internal_linking_score = 0
        if 'Inlinks' in df.columns and 'Unique Inlinks' in df.columns:
            has_inlinks = df['Inlinks'] > 0
            has_unique_inlinks = df['Unique Inlinks'] > 0
            internal_linking_score = ((has_inlinks & has_unique_inlinks).mean() * 100)
        scores['internal_linking'] = round(internal_linking_score)

        # Content Quality
        content_quality_score = 0
        if 'Word Count' in df.columns and 'Flesch Reading Ease Score' in df.columns:
            good_length = df['Word Count'] >= 300
            readable = df['Flesch Reading Ease Score'] >= 60
            content_quality_score = ((good_length & readable).mean() * 100)
        scores['content_quality'] = round(content_quality_score)

        return round(np.mean(list(scores.values()))), scores
    def analyze_technical_seo(self, df):
        scores = {}

        # Response Time Analysis
        response_score = 0
        if 'Response Time' in df.columns:
            good_response = df['Response Time'] <= 1.0  # 1 second threshold
            response_score = good_response.mean() * 100
        scores['response_time'] = round(response_score)

        # Status Code Analysis
        status_score = 0
        if 'Status Code' in df.columns:
            good_status = df['Status Code'] == 200
            status_score = good_status.mean() * 100
        scores['status_codes'] = round(status_score)

        # Indexability
        index_score = 0
        if 'Indexability' in df.columns:
            indexable = df['Indexability'] == 'Indexable'
            index_score = indexable.mean() * 100
        scores['indexability'] = round(index_score)

        # Canonical Implementation
        canonical_score = 0
        if 'Canonical Link Element 1' in df.columns:
            valid_canonical = df['Canonical Link Element 1'].notna()
            canonical_score = valid_canonical.mean() * 100
        scores['canonical_tags'] = round(canonical_score)

        return round(np.mean(list(scores.values()))), scores

    def analyze_user_experience(self, df):
        scores = {}

        # Mobile Friendliness
        mobile_score = 0
        if 'Mobile Alternate Link' in df.columns:
            mobile_score = df['Mobile Alternate Link'].notna().mean() * 100
        scores['mobile_friendly'] = round(mobile_score)

        # Page Speed Metrics from Screaming Frog
        lcp_score = 0
        if 'LCP' in df.columns:
            good_lcp = df['LCP'] <= 2.5
            lcp_score = good_lcp.mean() * 100
        scores['largest_contentful_paint'] = round(lcp_score)

        fid_score = 0
        if 'FID' in df.columns:
            good_fid = df['FID'] <= 100
            fid_score = good_fid.mean() * 100
        scores['first_input_delay'] = round(fid_score)

        cls_score = 0
        if 'CLS' in df.columns:
            good_cls = df['CLS'] <= 0.1
            cls_score = good_cls.mean() * 100
        scores['cumulative_layout_shift'] = round(cls_score)

        # Overall PageSpeed Score
        pagespeed_score = 0
        if 'PageSpeed Score' in df.columns:
            pagespeed_score = df['PageSpeed Score'].mean()
        scores['pagespeed_score'] = round(pagespeed_score)

        return round(np.mean(list(scores.values()))), scores
    def calculate_overall_score(self, content_score, technical_score, ux_score):
        # Normalize input scores to 0-1 scale
        content_score = content_score / 100
        technical_score = technical_score / 100
        ux_score = ux_score / 100

        # Weighted aggregation
        weighted_scores = {
            'Content SEO': content_score * self.weights['content_seo'],
            'Technical SEO': technical_score * self.weights['technical_seo'],
            'User Experience': ux_score * self.weights['user_experience']
        }

        overall_score = sum(weighted_scores.values()) / sum(self.weights.values()) * 100

        # Categorize score into Good, Medium, or Bad
        if overall_score >= 90:
            category = "Good"
            color = "green"
        elif overall_score >= 50:
            category = "Medium"
            color = "orange"
        else:
            category = "Bad"
            color = "red"

        return round(overall_score), category, color

def main():
    st.set_page_config(page_title="SEO Readiness Scorer", layout="wide")

    st.title("SEO Readiness Score Calculator")
    st.write("Upload your Screaming Frog exports to analyze SEO readiness")

    uploaded_file = st.file_uploader("Upload Internal HTML Report (CSV or XLSX)", type=['csv', 'xlsx'])

    if uploaded_file:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith('.xlsx'):
                df = pd.read_excel(uploaded_file)

            scorer = SEOScorer()
            content_score, content_details = scorer.analyze_content_seo(df)
            technical_score, technical_details = scorer.analyze_technical_seo(df)
            ux_score, ux_details = scorer.analyze_user_experience(df)
            overall_score, category, color = scorer.calculate_overall_score(content_score, technical_score, ux_score)

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
            st.markdown(f"<h3 style='color:{color}; font-size:24px;'>Category: {category}</h3>", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error processing file: {str(e)}")

if __name__ == "__main__":
    main()
