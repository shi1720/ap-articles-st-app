# AP Article Evaluation App

## Overview

The AP Article Evaluation App is a powerful tool designed to assist educators and content creators in evaluating and improving Advanced Placement (AP) articles. This app uses advanced AI to analyze articles based on various criteria, ensuring they meet the rigorous standards required for AP courses.

**Live App**: [https://ap-articles-st-app.streamlit.app/](https://ap-articles-st-app.streamlit.app/)

## Features

- **Multiple AP Course Support**: 
  - Evaluate articles for various AP courses including World History, US History, Biology, Chemistry, and more.

- **Dual Input Methods**: 
  - Text input for individual articles
  - CSV upload for bulk processing

- **Comprehensive Evaluation**:
  - Format and word count check
  - Alignment with key concepts and skills
  - Relevance to themes and learning objectives
  - Concept and formula inclusion analysis
  - Sufficiency for AP question response
  - Factual accuracy and objectivity assessment
  - Engagement and clarity evaluation

- **Detailed Feedback**: 
  - Individual scores for each evaluation aspect
  - Final evaluation with strengths and weaknesses
  - Actionable feedback for improvement

- **User-Friendly Interface**:
  - Interactive Streamlit app
  - Progress tracking for bulk processing
  - Downloadable results for CSV input

## How to Use

1. **Access the App**: 
   Visit [https://ap-articles-st-app.streamlit.app/](https://ap-articles-st-app.streamlit.app/)

2. **Enter API Key**:
   - Input your Anthropic API Key in the provided field
   - This key is required for the AI-powered evaluations

3. **Select AP Course**:
   - Choose the relevant AP course for your article(s)

4. **Choose Input Method**:
   - **Text Input**: 
     - Enter article details including topic, themes, objectives, key concepts, article text, and sample questions
   - **CSV Upload**: 
     - Prepare a CSV file with columns: Topic, Themes, Objectives, Key Concepts, Article, Questions
     - Upload the CSV file

5. **Process Articles**:
   - For text input, click "Evaluate Article"
   - For CSV upload, click "Process CSV"

6. **Review Results**:
   - Examine individual evaluation aspects
   - Check the final evaluation for overall quality
   - For CSV input, download the processed file with results

## CSV Format

When using CSV upload, ensure your file has the following columns:
- Topic
- Themes
- Objectives
- Key Concepts
- Article
- Questions

## Local Development

To run the app locally:

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the app:
   ```
   streamlit run app.py
   ```

## Security Note

The app requires an Anthropic API key for operation. This key is entered by the user and is not stored or logged by the application. Always keep your API key confidential.

## Feedback and Contributions

We welcome feedback and contributions to improve the AP Article Evaluation App. Please open an issue or submit a pull request on our GitHub repository.
