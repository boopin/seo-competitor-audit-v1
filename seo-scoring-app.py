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
    """Create a visual score representation using HTML/CSS"""
    # Color based on score
    if score >= 80:
        color = "#28a745"  # Green
        bg_color = "#d4edda"
    elif score >= 60:
        color = "#ffc107"  # Yellow
        bg_color = "#fff3cd"
    elif score >= 40:
        color = "#fd7e14"  # Orange
        bg_color = "#ffeaa7"
    else:
        color = "#dc3545"  # Red
        bg_color = "#f8d7da"
    
    # Create a visual gauge using HTML/CSS
    gauge_html = f"""
    <div style="text-align: center; padding: 20px; background: {bg_color}; border-radius: 15px; margin: 10px 0;">
        <h4 style="margin-bottom: 15px; color: #333; font-size: 1.2rem;">{title}</h4>
        <div style="position: relative; width: 120px; height: 120px; margin: 0 auto;">
            <div style="
                width: 120px; 
                height: 120px; 
                border-radius: 50%; 
                background: conic-gradient({color} {score * 3.6}deg, #e9ecef {score * 3.6}deg);
                display: flex;
                align-items: center;
                justify-content: center;
                position: relative;
            ">
                <div style="
                    width: 90px; 
                    height: 90px; 
                    background: white; 
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    flex-direction: column;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                ">
                    <span style="font-size: 1.5rem; font-weight: bold; color: {color};">{score}</span>
                    <span style="font-size: 0.7rem; color: #666;">/ 100</span>
                </div>
            </div>
        </div>
        <div style="margin-top: 10px; font-weight: 600; color: {color};">
            {get_score_status(score)}
        </div>
    </div>
    """
    return gauge_html

def get_score_status(score):
    """Get status text based on score"""
    if score >= 90:
        return "🏆 Excellent"
    elif score >= 80:
        return "✅ Very Good"
    elif score >= 70:
        return "👍 Good"
    elif score >= 60:
        return "⚠️ Average"
    elif score >= 50:
        return "🔶 Below Average"
    else:
        return "❌ Needs Work"

