import ast
from concurrent.futures import ThreadPoolExecutor
import copy
from typing import Optional

from base.base_agent import BaseAgent
from base.deep_research import (
    build_context,
    create_deep_search_pipeline,
    format_docs,
    search_enhanced_rag as run_deep_search,
)
from base.search_rag import SearchRagManager, format_docs
from modules.personalized_resource_delivery.prompts.tailored_content_creation import *
from utils import sanitize_collection_name
from utils.preprocess import save_json


DEFAULT_VECTORSTORE_DIR = './data/vectorstore'
DEFAULT_CHUNK_SIZE = 1000
DEFAULT_NUM_SEARCH_RESULTS = 3
DEFAULT_NUM_RETRIEVAL_RESULTS = 5


# def search_enhanced_rag(
#     query,
#     db_collection_name,
#     db_persist_directory: str = DEFAULT_VECTORSTORE_DIR,
#     num_results: int = DEFAULT_NUM_SEARCH_RESULTS,
#     num_retrieval_results: int = DEFAULT_NUM_RETRIEVAL_RESULTS,
#     *,
#     chunk_size: int = DEFAULT_CHUNK_SIZE,
#     pro_mode: bool = False,
# ):
#     query = str(query)
#     print(f"Searching {query} for external resources...")
#     external_resources = run_deep_search(
#         query=query,
#         db_collection_name=db_collection_name,
#         db_persist_directory=db_persist_directory,
#         num_results=num_results,
#         num_retrieval_results=num_retrieval_results,
#         chunk_size=chunk_size,
#         pro_mode=pro_mode,
#     )
#     print(f"Found {len(external_resources)} external resources.")
#     return external_resources


class LearningContentCreator(BaseAgent):
    def __init__(
        self,
        model,
        use_search: bool = True,
        *,
        search_rag_manager: Optional[SearchRagManager] = None,
        # vectorstore_directory: str = DEFAULT_VECTORSTORE_DIR,
        # num_search_results: int = DEFAULT_NUM_SEARCH_RESULTS,
        # num_retrieval_results: int = DEFAULT_NUM_RETRIEVAL_RESULTS,
        # chunk_size: int = DEFAULT_CHUNK_SIZE,
    ):
        super().__init__(model=model, system_prompt=learning_content_creator_orag_system_prompt, jsonalize_output=True)
        self.use_search = use_search
        self.search_rag_manager = search_rag_manager
        if use_search:
            assert self.search_rag_manager is not None, "search_rag_manager must be provided when use_search is True"

        # self.vectorstore_directory = vectorstore_directory
        # self.num_search_results = num_search_results
        # self.num_retrieval_results = num_retrieval_results
        # self.chunk_size = chunk_size
        # self.search_rag_manager = search_rag_manager or SearchRagManager(
        #     persist_directory=vectorstore_directory,
        #     chunk_size=chunk_size,
        #     default_max_results=num_search_results,
        #     retriever_k=num_retrieval_results,
        # )

    @staticmethod
    def _ensure_mapping(value):
        if isinstance(value, str):
            return ast.literal_eval(value)
        return value

    # def _fetch_external_context(self, query: str, collection_name: str) -> str:
    #     if not self.search_pipeline:
    #         return ''

    #     docs = self.search_pipeline.run(
    #         query,
    #         collection_name,
    #         max_results=self.num_search_results,
    #         k=self.num_retrieval_results,
    #         persist_directory=self.vectorstore_directory,
    #         chunk_size=self.chunk_size,
    #     )
    #     return build_context(docs)

    def create_content(self, input_dict, system_prompt=None, task_prompt=None):
        if system_prompt is None:
            system_prompt = learning_content_creator_system_prompt
        if task_prompt is None:
            task_prompt = learning_content_creator_task_prompt_content
        self.set_prompts(system_prompt, task_prompt)

        input_dict.setdefault('external_resources', '')

        if self.use_search:
            learning_session = self._ensure_mapping(input_dict['learning_session'])
            input_dict['learning_session'] = learning_session
            learning_session_title = str(learning_session.get('title', 'learning_session'))
            if learning_session_title.isnumeric() or len(learning_session_title) < 3:
                learning_session_title = 'learning_session'
            db_collection_name = sanitize_collection_name(learning_session_title)
            retrieved_docs = self.search_rag_manager.invoke(learning_session_title)
            context = format_docs(retrieved_docs)
            if context:
                input_dict['external_resources'] = f"{input_dict['external_resources']}{context}"
        return self.invoke(input_dict, task_prompt=task_prompt)

    def draft_section(self, input_dict):
        if self.use_search:
            learning_session = self._ensure_mapping(input_dict['learning_session'])
            input_dict['learning_session'] = learning_session
            session_title = str(learning_session.get('title', 'learning_session'))
            if session_title.isnumeric() or len(session_title) < 3:
                session_title = 'learning_session'
            section_title = str(input_dict['document_section'])
            query = f"{session_title} {section_title}".strip()
            db_collection_name = sanitize_collection_name(session_title)
            retrieved_docs = self.search_rag_manager.invoke(query)
            context = format_docs(retrieved_docs)
            input_dict['external_resources'] = context
        else:
            input_dict['external_resources'] = ''
        return self.invoke(input_dict, task_prompt=learning_content_creator_task_prompt_draft)

    def create_content_with_outline(self, input_dict):
        document_outline = input_dict['document_outline']
        if isinstance(document_outline, str):
            document_outline = ast.literal_eval(document_outline)
        document_title = document_outline['title']
        document_sections = document_outline['sections']
        document_content = []
        document_content.append(f"# {document_title}")
        for section in document_sections:
            section_title = section['title']
            input_dict['document_section'] = section_title
            input_dict_copy = copy.deepcopy(input_dict)
            section_draft = self.draft_section(input_dict_copy)
            document_content.append(section_draft)
        return document_content

    def prepare_outline(self, input_dict, system_prompt=None, task_prompt=None):
        if task_prompt is None:
            task_prompt = learning_content_creator_task_prompt_outline
        self.set_prompts(system_prompt, task_prompt)
        return self.invoke(input_dict, task_prompt=task_prompt)



