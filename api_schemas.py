
from pydantic import BaseModel
from fastapi import File, UploadFile, Form


"""
:TODO: Restrict the input data types to the required ones

messages: dict
learner_profile: dict
llm_type: str

learning_goal: str
learner_information: dict

cv: file

skill_requirements: list
skill_gap: list

session_count: int
other_feedback: str

knowledge_point: dict
perspectives_of_knowledge_point: list
knowledge_perspective: list

drafts_of_perspectives: list

single_choice_count: int
multiple_choice_count: int
true_false_count: int
short_answer_count: int

use_search: bool
allow_parallel: bool
with_quiz: bool

learning_session: dict
knowledge_points: list

learning_document: dict
learning_path: list
"""


class BaseRequest(BaseModel):
    model_provider: str = "deepseek"
    model_name: str = "deepseek-chat"
    method_name: str = "genmentor"


class ChatWithAutorRequest(BaseRequest):

    messages: str
    learner_profile: str = ""


class LearningGoalRefinementRequest(BaseRequest):

    learning_goal: str
    learner_information: str = ""


class Goal2KnowledgePrestrionRequest(BaseRequest):

    learning_goal: str = Form(...),
    cv: UploadFile = File(...)


class SkillGapIdentificationRequest(BaseRequest):

    learning_goal: str
    learner_information: str
    skill_requirements: str = None


class LearnerProfileInitializationWithInfoRequest(BaseRequest):

    learning_goal: str
    learner_information: str
    skill_gap: str


class LearnerProfileInitializationRequest(BaseRequest):

    learning_goal: str
    skill_requirements: str
    skill_gap: str
    cv_path: str


class LearnerProfileUpdateRequest(BaseRequest):

    learner_profile: str
    learner_interactions: str
    learner_information: str = ""
    session_information: str = ""


class LearningPathSchedulingRequest(BaseRequest):

    learner_profile: str
    session_count: int


class LearningPathReschedulingRequest(BaseRequest):
    
    learner_profile: str
    learning_path: str
    session_count: int = -1
    other_feedback: str = ""


class TailoredContentGenerationRequest(BaseRequest):

    learner_profile: str
    learning_path: str
    knowledge_point: str


class KnowledgePerspectiveExplorationRequest(BaseRequest):

    learner_profile: str
    learning_path: str
    knowledge_point: str


class KnowledgePerspectiveDraftingRequest(BaseRequest):

    learner_profile: str
    learning_path: str
    knowledge_point: str
    perspectives_of_knowledge_point: str
    knowledge_perspective: str
    use_search: bool = True


class KnowledgeDocumentIntegrationRequest(BaseRequest):

    learner_profile: str
    learning_path: str
    knowledge_point: str
    perspectives_of_knowledge_point: str
    drafts_of_perspectives: str


class PointPerspectivesDraftingRequest(BaseModel):

    learner_profile: str
    learning_path: str
    knowledge_point: str
    perspectives_of_knowledge_point: str
    use_search: bool
    allow_parallel: bool
 

class KnowledgeQuizGenerationRequest(BaseModel):

    learner_profile: str
    learning_document: str
    single_choice_count: int = 3
    multiple_choice_count: int = 0
    true_false_count: int = 0
    short_answer_count: int = 0


class TailoredContentGenerationRequest(BaseModel):

    learner_profile: str
    learning_path: str
    learning_session: str
    use_search: bool = True
    allow_parallel: bool = True
    with_quiz: bool = True


class KnowledgePointExplorationRequest(BaseModel):
    
    learner_profile: str
    learning_path: str
    learning_session: str


class KnowledgePointDraftingRequest(BaseModel):

    learner_profile: str
    learning_path: str
    learning_session: str
    knowledge_points: str
    knowledge_point: str
    use_search: bool


class KnowledgePointsDraftingRequest(BaseModel):

    learner_profile: str
    learning_path: str
    learning_session: str
    knowledge_points: str
    use_search: bool
    allow_parallel: bool


class LearningDocumentIntegrationRequest(BaseModel):

    learner_profile: str
    learning_path: str
    learning_session: str
    knowledge_points: str
    knowledge_drafts: str
    output_markdown: bool = False
