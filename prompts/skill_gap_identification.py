from .basic_templetes import output_format_title_templete, cot_output_format_templete

skill_requirements_output_format = """
[
    {{
        "name": "skill name 1",
        "required_level": "advanced"
    }},
    ...
]
"""
skill_requirements_output_format_with_title = skill_requirements_output_format + output_format_title_templete
cot_skill_requirements_output_format_with_title = output_format_title_templete + cot_output_format_templete.replace("RESULT_OUTPUT_FORMAT", skill_requirements_output_format)

skill_gap_output_format = """
[
    {{
        "name": "skill name 1",
        "is_gap": true or false,
        "required_level": "xxx",
        "current_level": "xxx",
        "reason": "Explain the reason on current level. (Max 20 words)"
        "level_confidence": "xxx",
    }},
    ...
]
"""
skill_gap_output_format_with_title = skill_gap_output_format + output_format_title_templete
cot_skill_gap_output_format_with_title = output_format_title_templete + cot_output_format_templete.replace("RESULT_OUTPUT_FORMAT", skill_gap_output_format)

refined_learning_goal_output_format = """
{{
    "content": "Detailed and specific learning goal.",
}}

- The output should be a JSON object with a "content" key.
"""
refined_learning_goal_output_format_with_title = refined_learning_goal_output_format + output_format_title_templete

skill_gap_identifier_system_prompt_base = """
You are the Skill Gap Identifier in a goal-oriented Intelligent Tutoring System.
Your role is to map the learner's goal to essential skills and identify skill gaps based on the learner's current skill levels.

**Core Tasks**:
Task A: Goal-to-Skill Mapping
Map the learner's specified goal to the essential skills required for achieving it.
"""

skill_gap_identifier_system_prompt_requirements = """
**Requirements**:
- `required_level` should be one of the following: "beginner", "intermediate", "advanced".
- `current_level` should be one of the following: "unlearned", "beginner", "intermediate", "advanced".
- `level_confidence` should be one of the following: "low", "medium", "high".
- Ensure the output format is valid JSON and do not include any tags (e.g., `json` tag).
- Ensure that the output is clear and includes only the most critical skills required for goal completion.
- Ensure that the identified knowledge is precise and directly contributes to the goal.
- The identified skills should not exceed 10 in number, as less is more in this context.
- Ensure that the output is clear, focused, and includes only the most critical skill gaps necessary for achieving the goal.
- You possess excellent reasoning skills. When evaluating the learner's information, even if certain skills are not explicitly mentioned, you can infer their current proficiency based on the context provided. Avoid assuming these skills are unlearned without applying logical reasoning.
"""

skill_gap_identifier_system_prompt_cot = """
Chain of Thoughts for Task A

1.	Break Down the Learner's Goal into Key Objectives:
•	Analyze the learner's goal to understand its primary objectives.
•	Decompose the goal into specific, actionable objectives or components if it involves multiple aspects. Each objective should represent a measurable step toward achieving the overall goal.
2.	Identify Required Skills for Each Objective:
•	For each objective, identify specific skills that directly support its accomplishment. These skills should be actionable and goal-specific, not general abilities.
•	Consider both technical and essential soft skills that are directly relevant to each objective, avoiding broad or unrelated skills.
3.	Determine Required Proficiency Levels:
•	For each identified skill, specify the proficiency level necessary for the learner to accomplish the goal. Use “beginner,” “intermediate,” or “advanced” levels based on the complexity and demands of the objective.
•	Base proficiency levels on the degree of mastery expected to effectively complete the task tied to the goal.
4.	Rethink the additional necessary skills and proficiency levels and place them in the task titled "Additional Skills" in tracks.
•	Identify additional skills that are not directly related to the key objectives but are essential for the learner to achieve the goal.
•	Specify the required proficiency level for each additional skill.

Task B: Gap Identification
Identify skill gaps by comparing the learner's current skills with the skills identified in Skill Mapping.
"""
skill_gap_identifier_dirgen_system_prompt = skill_gap_identifier_system_prompt_base + skill_gap_identifier_system_prompt_requirements
skill_gap_identifier_cot_system_prompt = skill_gap_identifier_system_prompt_base + skill_gap_identifier_system_prompt_cot + skill_gap_identifier_system_prompt_requirements
skill_gap_identifier_system_prompt = skill_gap_identifier_cot_system_prompt

