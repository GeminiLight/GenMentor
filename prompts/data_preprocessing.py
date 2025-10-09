from .basic_templetes import output_format_title_templete


job_posting_extractor_output_format = """
{{
  "job_title": "<Job Title>",
  "job_type": "<Job Type>",
  "job_description": "<Job Description>",
  "skill_requirements": [
    {{
        "name": "<Skill Name>",
        "level": "<Skill Level>"
    }},
  ]
}}
"""
job_posting_extractor_output_format_with_title = output_format_title_templete + job_posting_extractor_output_format



job_posting_extractor_system_prompt = """
You are given a raw job posting containing job title, job type, job description, and skill requirements. Your task is to transform the job description into a goal-oriented statement that avoids addressing the reader directly with “You.” Instead, focus on the responsibilities and objectives of the role. Extract the information in the following format:
	1.	Title: Extract only the job title.
	2.	Job Type: Classify the job type based on the provided options.
        •	Marketing Strategy
        •	Engineering and IT Innovation
        •	Project Operations
        •	Academic Research
        •	Creative Design
        •	Legal Compliance
        •	Healthcare Counseling
        •	Human Resources
        •	Clinical Services
        •	Financial Accounting
	3.	Job Description: 
    - Rewrite the description as a goal-oriented, third-person statement focused on role objectives and responsibilities.
    - Should be concise, clear, and core responsibilities, max word count: 100 words.
	4.	Skill Requirements: 
    - Merely include core technical and soft skills, excluding meaningless skills like “Multitasking”, Supervision, or “Prioritization,”. Ignore the inrelevant and non-core skills.
    - Specify each skill level, select one from “beginner,” “intermediate,” or “advanced.”

Requirements:
•	Output should be formatted strictly in JSON.
•	Do not include any additional information, commentary, or tags, such ```.
•	Ensure only the requested fields are included, without any extra details or formatting.
•	When extracting skills, omit any text in parentheses or “e.g.” examples.
•	When extracting skills, include only those relevant to the job, omitting general attributes such as “Multitasking” and “Prioritization.”
- The level of skills should be one of the following: “beginner,” “intermediate,” or “advanced.”
"""

job_posting_extractor_task_prompt = """
Given the following job posting, extract the job title, job type, job description, and skill requirements.
{job_posting}

JOB_POSTING_EXTRACTION_OUTPUT_FORMAT
"""
job_posting_extractor_task_prompt = job_posting_extractor_task_prompt.replace("JOB_POSTING_EXTRACTION_OUTPUT_FORMAT", job_posting_extractor_output_format)

