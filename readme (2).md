# SEO Readiness Scorer

SEO Readiness Scorer is a Streamlit application that evaluates key on-page, technical, and user experience SEO metrics using exported data from Screaming Frog (CSV or XLSX).

## Features

- **Content SEO Analysis**

  - Meta title length and presence (`Title 1`, `Title 1 Length`)
  - Meta description length and presence (`Meta Description 1`, `Meta Description 1 Length`)
  - H1 tag presence (`H1-1`)
  - Internal linking checks (`Inlinks`)

- **Technical SEO Analysis**

  - Server response time (`Response Time`)
  - Indexability status (`Indexability`)

- **User Experience Analysis**

  - Mobile-friendly support (`Mobile Alternate Link`)
  - Largest Contentful Paint (`Largest Contentful Paint Time (ms)`)
  - Cumulative Layout Shift (`Cumulative Layout Shift`)

- **Weighted Scoring**

  - Configurable weights for content, technical, and UX components
  - Overall SEO readiness score out of 100

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/seo-readiness-scorer.git
   cd seo-readiness-scorer
   ```
2. Create a virtual environment and install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## Usage

Run the Streamlit app:

```bash
streamlit run app.py
```

1. Open the link displayed in your browser.
2. Upload your Screaming Frog export (`.csv` or `.xlsx`).
3. View Content SEO, Technical SEO, and User Experience scores along with detected weaknesses.
4. See the overall SEO readiness score.

## Configuration

- **Adjusting Weights**: Edit `SEOScorer.__init__` to change the relative weights for:

  - `content_seo` (default: 0.4)
  - `technical_seo` (default: 0.4)
  - `user_experience` (default: 0.2)

- **Thresholds**: Modify threshold values in each analysis method for customized pass/fail criteria.

## Supported Columns

The following columns are required (if missing, their score defaults to 0):

| Analysis Type            | Column                                            |
| ------------------------ | ------------------------------------------------- |
| Meta Title               | `Title 1`, `Title 1 Length`                       |
| Meta Description         | `Meta Description 1`, `Meta Description 1 Length` |
| H1 Tags                  | `H1-1`                                            |
| Internal Linking         | `Inlinks`                                         |
| Response Time            | `Response Time`                                   |
| Indexability             | `Indexability`                                    |
| Mobile-Friendly          | `Mobile Alternate Link`                           |
| Largest Contentful Paint | `Largest Contentful Paint Time (ms)`              |
| Cumulative Layout Shift  | `Cumulative Layout Shift`                         |

## Error Handling

- The app will display an error message if the uploaded file cannot be processed.

## Contributing

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature-name`).
3. Commit your changes (`git commit -m "Add new feature"`).
4. Push to the branch (`git push origin feature-name`).
5. Create a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

