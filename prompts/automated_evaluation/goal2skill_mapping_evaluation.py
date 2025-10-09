from ..basic_templetes import output_format_title_templete, cot_output_format_templete


goal2skill_mapping_evaluation_scoring_output_format = """
{{
    "necessity": {{
        "agreement": "Points of agreement (max 50 words).",
        "disagreement": "Points of disagreement (max 50 words).",
        "score": necessity_score
    }},
    "completeness": {
        "agreement": "Points of agreement (max 50 words).",
        "disagreement": "Points of disagreement (max 50 words).",
        "score": completeness_score
    }},
    "feedback": "Feedback on the scoring results.",
    "suggestions": "Suggestions for improvement."
}}
"""
goal2skill_mapping_evaluation_scoring_output_format_with_title = output_format_title_templete + goal2skill_mapping_evaluation_scoring_output_format

goal2skill_mapping_evaluation_batch_scoring_output_format = """
[
    {{
        "id": "Method Name Identifier",
        "necessity": {{ 
            "agreement": "Points of agreement (max 50 words).",
            "disagreement": "Points of disagreement (max 50 words).",
            "score": necessity_score
        }},
        "completeness": {{
            "agreement": "Points of agreement (max 50 words).",
            "disagreement": "Points of disagreement (max 50 words).",
            "score": completeness_score
        }},
        "feedback": "Feedback on the scoring results.",
        "suggestions": "Suggestions for improvement."
    }},
    ...
]
"""
goal2skill_mapping_evaluation_batch_scoring_output_format_with_title = output_format_title_templete + goal2skill_mapping_evaluation_batch_scoring_output_format

goal2skill_mapping_evaluation_validation_output_format = """
{{
    "num_validated_skills": num_validated_skills,
    "num_skill_requirements": num_skill_requirements,
    "num_recalled_skills": num_recalled_skills,
    "recalled_skills": [Array of recalled skills],
    "recall": {{
        "value": recall_value,
        "explanation": "Explanation of the Recall score (max 50 words)."
    }},
    "precision": {{
        "value": precision_value,
        "explanation": "Explanation of the Precision score (max 50 words)."
    }},
    "necessity": {{
        "agreement": "Points of agreement (max 50 words).",
        "disagreement": "Points of disagreement (max 50 words).",
        "score": necessity_score
    }},
    "completeness": {{
        "agreement": "Points of agreement (max 50 words).",
        "disagreement": "Points of disagreement (max 50 words).",
        "score": completeness_score
    }},
    "alignment": {{
        "agreement": "Points of agreement (max 50 words).",
        "disagreement": "Points of disagreement (max 50 words).",
        "score": alignment_score
    }},
    "feedback": "Feedback on the validation results. (more details)",
    "suggestions": "Suggestions for improvement. (more details)""
}}
"""
goal2skill_mapping_evaluation_validation_output_format_with_title = output_format_title_templete + goal2skill_mapping_evaluation_validation_output_format

goal2skill_mapping_evaluation_batch_validation_output_format = """
[
    {{
        "id": "Method Name Identifier",
        "num_validated_skills": num_validated_skills,
        "num_skill_requirements": num_skill_requirements,
        "num_recalled_skills": num_recalled_skills,
        "recalled_skills": [Array of recalled skills],
        "recall": {{
            "value": recall_value,
            "explanation": "Explanation of the Recall score (max 50 words)."
        }},
        "precision": {{
            "value": precision_value,
            "explanation": "Explanation of the Precision score (max 50 words)."
        }},
        "necessity": {{ 
            "agreement": "Points of agreement (max 50 words).",
            "disagreement": "Points of disagreement (max 50 words).",
            "score": necessity_score
        }},
        "completeness": {{
            "agreement": "Points of agreement (max 50 words).",
            "disagreement": "Points of disagreement (max 50 words).",
            "score": completeness_score
        }},
        "alignment": {{
            "agreement": "Points of agreement (max 50 words).",
            "disagreement": "Points of disagreement (max 50 words).",
            "score": alignment_score]
        }},
        "feedback": "Feedback on the validation results.",
        "suggestions": "Suggestions for improvement."
    }},
    ...
]
"""
goal2skill_mapping_evaluation_batch_validation_output_format_with_title = output_format_title_templete + goal2skill_mapping_evaluation_batch_validation_output_format


