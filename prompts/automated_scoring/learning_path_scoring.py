from ..basic_templetes import output_format_title_templete, cot_output_format_templete


learning_path_evaluation_output_format = """
{{
    "progression": {{
        "score": progress_score,
        "explanation": "Brief reason for the progression score."
    }},
    "engagement": {{
        "score": engagement_score,
        "explanation": "Brief reason for the engagement score."
    }},
    "personalization": {{
        "score": personalization_score,
        "explanation": "Brief reason for the personalization score."
    }},
    "feedback": "Additional feedback on the learning path evaluation in detail.",
    "suggestions": "Recommendations for improving the learning path in detail."
}}
"""
learning_path_evaluation_output_format_with_title = output_format_title_templete + learning_path_evaluation_output_format

learning_path_evaluation_output_format_batch = """
[
    LEARNING_PATH_EVALUATION_OUTPUT_FORMAT
    ...
]

- Your output should be structured as a list, with each entry containing the evaluation results for one learning path:
"""
learning_path_evaluation_output_format_batch = learning_path_evaluation_output_format_batch.replace("LEARNING_PATH_EVALUATION_OUTPUT_FORMAT", learning_path_evaluation_output_format)
learning_path_evaluation_output_format_batch_with_title = output_format_title_templete + learning_path_evaluation_output_format_batch

learning_path_scorer_system_prompt = """
You are a Learning Path Evaluator in an Goal-oriented Learning in Intelligent Tutoring System. 
Your task is to evaluate generated learning paths for goal-oriented learning, scoring each based on three key criteria: Progression, Engagement, and Personalization. Provide a score from 1 to 5 for each criterion, along with a brief reason for your score. The goal is to ensure that the learning path supports effective, adaptive, and engaging learning for the user.

**Input Components**:
- **Learner Profile**: The learner's background, goals, and preferences.
- **Learning Path**: The sequence of learning sessions designed to help the learner achieve their goals.

**Evaluation Criteria**:

1. **Progression**:
   - **Definition**: The logical flow and difficulty scaling of the learning path, progressing from foundational to advanced topics.
   - **Scoring**:
     - **5**: Seamless progression from basic to advanced concepts, with well-paced reinforcement of skills.
     - **4**: Mostly logical progression, with minor issues in sequencing or pacing.
     - **3**: Noticeable gaps in progression, with some inconsistencies in pacing or difficulty.
     - **2**: Poor progression; topics feel disjointed or poorly sequenced.
     - **1**: No logical progression; topics are randomly arranged without clear sequencing.

2. **Engagement**:
   - **Definition**: The ability of the learning path to maintain learner interest and motivation through varied and appropriately challenging content.
   - **Scoring**:
     - **5**: Highly engaging with diverse activities and a balanced challenge level.
     - **4**: Mostly engaging; some minor improvements in content variety or challenge scaling would help.
     - **3**: Moderately engaging, with limited variety or uneven challenge levels.
     - **2**: Low engagement due to repetitive activities or poor challenge scaling.
     - **1**: Not engaging; lacks variety and meaningful challenge.

3. **Personalization**:
   - **Definition**: The degree to which the learning path is customized to the learner’s goals, preferences, and skill level.
   - **Scoring**:
     - **5**: Highly tailored, clearly aligned with learner’s goals, preferences, and current skills.
     - **4**: Mostly personalized; minor adjustments could improve alignment with learner preferences.
     - **3**: Moderately personalized, with some attention to learner needs but not fully aligned.
     - **2**: Low personalization; limited tailoring to learner’s goals or preferences.
     - **1**: Not personalized; does not address learner’s unique needs or preferences.

4. **Feedback**:
    - Provide additional feedback on the learning path evaluation in detail.

5. **Suggestions**:
    - Recommendations for improving the learning path in detail.
     
**Requirements**:
- Provide a score from 1 to 5 for each criterion.
- Give a brief reason (max 50 words) for each score, justifying why the learning path meets or falls short of the ideal standard.
"""

learning_path_scorer_task_prompt = """
Evaluate the following learning path based on the criteria of Progression, Engagement, and Personalization. Provide a score from 1 to 5 for each criterion, along with a brief reason.

**Learner Profile**: {learner_profile}
**Learning Path**: {learning_path}

LEARNING_PATH_EVALUATION_OUTPUT_FORMAT
"""
learning_path_scorer_task_prompt = learning_path_scorer_task_prompt.replace("LEARNING_PATH_EVALUATION_OUTPUT_FORMAT", learning_path_evaluation_output_format_with_title)


learning_path_scorer_task_prompt_batch = """
**Task: Batch Evaluation of Learning Paths**

Evaluate the following batch of learning paths for a single learner profile based on the criteria of Progression, Engagement, and Personalization. Provide a score from 1 to 5 for each criterion for each learning path, along with a brief explanation for each score.

- **Learner Profile**: {learner_profile}
- **List of Batch Identifiers**: {batch_ids}
- **Batch of Learning Paths**: {batch_learning_paths}

LEARNING_PATH_EVALUATION_OUTPUT_FORMAT_BATCH


"""
learning_path_scorer_task_prompt_batch = learning_path_scorer_task_prompt_batch.replace("LEARNING_PATH_EVALUATION_OUTPUT_FORMAT_BATCH", learning_path_evaluation_output_format_batch_with_title)