def create_export_data(overall_score, content_score, technical_score, ux_score, 
                      content_details, technical_details, ux_details,
                      content_weaknesses, technical_weaknesses, ux_weaknesses,
                      df, scorer):
    """Create structured data for export"""
    
    # Summary data
    summary_data = {
        'Overall Score': overall_score,
        'Grade': scorer.get_grade(overall_score),
        'Content SEO Score': content_score,
        'Technical SEO Score': technical_score,
        'User Experience Score': ux_score,
        'Total Pages Analyzed': len(df),
        'Analysis Date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Detailed metrics
    all_metrics = {}
    
    # Content SEO metrics
    for metric, score in content_details.items():
        all_metrics[f"Content SEO - {metric.replace('_', ' ').title()}"] = score
    
    # Technical SEO metrics  
    for metric, score in technical_details.items():
        all_metrics[f"Technical SEO - {metric.replace('_', ' ').title()}"] = score
        
    # UX metrics
    for metric, score in ux_details.items():
        all_metrics[f"User Experience - {metric.replace('_', ' ').title()}"] = score
    
    # Issues and recommendations
    issues_data = {
        'Content SEO Issues': '; '.join(content_weaknesses) if content_weaknesses else 'No issues detected',
        'Technical SEO Issues': '; '.join(technical_weaknesses) if technical_weaknesses else 'No issues detected', 
        'User Experience Issues': '; '.join(ux_weaknesses) if ux_weaknesses else 'No issues detected'
    }
    
    # Additional stats
    if 'Indexability' in df.columns:
        indexable_pages = df[df['Indexability'] == 'Indexable'].shape[0]
        indexable_percentage = round((indexable_pages / len(df)) * 100, 1)
        summary_data['Indexable Pages'] = indexable_pages
        summary_data['Indexable Percentage'] = f"{indexable_percentage}%"
    
    if 'Response Time' in df.columns:
        avg_response_time = round(df['Response Time'].mean(), 2)
        summary_data['Average Response Time (s)'] = avg_response_time
    
    return summary_data, all_metrics, issues_data

def create_summary_report(summary_data, all_metrics, issues_data, scorer):
    """Create a text-based summary report"""
    
    report = f"""
# SEO READINESS ANALYSIS REPORT
Generated: {summary_data['Analysis Date']}

## EXECUTIVE SUMMARY
Overall SEO Score: {summary_data['Overall Score']}/100 (Grade: {summary_data['Grade']})
Status: {get_score_status(summary_data['Overall Score'])}

## CATEGORY BREAKDOWN
• Content SEO: {summary_data['Content SEO Score']}/100
• Technical SEO: {summary_data['Technical SEO Score']}/100  
• User Experience: {summary_data['User Experience Score']}/100

## DETAILED METRICS
"""
    
    # Add all metrics
    for metric, score in all_metrics.items():
        status = get_score_status(score)
        report += f"• {metric}: {score}/100 - {status}\n"
    
    report += f"""
## ISSUES IDENTIFIED

### Content SEO Issues:
{issues_data['Content SEO Issues']}

### Technical SEO Issues:
{issues_data['Technical SEO Issues']}

### User Experience Issues:
{issues_data['User Experience Issues']}

## KEY STATISTICS
• Total Pages Analyzed: {summary_data['Total Pages Analyzed']:,}
"""
    
    if 'Indexable Pages' in summary_data:
        report += f"• Indexable Pages: {summary_data['Indexable Pages']:,} ({summary_data['Indexable Percentage']})\n"
    
    if 'Average Response Time (s)' in summary_data:
        report += f"• Average Response Time: {summary_data['Average Response Time (s)']}s\n"
    
    # Add recommendations
    report += f"""
## RECOMMENDATIONS

### Priority Actions:
"""
    
    # Determine priority based on lowest scores
    categories = [
        ("Content SEO", summary_data['Content SEO Score'], "Focus on meta titles, descriptions, and H1 optimization"),
        ("Technical SEO", summary_data['Technical SEO Score'], "Improve page speed and ensure all pages are indexable"),
        ("User Experience", summary_data['User Experience Score'], "Optimize Core Web Vitals and mobile experience")
    ]
    
    sorted_categories = sorted(categories, key=lambda x: x[1])
    
    for i, (category, score, recommendation) in enumerate(sorted_categories, 1):
        priority = "HIGH" if score < 60 else "MEDIUM" if score < 80 else "LOW"
        report += f"{i}. {category} ({score}/100) - {priority} PRIORITY\n   → {recommendation}\n"
    
    return report

def create_progress_bar(score, label):
    """Create a styled progress bar"""
    color = "#28a745" if score >= 80 else "#ffc107" if score >= 60 else "#fd7e14" if score >= 40 else "#dc3545"
    
    return f"""
    <div style="margin: 10px 0;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
            <span style="font-weight: 600; color: #333;">{label}</span>
            <span style="font-weight: 600; color: {color};">{score}/100</span>
        </div>
        <div style="background-color: #e9ecef; border-radius: 10px; height: 20px; overflow: hidden;">
            <div style="
                background-color: {color}; 
                height: 100%; 
                width: {score}%; 
                border-radius: 10px;
                transition: width 0.5s ease-in-out;
            "></div>
        </div>
    </div>
    """

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
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .score-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2.5rem;
        border-radius: 20px;
        text-align: center;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    .score-value {
        font-size: 4rem;
        font-weight: bold;
        margin: 0.5rem 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .grade {
        font-size: 2rem;
        font-weight: bold;
        margin: 0.5rem 0;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
    }
    .metric-container {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-left: 5px solid #1f77b4;
    }
    .weakness-box {
        background: #fff5f5;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #dc3545;
        margin: 0.5rem 0;
        box-shadow: 0 2px 5px rgba(220,53,69,0.1);
    }
    .success-box {
        background: #f0f9f0;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #28a745;
        margin: 0.5rem 0;
        box-shadow: 0 2px 5px rgba(40,167,69,0.1);
    }
    .upload-section {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 2rem;
        border-radius: 20px;
        margin: 2rem 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    .stProgress > div > div > div > div {
        background-image: linear-gradient(to right, #667eea, #764ba2);
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
        - **90-100**: A+ (Excellent) 🏆
        - **80-89**: A (Very Good) ✅
        - **70-79**: B (Good) 👍
        - **60-69**: C (Average) ⚠️
        - **50-59**: D (Below Average) 🔶
        - **0-49**: F (Poor) ❌
        """)

        st.header("🎨 Features")
        st.write("""
        - **Visual Gauges**: Circular progress indicators
        - **Color Coding**: Red, orange, yellow, green scoring
        - **Detailed Breakdown**: Individual metric analysis
        - **Actionable Insights**: Specific improvement suggestions
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
                    <h2>🎯 Overall SEO Readiness Score</h2>
                    <div class="score-value">{overall_score}/100</div>
                    <div class="grade">Grade: {grade}</div>
                    <p style="margin-top: 1rem; font-size: 1.1rem;">
                        {get_score_status(overall_score)}
                    </p>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("---")

            # Individual score gauges
            st.header("📈 Category Breakdown")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                gauge_html1 = create_score_gauge(content_score, "🎯 Content SEO")
                st.markdown(gauge_html1, unsafe_allow_html=True)
                
            with col2:
                gauge_html2 = create_score_gauge(technical_score, "⚙️ Technical SEO")
                st.markdown(gauge_html2, unsafe_allow_html=True)
                
            with col3:
                gauge_html3 = create_score_gauge(ux_score, "👥 User Experience")
                st.markdown(gauge_html3, unsafe_allow_html=True)

            # Progress bars for all metrics
            st.header("🔍 Detailed Metrics")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📝 Content SEO Metrics")
                for metric, score in content_details.items():
                    label = metric.replace('_', ' ').title()
                    st.markdown(create_progress_bar(score, label), unsafe_allow_html=True)
                
                st.subheader("⚙️ Technical SEO Metrics")
                for metric, score in technical_details.items():
                    label = metric.replace('_', ' ').title()
                    st.markdown(create_progress_bar(score, label), unsafe_allow_html=True)
            
            with col2:
                st.subheader("👥 User Experience Metrics")
                for metric, score in ux_details.items():
                    label = metric.replace('_', ' ').title()
                    st.markdown(create_progress_bar(score, label), unsafe_allow_html=True)
                
                # Create summary chart data
                st.subheader("📊 Score Summary")
                summary_data = pd.DataFrame({
                    'Category': ['Content SEO', 'Technical SEO', 'User Experience'],
                    'Score': [content_score, technical_score, ux_score]
                })
                st.bar_chart(summary_data.set_index('Category')['Score'])

            # Category summaries with improved styling
            st.markdown("---")
            st.header("📋 Issue Analysis & Recommendations")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                <div class="metric-container">
                    <h3>🎯 Content SEO Analysis</h3>
                    <div style="font-size: 1.5rem; font-weight: bold; color: {scorer.get_score_color(content_score)}; text-align: center; margin: 1rem 0;">
                        {content_score}/100
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if content_weaknesses:
                    st.markdown("**Issues Found:**")
                    for weakness in content_weaknesses:
                        st.markdown(f'<div class="weakness-box">⚠️ {weakness}</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="success-box">✅ No major issues detected in content SEO!</div>', unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div class="metric-container">
                    <h3>⚙️ Technical SEO Analysis</h3>
                    <div style="font-size: 1.5rem; font-weight: bold; color: {scorer.get_score_color(technical_score)}; text-align: center; margin: 1rem 0;">
                        {technical_score}/100
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if technical_weaknesses:
                    st.markdown("**Issues Found:**")
                    for weakness in technical_weaknesses:
                        st.markdown(f'<div class="weakness-box">⚠️ {weakness}</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="success-box">✅ No major issues detected in technical SEO!</div>', unsafe_allow_html=True)

            with col3:
                st.markdown(f"""
                <div class="metric-container">
                    <h3>👥 User Experience Analysis</h3>
                    <div style="font-size: 1.5rem; font-weight: bold; color: {scorer.get_score_color(ux_score)}; text-align: center; margin: 1rem 0;">
                        {ux_score}/100
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if ux_weaknesses:
                    st.markdown("**Issues Found:**")
                    for weakness in ux_weaknesses:
                        st.markdown(f'<div class="weakness-box">⚠️ {weakness}</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="success-box">✅ No major issues detected in user experience!</div>', unsafe_allow_html=True)

            # Data summary with enhanced metrics
            st.markdown("---")
            st.header("📊 Analysis Summary")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Total Pages Analyzed", 
                    f"{len(df):,}",
                    help="Total number of pages in your crawl data"
                )
            
            with col2:
                st.metric(
                    "Analysis Date", 
                    datetime.now().strftime("%Y-%m-%d"),
                    help="Date when this analysis was performed"
                )
            
            with col3:
                if 'Indexability' in df.columns:
                    indexable_pages = df[df['Indexability'] == 'Indexable'].shape[0]
                    indexable_percentage = round((indexable_pages / len(df)) * 100, 1)
                    st.metric(
                        "Indexable Pages", 
                        f"{indexable_pages:,}",
                        delta=f"{indexable_percentage}%",
                        help="Number and percentage of indexable pages"
                    )
                else:
                    st.metric("Indexable Pages", "N/A")
            
            with col4:
                if 'Response Time' in df.columns:
                    avg_response_time = round(df['Response Time'].mean(), 2)
                    st.metric(
                        "Avg Response Time", 
                        f"{avg_response_time}s",
                        delta="Target: < 1.0s" if avg_response_time <= 1.0 else "Target: < 1.0s",
                        delta_color="normal" if avg_response_time <= 1.0 else "inverse",
                        help="Average page response time across all pages"
                    )
                else:
                    st.metric("Avg Response Time", "N/A")

            # Additional insights
            st.markdown("---")
            
            # Export Section
            st.header("📥 Export Results")
            st.write("Download your SEO analysis results for presentations, reports, or further analysis.")
            
            # Prepare export data
            summary_data, all_metrics, issues_data = create_export_data(
                overall_score, content_score, technical_score, ux_score,
                content_details, technical_details, ux_details,
                content_weaknesses, technical_weaknesses, ux_weaknesses,
                df, scorer
            )
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                # Excel Export - Summary + Metrics
                summary_df = pd.DataFrame([summary_data]).T
                summary_df.columns = ['Value']
                summary_df.index.name = 'Metric'
                
                metrics_df = pd.DataFrame([all_metrics]).T
                metrics_df.columns = ['Score']
                metrics_df.index.name = 'SEO Metric'
                
                issues_df = pd.DataFrame([issues_data]).T
                issues_df.columns = ['Issues Found']
                issues_df.index.name = 'Category'
                
                # Create Excel file in memory
                from io import BytesIO
                buffer = BytesIO()
                
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    summary_df.to_excel(writer, sheet_name='Summary')
                    metrics_df.to_excel(writer, sheet_name='Detailed Metrics')
                    issues_df.to_excel(writer, sheet_name='Issues & Recommendations')
                
                buffer.seek(0)
                
                st.download_button(
                    label="📊 Download Excel Report",
                    data=buffer.getvalue(),
                    file_name=f"seo_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    help="Comprehensive Excel report with multiple sheets"
                )
            
            with col2:
                # CSV Export - All data combined
                export_df = pd.DataFrame({
                    'Category': ['Summary'] * len(summary_data) + ['Metrics'] * len(all_metrics) + ['Issues'] * len(issues_data),
                    'Item': list(summary_data.keys()) + list(all_metrics.keys()) + list(issues_data.keys()),
                    'Value': [str(v) for v in summary_data.values()] + [str(v) for v in all_metrics.values()] + list(issues_data.values())
                })
                
                csv_data = export_df.to_csv(index=False)
                
                st.download_button(
                    label="📋 Download CSV Data",
                    data=csv_data,
                    file_name=f"seo_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv",
                    help="Raw data in CSV format for further analysis"
                )
            
            with col3:
                # Text Report Export
                text_report = create_summary_report(summary_data, all_metrics, issues_data, scorer)
                
                st.download_button(
                    label="📄 Download Text Report",
                    data=text_report,
                    file_name=f"seo_report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                    mime="text/plain",
                    help="Formatted text report for presentations"
                )
            
            with col4:
                # JSON Export for developers
                import json
                json_data = {
                    'summary': summary_data,
                    'metrics': all_metrics,
                    'issues': issues_data,
                    'metadata': {
                        'export_timestamp': datetime.now().isoformat(),
                        'tool_version': '2.0',
                        'weights': scorer.weights
                    }
                }
                
                json_string = json.dumps(json_data, indent=2)
                
                st.download_button(
                    label="🔧 Download JSON Data",
                    data=json_string,
                    file_name=f"seo_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                    mime="application/json",
                    help="Structured data in JSON format for developers"
                )
            
            # Export instructions
            with st.expander("💡 How to use exported data in presentations"):
                st.write("""
                **For PowerPoint/Google Slides:**
                - Use the **Text Report** for copy-paste content
                - Import **Excel charts** directly into slides
                - Use **CSV data** to create custom charts
                
                **For Further Analysis:**
                - **Excel Report**: Multiple sheets with detailed breakdowns
                - **CSV Data**: Import into analytics tools
                - **JSON Data**: For developers and custom integrations
                
                **Tips:**
                - Screenshots of the gauges work great in presentations
                - The text report includes executive summary and recommendations
                - Excel file contains multiple tabs for different aspects
                """)

            st.markdown("---")
            st.header("💡 Key Insights")
            
            insights = []
            if overall_score >= 80:
                insights.append("🎉 **Excellent work!** Your site has strong SEO fundamentals.")
            elif overall_score >= 60:
                insights.append("👍 **Good foundation** with room for targeted improvements.")
            else:
                insights.append("⚠️ **Significant improvements needed** to boost SEO performance.")
            
            # Priority recommendations based on lowest scores
            categories = [
                ("Content SEO", content_score, "Focus on meta titles, descriptions, and H1 optimization"),
                ("Technical SEO", technical_score, "Improve page speed and ensure all pages are indexable"),
                ("User Experience", ux_score, "Optimize Core Web Vitals and mobile experience")
            ]
            
            lowest_category = min(categories, key=lambda x: x[1])
            insights.append(f"🎯 **Priority area**: {lowest_category[0]} (Score: {lowest_category[1]}) - {lowest_category[2]}")
            
            for insight in insights:
                st.markdown(insight)

        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")
            st.info("💡 Please ensure your file is a valid Screaming Frog export with the expected column names.")
            
            with st.expander("🔍 Common Issues & Solutions"):
                st.write("""
                **Common file issues:**
                - File is not from Screaming Frog Internal HTML export
                - Missing required columns (check export settings)
                - File format issues (try saving as CSV)
                - Empty or corrupted file
                
                **Solutions:**
                - Re-export from Screaming Frog using Internal HTML tab
                - Ensure all columns are included in export
                - Try uploading as CSV format
                """)

    else:
        # Instructions when no file is uploaded
        st.info("👆 Please upload a Screaming Frog CSV or Excel file to begin the SEO analysis.")
        
        # Feature showcase
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            ### 🎯 Content Analysis
            - Meta title optimization
            - Meta description analysis
            - H1 tag evaluation
            - Internal linking assessment
            """)
        
        with col2:
            st.markdown("""
            ### ⚙️ Technical Evaluation
            - Page response times
            - Indexability status
            - Crawl error detection
            - Server response analysis
            """)
        
        with col3:
            st.markdown("""
            ### 👥 User Experience
            - Mobile friendliness
            - Core Web Vitals (LCP)
            - Layout stability (CLS)
            - Performance metrics
            """)
        
        with st.expander("📖 How to export data from Screaming Frog", expanded=True):
            st.write("""
            **Step-by-step instructions:**
            
            1. **Open Screaming Frog SEO Spider**
            2. **Crawl your website** (enter URL and click Start)
            3. **Wait for crawl to complete**
            4. **Go to Bulk Export menu** → Response Codes → All
            5. **Select the Internal HTML tab**
            6. **Click Export** and save as CSV or Excel
            7. **Upload the file here** using the file uploader above
            
            ✅ **Tip**: Make sure to export from the "Internal HTML" tab for best results!
            """)

if __name__ == "__main__":
    main()