goal2skill_mapping_evaluator_system_prompt = """
You are an Evaluator tasked with assessing the Necessity and Completeness of skills identified for achieving a learner’s specified goal. Evaluate each skill on a scale of 1-5 based on the following criteria.

## Evaluation Criteria A for Scoring

1. **Necessity**:
   - **Definition**: How essential is each identified skill for achieving the learner's goal?
   - **Scoring**:
        - **5 (Excellent)**: Each skill is crucial and directly contributes to goal attainment.
        - **4 (Good)**: Most skills are essential, with minor exceptions that could be more specific.
        - **3 (Fair)**: Some skills are necessary, but others could be more relevant or specific.
        - **2 (Poor)**: Few skills are essential, with many lacking direct necessity to the goal.
        - **1 (Very Poor)**: The identified skills are largely irrelevant and do not support goal achievement.

2. **Completeness**:
   - **Definition**: How well does the identified skill set cover all key components required to achieve the goal?
   - **Scoring**:
     - **5 (Excellent)**: The skill set comprehensively covers all necessary components, providing a complete foundation for achieving the goal.
     - **4 (Good)**: The skill set covers most core components, with only minor gaps.
     - **3 (Fair)**: The skill set partially covers the goal requirements, but some important skills are missing.
     - **2 (Poor)**: The skill set has major gaps, missing essential skills needed for the goal.
     - **1 (Very Poor)**: The skill set is incomplete, lacking most of the critical skills for the goal.

3. **Alignment**:
    - **Definition**: How well do the identified skills align with the learner's goal and expected outcomes?
    - **Scoring**:
        - **5 (Excellent)**: The identified skills are highly aligned with the learner's goal and expected outcomes.
        - **4 (Good)**: The identified skills are mostly aligned with the learner's goal and expected outcomes.
        - **3 (Fair)**: The identified skills are somewhat aligned with the learner's goal and expected outcomes.
        - **2 (Poor)**: The identified skills have limited alignment with the learner's goal and expected outcomes.
        - **1 (Very Poor)**: The identified skills are not aligned with the learner's goal and expected outcomes.

## Evaluation Criteria B for Validation

If provided with a validation skill set, evaluate the Recall and Precision of the identified skills against this set.

1. **Recall (Number of Skills)**:
   - **Definition**: Measures the proportion of relevant skills (including synonyms or similar skills) from the provided validation skill list that appear in the identified skills.
   - **Formula**: 
     ```
     Recall = (Number of successfully recalled skills) / (Total number of skills in validation set)
     ```

2. **Precision (Number of Skills)**:
   - **Definition**: Measures the proportion of identified skills that match (including synonyms or similar skills) those in the validation skill list.
   - **Formula**: 
     ```
     Precision = (Number of successfully recalled skills) / (Total number of identified skills)
     ```

3. **Necessity**F same as above

4. **Completeness**F same as above

5. **Alignment**F same as above

6. **Feedback**:
    - Provide constructive feedback on the identified skills, highlighting strengths and areas for improvement.

7. **Suggestions**:
    - Offer suggestions for enhancing the identified skill set to better align with the learner's goal and improve goal achievement.

Requirements:

- Rate each skill on a scale from 1-5, justifying your evaluation with concise points of agreement and disagreement.
- Ensure the output format is valid JSON, excluding any tags (e.g., `json` tag).
"""

goal2skill_mapping_evaluator_task_prompt_scoring = """
**Evaluation Criteria A for Scoring**

Evaluate the following skill requirements for the learner’s goal based on the criteria of Necessity and Completeness. Provide a score from 1 to 5 for each criterion, along with a brief reason for your assessment.

- Learner Goal: {learning_goal}
- Mapped Skills: {skill_requirements}

**Output Template**
"""
goal2skill_mapping_evaluator_task_prompt_scoring += goal2skill_mapping_evaluation_scoring_output_format


goal2skill_mapping_evaluator_task_prompt_batch_scoring = """
**Evaluation Criteria A for Batch Scoring**

Evaluate the following sets of skill requirements for the same learner goal based on the criteria of Necessity and Completeness. Provide a score from 1 to 5 for each criterion, along with a brief reason for your assessment for each set of skill requirements.


- Learner Goal: {learning_goal}
- List of Batch IDs: {batch_ids}
- Batch of Mapped Skills: {skill_requirements}

GOAL2SKILL_MAPPING_EVALUATION_BATCH_SCORING_OUTPUT_FORMAT

Requirements:

- Use concise, specific justifications for both Necessity and Completeness.
- Ensure each entry in the output corresponds to an input result by using the "id" field to identify each set of skill requirements.
- Limit response explanations to 50 words per section for clarity.
"""
goal2skill_mapping_evaluator_task_prompt_batch_scoring = goal2skill_mapping_evaluator_task_prompt_batch_scoring.replace("GOAL2SKILL_MAPPING_EVALUATION_BATCH_SCORING_OUTPUT_FORMAT", goal2skill_mapping_evaluation_batch_scoring_output_format_with_title)

goal2skill_mapping_evaluator_task_prompt_validation = """
**Evaluation Criteria B for Validation**

Evaluate the identified skills based on the criteria of Recall and Precision. Provide the Recall and Precision scores along with a brief explanation for each.

- Learner Goal: {learning_goal}
- Skills in Validation Set: {skills_in_validation}
- Mapped Skills: {skill_requirements}

**Output Template**
GOAL2SKILL_MAPPING_EVALUATION_VALIDATION_OUTPUT_FORMAT
"""
goal2skill_mapping_evaluator_task_prompt_validation = goal2skill_mapping_evaluator_task_prompt_validation.replace("GOAL2SKILL_MAPPING_EVALUATION_VALIDATION_OUTPUT_FORMAT", goal2skill_mapping_evaluation_validation_output_format_with_title)

goal2skill_mapping_evaluator_task_prompt_batch_validation = """
**Evaluation Criteria B for Batch Validation**

Evaluate the following sets of skill requirements for the same learner goal based on the criteria of Recall and Precision. Provide Recall and Precision scores, along with a brief explanation for each, for every set of skill requirements.

- Learner Goal: {learning_goal}
- Skills in Validation Set: {skills_in_validation}
- List of Batch IDs: {batch_ids}
- Batch of Mapped Skills: {batch_skill_requirements}

GOAL2SKILL_MAPPING_EVALUATION_BATCH_VALIDATION_OUTPUT_FORMAT

Requirements:

- For each entry, use concise justifications for Recall and Precision.
- Ensure each evaluation is clearly linked to its respective set of skill requirements by using the "id" field.
- Limit explanations to 50 words for clarity and brevity.
"""
goal2skill_mapping_evaluator_task_prompt_batch_validation = goal2skill_mapping_evaluator_task_prompt_batch_validation.replace("GOAL2SKILL_MAPPING_EVALUATION_BATCH_VALIDATION_OUTPUT_FORMAT", goal2skill_mapping_evaluation_batch_validation_output_format_with_title)