import streamlit as st
import pandas as pd
import requests
import json
import time
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor, as_completed
import base64
from streamlit_lottie import st_lottie
from streamlit_extras.add_vertical_space import add_vertical_space
import threading

# Constants
API_URL = "https://api.anthropic.com/v1/messages"

# Helper functions
def load_lottie_url(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

def call_claude_api(prompt, api_key):
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    payload = {
        "model": "claude-3-5-sonnet-20240620",
        "max_tokens": 8192,
        "temperature": 0.6,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()['content'][0]['text']
    else:
        st.error(f"API call failed with status code: {response.status_code}")
        st.error(f"Response: {response.text}")
        return None

def parallel_api_calls(prompts, api_key):
    responses = [None] * len(prompts)
    with ThreadPoolExecutor(max_workers=7) as executor:
        future_to_index = {executor.submit(call_claude_api, prompt, api_key): i for i, prompt in enumerate(prompts)}

        for future in concurrent.futures.as_completed(future_to_index):
            index = future_to_index[future]
            try:
                responses[index] = future.result()
            except Exception as exc:
                st.error(f'Prompt {index} generated an exception: {exc}')
                responses[index] = f"Error: {exc}"

    for i, response in enumerate(responses):
        if response is None:
            st.warning(f"Warning: No response received for prompt {i}")
            responses[i] = "No response received"

    return responses


def generate_prompt1(ARTICLE, COURSE):
    return f"""
You are an expert AP {COURSE} educator and assessment specialist with 30 years of experience in crafting and evaluating high-quality educational content. Your task is to evaluate the format of an AP {COURSE} article critically.

Article to evaluate:
<article>
{ARTICLE}
</article>

Please follow the instructions below carefully and thoroughly. Analyze each point step by step internally, but present only the final JSON output as specified. If you do not follow the instructions exactly, you will be penalized.

Evaluation Steps:

1. Equation Formatting:
   - Determine if any equations are present in the article.
   - If equations are present:
     - Verify that all equations are correctly formatted and easily readable.
     - Ensure that no LaTeX formatting code or errors are visible in the final text.
   Definition:
   - "Correctly formatted and easily readable equations" means that equations are properly typeset and presented in standard mathematical notation without any formatting issues.

2. Word Count:
   - Calculate the total word count of the article.
   - Verify that the word count is between 1500 and 3000 words, inclusive.
   Definition:
   - "Word count between 1500 and 3000 words" means the article has at least 1500 words and no more than 3000 words.

Scoring Criteria:

- Assign a score of 1 if both of the following conditions are met:
  1. All equations (if any) are correctly formatted and readable, with no visible LaTeX code.
  2. The word count is between 1500 and 3000 words.
- Assign a score of 0 if either condition is not met.

Response Instructions:

- Provide your answer strictly in the following JSON format:

{{
  "score": 0 or 1,
  "rationale": "Two sentences explaining your scoring decision.",
  "feedback": "Two sentences of constructive feedback."
}}

Important:

- Only provide the JSON response.
- Do not include any additional text or explanations outside the JSON format.
- Ensure that your rationale and feedback are concise, each limited to two sentences.
- If you do not follow these instructions precisely, you will be penalized.
"""

def generate_prompt2(ARTICLE, KEY_CONCEPTS, COURSE):
    return f"""
You are a senior AP {COURSE} curriculum developer with 30 years of experience in aligning educational content with AP standards. Your task is to evaluate an article's alignment with specified AP Key Concepts and Skills.

Article to evaluate:
<article>
{ARTICLE}
</article>

Key Concepts to check:
{KEY_CONCEPTS}

Please follow the instructions below carefully and thoroughly. Analyze each point step by step internally, but present only the final JSON output as specified. If you do not follow the instructions exactly, you will be penalized.

Evaluation Steps:

1. Key Concepts Coverage:
   - For each Key Concept listed in {KEY_CONCEPTS}:
     - Determine whether the article addresses the Key Concept.
     - Assess the depth and accuracy of coverage for each Key Concept.
   Definition:
   - "Thoroughly covers all listed Key Concepts" means that each Key Concept is clearly explained, accurately presented, and adequately elaborated upon.

2. Skills Demonstration:
   - Identify examples or opportunities within the article that support the development of AP {COURSE} skills.
   - Evaluate how effectively the article promotes these skills.
   Definition:
   - "Provides clear examples or opportunities for AP skills" means that the article includes content or activities that allow students to practice and develop key AP {COURSE} skills.

Scoring Criteria:

- Assign a score of 1 if both of the following conditions are met:
  1. The article thoroughly covers all listed Key Concepts.
  2. The article provides clear examples or opportunities for AP {COURSE} skills.
- Assign a score of 0 if either condition is not fully met.

Response Instructions:

- Provide your answer strictly in the following JSON format:

{{
  "score": 0 or 1,
  "rationale": "Two sentences explaining your scoring decision.",
  "feedback": "Two sentences of constructive feedback."
}}

Important:

- Only provide the JSON response.
- Do not include any additional text or explanations outside the JSON format.
- Ensure that your rationale and feedback are concise, each limited to two sentences.
- If you do not follow these instructions precisely, you will be penalized.
"""

def generate_prompt3(ARTICLE, THEMES, OBJECTIVE, COURSE):
    return f"""
You are a distinguished AP {COURSE} assessment specialist with 30 years of experience in curriculum alignment. Your task is to evaluate an article's coverage of specified Themes and Learning Objectives.

Article to evaluate:
<article>
{ARTICLE}
</article>

Themes to check:
{THEMES}

Learning Objectives to check:
{OBJECTIVE}

Please follow the instructions below carefully and thoroughly. Analyze each point step by step internally, but present only the final JSON output as specified. If you do not follow the instructions exactly, you will be penalized.

Evaluation Steps:

1. Themes Coverage:
   - For each Theme listed in {THEMES}:
     - Identify explicit or implicit references to the Theme within the article.
     - Assess the depth and accuracy of coverage for each Theme.
   Definition:
   - "Thoroughly covers all listed Themes" means that the article discusses each Theme in sufficient detail, providing clear explanations and relevant examples.

2. Learning Objectives Alignment:
   - For each Learning Objective listed in {OBJECTIVE}:
     - Determine how well the article supports the Learning Objective.
     - Evaluate whether the content provides students with the necessary information and context to meet the objective.
   Definition:
   - "Clearly supports all listed Learning Objectives" means that the article includes content that directly helps students achieve the objectives.

3. Integration and Balance:
   - Assess whether there is balanced coverage and integration of all listed Themes and Learning Objectives.
   Definition:
   - "Balanced integration" means that the article covers all Themes and Learning Objectives evenly, without overemphasizing or neglecting any.

4. Foundational Principles:
   - Identify the presence of necessary foundational principles related to the topic.
   - Evaluate how well these principles are explained and integrated into the content.
   Definition:
   - "Necessary foundational principles are present and well-explained" means that the article includes essential background information that supports understanding of the main content.

Scoring Criteria:

- Assign a score of 1 if all of the following conditions are met:
  1. The article thoroughly covers all listed Themes.
  2. The article clearly supports all listed Learning Objectives.
  3. Necessary foundational principles are present and well-explained.
  4. There is balanced integration of Themes and Learning Objectives.
- Assign a score of 0 if any of the above conditions are not fully met.

Response Instructions:

- Provide your answer strictly in the following JSON format:

{{
  "score": 0 or 1,
  "rationale": "Two sentences explaining your scoring decision.",
  "feedback": "Two sentences of constructive feedback."
}}

Important:

- Only provide the JSON response.
- Do not include any additional text or explanations outside the JSON format.
- Ensure that your rationale and feedback are concise, each limited to two sentences.
- If you do not follow these instructions precisely, you will be penalized.
"""

def generate_prompt4(ARTICLE, TOPIC, COURSE):
    return f"""
You are a veteran AP {COURSE} educator and textbook author with 30 years of experience. Your task is to evaluate the inclusion and explanation of necessary concepts and formulas in an article.

Article to evaluate:
<article>
{ARTICLE}
</article>

Topic:
{TOPIC}

Please follow the instructions below carefully and thoroughly. Analyze each point step by step internally, but present only the final JSON output as specified. If you do not follow the instructions exactly, you will be penalized.

Evaluation Steps:

1. Concept Identification:
   - Identify all key concepts related to the topic {TOPIC} that should be included in an AP-level article.
   - Determine whether each of these concepts is present in the article.
   Definition:
   - "All necessary concepts are included" means that the article covers all fundamental and essential concepts required for understanding the topic at an AP level.

2. Concept Explanation:
   - For each concept present:
     - Evaluate the quality and depth of its explanation.
     - Assess whether the explanations are accurate and appropriate for AP-level students.
   Definition:
   - "Well-explained concepts" means that explanations are clear, detailed, and facilitate student understanding.

3. Formula Identification (if applicable):
   - Identify any formulas that are crucial for understanding the topic {TOPIC} at an AP level.
   - Determine whether these formulas are included in the article.
   Definition:
   - "All relevant formulas are included" means that all essential mathematical expressions are present.

4. Formula Explanation (if applicable):
   - For each formula present:
     - Evaluate how well it is explained and contextualized.
     - Assess whether the article provides sufficient information for students to understand and apply the formulas.
   Definition:
   - "Properly explained formulas" means that formulas are accompanied by explanations of variables, derivations if appropriate, and examples of application.

5. Appropriateness and Accuracy:
   - Verify that all included concepts and formulas are accurate and up-to-date.
   - Ensure that the level of detail is appropriate for AP {COURSE} students.

Scoring Criteria:

- Assign a score of 1 if all of the following conditions are met:
  1. All necessary concepts for the topic are included and well-explained.
  2. All relevant formulas (if applicable) are included and properly explained.
  3. The explanations are accurate and appropriate for AP-level students.
- Assign a score of 0 if any of the above conditions are not fully met.

Response Instructions:

- Provide your answer strictly in the following JSON format:

{{
  "score": 0 or 1,
  "rationale": "Two sentences explaining your scoring decision.",
  "feedback": "Two sentences of constructive feedback."
}}

Important:

- Only provide the JSON response.
- Do not include any additional text or explanations outside the JSON format.
- Ensure that your rationale and feedback are concise, each limited to two sentences.
- If you do not follow these instructions precisely, you will be penalized.
"""

def generate_prompt5(ARTICLE, QUESTIONS, COURSE):
    return f"""
You are a highly experienced AP {COURSE} exam writer and grader with 30 years of experience. Your task is to evaluate whether an article provides sufficient information for students to respond to AP-style questions.

Article to evaluate:
<article>
{ARTICLE}
</article>

Sample AP-style questions:
{QUESTIONS}

Please follow the instructions below carefully and thoroughly. Analyze each point step by step internally, but present only the final JSON output as specified. If you do not follow the instructions exactly, you will be penalized.

Evaluation Steps:

1. Question Analysis:
   - For each AP-style question in {QUESTIONS}:
     - Identify the key information and concepts needed to answer the question effectively.

2. Content Sufficiency:
   - Determine whether the article contains all the necessary information to answer each question fully.
   - Check for the presence of relevant facts, concepts, explanations, and examples.
   Definition:
   - "Provides sufficient information to answer all given AP-style questions" means that a student could answer each question completely based solely on the content of the article.

3. Depth of Knowledge (DOK) Assessment:
   - Evaluate whether the article provides enough depth for students to respond at DOK levels 3 and 4.
   - DOK levels 3 and 4 involve strategic thinking and extended reasoning.

4. Task Verb Alignment:
   - Assess whether the article's content allows students to perform tasks associated with AP task verbs such as "explain," "analyze," "evaluate," "compare," "justify," "synthesize."

5. Additional Information Check:
   - Identify if any crucial information is missing that would be necessary for students to fully answer the questions.

Scoring Criteria:

- Assign a score of 1 if all of the following conditions are met:
  1. The article provides sufficient information to answer all given AP-style questions.
  2. The content supports responses at DOK levels 3 and 4.
  3. The article allows students to engage with all mentioned AP task verbs.
  4. No additional crucial information is needed to answer the questions fully.
- Assign a score of 0 if any of the above conditions are not fully met.

Response Instructions:

- Provide your answer strictly in the following JSON format:

{{
  "score": 0 or 1,
  "rationale": "Two sentences explaining your scoring decision.",
  "feedback": "Two sentences of constructive feedback."
}}

Important:

- Only provide the JSON response.
- Do not include any additional text or explanations outside the JSON format.
- Ensure that your rationale and feedback are concise, each limited to two sentences.
- If you do not follow these instructions precisely, you will be penalized.
"""

def generate_prompt6(ARTICLE, COURSE):
    return f"""
You are a highly respected AP {COURSE} fact-checker and academic reviewer with 30 years of experience. Your task is to evaluate the factual accuracy and objectivity of an article.

Article to evaluate:
<article>
{ARTICLE}
</article>

Please follow the instructions below carefully and thoroughly. Analyze each point step by step internally, but present only the final JSON output as specified. If you do not follow the instructions exactly, you will be penalized.

Evaluation Steps:

1. Fact Verification:
   - Identify all factual claims, data, dates, names, events, and statements in the article.
   - Verify the accuracy of each factual element based on your expertise.
   Definition:
   - "All factual information is accurate and up-to-date" means there are no errors or outdated information.

2. Source Assessment:
   - Assess whether the information appears to come from reliable, academic sources appropriate for AP-level content.

3. Bias Detection:
   - Analyze the language and presentation for any signs of bias or subjective language.
   - Ensure that the article maintains neutrality and objectivity.
   Definition:
   - "Maintains objectivity and avoids biased language" means the article presents information fairly without promoting a particular viewpoint.

4. Distinction Between Fact and Interpretation:
   - Check whether the article clearly distinguishes between established facts and interpretations or theories.
   - Interpretations should be presented as such, not as undisputed facts.

5. Completeness of Information:
   - Evaluate whether the article provides a complete picture without omitting crucial information that could lead to misunderstandings.

Scoring Criteria:

- Assign a score of 1 if all of the following conditions are met:
  1. All factual information in the article is accurate and up-to-date.
  2. The article maintains objectivity and avoids biased language or perspectives.
  3. There is a clear distinction between established facts and interpretations.
  4. The information provided is complete and does not omit crucial context.
- Assign a score of 0 if any of the above conditions are not fully met.

Response Instructions:

- Provide your answer strictly in the following JSON format:

{{
  "score": 0 or 1,
  "rationale": "Two sentences explaining your scoring decision.",
  "feedback": "Two sentences of constructive feedback."
}}

Important:

- Only provide the JSON response.
- Do not include any additional text or explanations outside the JSON format.
- Ensure that your rationale and feedback are concise, each limited to two sentences.
- If you do not follow these instructions precisely, you will be penalized.
"""

def generate_prompt7(ARTICLE, COURSE):
    return f"""
You are a veteran AP {COURSE} educator and curriculum developer with 30 years of experience. Your task is to provide constructive feedback on an article based on several "good to have" factors that enhance student engagement and learning.

Article to evaluate:
<article>
{ARTICLE}
</article>

Please evaluate the article based on the following factors:

1. Interesting:
   - Does the article engage the reader's interest?
   - Are there elements that make the content compelling?

2. Clarity:
   - Is the article written clearly and understandably?
   - Does it avoid unnecessary jargon or explain terms when used?

3. Real-world Examples/Analogies:
   - Does the article include real-world examples or analogies to illustrate concepts?

4. Addresses Common Misconceptions:
   - Does the article identify and correct common misconceptions related to the topic?

5. Promotes Higher-order Thinking and Reasoning Skills:
   - Does the article encourage analysis, evaluation, and synthesis?
   - Does it pose questions or challenges that stimulate critical thinking?

Response Instructions:

- Provide your feedback in the following JSON format:

{{
  "feedback": "Two sentences of constructive feedback addressing the above factors."
}}

Important:

- Only provide the JSON response.
- Do not include any additional text or explanations outside the JSON format.
- Ensure that your feedback is concise, limited to two sentences, and addresses the factors above.
- If you do not follow these instructions precisely, you will be penalized.
"""

def generate_final_prompt(all_responses, COURSE):
    return f"""
You are a senior AP {COURSE} program director and assessment specialist with 30 years of experience in curriculum development and quality assurance. Your expertise in {COURSE} analysis, pedagogical best practices, and AP standards is unparalleled. Your task is to synthesize the results from multiple evaluation prompts and provide a comprehensive, authoritative assessment of an AP {COURSE} article.

You will analyze a set of JSON responses, each containing a score (0 or 1) and a rationale from different evaluation prompts. These responses are provided below.

Evaluation results to analyze:
{all_responses}

Please follow the instructions below carefully and thoroughly. Analyze each point step by step internally, but present only the final JSON output as specified. If you do not follow the instructions exactly, you will be penalized.

Evaluation Steps:

1. Score Tabulation:
   - Go through the evaluation prompts.
   - Count the number of scores of 1 and scores of 0.
   - Calculate the total_score, which is the sum of all scores.

2. Key Strengths:
   - Identify areas where the article consistently received a score of 1.
   - Summarize the key strengths based on the rationales provided.

3. Key Weaknesses:
   - Identify areas where the article received a score of 0.
   - Summarize the main weaknesses and areas for improvement.

Scoring Definition:

- "total_score": The sum of all individual scores from the evaluation prompts.

Response Instructions:

- Provide your assessment in the following JSON format:

{{
  "total_score": X (max score can be 6),
  "key_strengths": ["Strength 1", "Strength 2", ...],
  "key_weaknesses": ["Weakness 1", "Weakness 2", ...],
  "recommendation": "Your recommendation from options a, b, c, or d."
}}

Recommendation Options:

- a) "Approved for immediate use"
- b) "Approved with minor revisions"
- c) "Major revisions required"
- d) "Rejected as unsuitable for AP {COURSE}"

- Choose one option and provide a brief justification (two sentences).

Important:

- Only provide the JSON response.
- Do not include any additional text or explanations outside the JSON format.
- Ensure that your strengths, weaknesses, and justification are concise.
- If you do not follow these instructions precisely, you will be penalized.
"""


def process_row(row_data, course, api_key):
    try:
        TOPIC, THEMES, OBJECTIVES, KEY_CONCEPTS, ARTICLE, QUESTIONS = row_data

        prompts = [
            generate_prompt1(ARTICLE, course),
            generate_prompt2(ARTICLE, KEY_CONCEPTS, course),
            generate_prompt3(ARTICLE, THEMES, OBJECTIVES, course),
            generate_prompt4(ARTICLE, TOPIC, course),
            generate_prompt5(ARTICLE, QUESTIONS, course),
            generate_prompt6(ARTICLE, course),
            generate_prompt7(ARTICLE, course)
        ]

        responses = parallel_api_calls(prompts, api_key)

        all_responses = f"""
        <evaluation_results>
        <format_evaluation>
            {responses[0]}
        </format_evaluation>
        <alignment_with_key_concepts_and_skills>
            {responses[1]}
        </alignment_with_key_concepts_and_skills>
        <alignment_with_themes_and_learning_objectives>
            {responses[2]}
        </alignment_with_themes_and_learning_objectives>
        <concept_formula_inclusion>
            {responses[3]}
        </concept_formula_inclusion>
        <ap_question_sufficiency>
            {responses[4]}
        </ap_question_sufficiency>
        <factual_accuracy>
            {responses[5]}
        </factual_accuracy>
        <good_to_have_factors>
            {responses[6]}
        </good_to_have_factors>
        </evaluation_results>
        """

        final_prompt = generate_final_prompt(all_responses, course)
        final_response = call_claude_api(final_prompt, api_key)

        return responses + [final_response]
    except Exception as e:
        st.error(f"Error in process_row: {str(e)}")
        return ["NA"] * 8

def get_csv_download_link(df, filename="processed_articles.csv"):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download Processed CSV</a>'
    return href

def process_csv(df, course, api_key, start_row, end_row, progress_bar, stop_flag, download_button):
    results = []
    for index, row in df.iloc[start_row:end_row+1].iterrows():
        if stop_flag.is_set():
            break
        try:
            row_data = row.tolist()
            responses = process_row(row_data, course, api_key)
            results.append(responses)
        except Exception as e:
            st.error(f"Error processing row {index}: {str(e)}")
            responses = ["NA"] * 8  # Add NA for all 8 columns
            results.append(responses)
        
        # Update the DataFrame after each row is processed
        for j in range(min(7, len(responses))):
            df.loc[index, f'Evaluation_{j+1}'] = responses[j]
        
        if len(responses) > 7:
            df.loc[index, 'Final_Evaluation'] = responses[7]
        else:
            df.loc[index, 'Final_Evaluation'] = "NA"
        
        progress = (index - start_row + 1) / (end_row - start_row + 1)
        progress_bar.progress(progress)
        
        # Update the download button after each row
        download_button.markdown(get_csv_download_link(df), unsafe_allow_html=True)
    
    return results

def main():
    st.set_page_config(page_title="AP Article Evaluation", page_icon="📝", layout="wide")

    # Load Lottie animation
    lottie_book = load_lottie_url("https://assets5.lottiefiles.com/packages/lf20_1a8dx7zj.json")

    # Title and animation
    col1, col2 = st.columns([2, 1])
    with col1:
        st.title("AP Article Evaluation")
        st.write("Evaluate your AP Articles with ease!")
    with col2:
        st_lottie(lottie_book, speed=1, height=150, key="initial")

    # API Key input
    api_key = st.text_input("Enter your Anthropic API Key:", type="password")
    if not api_key:
        st.warning("Please enter your Anthropic API Key to proceed.")
        return

    # Course selection (common for both input methods)
    course = st.selectbox("Select AP course", 
                          ["World History", "US History", "European History", "Human Geography", 
                           "Biology", "Chemistry", "Physics", "Environmental Science", 
                           "Calculus AB", "Calculus BC", "Statistics", 
                           "English Language", "English Literature", 
                           "Psychology", "Economics", "Government and Politics"])

    # Input method selection
    input_method = st.radio("Choose input method:", ("Text Input", "CSV Upload"))

    if input_method == "Text Input":
        articles = []
        for i in range(1):  # Allow 1 article at a time
            st.subheader(f"Article {i+1}")
            topic = st.text_input(f"Enter topic for article {i+1}", key=f"t{i}")
            themes = st.text_area(f"Enter themes for article {i+1}", key=f"th{i}")
            objectives = st.text_area(f"Enter learning objectives for article {i+1}", key=f"o{i}")
            key_concepts = st.text_area(f"Enter key concepts for article {i+1}", key=f"k{i}")
            article = st.text_area(f"Enter article {i+1}", key=f"a{i}", height=300)
            questions = st.text_area(f"Enter sample AP-style questions for article {i+1}", key=f"q{i}")
            
            if topic and themes and objectives and key_concepts and article and questions:
                articles.append([topic, themes, objectives, key_concepts, article, questions])

        if st.button("Evaluate Article"):
            if articles:
                with st.spinner("Evaluating article..."):
                    results = []
                    progress_bar = st.progress(0)
                    for i, a in enumerate(articles):
                        result = process_row(a, course, api_key)
                        results.append(result)
                        progress_bar.progress((i + 1) / len(articles))

                    for i, (article, result) in enumerate(zip(articles, results)):
                        st.subheader(f"Results for Article {i+1}")
                        st.write(f"**Course:** {course}")
                        st.write(f"**Topic:** {article[0]}")
                        
                        for j, response in enumerate(result[:7]):
                            with st.expander(f"Evaluation {j+1}"):
                                st.json(json.loads(response))
                        
                        with st.expander("Final Evaluation"):
                            st.json(json.loads(result[7]))
            else:
                st.warning("Please enter an article to evaluate.")

    else:  # CSV Upload
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            st.write(df)

            expected_columns = ["Topic", "Themes", "Objectives", "Key Concepts", "Article", "Questions"]
            if not all(col in df.columns for col in expected_columns):
                st.error(f"The CSV file must include these columns: {', '.join(expected_columns)}")
                return

            # Row range selection
            col1, col2 = st.columns(2)
            with col1:
                start_row = st.number_input("Start Row", min_value=0, max_value=len(df)-1, value=0)
            with col2:
                end_row = st.number_input("End Row", min_value=start_row, max_value=len(df)-1, value=len(df)-1)

            if st.button("Process CSV"):
                progress_bar = st.progress(0)
                stop_flag = threading.Event()
                
                # Create placeholders for pause button and download button
                pause_button = st.empty()
                download_button = st.empty()
                
                def pause_processing():
                    stop_flag.set()
                    st.warning("Processing paused. You can download the CSV with processed rows so far.")
                    # Ensure the download button is visible when paused
                    download_button.markdown(get_csv_download_link(df), unsafe_allow_html=True)

                pause_button.button("Pause Processing", on_click=pause_processing)

                with st.spinner("Processing CSV..."):
                    results = process_csv(df, course, api_key, start_row, end_row, progress_bar, stop_flag, download_button)

                if stop_flag.is_set():
                    st.success("Processing paused. You can download the CSV with processed rows above.")
                else:
                    st.success("Processing completed. You can download the full CSV above.")

                st.write(df)

if __name__ == "__main__":
    main()