class TailoredContentCreator(BaseAgent):
    """
    Talior learning content based on the learner's profile, learning path, and learning session.

    A. Goal-Oriented Exploration: Explore knowledge points of selected learning session
    - Input: Learner Profile, Learning Path, Learning Session
    - Output: Knowledge Points

    B. Search-Enhanced Drafting: Draft perspective of knowledge points
    - Input: Learner Profile, Learning Path, Selected Learning Session, All Knowledge Points, Selected Knowledge Point, External Resources
    - Output: Knowledge Draft

    C. Integration and Refinement: Integrate knowledge drafts into a learning document
    - Input: Learner Profile, Learning Path, Learning Session, Knowledge Points, Drafts of These knowledge Points
    - Output: Learning Document

    D. Document Quiz Generation: Generate a quiz based on the learning document
    - Input: Learner Profile, Learning Document, Number of Single Choice Questions, Number of Multiple Choice Questions, Number of True/False Questions, Number of Short Answer Questions
    - Output: Quiz Questions
    """
    def __init__(self, llm, *, search_pipeline=None):
        super().__init__(model=llm, jsonalize_output=True)
        self.search_pipeline = search_pipeline or create_deep_search_pipeline(
            persist_directory=DEFAULT_VECTORSTORE_DIR,
            chunk_size=DEFAULT_CHUNK_SIZE,
            default_max_results=DEFAULT_NUM_SEARCH_RESULTS,
            retriever_k=DEFAULT_NUM_RETRIEVAL_RESULTS,
        )
        self.goal_oriented_explorer = GoalOrientedKnowledgeExplorer(llm)
        self.search_enhanced_drafter = SearchEnhancedKnowledgeDraftor(
            llm,
            search_pipeline=self.search_pipeline,
            vectorstore_directory=DEFAULT_VECTORSTORE_DIR,
            num_search_results=DEFAULT_NUM_SEARCH_RESULTS,
            num_retrieval_results=DEFAULT_NUM_RETRIEVAL_RESULTS,
            chunk_size=DEFAULT_CHUNK_SIZE,
        )
        self.learning_document_integrator = LearningDocumentIntegrator(llm)
        self.document_quiz_generator = DocumentQuizGenerator(llm)

    def create_content(self, input_dict, system_prompt=None, task_prompt=None):
        """
        Create learning content based on the provided input dictionary.

        Args:
            input_dict (dict): A dictionary containing the following keys:
                - learner_profile (dict): Information about the learner's profile.
                - learning_path (dict): The learning path chosen.
                - learning_session (dict): Data regarding the current learning session.
                - external_resources (str, optional): External resources related to the knowledge point.
                - outline (str, optional): The outline of the learning content.

        Returns:
            dict: A dictionary containing the learning content and quiz questions.
        """
        if task_prompt is None:
            task_prompt = learning_content_creator_task_prompt_content
        return self.invoke(input_dict, task_prompt=task_prompt)

    def prepare_outline(self, input_dict, system_prompt=None, task_prompt=None):
        """
        Prepare the outline of the learning content based on the provided input dictionary.

        Args:
            input_dict (dict): A dictionary containing the following keys:
                - learner_profile (dict): Information about the learner's profile.
                - learning_path (dict): The learning path chosen.
                - learning_session (dict): Data regarding the current learning session.
                - external_resources (str, optional): External resources related to the knowledge point.

        Returns:
            dict: A dictionary containing the outline of the learning content.
        """
        if task_prompt is None:
            task_prompt = learning_content_creator_task_prompt_outline
        return self.invoke(input_dict, task_prompt=task_prompt)
        

    def goal_oriented_exploration(self, input_dict):
        knowledge_points = self.goal_oriented_explorer.explore_knowledges(input_dict)
        return knowledge_points

    def search_enhanced_drafting(self, input_dict):
        knowledge_draft = self.search_enhanced_drafter.draft_knowledge(input_dict)
        return knowledge_draft

    def integratation_and_refinement(self, input_dict):
        learning_document = self.learning_document_integrator.integrate_document(input_dict)
        return learning_document

    def document_quiz_generation(self, input_dict):
        quiz_questions = self.document_quiz_generator.generate_quiz(input_dict)
        return quiz_questions


