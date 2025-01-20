import streamlit as st
import pandas as pd

# Define static benchmarks
benchmarks = {
    "Content SEO": 30,  # out of 40
    "Technical SEO": 20,  # out of 30
    "UX Score": 15,  # out of 30
    "Total Score": 65  # out of 100
}

# Scoring Logic for internal_html.csv
def calculate_scores_from_internal_html(file):
    # Load the CSV file
    data = pd.read_csv(file)

    # Initialize scores
    content_score = 0
    technical_score = 0
    ux_score = 0

    # Content SEO Scoring
    # Check for missing titles
    missing_titles = data["Title 1"].isnull().sum()
    if missing_titles == 0:
        content_score += 10  # Fully optimized
    elif missing_titles < 5:
        content_score += 5  # Partially optimized

    # Check for missing meta descriptions
    missing_meta = data["Meta Description 1"].isnull().sum()
    if missing_meta == 0:
        content_score += 10
    elif missing_meta < 5:
        content_score += 5

    # Check for missing H1 tags
    missing_h1 = data["H1-1"].isnull().sum()
    if missing_h1 == 0:
        content_score += 5
    elif missing_h1 < 10:
        content_score += 2.5

    # Technical SEO Scoring
    # Count 2xx status codes
    valid_status = data["Status Code"].value_counts().get(200, 0)
    if valid_status == len(data):
        technical_score += 10  # All pages valid
    elif valid_status / len(data) > 0.9:
        technical_score += 5  # Most pages valid

    # UX Scoring
    # Calculate average inlinks
    average_inlinks = data["Inlinks"].mean()
    if average_inlinks >= 10:
        ux_score += 10
    elif average_inlinks >= 5:
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
    st.write("Upload your Screaming Frog audit files (e.g., `internal_html.csv`) to calculate SEO scores dynamically.")

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
            if "internal_html.csv" in file.name:
                # Use the scoring function for internal_html.csv
                result = calculate_scores_from_internal_html(file)
            else:
                # Handle other Screaming Frog files here if needed
                st.warning(f"File {file.name} is not supported yet.")
                continue

            result = add_benchmarks(result)
            results.append(result)

        # Convert results to DataFrame and display
        results_df = pd.DataFrame(results)
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
        st.subheader("Missing Metadata Insights")
        missing_data = {
            "Missing Titles": data["Title 1"].isnull().sum(),
            "Missing Meta Descriptions": data["Meta Description 1"].isnull().sum(),
            "Missing H1 Tags": data["H1-1"].isnull().sum()
        }
        st.bar_chart(pd.Series(missing_data))

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
