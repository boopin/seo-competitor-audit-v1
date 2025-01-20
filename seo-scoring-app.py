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
def calculate_scores_from_internal_html(data):
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
    st.title("SEO Competitor Scoring Tool (Single File - internal_html.csv)")
    st.write("Upload your Screaming Frog `internal_html.csv` file to calculate SEO scores dynamically.")

    # File uploader
    uploaded_file = st.file_uploader(
        "Upload Screaming Frog internal_html.csv file", 
        type=["csv"]
    )

    # Process the uploaded file
    if uploaded_file:
        # Load the file efficiently
        try:
            data = pd.read_csv(uploaded_file, low_memory=False)
        except Exception as e:
            st.error(f"Error reading file: {e}")
            return

        # Check for required columns
        required_columns = ["Title 1", "Meta Description 1", "H1-1", "Status Code", "Inlinks"]
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            st.error(f"The following required columns are missing: {', '.join(missing_columns)}")
            return

        # Calculate scores
        result = calculate_scores_from_internal_html(data)
        result = add_benchmarks(result)
        
        # Display results
        st.subheader("SEO Scoring Results with Benchmarks")
        st.write(result)

        # Visualizations for missing metadata
        st.subheader("Missing Metadata Insights")
        missing_data = {
            "Missing Titles": data["Title 1"].isnull().sum(),
            "Missing Meta Descriptions": data["Meta Description 1"].isnull().sum(),
            "Missing H1 Tags": data["H1-1"].isnull().sum()
        }
        st.bar_chart(pd.Series(missing_data))

        # Download results as Excel
        st.subheader("Download Results")
        results_df = pd.DataFrame([result])
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