class GoalOrientedKnowledgeExplorer(BaseAgent):

    def __init__(self, llm):
        super().__init__(model=llm, system_prompt=goal_oriented_knowledge_explorer_system_prompt, jsonalize_output=True)

    def check_json_output(self, output, input_dict):
        try:
            for knowledge_point in output:
                if knowledge_point.keys() == {'name', 'type'}:
                    return True
            return False
        except:
            return False

    def explore_knowledges(self, input_dict):
        """
        Explores knowledge based on the provided input dictionary.

        Args:
            input_dict (dict): A dictionary containing the following keys:
                - learner_profile (dict): Information about the learner's profile.
                - learning_path (dict): Details about the learner's intended learning path.
                - learning_session (dict): Data regarding the current learning session.

        Returns:
            dict: The result of the knowledge exploration process.
        """
        from .schemas import parse_knowledge_points
        raw_output = self.invoke(input_dict, task_prompt=goal_oriented_knowledge_explorer_task_prompt)
        try:
            validated = parse_knowledge_points(raw_output)
            return validated.model_dump()
        except Exception:
            return raw_output


class SearchEnhancedKnowledgeDraftor(BaseAgent):

    def __init__(
        self,
        llm,
        use_search: bool = True,
        *,
        num_search_results: int = DEFAULT_NUM_SEARCH_RESULTS,
        num_retrieval_results: int = DEFAULT_NUM_RETRIEVAL_RESULTS,
        search_pipeline=None,
        vectorstore_directory: str = DEFAULT_VECTORSTORE_DIR,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
    ):
        super().__init__(model=llm, system_prompt=search_enhanced_knowledge_drafter_system_prompt, jsonalize_output=True)
        self.use_search = use_search
        self.vectorstore_directory = vectorstore_directory
        self.num_search_results = num_search_results
        self.num_retrieval_results = num_retrieval_results
        self.chunk_size = chunk_size
        self.search_pipeline = None
        if self.use_search:
            self.search_pipeline = search_pipeline or create_deep_search_pipeline(
                persist_directory=vectorstore_directory,
                chunk_size=chunk_size,
                default_max_results=num_search_results,
                retriever_k=num_retrieval_results,
            )

    def check_json_output(self, output, input_dict):
        try:
            return output.keys() == {'title', 'content'}
        except:
            return False

    @staticmethod
    def _ensure_mapping(value):
        if isinstance(value, str):
            return ast.literal_eval(value)
        return value

    def _fetch_external_context(self, query: str, collection_name: str) -> str:
        if not self.search_pipeline:
            return ''

        docs = self.search_pipeline.run(
            query,
            collection_name,
            max_results=self.num_search_results,
            k=self.num_retrieval_results,
            persist_directory=self.vectorstore_directory,
            chunk_size=self.chunk_size,
        )
        return build_context(docs)

    def draft_knowledge(self, input_dict):
        """
        Drafts a perspective based on the provided input dictionary.

        Args:
            input_dict (dict): A dictionary containing the following keys:
                - learner_profile (str): The profile of the learner.
                - learning_path (str): The learning path chosen.
                - learning_session (str): The selected learning session.
                - knowledge_points (str): All knowledge points.
                - knowledge_point (str): The specific knowledge point selected.
                - external_resources (str, optional): External resources related to the knowledge point.

        Returns:
            dict: A dictionary containing the drafted perspective with potentially enhanced external resources.

        If `use_search` is enabled, the method will search for external resources related to the selected knowledge point,
        store them in a vector store, and retrieve relevant results. These results are then added to the `input_dict` under
        the key `external_resources`. If `use_search` is not enabled, `external_resources` will be set to an empty string.

        The method sets the system and task prompts for the knowledge drafter and invokes the `act` method to generate the
        final perspective.
        """
        if "external_resources" not in input_dict:
            input_dict["external_resources"] = ""
        else:
            input_dict["external_resources"] = str(input_dict["external_resources"])

        learning_session = self._ensure_mapping(input_dict['learning_session'])
        knowledge_point = self._ensure_mapping(input_dict['knowledge_point'])
        input_dict['learning_session'] = learning_session
        input_dict['knowledge_point'] = knowledge_point

        if self.use_search:
            learning_session_title = str(learning_session.get('title', 'learning_session'))
            knowledge_point_name = str(knowledge_point.get('name', '')).strip()
            query = f"{learning_session_title} {knowledge_point_name}".strip()
            if learning_session_title.isnumeric() or len(learning_session_title) < 3:
                learning_session_title = 'learning_session'
            db_collection_name = sanitize_collection_name(learning_session_title)
            context = self._fetch_external_context(query, db_collection_name)
            if context:
                input_dict['external_resources'] = f"{input_dict['external_resources']}{context}"
        else:
            input_dict['external_resources'] += ""
        from .schemas import parse_knowledge_draft
        raw_output = self.invoke(input_dict, task_prompt=search_enhanced_knowledge_drafter_task_prompt)
        try:
            validated = parse_knowledge_draft(raw_output)
            return validated.model_dump()
        except Exception:
            return raw_output

