import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

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

    def get_score_color(self, score):
        """Return color based on score range"""
        if score >= 80:
            return "#28a745"  # Green
        elif score >= 60:
            return "#ffc107"  # Yellow
        elif score >= 40:
            return "#fd7e14"  # Orange
        else:
            return "#dc3545"  # Red

    def get_grade(self, score):
        """Return letter grade based on score"""
        if score >= 90:
            return "A+"
        elif score >= 80:
            return "A"
        elif score >= 70:
            return "B"
        elif score >= 60:
            return "C"
        elif score >= 50:
            return "D"
        else:
            return "F"

def create_score_gauge(score, title):
    """Create a visual score representation using Streamlit components"""
    # Calculate percentage for progress bar
    progress_value = score / 100
    
    # Color based on score
    if score >= 80:
        color = "#28a745"  # Green
    elif score >= 60:
        color = "#ffc107"  # Yellow
    elif score >= 40:
        color = "#fd7e14"  # Orange
    else:
        color = "#dc3545"  # Red
    
    # Create a visual gauge using HTML/CSS
    gauge_html = f"""
    <div style="text-align: center; padding: 20px;">
        <h4 style="margin-bottom: 10px; color: #333;">{title}</h4>
        <div style="position: relative; width: 200px; height: 200px; margin: 0 auto;">
            <div style="
                width: 200px; 
                height: 200px; 
                border-radius: 50%; 
                background: conic-gradient({color} {score * 3.6}deg, #e9ecef {score * 3.6}deg);
                display: flex;
                align-items: center;
                justify-content: center;
                position: relative;
            ">
                <div style="
                    width: 160px; 
                    height: 160px; 
                    background: white; 
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    flex-direction: column;
                ">
                    <span style="font-size: 2rem; font-weight: bold; color: {color};">{score}</span>
                    <span style="font-size: 0.9rem; color: #666;">out of 100</span>
                </div>
            </div>
        </div>
    </div>
    """
    return gauge_html

def create_category_breakdown(content_details, technical_details, ux_details):
    """Create a detailed breakdown using Streamlit's built-in charts"""
    categories = []
    scores = []
    category_types = []
    
    for metric, score in content_details.items():
        categories.append(metric.replace('_', ' ').title())
        scores.append(score)
        category_types.append('Content SEO')
    
    for metric, score in technical_details.items():
        categories.append(metric.replace('_', ' ').title())
        scores.append(score)
        category_types.append('Technical SEO')
    
    for metric, score in ux_details.items():
        categories.append(metric.replace('_', ' ').title())
        scores.append(score)
        category_types.append('User Experience')
    
    # Create DataFrame for the chart
    chart_data = pd.DataFrame({
        'Metric': categories,
        'Score': scores,
        'Category': category_types
    })
    
    return chart_data

