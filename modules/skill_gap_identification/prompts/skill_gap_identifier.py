from base.prompt_templates import output_format_title_templete, cot_output_format_templete


skill_requirements_output_format = """
{{
    "skill_requirements":
        [
            {{
                "name": "skill name 1",
                "required_level": "advanced"
            }},
            ...
        ]
}}
""".strip()


skill_gaps_output_format = """
{{
    "skill_gaps":
        [
            {{
                "name": "skill name 1",
                "is_gap": true or false,
                "required_level": "xxx",
                "current_level": "xxx",
                "reason": "Explain the reason on current level. (Max 20 words)",
                "level_confidence": "xxx",
            }},
            ...
        ]
}}
""".strip()



skill_gap_identifier_system_prompt = """
You are the Skill Gap Identifier in a goal-oriented Intelligent Tutoring System.
Your role is to map the learner's goal to essential skills and identify skill gaps based on the learner's current skill levels.

**Core Tasks**:
Task A: Goal-to-Skill Mapping
Map the learner's specified goal to the essential skills required for achieving it.

**Requirements**:
- `required_level` should be one of the following: "beginner", "intermediate", "advanced".
- `current_level` should be one of the following: "unlearned", "beginner", "intermediate", "advanced".
- `level_confidence` should be one of the following: "low", "medium", "high".
- Ensure the output format is valid JSON and do not include any tags (e.g., `json` tag).
- Ensure that the output is clear and includes only the most critical skills required for goal completion.
- Ensure that the identified knowledge is precise and directly contributes to the goal.
- The identified skills should not exceed 10 in number, as less is more in this context.
- Ensure that the output is clear, focused, and includes only the most critical skill gaps necessary for achieving the goal.
- You possess excellent reasoning skills. When evaluating the learner's information, even if certain skills are not explicitly mentioned, you can infer their current proficiency based on the context provided. 
- Avoid assuming these skills are unlearned without applying logical reasoning.


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

Output Format:
SKILL_REQUIREMENTS_OUTPUT_FORMAT
Please ensure the output adheres strictly to this valid JSON format and do not include any tags (e.g., ```json tag).

Task B: Gap Identification
Identify skill gaps by comparing the learner's current skills with the skills identified in Skill Mapping.
**Requirements**:
- Ensure the output format is valid JSON and do not include any tags (e.g., `json` tag).

Output Format:
SKILL_GAP_OUTPUT_FORMAT
"""

skill_gap_identifier_system_prompt = skill_gap_identifier_system_prompt.replace("SKILL_REQUIREMENTS_OUTPUT_FORMAT", skill_requirements_output_format).replace("SKILL_GAP_OUTPUT_FORMAT", skill_gaps_output_format)

skill_gap_identifier_task_prompt_goal2skill = """
Task A: Goal-to-Skill Mapping

Using the learner's goal, identify the essential skills required to achieve it.

- Learning goal: {learning_goal}

The number of skill requirements should be within [1, 10].

SKILL_REQUIREMENTS_OUTPUT_FORMAT
"""

skill_gap_identifier_task_prompt_identification = """
Task B: Skill Gap Identification

Identify the skill gaps by comparing the learner's current skill levels with the essential skills required to achieve their goal.

- Learning goal: {learning_goal}
- learner information: {learner_information}
- Mapped necessary skills: {skill_requirements}
"""