class LearningDocumentIntegrator(BaseAgent):

    def __init__(self, llm, output_markdown=True):
        super().__init__(model=llm, system_prompt=integrated_document_generator_system_prompt, jsonalize_output=True)
        self.output_markdown = output_markdown

    def check_json_output(self, output, input_dict):
        try:
            return output.keys() == {'title', 'overview', 'summary'}
        except:
            return False

    def integrate_document(self, input_dict):
        """
        Integrates various components of a learning document based on the provided input dictionary.

        Args:
            input_dict (dict): A dictionary containing the following keys:
                - learner_profile (str): Information about the learner's profile.
                - learning_path (str): The learning path the learner is following.
                - learning_session (str): Details about the current learning session.
                - knowledge_points (list): A list of knowledge points to be covered.
                - knowledge_drafts (list): Drafts related to the specified knowledge points.

        Returns:
            dict: The integrated document generated based on the input dictionary.
        """
        from .schemas import parse_document_structure
        raw_output = self.invoke(input_dict, task_prompt=integrated_document_generator_task_prompt)
        document_structure = raw_output
        try:
            document_structure = parse_document_structure(raw_output).model_dump()
        except Exception:
            pass
        
        if not self.output_markdown:
            return document_structure
        print('Preparing markdown document...')
        learning_document = prepare_markdown_document(document_structure, input_dict['knowledge_points'], input_dict['knowledge_drafts'])
        return learning_document


