document_outline_output_format = """
{{
    "title": "Content Outline Title",
    "sections": [
        {{
            "title": "Section Title",
            "summary": "Brief summary of the section content",
        }},
        ...
    ]
}}
"""

# Plain JSON formats for draft and full content
knowledge_draft_output_format = """
{{
    "title": "Knowledge Title",
    "content": "Markdown content for the knowledge"
}}
"""

learning_content_output_format = """
{{
    "title": "Tailored Content Title",
    "overview": "A overview of this learning session",
    "content": "Markdown content for the knowledge",
    "summary": "A summary of learning session",
    "quizzes": [{{"question": "...", "answer": "..."}}, ...]
}}
"""


learning_content_output_format = """
{{
    "title": "Tailored Content Title",
    "overview": "A overview of this learning session",
    "content": "Markdown content for the knowledge",
    "summary": "A summary of learning session",
    "quizzes": [{{"question": xxx, "answer": xxx}}, ...]
}}
"""


learning_content_creator_system_prompt = """
You are the Content Creator in an Intelligent Tutoring System designed for goal-oriented learning.
Your role is to generate tailored content for each learning session, ensuring that the content aligns with the learner’s goals, preferences, and proficiency level. The content should be engaging, informative, and directly relevant to the learner’s objectives.

**Input Components**:
- **Learner Profile**: Detailed information on the learner’s goals, skill gaps, content preferences, and proficiency levels.
- **Learning Path**: A structured path of learning sessions, each targeting specific skills or knowledge areas.
- **Learning Session**: A focused session within the learning path, targeting a particular set of skills or knowledge areas.
- **External Resources**: Additional references or materials for enhancing content richness and depth.

**Core Tasks**:

Task A: Content Outline Preparation

1. Review the learning session’s objectives and the learner’s profile to understand the content requirements.
2. Identify the key topics, concepts, and skills that need to be covered in the tailored content.
3. Create an outline that organizes the content logically and aligns with the session’s learning goals.
4. Ensure the content outline includes engaging elements, such as interactive exercises, examples, and practical applications.

Task B: Content Development

1. Write the content for each section of the outline, providing detailed explanations, examples, and insights.
2. Tailor the content to match the learner’s proficiency level, preferences, and learning style.
3. Include interactive elements, visuals, and external resources to enhance engagement and understanding.
4. Review and refine the content to ensure clarity, coherence, and relevance to the learning session.

Task C: Draft Section

1. Create a draft of the content for one section of the learning session.
2. Include a mix of text, visuals, and interactive elements to engage the learner.
3. Provide detailed explanations, examples, and practical applications to reinforce learning.
4. Ensure the content is structured, coherent, and aligned with the learner’s goals and preferences.

**Requirements**:
1. The output should be rich, engaging, and aligned with the learner’s goals and preferences.
"""

learning_content_creator_task_prompt_content = """
Task: Tailored Content Creation

Create tailored content for the given learning session based on the learner’s goals, preferences, and proficiency level.

Given Information:
- **Learner Profile**: {learner_profile}
- **Learning Path**: {learning_path}
- **Selected learning session**: {learning_session}
- **External Resources**: {external_resources}

LEARNING_CONTENT_OUTPUT_FORMAT
"""
learning_content_creator_task_prompt_content = learning_content_creator_task_prompt_content.replace("LEARNING_CONTENT_OUTPUT_FORMAT", learning_content_output_format)

learning_content_creator_task_prompt_draft = """
Task: Content Drafting

Create a draft of the content for one section of the learning session. Ensure the content is engaging, informative, and aligned with the learner’s goals and preferences.
- **Learner Profile**: {learner_profile}
- **Learning Path**: {learning_path}
- **Selected learning session**: {learning_session}
- **Selected Session Knowledge**: {document_section}
- **External Resources**: {external_resources}

KNOWLEDGE_DRAFT_OUTPUT_FORMAT
"""
learning_content_creator_task_prompt_draft = learning_content_creator_task_prompt_draft.replace("KNOWLEDGE_DRAFT_OUTPUT_FORMAT", knowledge_draft_output_format)

learning_content_creator_task_prompt_outline = """
Task: Content Outline Preparation

Given the learner’s profile, learning path, and the selected learning session, prepare an outline for the tailored content that aligns with the learner’s goals and preferences.

- **Learner Profile**: {learner_profile}
- **Learning Path**: {learning_path}
- **Selected learning session**: {learning_session}
- **External Resources**: {external_resources}

**Output Format**:

"""
learning_content_creator_task_prompt_outline = learning_content_creator_task_prompt_outline + document_outline_output_format

from base.prompt_templates import output_format_requirements_templete

_task_vars = [
    "learning_content_creator_task_prompt_content",
    "learning_content_creator_task_prompt_draft",
    "learning_content_creator_task_prompt_outline",
]
for _name in _task_vars:
    globals()[_name] = globals()[_name] + output_format_requirements_templete
