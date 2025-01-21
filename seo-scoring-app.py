import streamlit as st
import pandas as pd
import numpy as np
import json
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import xlsxwriter
import seaborn as sns
import zipfile

class SEOScorer:
    # ... (previous methods remain the same) ...

    def process_multiple_files(self, files):
        """Process multiple CSV files and return aggregated results"""
        all_results = {}
        combined_df = pd.DataFrame()
        
        for file in files:
            try:
                df = pd.read_csv(file)
                filename = file.name
                
                # Calculate scores for this file
                content_score, content_details = self.analyze_content_seo(df)
                technical_score, technical_details = self.analyze_technical_seo(df)
                ux_score, ux_details = self.analyze_user_experience(df)
                overall_score = self.calculate_overall_score(content_score, technical_score, ux_score)
                
                # Store results
                all_results[filename] = {
                    'df': df,
                    'scores': {
                        'overall': overall_score,
                        'content': {'score': content_score, 'details': content_details},
                        'technical': {'score': technical_score, 'details': technical_details},
                        'ux': {'score': ux_score, 'details': ux_details}
                    }
                }
                
                # Add to combined DataFrame
                df['source_file'] = filename
                combined_df = pd.concat([combined_df, df], ignore_index=True)
                
            except Exception as e:
                st.error(f"Error processing {file.name}: {str(e)}")
                
        return all_results, combined_df

    def generate_bulk_excel_report(self, all_results):
        """Generate comprehensive Excel report for multiple files"""
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        bold = workbook.add_format({'bold': True})
        
        # Summary sheet
        summary_sheet = workbook.add_worksheet('Summary')
        summary_sheet.write('A1', 'Bulk SEO Analysis Summary', bold)
        
        # Headers
        headers = ['Filename', 'Overall Score', 'Content Score', 'Technical Score', 'UX Score']
        for col, header in enumerate(headers):
            summary_sheet.write(0, col, header, bold)
        
        # Write data
        row = 1
        for filename, results in all_results.items():
            scores = results['scores']
            summary_sheet.write(row, 0, filename)
            summary_sheet.write(row, 1, scores['overall'])
            summary_sheet.write(row, 2, scores['content']['score'])
            summary_sheet.write(row, 3, scores['technical']['score'])
            summary_sheet.write(row, 4, scores['ux']['score'])
            row += 1
        
        # Individual file sheets
        for filename, results in all_results.items():
            sheet_name = filename[:31]  # Excel sheet names limited to 31 chars
            sheet = workbook.add_worksheet(sheet_name)
            
            # Write detailed scores
            sheet.write('A1', f'Detailed Analysis - {filename}', bold)
            current_row = 2
            
            for category, data in results['scores'].items():
                if category != 'overall':
                    sheet.write(current_row, 0, f"{category.title()} Score:", bold)
                    sheet.write(current_row, 1, data['score'])
                    current_row += 1
                    
                    for metric, score in data['details'].items():
                        sheet.write(current_row, 0, f"  - {metric.replace('_', ' ').title()}")
                        sheet.write(current_row, 1, score)
                        current_row += 1
                    current_row += 1
        
        workbook.close()
        return output.getvalue()

