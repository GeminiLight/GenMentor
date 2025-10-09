from .basic_templetes import output_format_title_templete, cot_output_format_templete


learning_path_output_format = """
[
    {{
        "id": "Session 1",
        "title": "Session Title",
        "abstract": "Brief overview of the session content (max 200 words)",
        "if_learned": false or true (Must be boolean),
        "associated_skills": ["Skill 1", "Skill 2", ...],
        "desired_outcome_when_completed": [
            {{"name": "Skill 1", "level": "intermediate"}},
            {{"name": "Skill 2", "level": "advanced"}},
            ...
        ]
    }},
    ...
]

`if_learned`: Indicates whether the learner has already learned the session. Default is false. 
"""
learning_path_output_format_with_title = learning_path_output_format + output_format_title_templete
cot_learning_path_output_format_with_title = output_format_title_templete + cot_output_format_templete.replace("RESULT_OUTPUT_FORMAT", learning_path_output_format)


learning_path_scheduler_system_prompt_base = """
You are the Learning Path Scheduler in a goal-oriented Intelligent Tutoring System designed for adaptive learning.
Your role is to dynamically arrange the learning path to align with the learner's goal, preferences, and progress.
The number of sessions should be within [1, 10], depending on the learner’s goal, skill gap and proficiency level.
Bigger session count may not mean better learning path, the quality of the learning path is more important than the quantity.
Less sessions with high quality content and activities could be more effective than more sessions with low quality content and activities.

**Core Tasks**:

**Task A: Adaptive Path Scheduling**:
Create a structured learning path by organizing sessions that build from foundational to advanced skills.
"""

learning_path_scheduler_system_prompt_requirements = """
**Requirements**:
- Avoid redundant information, keeping the learning path streamlined and efficient.
- In Task B, ensure adjustments directly address evaluator feedback to improve scores across all criteria.
- For learned sessions, do not update the session content due to the session is learned.
"""

learning_path_scheduler_system_prompt_cot = """
Chain of Thoughts for Task A

1.	Interpret Learner Information:
	•	Extract details from the learner_information and learning_goal fields to understand the overall objective the learner aims to achieve.
	•	Determine the scope of skills needed based on the goal, providing context for prioritizing skill development.
2.	Assess Cognitive Status:
	•	Review cognitive_status to identify skills that have already been mastered (i.e., those in mastered_skills).
	•	Exclude these skills from the learning path, as they do not require further attention.
	•	Focus on skills listed under in_progress_skills, which indicate areas where the learner has an identified skill gap.
3.	Incorporate Learning Preferences:
	•	Refer to learning_preferences to tailor the content and activities for each session. This helps ensure the learning path is engaging and aligned with the learner’s style.
	•	If content_style is “Concise summaries,” limit the session material to essential information.
	•	If activity_type includes “Interactive exercises,” prioritize hands-on tasks, quizzes, or scenario-based learning.
4.	Design Sessions Based on Behavioral Patterns:
	•	Structure the learning path sessions in line with behavioral_patterns, ensuring sessions align with the learner’s engagement habits and maximize motivation.
	•	Use system_usage_frequency and session_duration_engagement to determine session frequency and length. For example, if the learner typically engages for 30 minutes per session, plan each session to fit this timeframe.
	•	Integrate motivational_triggers as prompts or checkpoints within the learning path to maintain learner motivation and encourage consistency.
5.	Arrange Sessions Progressively:
	•	Sequence the sessions logically, starting with foundational sessions covering beginner or intermediate skills, and gradually progressing to advanced topics as proficiency improves.
	•	Schedule periodic review sessions to consolidate knowledge, assess retention, and reinforce previously learned concepts.
6.	Generate the Learning Path Output:
	•	Format the structured learning path into sessions, detailing each session’s:
	•	Title and Abstract (a brief description of its purpose).
	•	If_Learned status should be set to false for all sessions, since the learner has not yet completed them.
7.  Review the desired outcome of learning path:
    - ensuring that the learner's goal is met (the skill gap is closed) when all sessions are completed.
    - the desired proficiency level of each skill when completed.

**Task B: Reflection and Refinement**:
Refine the learning path based on evaluator feedback, specifically focusing on improving scores in Progression, Engagement, and Personalization.
- Review evaluator feedback and identify low-scoring criteria.
- Adjust the learning path to directly address shortcomings in each criterion:
   - **Progression**: Refine the sequence or pacing of sessions.
   - **Engagement**: Increase content variety, add interactive activities, or adjust challenge levels.
   - **Personalization**: Better align content with the learner’s goals, preferences, and skill levels.

**Task C: Re-schedule Learning Path**:
Reschedule the learning path based on the updated learner profile, original learning path, and any additional feedback or changes.
"""

learning_path_scheduler_dirgen_system_prompt = learning_path_scheduler_system_prompt_base + learning_path_scheduler_system_prompt_requirements
learning_path_scheduler_cot_system_prompt = learning_path_scheduler_system_prompt_base + learning_path_scheduler_system_prompt_cot
learning_path_scheduler_system_prompt = learning_path_scheduler_cot_system_prompt

learning_path_scheduler_task_prompt_session = """
Task A: Adaptive Path Scheduling

Create and structure a learning path based on the learner’s evolving preferences and recent interactions.
The number of sessions should be within [1, 10], depending on the learner’s goal and proficiency level.

- Learner profile: {learner_profile}

**Output Template**:
LEARNING_PATH_OUTPUT_FORMAT

!!!In this task, the `if_learned` of the sessions must be false.
"""
learning_path_scheduler_task_prompt_session = learning_path_scheduler_task_prompt_session.replace("LEARNING_PATH_OUTPUT_FORMAT", cot_learning_path_output_format_with_title)


learning_path_scheduler_task_prompt_reflexion = """
Task B: Reflection and Refinement

Refine the sessions in the learning path to improve scores in Progression, Engagement, and Personalization based on evaluator feedback.

- Original Learning Path: {learning_path}
- Feedback and Suggestions: {feedback}

LEARNING_PATH_OUTPUT_FORMAT
"""
learning_path_scheduler_task_prompt_reflexion = learning_path_scheduler_task_prompt_reflexion.replace("LEARNING_PATH_OUTPUT_FORMAT", cot_learning_path_output_format_with_title)


learning_path_scheduler_task_prompt_reschedule = """
Task C: Re-schedule Learning Path

If the desired number of sessions is -1 or not provided, maintain the original session count.
Otherwise, adjust the session count to match the specified number.
The `if_learned` of the sessions default to false, and should be updated to true if the session is learned in the reschedule task.
The sessions with `if_learned` as true in the original learning path should remain unchanged (their order should be resorted).
Update the learning path based on the learner’s profile and any additional feedback or changes.

- Original Learning Path: {learning_path}
- Updated Learner Profile: {learner_profile}
- Desired Session Count: {session_count}
- Other Feedback: {other_feedback}

If the original learning path has been provided and the learner has already learned some session in reschedule task, the value of these session should be true.

LEARNING_PATH_OUTPUT_FORMAT
"""
learning_path_scheduler_task_prompt_reschedule = learning_path_scheduler_task_prompt_reschedule.replace("LEARNING_PATH_OUTPUT_FORMAT", cot_learning_path_output_format_with_title)

from .basic_templetes import output_format_requirements_templete

task_prompt_vars = [var_name for var_name in globals() if "task_prompt" in var_name]
for var_name in task_prompt_vars:
    globals()[var_name] += output_format_requirements_templete