class DocumentQuizGenerator(BaseAgent):

    def __init__(self, llm):
        super().__init__(model=llm, system_prompt=document_quiz_generator_system_prompt, jsonalize_output=True)

    def check_json_output(self, output, input_dict):
        try:
            return output.keys() == {'single_choice_questions', 'multiple_choice_questions', 'true_false_questions', 'short_answer_questions'}
        except Exception:
            return False

    def generate_quiz(self, input_dict):
        """Generate a quiz based on the integrated learning document and parameters."""
        if 'single_choice_count' not in input_dict:
            input_dict['single_choice_count'] = 0
        if 'multiple_choice_count' not in input_dict:
            input_dict['multiple_choice_count'] = 0
        if 'true_false_count' not in input_dict:
            input_dict['true_false_count'] = 0
        if 'short_answer_count' not in input_dict:
            input_dict['short_answer_count'] = 0

        from .schemas import parse_document_quiz
        raw_output = self.invoke(input_dict, task_prompt=document_quiz_generator_task_prompt)
        try:
            validated = parse_document_quiz(raw_output)
            return validated.model_dump()
        except Exception:
            return raw_output


def explore_knowledge_points_with_llm(llm, learner_profile, learning_path, learning_session):
    input_dict = {
        'learner_profile': learner_profile,
        'learning_path': learning_path,
        'learning_session': learning_session
    }
    goal_oriented_explorer = GoalOrientedKnowledgeExplorer(llm)
    perspective_of_knowledge_point = goal_oriented_explorer.explore_knowledges(input_dict)
    return perspective_of_knowledge_point


def draft_knowledge_point_with_llm(
    llm,
    learner_profile,
    learning_path,
    learning_session,
    knowledge_points,
    knowledge_point,
    use_search: bool = True,
    *,
    search_pipeline=None,
    vectorstore_directory: str = DEFAULT_VECTORSTORE_DIR,
    num_search_results: int = DEFAULT_NUM_SEARCH_RESULTS,
    num_retrieval_results: int = DEFAULT_NUM_RETRIEVAL_RESULTS,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
):
    input_dict = {
        'learner_profile': learner_profile,
        'learning_path': learning_path,
        'learning_session': learning_session,
        'knowledge_points': knowledge_points,
        'knowledge_point': knowledge_point,
    }
    if search_pipeline is None and use_search:
        search_pipeline = create_deep_search_pipeline(
            persist_directory=vectorstore_directory,
            chunk_size=chunk_size,
            default_max_results=num_search_results,
            retriever_k=num_retrieval_results,
        )
    search_enhanced_drafter = SearchEnhancedKnowledgeDraftor(
        llm,
        num_search_results=num_search_results,
        num_retrieval_results=num_retrieval_results,
        use_search=use_search,
        search_pipeline=search_pipeline,
        vectorstore_directory=vectorstore_directory,
        chunk_size=chunk_size,
    )
    return search_enhanced_drafter.draft_knowledge(input_dict)

