import streamlit as st
import pandas as pd
import numpy as np
import json
from datetime import datetime
import io
import xlsxwriter

class SEOScorer:
    # [Previous SEOScorer class code remains exactly the same]
    def __init__(self):
        self.weights = {
            'content_seo': 0.3,
            'technical_seo': 0.3,
            'user_experience': 0.2,
            'off_page_seo': 0.2
        }

    # [Keep all the analysis methods exactly the same as in the previous version]
    def analyze_content_seo(self, df):
        # [Keep existing method]
        pass

    def analyze_technical_seo(self, df):
        # [Keep existing method]
        pass

    def analyze_user_experience(self, df):
        # [Keep existing method]
        pass

    def calculate_overall_score(self, content_score, technical_score, ux_score):
        # [Keep existing method]
        pass

def read_file(uploaded_file):
    """Read either CSV or Excel file"""
    file_type = uploaded_file.name.split('.')[-1].lower()
    try:
        if file_type == 'csv':
            df = pd.read_csv(uploaded_file)
        elif file_type in ['xlsx', 'xls']:
            df = pd.read_excel(uploaded_file)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
        return df
    except Exception as e:
        st.error(f"Error reading file: {str(e)}")
        return None

def generate_excel_report(content_score, content_details, technical_score, technical_details, 
                         ux_score, ux_details, overall_score):
    """Generate Excel report with all SEO scores"""
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        workbook = writer.book
        
        # Create formats
        header_format = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'bg_color': '#4B8BBE',
            'font_color': 'white',
            'border': 1
        })
        
        cell_format = workbook.add_format({
            'font_size': 11,
            'border': 1
        })
        
        # Summary sheet
        summary_data = {
            'Category': ['Content SEO', 'Technical SEO', 'User Experience', 'Overall Score'],
            'Score': [content_score, technical_score, ux_score, overall_score]
        }
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Format Summary sheet
        summary_sheet = writer.sheets['Summary']
        summary_sheet.set_column('A:A', 20)
        summary_sheet.set_column('B:B', 15)
        
        # Content SEO Details
        content_df = pd.DataFrame(list(content_details.items()), columns=['Metric', 'Score'])
        content_df.to_excel(writer, sheet_name='Content SEO', index=False)
        
        # Technical SEO Details
        technical_df = pd.DataFrame(list(technical_details.items()), columns=['Metric', 'Score'])
        technical_df.to_excel(writer, sheet_name='Technical SEO', index=False)
        
        # UX Details
        ux_df = pd.DataFrame(list(ux_details.items()), columns=['Metric', 'Score'])
        ux_df.to_excel(writer, sheet_name='User Experience', index=False)
        
        # Format all sheets
        for sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]
            worksheet.set_row(0, None, header_format)
            worksheet.set_column('A:B', 30, cell_format)
    
    return output.getvalue()

def main():
    st.set_page_config(page_title="SEO Readiness Scorer", layout="wide")
    
    st.title("SEO Readiness Score Calculator")
    st.write("Upload your Screaming Frog export to analyze SEO readiness")
    
    uploaded_file = st.file_uploader(
        "Upload Internal HTML Report (CSV or Excel)", 
        type=['csv', 'xlsx', 'xls']
    )
    
    if uploaded_file:
        df = read_file(uploaded_file)
        
        if df is not None:
            try:
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
                
                st.header("Overall SEO Readiness Score")
                st.metric("Final Score", f"{overall_score:.1f}/100")

                # Export section
                st.header("Export Results")
                col1, col2 = st.columns(2)
                
                # Generate reports
                with col1:
                    # Excel Export
                    excel_report = generate_excel_report(
                        content_score, content_details,
                        technical_score, technical_details,
                        ux_score, ux_details,
                        overall_score
                    )
                    
                    st.download_button(
                        label="Download Excel Report",
                        data=excel_report,
                        file_name=f"seo_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                
                with col2:
                    # JSON Export
                    report_data = {
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "overall_score": float(overall_score),
                        "scores": {
                            "content_seo": {
                                "total": float(content_score),
                                "details": {k: float(v) for k, v in content_details.items()}
                            },
                            "technical_seo": {
                                "total": float(technical_score),
                                "details": {k: float(v) for k, v in technical_details.items()}
                            },
                            "user_experience": {
                                "total": float(ux_score),
                                "details": {k: float(v) for k, v in ux_details.items()}
                            }
                        }
                    }
                    
                    json_str = json.dumps(report_data, indent=2)
                    st.download_button(
                        label="Download JSON Report",
                        data=json_str,
                        file_name=f"seo_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                        mime="application/json"
                    )
                
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")
                st.write("Please make sure you're uploading the correct Screaming Frog export file.")

if __name__ == "__main__":
    main()
