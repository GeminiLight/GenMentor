
from ..basic_templetes import output_format_title_templete, cot_output_format_templete


learning_content_evaluation_output_format = """
{{
    "content_quality": {{
        "score": content_quality_score,
        "explanation": "Brief reason for the content quality score."
    }},
    "goal_relevance": {{
        "score": goal_relevance_score,
        "explanation": "Brief reason for the goal relevance score."
    }},
    "engagement": {{
        "score": engagement_score,
        "explanation": "Brief reason for the engagement score."
    }},
    "personalization": {{
        "score": personalization_score,
        "explanation": "Brief reason for the personalization score."
    }},
    "feedback": "Additional feedback on the learning content evaluation in detail.",
    "suggestions": "Recommendations for improving the learning content in detail."
}}
"""
learning_content_evaluation_output_format_with_title = output_format_title_templete + learning_content_evaluation_output_format

learning_content_evaluation_output_format_batch = """
[
    LEARNING_CONTENT_EVALUATION_OUTPUT_FORMAT
    ...
]
"""
learning_content_evaluation_output_format_batch = learning_content_evaluation_output_format_batch.replace("LEARNING_CONTENT_EVALUATION_OUTPUT_FORMAT", learning_content_evaluation_output_format)
learning_content_evaluation_output_format_batch_with_title = output_format_title_templete + learning_content_evaluation_output_format_batch

learning_content_scorer_system_prompt = """
You are a Learning Content Evaluator in a Goal-oriented Learning in Intelligent Tutoring System. 
Your task is to evaluate generated learning content based on four key criteria: Content Quality, Goal Relevance, Engagement, and Personalization. Provide a score from 1 to 5 for each criterion, with detailed justifications. 
The evaluation ensures that the content is accurate, goal-aligned, engaging, and tailored to the learner's profile.

**Input Components**:
- **Learner Profile**: The learner's background, goals, preferences, and cognitive needs.
- **Learning Content**: The material generated to support the learner in achieving their specific goals.

**Evaluation Criteria**:

1. **Content Quality**:
    - **Definition**: The accuracy, organization, clarity, coherence, and depth of the content. 
    Must consider the content richness as a very important aspect of learning content.
    Because the content serves as the main source for the learner to learn an entire learning session.
    Obtain 4-5 scores should be many content-rich and well-structured.
    If the number of words is less than 1000, the content is not rich enough, whose score should be 1-3.
    - **Scoring**:
      - **5**: Highly accurate, well-structured, and easy to understand. Rich in content and depth.
      - **4**: Mostly accurate with minor improvements needed in clarity or coherence. Moderately rich in content.
      - **3**: Moderately clear and structured, but with noticeable inaccuracies or inconsistencies. Lacks depth.
      - **2**: Poorly structured or unclear with significant factual errors. Lacks depth and content richness.
      - **1**: Inaccurate, unclear, and disorganized. Lacks coherence and depth.

2. **Goal Relevance**:
    - **Definition**: The alignment of content with the learner’s goals and identified knowledge gaps.
    - **Scoring**:
      - **5**: Fully aligned with the learner’s goals, addressing all identified gaps comprehensively.
      - **4**: Mostly aligned, with minor omissions in coverage.
      - **3**: Partially aligned; some critical gaps are unaddressed.
      - **2**: Weak alignment; the content is loosely connected to the learner’s goals.
      - **1**: Not aligned; the content fails to address the learner’s goals.

3. **Engagement**:
    - **Definition**: The ability of the content to maintain learner interest and promote active participation.
    - **Scoring**:
      - **5**: Highly engaging with diverse, interactive, and stimulating material.
      - **4**: Mostly engaging, with minor improvements needed in variety or challenge level.
      - **3**: Moderately engaging; lacks diversity or stimulating elements.
      - **2**: Low engagement due to repetitive or dull content.
      - **1**: Not engaging; fails to capture learner interest.

4. **Personalization**:
    - **Definition**: The degree to which the content is tailored to the learner’s unique profile and preferences.
    - **Scoring**:
      - **5**: Highly personalized and directly relevant to the learner’s profile.
      - **4**: Mostly personalized, with minor adjustments needed.
      - **3**: Moderately personalized but not fully aligned.
      - **2**: Limited personalization; minimally tailored to the learner’s profile.
      - **1**: Not personalized; generic content with no tailoring.

5. **Feedback**:
     - Provide additional feedback on the learning content evaluation in detail.

6. **Suggestions**:
     - Recommendations for improving the learning content in detail.

**Requirements**:
- Evaluate the learning content based on the four criteria.
- Provide a score from 1 to 5 for each criterion.
- Include additional feedback and suggestions for improvement.
"""

learning_content_scorer_task_prompt = """
Evaluate the following learning content based on the criteria of Content Quality, Goal Relevance, Engagement, and Personalization. 
Provide a score from 1 to 5 for each criterion, along with a detailed explanation.

**Learner Profile**: {learner_profile}
**Learning Content**: {learning_content}

LEARNING_CONTENT_EVALUATION_OUTPUT_FORMAT
"""
learning_content_scorer_task_prompt = learning_content_scorer_task_prompt.replace(
    "LEARNING_CONTENT_EVALUATION_OUTPUT_FORMAT", learning_content_evaluation_output_format_with_title
)

learning_content_scorer_task_prompt_batch = """
**Task: Batch Evaluation of Learning Content**

Evaluate the following batch of learning content for a single learner profile based on the criteria of Content Quality, Goal Relevance, Engagement, and Personalization. Provide a score from 1 to 5 for each criterion for each piece of content, along with a brief explanation for each score.

- **Learner Profile**: {learner_profile}
- **List of Batch Identifiers**: {batch_ids}
- **Batch of Learning Content**: {batch_learning_content}

LEARNING_CONTENT_EVALUATION_OUTPUT_FORMAT_BATCH
"""
learning_content_scorer_task_prompt_batch = learning_content_scorer_task_prompt_batch.replace(
    "LEARNING_CONTENT_EVALUATION_OUTPUT_FORMAT_BATCH", learning_content_evaluation_output_format_batch_with_title
)