def draft_knowledge_points_with_llm(
    llm,
    learner_profile,
    learning_path,
    learning_session,
    knowledge_points,
    allow_parallel: bool = True,
    use_search: bool = True,
    max_workers: int = 3,
    *,
    search_pipeline=None,
    vectorstore_directory: str = DEFAULT_VECTORSTORE_DIR,
    num_search_results: int = DEFAULT_NUM_SEARCH_RESULTS,
    num_retrieval_results: int = DEFAULT_NUM_RETRIEVAL_RESULTS,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
):
    if isinstance(knowledge_points, str):
        knowledge_points = ast.literal_eval(knowledge_points)
    knowledge_drafts = []
    if search_pipeline is None and use_search:
        search_pipeline = create_deep_search_pipeline(
            persist_directory=vectorstore_directory,
            chunk_size=chunk_size,
            default_max_results=num_search_results,
            retriever_k=num_retrieval_results,
        )

    def draft_single_knowledge(knowledge_point):
        knowledge_draft = draft_knowledge_point_with_llm(
            llm,
            learner_profile,
            learning_path,
            learning_session,
            knowledge_points,
            knowledge_point,
            use_search=use_search,
            search_pipeline=search_pipeline,
            vectorstore_directory=vectorstore_directory,
            num_search_results=num_search_results,
            num_retrieval_results=num_retrieval_results,
            chunk_size=chunk_size,
        )
        return knowledge_draft
    if allow_parallel:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            knowledge_drafts = list(executor.map(draft_single_knowledge, knowledge_points))
    else:
        for pid, knowledge_point in enumerate(knowledge_points):
            knowledge_draft = draft_knowledge_point_with_llm(
                llm,
                learner_profile,
                learning_path,
                learning_session,
                knowledge_points,
                knowledge_point,
                use_search=use_search,
                search_pipeline=search_pipeline,
                vectorstore_directory=vectorstore_directory,
                num_search_results=num_search_results,
                num_retrieval_results=num_retrieval_results,
                chunk_size=chunk_size,
            )
            knowledge_drafts.append(knowledge_draft)
    return knowledge_drafts

def integrate_learning_document_with_llm(llm, learner_profile, learning_path, learning_session, knowledge_points, knowledge_drafts, output_markdown=True):
    print(f'Integrating learning document with {len(knowledge_points)} knowledge points and {len(knowledge_drafts)} drafts...')
    input_dict = {
        'learner_profile': learner_profile,
        'learning_path': learning_path,
        'learning_session': learning_session,
        'knowledge_points': knowledge_points,
        'knowledge_drafts': knowledge_drafts
    }
    learning_document_integrator = LearningDocumentIntegrator(llm, output_markdown=output_markdown)
    learning_document = learning_document_integrator.integrate_document(input_dict)
    return learning_document

def generate_document_quizzes_with_llm(llm, learner_profile, learning_document, single_choice_count=3, multiple_choice_count=0, true_false_count=0, short_answer_count=0):
    input_dict = {
        'learner_profile': learner_profile,
        'learning_document': learning_document,
        'single_choice_count': single_choice_count,
        'multiple_choice_count': multiple_choice_count,
        'true_false_count': true_false_count,
        'short_answer_count': short_answer_count
    }
    document_quiz_generator = DocumentQuizGenerator(llm)
    quiz_questions = document_quiz_generator.generate_quiz(input_dict)
    return quiz_questions