goal2skill_cot_completor_system_prompt = """
You are given a raw job posting that includes information such as job title, job description, and required skills. 
The goal is to transform the job description into a goal-oriented structure by breaking down high-level responsibilities into actionable tasks and associating each task with relevant skills. 
Use the following Chain of Thought (CoT) steps to clarify the connection between the job’s objectives and skill requirements.
Please ensure the skills are nessary and core to the job role and professional goal.

Follow these steps to produce the desired output format:

Chain of Thought (CoT) Reasoning Steps:

	1.	Identify High-Level Goals:
	•	Read the job description and identify the main objectives or overarching goals for the role. These goals capture the primary outcomes the role is expected to achieve within the organization.
	2.	Break Down Goals into Key Tasks:
	•	For each goal, identify specific, actionable tasks that the role would regularly perform to accomplish these objectives. Each task should be a concrete action linked to the job’s high-level responsibilities.
	3.	Map Tasks to Core Skills:
	•	For each identified task, determine the technical or soft skills required to execute it effectively. Exclude general attributes like “Multitasking” or “Prioritization” unless they are contextually essential.
	4.	Identify Skill Levels:
	•	Specify the required proficiency level (e.g., “Beginner,” “Intermediate,” “Advanced”) for each skill based on task complexity and job requirements.
	5.	Structure Output:
	•	Organize the tasks, associated skills, and skill levels into a JSON format that maps each task to the skills it requires.

Desired Output Format:

Your output should be formatted as follows:

{{
  "tracks": [
    {{
      "task": "<Key Task Title 1>",
      "skills": [
        {{ "skill": "<Skill 1>", "level": "<Skill Level>", "relation": "<Relation to Task>" }},
      ]
    }},
    {{
      "task": "<Key Task Title 2>",
      "skills": [
        {{ "skill": "<Skill 3>", "level": "<Skill Level>", "relation": "<Relation to Task>" }},
        {{ "skill": "<Skill 4>", "level": "<Skill Level>", "relation": "<Relation to Task>" }},
      ]
    }}
  ]
}}

Example Input:
Job Title: Marketing Coordinator  
Job Description: "Oversees brand strategy, coordinates marketing requests, prepares materials, and manages event planning and promotion."
Skill Requirements: [
    {{ "skill": "Brand Strategy Management", "level": "Intermediate" }},
    {{ "skill": "Content Development", "level": "Intermediate" }},
    {{ "skill": "Project Coordination", "level": "Intermediate" }},
    {{ "skill": "Adobe Creative Cloud", "level": "Intermediate" }},
    {{ "skill": "Graphic Design", "level": "Intermediate" }},
    {{ "skill": "Event Planning", "level": "Intermediate" }},
    {{ "skill": "Organizational Skills", "level": "Intermediate" }}
]

Example Output:

Following the CoT steps, the output should look like this:

{{
    "tracks": [
    {{
      "task": "Manage brand strategy and messaging",
      "skills": [
        {{ "skill": "Brand Strategy Management", "level": "Intermediate", "relation": "It is ... (max 20 words)" }},
        {{ "skill": "Content Development", "level": "Intermediate", "relation": "It is ... (max 20 words)" }},
      ]
    }},
    {{
      "task": "Coordinate marketing requests from agents",
      "skills": [
        {{ "skill": "Project Coordination", "level": "Intermediate", "relation": "It is ... (max 20 words)" }},
      ]
    }},
    {{
      "task": "Prepare print and digital materials",
      "skills": [
        {{ "skill": "Adobe Creative Cloud", "level": "Intermediate", "relation": "It is ... (max 20 words)" }},
        {{ "skill": "Graphic Design", "level": "Intermediate", "relation": "It is ... (max 20 words)" }},
      ]
    }},
    {{
      "task": "Plan and execute promotional events",
      "skills": [
        {{ "skill": "Event Planning", "level": "Intermediate", "relation": "It is ... (max 20 words)" }},
        {{ "skill": "Organizational Skills", "level": "Intermediate", "relation": "It is ... (max 20 words)" }},
      ]
    }}
  ]
}}

Requirements:

	•	Use the CoT steps outlined above to produce the output.
	•	Ensure the output strictly follows the JSON format, with each task paired with relevant skills and skill levels.
	•	Do not include any additional information, commentary, or tags, such ```.
	•	Exclude general attributes like “Multitasking” and “Prioritization” unless explicitly relevant to the task.
"""

goal2skill_cot_completor_task_prompt = """
You are provided with a job posting that contains a job title, job description, and a list of required skills. Your task is to transform this information into a structured, goal-oriented output using the Chain of Thought (CoT) reasoning steps provided. Follow each step carefully to break down high-level responsibilities, extract actionable tasks, and associate each task with necessary and core skills.

Ensure that:

	•	Only essential skills directly related to achieving the job’s goals are selected.
	•	Each skill is assigned an appropriate proficiency level based on the job requirements.
	•	The output is organized in a JSON format with two main components: “tracks” and “skills.”

In “tracks,” outline each task with its associated skills and proficiency levels. 
In “skills,” list each skill with its proficiency level. U
se the example provided as a guide to structure your output correctly. 
Aim for accuracy and clarity to ensure the goal-to-skill relationships are effectively captured.

Given:
Job Title: {job_title}
Job Description: {job_description}
Skill Requirements: {skill_requirements}
"""



from .basic_templetes import output_format_requirements_templete

task_prompt_vars = [var_name for var_name in globals() if "task_prompt" in var_name]
for var_name in task_prompt_vars:
    globals()[var_name] += output_format_requirements_templete