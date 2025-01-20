import streamlit as st
import pandas as pd
import os

# Define static benchmarks
benchmarks = {
    "Content SEO": 30,  # out of 40
    "Technical SEO": 20,  # out of 30
    "UX Score": 15,  # out of 30
    "Total Score": 65  # out of 100
}

# Scoring Logic Function
def calculate_scores(file):
    # Read the uploaded CSV file
    data = pd.read_csv(file)
    
    # Initialize scores
    content_score = 0
    technical_score = 0
    ux_score = 0

    # Content SEO Scoring
    if 'Missing Title Tags.csv' in file.name:
        missing_titles = len(data)
        if missing_titles == 0:
            content_score += 10  # Fully optimized
        elif missing_titles < 5:
            content_score += 5

    if 'Missing Meta Descriptions.csv' in file.name:
        missing_meta = len(data)
        if missing_meta == 0:
            content_score += 10
        elif missing_meta < 5:
            content_score += 5

    if 'Images Missing Alt Text.csv' in file.name:
        missing_alt = len(data)
        if missing_alt == 0:
            content_score += 5
        elif missing_alt < 10:
            content_score += 2.5

    # UX Scoring Example
    if 'Mobile Usability Issues.csv' in file.name:
        mobile_issues = len(data)
        if mobile_issues == 0:
            ux_score += 10
        elif mobile_issues < 5:
            ux_score += 5

    # Total score
    total_score = content_score + technical_score + ux_score
    return {
        "File": file.name,
        "Content SEO Score": content_score,
        "Technical SEO Score": technical_score,
        "UX Score": ux_score,
        "Total Score": total_score
    }

# Add benchmark comparisons
def add_benchmarks(result):
    result["Content Benchmark"] = "Below" if result["Content SEO Score"] < benchmarks["Content SEO"] else "Above"
    result["Technical Benchmark"] = "Below" if result["Technical SEO Score"] < benchmarks["Technical SEO"] else "Above"
    result["UX Benchmark"] = "Below" if result["UX Score"] < benchmarks["UX Score"] else "Above"
    result["Overall Benchmark"] = "Below" if result["Total Score"] < benchmarks["Total Score"] else "Above"
    return result

# Streamlit App
def main():
    st.title("SEO Competitor Scoring Tool")
    st.write("Upload your Screaming Frog audit files to calculate SEO scores dynamically.")

    # File uploader
    uploaded_files = st.file_uploader(
        "Upload Screaming Frog CSV files", 
        type=["csv"], 
        accept_multiple_files=True
    )

    # Results list
    results = []

    # Process files when uploaded
    if uploaded_files:
        for file in uploaded_files:
            # Calculate scores for each uploaded file
            result = calculate_scores(file)
            result = add_benchmarks(result)
            results.append(result)

        # Convert results to DataFrame for display
        results_df = pd.DataFrame(results)

        # Display results
        st.subheader("SEO Scoring Results with Benchmarks")
        st.dataframe(results_df)

        # Highlight below-benchmark scores
        st.subheader("Competitor Performance vs Benchmarks")
        below_benchmark = results_df[
            (results_df["Content Benchmark"] == "Below") |
            (results_df["Technical Benchmark"] == "Below") |
            (results_df["UX Benchmark"] == "Below")
        ]
        st.dataframe(below_benchmark)

        # Visualizations
        st.subheader("Score Comparison")
        st.bar_chart(results_df.set_index("File")[["Content SEO Score", "Technical SEO Score", "UX Score"]])

        # Download results as Excel
        st.subheader("Download Results")
        output_file = "seo_scores_report.xlsx"
        results_df.to_excel(output_file, index=False)
        with open(output_file, "rb") as f:
            st.download_button(
                label="Download Excel Report",
                data=f,
                file_name=output_file,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

# Run the app
if __name__ == "__main__":
    main()
