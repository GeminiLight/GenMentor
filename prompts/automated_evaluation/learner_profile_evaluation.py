from ..basic_templetes import output_format_title_templete, cot_output_format_templete


learner_profile_evaluation_output_format = """
{{
    "overall_accuracy": {{
        "value": {{overall_accuracy_value}},
        "explanation": "Overall accuracy based on average of component scores (max 50 words)."
    }},
    "feedback": "Additional feedback on the learner profile evaluation in detail.",
    "suggestions": "Recommendations for improving the learner profile in detail."
}}
"""
learner_profile_evaluation_output_format_with_title = output_format_title_templete + learner_profile_evaluation_output_format

learner_profile_evaluation_output_format_batch = """
[
    LEARNER_PROFILE_EVALUATION_OUTPUT_FORMAT,
    ...
]
"""
learner_profile_evaluation_output_format_batch = learner_profile_evaluation_output_format_batch.replace("LEARNER_PROFILE_EVALUATION_OUTPUT_FORMAT", learner_profile_evaluation_output_format)
learner_profile_evaluation_output_format_batch_with_title = output_format_title_templete + learner_profile_evaluation_output_format_batch


learner_profile_evaluator_system_prompt = """
You are an Evaluator tasked with assessing the Accuracy of generated learner profiles by comparing them to a ground-truth profile. 
Each learner profile contains multiple components, including cognitive status, learning preferences, and behavioral patterns. 
Your goal is to provide a comprehensive accuracy evaluation on a 100-point scale.

### Main Components of the Learner Profile

1. **Cognitive Status**:
    - Mastered Skills: Skills the learner has mastered.
    - In-Progress Skills: Skills the learner is currently learning.
    - Knowledge Gaps: Areas where the learner lacks proficiency.

2. **Learning Preferences**:
    - Content Style: The preferred style of learning content.
    - Activity Type: The preferred type of learning activity.
    - Additional Notes: Any other relevant preferences.

3. **Behavioral Patterns**:
    - Participation Frequency: Frequency of system usage.
    - Session Duration: Average duration of learning sessions.
    - Additional Notes: Any other behavioral patterns.

### Evaluation Criteria for Each Component

1. **Cognitive Status**:
   - Compare the generated cognitive status (mastered skills, in-progress skills, knowledge gaps) to the ground-truth cognitive status.
2. **Learning Preferences**:
   - Assess the generated learning preferences (content style, activity type) against the ground-truth preferences.
3. **Behavioral Patterns**:
   - Evaluate the generated behavioral patterns (participation frequency, session duration) in relation to the ground-truth.

### Evaluation Requirements

- Calculate an overall accuracy score directly.
- Include brief explanations (maximum 50 words) describing the alignment or misalignment for each component.
- Ensure the output is structured in valid JSON format.
"""

learner_profile_evaluator_task_prompt = """
**Task: Evaluate Generated Learner Profiles for Comprehensive Accuracy (100-Point Scale)**

Evaluate the following generated learner profiles for the specified learner goal, comparing each profile to the ground-truth profile. Calculate individual accuracy scores for Cognitive Status, Learning Preferences, and Behavioral Patterns, and provide an overall accuracy score based on these components.

- Ground-truth Profile: {ground_truth_profile}
- Generated Profiles: {generated_profiles}

LEARNER_PROFILE_EVALUATION_OUTPUT_FORMAT

Requirements:

- Use concise explanations for each component and the overall accuracy score, limited to 50 words.
- Ensure each output is linked to the correct generated profile using the "id" field.
"""
learner_profile_evaluator_task_prompt = learner_profile_evaluator_task_prompt.replace("LEARNER_PROFILE_EVALUATION_OUTPUT_FORMAT", learner_profile_evaluation_output_format)


learner_profile_evaluator_task_prompt_batch = """
**Task: Batch Evaluation of Learner Profiles**

Evaluate the following batch of generated learner profiles for the specified learner goal, comparing each profile to the ground-truth profile. Calculate individual accuracy scores for Cognitive Status, Learning Preferences, and Behavioral Patterns, and provide an overall accuracy score based on these components.

- Ground-truth Profile: {ground_truth_profile}
- List of Batch Identifiers: {batch_ids}
- Batch of Generated Profiles: {batch_generated_profiles}

LEARNER_PROFILE_EVALUATION_OUTPUT_FORMAT_BATCH
"""
learner_profile_evaluator_task_prompt_batch = learner_profile_evaluator_task_prompt_batch.replace(
    "LEARNER_PROFILE_EVALUATION_OUTPUT_FORMAT_BATCH", learner_profile_evaluation_output_format_batch_with_title
)
