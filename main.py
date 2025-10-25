import ast
import json
import time
import uvicorn
import hydra
from omegaconf import DictConfig
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from base.llm_factory import LLMFactory
from utils.preprocess import extract_text_from_pdf
from fastapi.responses import JSONResponse
from modules.skill_gap_identification import *
from modules.adaptive_learner_modeling import *
from modules.personalized_resource_delivery.learning_path_scheduler import *
from modules.personalized_resource_delivery.tailored_content_creator import *

from prompts.ai_tutor_chatbot import ai_tutor_chatbot_system_prompt
from base.schemas import *


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_CFG: DictConfig | None = None

def get_llm(model_provider: str | None = None, model_name: str | None = None, **kwargs):
    # Prefer provided args; fall back to Hydra config if available; else final hard defaults
    global _CFG
    if _CFG is not None:
        model_provider = model_provider or _CFG.get("llm", {}).get("provider")
        model_name = model_name or _CFG.get("llm", {}).get("model_name")
    model_provider = model_provider or "deepseek"
    model_name = model_name or "deepseek-chat"
    return LLMFactory.create(model=model_name, model_provider=model_provider, **kwargs)

UPLOAD_LOCATION = "/mnt/datadrive/tfwang/code/llm-mentor/data/cv/"


@app.post("/chat-with-tutor")
async def chat_with_autor(request: ChatWithAutorRequest):
    llm = get_llm(request.model_provider, request.model_name)
    # convert request.messages (str) to list of dict
    learner_profile = request.learner_profile
    system_message = [{"role": "system", "content": ai_tutor_chatbot_system_prompt+learner_profile}]
    try:
        # Check if request.messages is a valid JSON string
        if isinstance(request.messages, str) and request.messages.strip().startswith("["):
            converted_messages = ast.literal_eval(request.messages)
        else:
            print("Error: request.messages is not in the correct JSON format.")
            # Optionally, set a default or handle it as needed
            converted_messages = [{"error": "Invalid format"}]
        chat_messages = system_message + converted_messages
        try:
            response = llm.invoke(chat_messages).content
            return {"response": response}
        except Exception as e:
            return JSONResponse(status_code=500, content={"detail": str(e)})

    except json.JSONDecodeError as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})

@app.post("/refine-learning-goal")
async def refine_learning_goal(request: LearningGoalRefinementRequest):
    llm = get_llm(request.model_provider, request.model_name)
    try:
        refined_learning_goal = refine_learning_goal_with_llm(llm, request.learning_goal, request.learner_information)
        return {"refined_learning_goal": refined_learning_goal}
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})

@app.post("/identify-skill-gap-with-info")
async def identify_skill_gap_with_info(request: SkillGapIdentificationRequest):
    llm = get_llm(request.model_provider, request.model_name)
    learning_goal = request.learning_goal
    learner_information = request.learner_information
    skill_requirements = request.skill_requirements
    method_name = request.method_name
    try:
        skill_gap, skill_requirements = identify_skill_gap_with_llm(llm, learning_goal, learner_information, skill_requirements, method_name)
        return {"skill_gap": skill_gap, "skill_requirements": skill_requirements}
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})


@app.post("/identify-skill-gap")
async def identify_skill_gap(goal: str = Form(...), cv: UploadFile = File(...), model_provider: str = Form("deepseek"), model_name: str = Form("deepseek-chat")):
    llm = get_llm(model_provider, model_name)
    skill_gap_identifier = SkillGapIdentifier(llm)
    try:
        file_location = f"{UPLOAD_LOCATION}{cv.filename}"
#         with open(file_location, "wb") as file_object:
#             file_object.write(await cv.read())
        with open(file_location, "wb") as file_object:
            file_object.write(await cv.read())
        # print(file_location)
        cv_text = extract_text_from_pdf(file_location)  
        skill_requirements = skill_gap_identifier.map_goal_to_skill({
            "learning_goal": goal
        })
        skill_gap = skill_gap_identifier.identify_skill_gap({
            "learning_goal": goal,
            "skill_requirements": skill_requirements,
            "learner_information": cv_text
        })
        return {"skill_gap": skill_gap, "skill_requirements": skill_requirements}
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})

@app.post("/create-learner-profile-with-info")
async def create_learner_profile_with_info(request: LearnerProfileInitializationWithInfoRequest):
    llm = get_llm(request.model_provider, request.model_name)
    learner_information = request.learner_information
    learning_goal = request.learning_goal
    skill_gap = request.skill_gap
    method_name = request.method_name
    try:
        learner_profile = initialize_learner_profile_with_llm(llm, learning_goal, learner_information, skill_gap, method_name)
        return {"learner_profile": learner_profile}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/create-learner-profile")
async def create_learner_profile(request: LearnerProfileInitializationRequest):
    llm = get_llm(request.model_provider, request.model_name)
    file_location = f"{UPLOAD_LOCATION}{request.cv_path}"
    learner_information = extract_text_from_pdf(file_location)
    learning_goal = request.learning_goal
    skill_gap = request.skill_gap
    try:
        learner_profile = initialize_learner_profile_with_llm(llm, learning_goal, learner_information, skill_gap)
        return {"learner_profile": learner_profile}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/update-learner-profile")