def main():
    st.set_page_config(
        page_title="SEO Readiness Scorer", 
        layout="wide", 
        page_icon="🔍",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .score-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin: 1rem 0;
    }
    .score-value {
        font-size: 3rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    .grade {
        font-size: 2rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    .metric-container {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-left: 4px solid #1f77b4;
    }
    .weakness-box {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #dc3545;
        margin: 0.5rem 0;
    }
    .success-box {
        background: #d4edda;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
        margin: 0.5rem 0;
    }
    .upload-section {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 2rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown('<h1 class="main-header">🔍 SEO Readiness Score Calculator</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Upload your Screaming Frog exports to get a comprehensive SEO analysis</p>', unsafe_allow_html=True)

    # Sidebar with information
    with st.sidebar:
        st.header("📊 About This Tool")
        st.write("""
        This tool analyzes your website's SEO readiness across three key areas:
        
        **🎯 Content SEO (40%)**
        - Meta titles and descriptions
        - H1 tag optimization
        - Internal linking structure
        
        **⚙️ Technical SEO (40%)**
        - Page response times
        - Indexability status
        
        **👥 User Experience (20%)**
        - Mobile friendliness
        - Core Web Vitals (LCP, CLS)
        """)
        
        st.header("📋 Score Guide")
        st.write("""
        - **90-100**: A+ (Excellent)
        - **80-89**: A (Very Good)
        - **70-79**: B (Good)
        - **60-69**: C (Average)
        - **50-59**: D (Below Average)
        - **0-49**: F (Poor)
        """)

    # File upload section
    st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    st.subheader("📁 Upload Your Data")
    uploaded_file = st.file_uploader(
        "Choose your Screaming Frog Internal HTML Report", 
        type=['csv', 'xlsx'],
        help="Upload a CSV or Excel file exported from Screaming Frog"
    )
    st.markdown('</div>', unsafe_allow_html=True)

    if uploaded_file:
        try:
            # Show loading spinner
            with st.spinner('🔄 Analyzing your SEO data...'):
                df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
                scorer = SEOScorer()

                # Analyze scores
                content_score, content_details, content_weaknesses = scorer.analyze_content_seo(df)
                technical_score, technical_details, technical_weaknesses = scorer.analyze_technical_seo(df)
                ux_score, ux_details, ux_weaknesses = scorer.analyze_user_experience(df)
                overall_score = scorer.calculate_overall_score(content_score, technical_score, ux_score)

            st.success("✅ Analysis complete!")
            
            # Overall Score - Prominent display
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                grade = scorer.get_grade(overall_score)
                st.markdown(f"""
                <div class="score-card">
                    <h2>Overall SEO Readiness Score</h2>
                    <div class="score-value">{overall_score}/100</div>
                    <div class="grade">Grade: {grade}</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("---")

            # Individual score gauges
            st.header("📈 Detailed Scores")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                gauge_html1 = create_score_gauge(content_score, "Content SEO")
                st.markdown(gauge_html1, unsafe_allow_html=True)
                
            with col2:
                gauge_html2 = create_score_gauge(technical_score, "Technical SEO")
                st.markdown(gauge_html2, unsafe_allow_html=True)
                
            with col3:
                gauge_html3 = create_score_gauge(ux_score, "User Experience")
                st.markdown(gauge_html3, unsafe_allow_html=True)

            # Detailed breakdown chart
            st.header("🔍 Metric Breakdown")
            chart_data = create_category_breakdown(content_details, technical_details, ux_details)
            st.bar_chart(chart_data.set_index('Metric')['Score'])
            
            # Show the data in a more detailed way
            st.subheader("📊 Detailed Metrics Table")
            
            # Color code the scores in the dataframe display
            def color_scores(val):
                if val >= 80:
                    color = '#d4edda'  # Light green
                elif val >= 60:
                    color = '#fff3cd'  # Light yellow
                elif val >= 40:
                    color = '#f8d7da'  # Light red
                else:
                    color = '#f5c6cb'  # Darker red
                return f'background-color: {color}'
            
            styled_df = chart_data.style.applymap(color_scores, subset=['Score'])
            st.dataframe(styled_df, use_container_width=True)

            # Category summaries with improved styling
            st.header("📋 Detailed Analysis")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                <div class="metric-container">
                    <h3>🎯 Content SEO Score: {content_score}/100</h3>
                    <h4>Issues Found:</h4>
                </div>
                """, unsafe_allow_html=True)
                
                if content_weaknesses:
                    for weakness in content_weaknesses:
                        st.markdown(f'<div class="weakness-box">⚠️ {weakness}</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="success-box">✅ No major issues detected.</div>', unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div class="metric-container">
                    <h3>⚙️ Technical SEO Score: {technical_score}/100</h3>
                    <h4>Issues Found:</h4>
                </div>
                """, unsafe_allow_html=True)
                
                if technical_weaknesses:
                    for weakness in technical_weaknesses:
                        st.markdown(f'<div class="weakness-box">⚠️ {weakness}</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="success-box">✅ No major issues detected.</div>', unsafe_allow_html=True)

            with col3:
                st.markdown(f"""
                <div class="metric-container">
                    <h3>👥 User Experience Score: {ux_score}/100</h3>
                    <h4>Issues Found:</h4>
                </div>
                """, unsafe_allow_html=True)
                
                if ux_weaknesses:
                    for weakness in ux_weaknesses:
                        st.markdown(f'<div class="weakness-box">⚠️ {weakness}</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="success-box">✅ No major issues detected.</div>', unsafe_allow_html=True)

            # Data summary
            st.markdown("---")
            st.header("📊 Data Summary")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Pages Analyzed", len(df))
            with col2:
                st.metric("Analysis Date", datetime.now().strftime("%Y-%m-%d"))
            with col3:
                indexable_pages = df[df['Indexability'] == 'Indexable'].shape[0] if 'Indexability' in df.columns else 0
                st.metric("Indexable Pages", indexable_pages)
            with col4:
                avg_response_time = round(df['Response Time'].mean(), 2) if 'Response Time' in df.columns else 0
                st.metric("Avg Response Time (s)", avg_response_time)

        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")
            st.info("Please ensure your file is a valid Screaming Frog export with the expected column names.")

    else:
        # Instructions when no file is uploaded
        st.info("👆 Please upload a Screaming Frog CSV or Excel file to begin the analysis.")
        
        with st.expander("📖 How to export data from Screaming Frog"):
            st.write("""
            1. Open Screaming Frog SEO Spider
            2. Crawl your website
            3. Go to **Bulk Export** > **Response Codes** > **All**
            4. Choose **Internal HTML** tab
            5. Export as CSV or Excel
            6. Upload the file here
            """)

if __name__ == "__main__":
    main()
