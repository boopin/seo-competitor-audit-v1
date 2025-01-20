import streamlit as st
import pandas as pd
import numpy as np
import json
from datetime import datetime
import base64
import io

class SEOScorer:
    # [Previous SEOScorer class code remains the same]
    def __init__(self):
        self.weights = {
            'content_seo': 0.3,
            'technical_seo': 0.3,
            'user_experience': 0.2,
            'off_page_seo': 0.2
        }

    def analyze_content_seo(self, html_report):
        scores = {}
        
        # Meta Title & Description
        meta_titles = html_report['Title'].notna().mean() * 100
        meta_desc = html_report['Meta Description'].notna().mean() * 100
        scores['meta_optimization'] = (meta_titles + meta_desc) / 2
        
        # Internal Linking
        internal_links = html_report['Internal Out Links'].notna().mean() * 100
        scores['internal_linking'] = internal_links
        
        # Image Alt Text
        if 'Images' in html_report.columns:
            alt_text = html_report['Images'].notna().mean() * 100
            scores['image_alt'] = alt_text
        else:
            scores['image_alt'] = 0
            
        # Calculate overall content score
        content_score = np.mean(list(scores.values()))
        return content_score, scores

    def analyze_technical_seo(self, speed_report):
        scores = {}
        
        # Speed Scores
        mobile_speed = float(speed_report['Mobile Score'].iloc[0]) if 'Mobile Score' in speed_report.columns else 0
        desktop_speed = float(speed_report['Desktop Score'].iloc[0]) if 'Desktop Score' in speed_report.columns else 0
        
        scores['mobile_speed'] = self.calculate_speed_score(mobile_speed)
        scores['desktop_speed'] = self.calculate_speed_score(desktop_speed)
        
        technical_score = np.mean(list(scores.values()))
        return technical_score, scores

    def analyze_user_experience(self, html_report):
        scores = {}
        
        # Mobile Friendliness (checking viewport meta tag)
        mobile_friendly = html_report['Meta Viewport'].notna().mean() * 100
        scores['mobile_friendly'] = mobile_friendly
        
        # Rich Results (checking schema markup)
        rich_results = html_report['Schema Types'].notna().mean() * 100 if 'Schema Types' in html_report.columns else 0
        scores['rich_results'] = rich_results
        
        ux_score = np.mean(list(scores.values()))
        return ux_score, scores

    def calculate_speed_score(self, speed_value):
        if speed_value >= 90: return 100
        elif speed_value >= 80: return 80
        elif speed_value >= 70: return 60
        elif speed_value >= 50: return 40
        else: return 20

    def calculate_overall_score(self, content_score, technical_score, ux_score):
        weighted_scores = {
            'Content SEO': content_score * self.weights['content_seo'],
            'Technical SEO': technical_score * self.weights['technical_seo'],
            'User Experience': ux_score * self.weights['user_experience']
        }
        
        return sum(weighted_scores.values()) / (sum(self.weights.values()) - self.weights['off_page_seo']) * 100

def generate_excel_report(content_score, content_details, technical_score, technical_details, 
                         ux_score, ux_details, overall_score):
    """Generate Excel report with all SEO scores"""
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Summary sheet
        summary_data = {
            'Category': ['Content SEO', 'Technical SEO', 'User Experience', 'Overall Score'],
            'Score': [content_score, technical_score, ux_score, overall_score]
        }
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Detailed scores sheets
        content_df = pd.DataFrame(list(content_details.items()), columns=['Metric', 'Score'])
        content_df.to_excel(writer, sheet_name='Content SEO Details', index=False)
        
        technical_df = pd.DataFrame(list(technical_details.items()), columns=['Metric', 'Score'])
        technical_df.to_excel(writer, sheet_name='Technical SEO Details', index=False)
        
        ux_df = pd.DataFrame(list(ux_details.items()), columns=['Metric', 'Score'])
        ux_df.to_excel(writer, sheet_name='UX Details', index=False)
        
    return output.getvalue()

def generate_json_report(content_score, content_details, technical_score, technical_details,
                        ux_score, ux_details, overall_score):
    """Generate JSON report with all SEO scores"""
    report = {
        'timestamp': datetime.now().isoformat(),
        'overall_score': float(overall_score),
        'categories': {
            'content_seo': {
                'score': float(content_score),
                'details': {k: float(v) for k, v in content_details.items()}
            },
            'technical_seo': {
                'score': float(technical_score),
                'details': {k: float(v) for k, v in technical_details.items()}
            },
            'user_experience': {
                'score': float(ux_score),
                'details': {k: float(v) for k, v in ux_details.items()}
            }
        }
    }
    return json.dumps(report, indent=2)

def main():
    st.set_page_config(page_title="SEO Readiness Scorer", layout="wide")
    
    st.title("SEO Readiness Score Calculator")
    st.write("Upload your Screaming Frog exports to analyze SEO readiness")
    
    # File uploaders
    col1, col2 = st.columns(2)
    
    with col1:
        html_file = st.file_uploader("Upload Internal HTML Report (CSV)", type=['csv'])
    with col2:
        speed_file = st.file_uploader("Upload Site Speed Report (CSV)", type=['csv'])
    
    if html_file and speed_file:
        try:
            # Load data
            html_report = pd.read_csv(html_file)
            speed_report = pd.read_csv(speed_file)
            
            # Initialize scorer
            scorer = SEOScorer()
            
            # Calculate scores
            content_score, content_details = scorer.analyze_content_seo(html_report)
            technical_score, technical_details = scorer.analyze_technical_seo(speed_report)
            ux_score, ux_details = scorer.analyze_user_experience(html_report)
            
            overall_score = scorer.calculate_overall_score(content_score, technical_score, ux_score)
            
            # Display results
            st.header("SEO Readiness Scores")
            
            # Create three columns for scores
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Content SEO Score", f"{content_score:.1f}/100")
                st.subheader("Content Details")
                for metric, score in content_details.items():
                    st.write(f"{metric.replace('_', ' ').title()}: {score:.1f}/100")
            
            with col2:
                st.metric("Technical SEO Score", f"{technical_score:.1f}/100")
                st.subheader("Technical Details")
                for metric, score in technical_details.items():
                    st.write(f"{metric.replace('_', ' ').title()}: {score:.1f}/100")
            
            with col3:
                st.metric("User Experience Score", f"{ux_score:.1f}/100")
                st.subheader("UX Details")
                for metric, score in ux_details.items():
                    st.write(f"{metric.replace('_', ' ').title()}: {score:.1f}/100")
            
            # Overall score at the bottom
            st.header("Overall SEO Readiness Score")
            st.metric("Final Score", f"{overall_score:.1f}/100")
            
            # Export section
            st.header("Export Results")
            
            # Generate reports
            excel_report = generate_excel_report(
                content_score, content_details,
                technical_score, technical_details,
                ux_score, ux_details,
                overall_score
            )
            
            json_report = generate_json_report(
                content_score, content_details,
                technical_score, technical_details,
                ux_score, ux_details,
                overall_score
            )
            
            col1, col2 = st.columns(2)
            
            # Excel download button
            with col1:
                st.download_button(
                    label="Download Excel Report",
                    data=excel_report,
                    file_name=f"seo_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            
            # JSON download button
            with col2:
                st.download_button(
                    label="Download JSON Report",
                    data=json_report,
                    file_name=f"seo_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
            
        except Exception as e:
            st.error(f"Error processing files: {str(e)}")
            st.write("Please make sure you're uploading the correct Screaming Frog export files.")

if __name__ == "__main__":
    main()