async def update_learner_profile(request: LearnerProfileUpdateRequest):
    llm = get_llm(request.model_provider, request.model_name)
    learner_profile = request.learner_profile
    learner_interactions = request.learner_interactions
    learner_information = request.learner_information
    session_information = request.session_information
    try:
        learner_profile = update_learner_profile_with_llm(llm, learner_profile, learner_interactions, learner_information, session_information)
        return {"learner_profile": learner_profile}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/schedule-learning-path")
async def schedule_learning_path(request: LearningPathSchedulingRequest):
    llm = get_llm(request.model_provider, request.model_name)
    learner_profile = request.learner_profile
    session_count = request.session_count
    method_name = request.method_name
    try:
        learning_path = schedule_learning_path_with_llm(llm, learner_profile, session_count, method_name)
        return {"learning_path": learning_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reschedule-learning-path")
async def reschedule_learning_path(request: LearningPathReschedulingRequest):
    llm = get_llm(request.model_provider, request.model_name)
    learner_profile = request.learner_profile
    learning_path = request.learning_path
    session_count = request.session_count
    other_feedback = request.other_feedback
    try:
        learning_path = reschedule_learning_path_with_llm(llm, learner_profile, learning_path, session_count, other_feedback)
        return {"rescheduled_learning_path": learning_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/explore-knowledge-points")
async def explore_knowledge_points(request: KnowledgePointExplorationRequest):
    llm = get_llm(request.model_provider, request.model_name)
    learner_profile = request.learner_profile
    learning_path = request.learning_path
    learning_session = request.learning_session
    try:
        knowledge_points = explore_knowledge_points_with_llm(llm, learner_profile, learning_path, learning_session)
        return {"knowledge_points": knowledge_points}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/draft-knowledge-point")
async def draft_knowledge_point(request: KnowledgePointDraftingRequest):
    llm = get_llm(request.model_provider, request.model_name)
    learner_profile = request.learner_profile
    learning_path = request.learning_path
    learning_session = request.learning_session
    knowledge_points = request.knowledge_points
    knowledge_point = request.knowledge_point
    use_search = request.use_search
    try:
        knowledge_draft = draft_knowledge_point_with_llm(llm, learner_profile, learning_path, learning_session, knowledge_points, knowledge_point, use_search)
        return {"knowledge_draft": knowledge_draft}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/draft-knowledge-points")
async def draft_knowledge_points(request: KnowledgePointsDraftingRequest):
    llm = get_llm(request.model_provider, request.model_name)
    learner_profile = request.learner_profile
    learning_path = request.learning_path
    learning_session = request.learning_session
    knowledge_points = request.knowledge_points
    use_search = request.use_search
    allow_parallel = request.allow_parallel
    try:
        knowledge_drafts = draft_knowledge_points_with_llm(llm, learner_profile, learning_path, learning_session, knowledge_points, allow_parallel, use_search)
        return {"knowledge_drafts": knowledge_drafts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/integrate-learning-document")
async def integrate_learning_document(request: LearningDocumentIntegrationRequest):
    llm = get_llm(request.model_provider, request.model_name)
    learner_profile = request.learner_profile
    learning_path = request.learning_path
    learning_session = request.learning_session
    knowledge_points = request.knowledge_points
    knowledge_drafts = request.knowledge_drafts
    output_markdown = request.output_markdown
    try:
        learning_document = integrate_learning_document_with_llm(llm, learner_profile, learning_path, learning_session, knowledge_points, knowledge_drafts, output_markdown)
        return {"learning_document": learning_document}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-document-quizzes")
async def generate_document_quizzes(request: KnowledgeQuizGenerationRequest):
    llm = get_llm(request.model_provider, request.model_name)
    learner_profile = request.learner_profile
    learning_document = request.learning_document
    single_choice_count = request.single_choice_count
    multiple_choice_count = request.multiple_choice_count
    true_false_count = request.true_false_count
    short_answer_count = request.short_answer_count
    try:
        document_quiz = generate_document_quizzes_with_llm(llm, learner_profile, learning_document, single_choice_count, multiple_choice_count, true_false_count, short_answer_count)
        return {"document_quiz": document_quiz}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tailor-knowledge-content")
async def tailor_knowledge_content(request: TailoredContentGenerationRequest):
    llm = get_llm(request.model_provider, request.model_name)
    learning_path = request.learning_path
    learner_profile = request.learner_profile
    learning_session = request.learning_session
    use_search = request.use_search
    allow_parallel = request.allow_parallel
    with_quiz = request.with_quiz
    method_name = request.method_name

    try:
        tailored_content = create_learning_content_with_llm(llm, learner_profile, learning_path, learning_session, allow_parallel, with_quiz, use_search, method_name)
        return {"tailored_content": tailored_content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@hydra.main(config_path="config", config_name="ppo_trainer", version_base=None)
def _hydra_main(cfg: DictConfig) -> None:
    """Hydra entrypoint to run the FastAPI app with config-driven settings."""
    global _CFG
    _CFG = cfg
    server_cfg = cfg.get("server", {}) if hasattr(cfg, "get") else {}
    host = server_cfg.get("host", "127.0.0.1")
    port = int(server_cfg.get("port", 5000))
    log_level = str(cfg.get("log_level", "debug")).lower()
    uvicorn.run(app, host=host, port=port, log_level=log_level)


if __name__ == "__main__":
    _hydra_main()


# Run using uvicorn, for example:
# uvicorn main:app --reload
# Replace 'main' with the name of your file if different.