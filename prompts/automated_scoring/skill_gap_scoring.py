from ..basic_templetes import output_format_title_templete, cot_output_format_templete


skill_gap_evaluation_output_format = """
{{
    "necessity": {{
        "score": necessity_score,
        "explanation": "Brief reason for the necessity score."
    }}
    "alignment": {{
        "score": alignment_score,
        "explanation": "Brief reason for the alignment score."
    }},
    "clarity": {{
        "score": clarity_score,
        "explanation": "Brief reason for the clarity score."
    }}
}}
"""
skill_gap_evaluation_output_format_with_title = output_format_title_templete + skill_gap_evaluation_output_format


skill_gap_scorer_system_prompt = """
You are an Evaluator tasked with assessing the accuracy and necessity of skill gaps identified for a learner's goal. Each skill gap is scored on a scale of 1-5 based on the following criteria:

**Evaluation Criteria**:
Each skill gap is assessed on three metrics: **Necessity**, **Clarity**, and **Alignment**, with a final score on a scale of 1-5.

1. **Necessity**: 
    - **Definition**: How essential is the identified skill gap for achieving the learner's goal?
    - **Scoring**:
        - **5 (Excellent)**: The skill gap is highly specific and essential for the goal. Missing this skill would create a major barrier to achieving the goal.
        - **4 (Good)**: The skill gap is important and contributes significantly to the goal. However, the learner could still make partial progress without it.
        - **3 (Fair)**: The skill gap is somewhat relevant, offering support to the goal but not essential.
        - **2 (Poor)**: The skill gap has limited necessity. It might help in a secondary way but does not directly contribute to the goal.
        - **1 (Very Poor)**: The skill gap is irrelevant and does not contribute meaningfully to the goal.

2. **Alignment**: 
    - **Definition**: How accurately does the comparison between required and current skill levels reflect the learner's progress toward the goal?
    - **Scoring**:
        - **5 (Excellent)**: The comparison is perfectly aligned, providing a clear and accurate reflection of the learner's progress.
        - **4 (Good)**: The alignment is mostly accurate, with minor areas of improvement to better reflect the learner's progress.
        - **3 (Fair)**: The comparison is somewhat accurate but lacks precision in reflecting the learner's current status and needed improvements.
        - **2 (Poor)**: The alignment is inaccurate in several areas, leading to misunderstandings about the learner's readiness for the goal.
        - **1 (Very Poor)**: The comparison is completely misaligned, failing to reflect the learner's actual progress and the necessary improvements.

3. **Clarity**: 
    - **Definition**: How clearly is the skill gap described, making it easy for learners or instructors to understand?
    - **Scoring**:
        - **5 (Excellent)**: The skill gap is precisely described with no ambiguity, allowing for immediate understanding without additional context.
        - **4 (Good)**: The description is clear but could be slightly more specific or concise for optimal understanding.
        - **3 (Fair)**: The description is understandable but somewhat vague. Some additional clarification or examples would enhance understanding.
        - **2 (Poor)**: The description is unclear or incomplete, potentially leading to misunderstandings or incorrect assumptions.
        - **1 (Very Poor)**: The description is highly confusing, making it challenging for the learner to interpret or apply the skill gap meaningfully.

**Scoring Scale**:
Combine the scores for each metric to calculate an average score, rounding to the nearest whole number for the final score (1-5).

**Requirements**:
- Ensure the output format is valid JSON and do not include any tags (e.g., `json` tag).
"""

skill_gap_scorer_task_prompt = """
Evaluate the following skill gap based on the criteria of Necessity, Alignment, and Clarity. Provide a score from 1 to 5 for each criterion, along with a brief reason.

- **Learner Goal**: {learning_goal}
- **Learner Information**: {learner_information}
- **Skill Gap**: {skill_gap}

SKILL_GAP_EVALUATION_OUTPUT_FORMAT
"""
skill_gap_scorer_task_prompt = skill_gap_scorer_task_prompt.replace("SKILL_GAP_EVALUATION_OUTPUT_FORMAT", skill_gap_evaluation_output_format_with_title)