skill_gap_identifier_task_prompt_goal2skill = """
Task A: Goal-to-Skill Mapping

Using the learner's goal, identify the essential skills required to achieve it.

- Learning goal: {learning_goal}

SKILL_REQUIREMENTS_OUTPUT_FORMAT
"""
skill_gap_identifier_task_prompt_goal2skill = skill_gap_identifier_task_prompt_goal2skill.replace("SKILL_REQUIREMENTS_OUTPUT_FORMAT", cot_skill_requirements_output_format_with_title)

skill_gap_identifier_task_prompt_goal2skill_reflexion = """
Task A: Goal-to-Skill Mapping - Reflexion

Refine the goal-to-skill mapping based on the feedback and suggestions provided.

- Learning goal: {learning_goal}
- Previous Mapped skills: {skill_requirements}
- Feedback and Suggestions: {feedback}

The number of skill requirements should be within [1, 10].

SKILL_REQUIREMENTS_OUTPUT_FORMAT
"""
skill_gap_identifier_task_prompt_goal2skill_reflexion = skill_gap_identifier_task_prompt_goal2skill_reflexion.replace("skill_requirements_output_format", cot_skill_requirements_output_format_with_title)

skill_gap_identifier_task_prompt_identification = """
Task B: Skill Gap Identification

Identify the skill gaps by comparing the learner's current skill levels with the essential skills required to achieve their goal.

- Learning goal: {learning_goal}
- learner information: {learner_information}
- Mapped necessary skills: {skill_requirements}

SKILL_GAP_OUTPUT_FORMAT
"""
skill_gap_identifier_task_prompt_identification = skill_gap_identifier_task_prompt_identification.replace("SKILL_GAP_OUTPUT_FORMAT", cot_skill_gap_output_format_with_title)

skill_gap_identifier_task_prompt_identification_reflexion = """
Task B: Skill Gap Identification - Reflexion

Refine the identified skill gaps based on the feedback and suggestions provided.

- Learning goal: {learning_goal}
- learner information: {learner_information}
- Mapped necessary skills: {skill_requirements}
- Previous Identified skill gaps: {identified_skill_gaps}
- Feedback and Suggestions: {feedback}

SKILL_GAP_OUTPUT_FORMAT
"""
skill_gap_identifier_task_prompt_identification_reflexion = skill_gap_identifier_task_prompt_identification_reflexion.replace("SKILL_GAP_OUTPUT_FORMAT", cot_skill_gap_output_format_with_title)


learning_goal_refiner_system_prompt = """
You are the Learning Goal Refiner in an Intelligent Tutoring System. 
Your role is to subtly enhance broad or vague learner goals to make them clearer and more actionable, while preserving the learner's original intent.
You are only refining the learning goal and do not need to consider specific skills or gaps.

**Requirements:**
- Aim to keep the essence of the learner's goal intact, making only minimal adjustments to improve clarity and specificity.
- Ensure the refined goal remains actionable and realistically achievable within the given context.
- Avoid introducing new objectives or changing the goal's scope significantly.
- Output in valid JSON format, without any tags (e.g., `json`) or additional information.
- Focus solely on clarifying the goal, without adding details on learning timelines or resources.
"""

learning_goal_refiner_task_prompt = """
Refine the learner's learning goal:

- Original Learning Goal: {learning_goal}
- Learner Information: {learner_information}

REFINED_LEARNING_GOAL_OUTPUT_FORMAT
"""
learning_goal_refiner_task_prompt = learning_goal_refiner_task_prompt.replace("REFINED_LEARNING_GOAL_OUTPUT_FORMAT", refined_learning_goal_output_format_with_title)


from .basic_templetes import output_format_requirements_templete

task_prompt_vars = [var_name for var_name in globals() if "task_prompt" in var_name]
for var_name in task_prompt_vars:
    globals()[var_name] += output_format_requirements_templete