def create_learning_content_with_llm(
    llm,
    learner_profile,
    learning_path,
    learning_session,
    document_outline=None,
    allow_parallel=True,
    with_quiz=True,
    max_wokrers=3,
    use_search=True,
    output_markdown=True,
    method_name="genmentor",
):
    search_pipeline = None
    if use_search:
        search_pipeline = create_deep_search_pipeline(
            persist_directory=DEFAULT_VECTORSTORE_DIR,
            chunk_size=DEFAULT_CHUNK_SIZE,
            default_max_results=DEFAULT_NUM_SEARCH_RESULTS,
            retriever_k=DEFAULT_NUM_RETRIEVAL_RESULTS,
        )

    if method_name == "genmentor":
        knowledge_points = explore_knowledge_points_with_llm(llm, learner_profile, learning_path, learning_session)
        knowledge_drafts = draft_knowledge_points_with_llm(
            llm,
            learner_profile,
            learning_path,
            learning_session,
            knowledge_points,
            allow_parallel=allow_parallel,
            use_search=use_search,
            max_workers=max_wokrers,
            search_pipeline=search_pipeline,
            vectorstore_directory=DEFAULT_VECTORSTORE_DIR,
            num_search_results=DEFAULT_NUM_SEARCH_RESULTS,
            num_retrieval_results=DEFAULT_NUM_RETRIEVAL_RESULTS,
            chunk_size=DEFAULT_CHUNK_SIZE,
        )
        learning_document = integrate_learning_document_with_llm(llm, learner_profile, learning_path, learning_session, knowledge_points, knowledge_drafts, output_markdown=output_markdown)
        learning_content = {'document': learning_document}
        if not with_quiz:
            return learning_content
        document_quiz = generate_document_quizzes_with_llm(llm, learner_profile, learning_document, single_choice_count=3, multiple_choice_count=0, true_false_count=0, short_answer_count=0)
        learning_content['quizzes'] = document_quiz
        return learning_content
    else:
        learning_content_creator = LearningContentCreator(
            llm,
            use_search=use_search,
            search_pipeline=search_pipeline,
            vectorstore_directory=DEFAULT_VECTORSTORE_DIR,
            num_search_results=DEFAULT_NUM_SEARCH_RESULTS,
            num_retrieval_results=DEFAULT_NUM_RETRIEVAL_RESULTS,
            chunk_size=DEFAULT_CHUNK_SIZE,
        )
        if document_outline is None:
            document_outline = prepare_content_outline_with_llm(
                llm,
                learner_profile,
                learning_path,
                learning_session,
                search_pipeline=search_pipeline,
            )
        learning_content = learning_content_creator.create_content_with_outline({
            'learner_profile': learner_profile,
            'learning_path': learning_path,
            'learning_session': learning_session,
            'document_outline': document_outline
        })
        return learning_content

def prepare_markdown_document(document_structure, knowledge_points, knowledge_drafts):
    if isinstance(knowledge_points, str):
        knowledge_points = ast.literal_eval(knowledge_points)
    if isinstance(knowledge_drafts, str):
        knowledge_drafts = ast.literal_eval(knowledge_drafts)
    if isinstance(document_structure, str):
        document_structure = ast.literal_eval(document_structure)

    part_titles = {
        'foundational': "## Foundational Concepts",
        'practical': "## Practical Applications",
        'strategic': "## Strategic Insights"
    }

    learning_document = f"# {document_structure['title']}"
    learning_document += f"\n\n{document_structure['overview']}"
    for k_type, part_title in part_titles.items():
        learning_document += f"\n\n{part_title}\n"
        for k_id, knowledge_point in enumerate(knowledge_points):
            if knowledge_point['type'] != k_type:
                continue
            knowledge_draft = knowledge_drafts[k_id]
            learning_document += f"\n\n### {knowledge_draft['title']}\n"
            learning_document += f"\n\n{knowledge_draft['content']}\n"
    learning_document += f"\n\n## Summary\n\n{document_structure['summary']}"
    return learning_document

def prepare_content_outline_with_llm(llm, learner_profile, learning_path, learning_session, *, search_pipeline=None):
    input_dict = {
        'learner_profile': learner_profile,
        'learning_path': learning_path,
        'learning_session': learning_session
    }
    tailored_content_creator = TailoredContentCreator(llm, search_pipeline=search_pipeline)
    outline = tailored_content_creator.prepare_outline(input_dict)
    return outline