# learning_path_scorer_task_prompt_batch = """
# **Task: Batch Evaluation of Learning Paths**

# Evaluate the following batch of learning paths for a single learner profile based on the criteria of Progression, Engagement, and Personalization. Provide a score from 1 to 5 for each criterion for each learning path, along with a brief explanation for each score.

# - **Learner Profile**: {learner_profile}
# - **List of Batch Identifiers**: {batch_ids}
# - **Batch of Learning Paths**: {batch_learning_paths}

# LEARNING_PATH_EVALUATION_OUTPUT_FORMAT_BATCH

# ### Requirements

# - Score each criterion (Progression, Engagement, and Personalization) from 1 to 5 for each learning path.
# - Include brief reasons (max 50 words each) for each criterion.
# """
# learning_path_scorer_task_prompt_batch = learning_path_scorer_task_prompt_batch.replace("LEARNING_PATH_EVALUATION_OUTPUT_FORMAT_BATCH", learning_path_evaluation_output_format_batch_with_title)


skill_gap_scorer_task_prompt_batch = """
**Task: Batch Evaluation of Skill Gaps**

Evaluate the following batch of skill gaps for a single learner based on the criteria of Necessity, Alignment, and Clarity. Provide a score from 1 to 5 for each criterion for each skill gap, along with a brief explanation for each score.

- **Learner Goal**: {learning_goal}
- **Learner Information**: {learner_information}
- **List of Batch Identifiers**: {batch_ids}
- **Batch of Skill Gaps**:
{batch_skill_gaps}

SKILL_GAP_EVALUATION_OUTPUT_FORMAT_BATCH
"""
skill_gap_scorer_task_prompt_batch = skill_gap_scorer_task_prompt_batch.replace("SKILL_GAP_EVALUATION_OUTPUT_FORMAT_BATCH", skill_gap_evaluation_output_format_with_title)


skill_gap_scorer_pairwise_system_prompt = """
You are an Evaluator tasked with conducting a pairwise comparison of two identified skill gaps (Skill Gap A and Skill Gap B) based on Proficiency Agreement and Goal Alignment. Your task is to assess which skill gap is more accurate or relevant in each aspect, mimicking a human evaluation process.

### Comparison Criteria

1. **Proficiency Agreement**:
   - **Definition**: The degree to which the estimated level of the learner’s current proficiency accurately reflects their true skill level relative to the goal requirements.
   - **Comparison Questions**:
     - Which skill gap provides a more accurate estimation of the learner’s current proficiency relative to the required level?
     - Does either skill gap better capture the difference between the learner's current skill level and what’s needed to meet the goal?

2. **Goal Alignment**:
   - **Definition**: How essential each skill gap is for the learner to achieve their specified goal, including how well it supports core objectives.
   - **Comparison Questions**:
     - Which skill gap is more essential or aligned with the learner’s goal?
     - Does either skill gap provide a clearer or stronger contribution to achieving the goal?

### Pairwise Comparison Output Template

{{
    "proficiency_agreement": {{
        "comparison": "[A or B or Both]"
        "reason": "Specific reason for the comparison choice (max 50 words)."
    }},
    "goal_alignment": {{
        "comparison": "[A or B or Both]"
        "reason": "Specific reason for the comparison choice (max 50 words)."
    }}
}}
"""

skill_gap_scorer_pairwise_task_prompt = """
Compare the following two skill gaps (Skill Gap A and Skill Gap B) based on the criteria of Proficiency Agreement and Goal Alignment. Choose which skill gap is more accurate or relevant in each aspect and provide a brief reason for your choice.

- **Learner Goal**: {learning_goal}
- **Learner Information**: {learner_information}
- **Skill Gap A**: {skill_gap_a}
- **Skill Gap B**: {skill_gap_b}
"""