def main():
    st.set_page_config(page_title="Bulk SEO Readiness Scorer", layout="wide")
    
    st.title("Bulk SEO Readiness Score Calculator")
    
    # Sidebar configuration
    st.sidebar.header("Configuration")
    score_threshold = st.sidebar.slider("Score Warning Threshold", 0, 100, 70)
    show_recommendations = st.sidebar.checkbox("Show Recommendations", True)
    show_charts = st.sidebar.checkbox("Show Visualization", True)
    
    # File upload - now accepts multiple files
    uploaded_files = st.file_uploader("Upload Internal HTML Reports (CSV)", 
                                    type=['csv'], 
                                    accept_multiple_files=True)
    
    if uploaded_files:
        try:
            scorer = SEOScorer()
            all_results, combined_df = scorer.process_multiple_files(uploaded_files)
            
            # Display results in tabs
            tab1, tab2, tab3 = st.tabs(["Overview", "Individual Analysis", "Comparative Analysis"])
            
            with tab1:
                st.header("Bulk Analysis Overview")
                
                # Summary metrics
                overall_scores = [results['scores']['overall'] 
                                for results in all_results.values()]
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Average Overall Score", 
                             f"{np.mean(overall_scores):.1f}")
                with col2:
                    st.metric("Best Score", 
                             f"{max(overall_scores):.1f}")
                with col3:
                    st.metric("Worst Score", 
                             f"{min(overall_scores):.1f}")
                
                # Summary chart
                if show_charts:
                    fig = px.bar(
                        x=list(all_results.keys()),
                        y=overall_scores,
                        title="Overall Scores by File",
                        labels={'x': 'File', 'y': 'Score'},
                        color=overall_scores,
                        color_continuous_scale=['red', 'yellow', 'green']
                    )
                    fig.update_layout(xaxis_tickangle=-45)
                    st.plotly_chart(fig)
            
            with tab2:
                st.header("Individual File Analysis")
                
                # File selector
                selected_file = st.selectbox(
                    "Select File to Analyze",
                    list(all_results.keys())
                )
                
                if selected_file:
                    results = all_results[selected_file]
                    scores = results['scores']
                    
                    # Display individual file analysis
                    st.subheader(f"Analysis for {selected_file}")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Content SEO Score", 
                                 f"{scores['content']['score']:.1f}/100")
                        for metric, score in scores['content']['details'].items():
                            color = 'red' if score < score_threshold else 'green'
                            st.markdown(f"**{metric.replace('_', ' ').title()}:** "
                                      f"<span style='color:{color}'>{score:.1f}/100</span>", 
                                      unsafe_allow_html=True)
                    
                    with col2:
                        st.metric("Technical SEO Score", 
                                 f"{scores['technical']['score']:.1f}/100")
                        for metric, score in scores['technical']['details'].items():
                            color = 'red' if score < score_threshold else 'green'
                            st.markdown(f"**{metric.replace('_', ' ').title()}:** "
                                      f"<span style='color:{color}'>{score:.1f}/100</span>", 
                                      unsafe_allow_html=True)
                    
                    with col3:
                        st.metric("User Experience Score", 
                                 f"{scores['ux']['score']:.1f}/100")
                        for metric, score in scores['ux']['details'].items():
                            color = 'red' if score < score_threshold else 'green'
                            st.markdown(f"**{metric.replace('_', ' ').title()}:** "
                                      f"<span style='color:{color}'>{score:.1f}/100</span>", 
                                      unsafe_allow_html=True)
            
            with tab3:
                st.header("Comparative Analysis")
                
                if show_charts:
                    # Prepare data for comparison
                    comparison_data = {
                        'File': [],
                        'Category': [],
                        'Score': []
                    }
                    
                    for filename, results in all_results.items():
                        scores = results['scores']
                        comparison_data['File'].extend([filename] * 3)
                        comparison_data['Category'].extend(['Content', 'Technical', 'UX'])
                        comparison_data['Score'].extend([
                            scores['content']['score'],
                            scores['technical']['score'],
                            scores['ux']['score']
                        ])
                    
                    comparison_df = pd.DataFrame(comparison_data)
                    
                    # Create comparison chart
                    fig = px.bar(
                        comparison_df,
                        x='File',
                        y='Score',
                        color='Category',
                        barmode='group',
                        title="Score Comparison Across Files"
                    )
                    fig.update_layout(xaxis_tickangle=-45)
                    st.plotly_chart(fig)
            
            # Export options
            st.header("Export Options")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Generate Bulk Excel Report"):
                    excel_data = scorer.generate_bulk_excel_report(all_results)
                    st.download_button(
                        label="Download Excel Report",
                        data=excel_data,
                        file_name=f"bulk_seo_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            
            with col2:
                if st.button("Generate JSON Report"):
                    json_data = {
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "summary": {
                            "average_score": float(np.mean(overall_scores)),
                            "best_score": float(max(overall_scores)),
                            "worst_score": float(min(overall_scores))
                        },
                        "individual_results": {
                            filename: {
                                "overall_score": float(results['scores']['overall']),
                                "content_score": float(results['scores']['content']['score']),
                                "technical_score": float(results['scores']['technical']['score']),
                                "ux_score": float(results['scores']['ux']['score']),
                                "detailed_scores": {
                                    category: {
                                        "score": float(data['score']),
                                        "details": {k: float(v) for k, v in data['details'].items()}
                                    } for category, data in results['scores'].items() 
                                    if category != 'overall'
                                }
                            } for filename, results in all_results.items()
                        }
                    }
                    
                    json_str = json.dumps(json_data, indent=2)
                    st.download_button(
                        label="Download JSON Report",
                        data=json_str,
                        file_name=f"bulk_seo_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                        mime="application/json"
                    )
                    
        except Exception as e:
            st.error(f"Error processing files: {str(e)}")
            st.write("Please make sure you're uploading the correct Screaming Frog export files.")

if __name__ == "__main__":
    main()
