"""Content creation utilities for personalized learning resources."""

from __future__ import annotations

import ast
import copy
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple, TypeVar, Union

from base.agent import Agent
from base.rag import search_and_store
from prompts.tailored_content_creation import *
from utils import sanitize_collection_name


JSONValue = Union[str, int, float, bool, None, Dict[str, "JSONValue"], List["JSONValue"]]
JSONDict = Dict[str, JSONValue]


logger = logging.getLogger(__name__)


_T = TypeVar("_T")


def _literal_eval_if_needed(value: Union[str, _T]) -> Union[_T, JSONValue]:
    """Safely parse stringified Python literals into Python objects."""

    if isinstance(value, str):
        try:
            return ast.literal_eval(value)
        except (ValueError, SyntaxError):
            logger.debug("Failed to literal_eval value; returning original string.")
            return value
    return value


def search_enhanced_rag(
    query: Union[str, JSONValue],
    db_collection_name: str,
    db_persist_directory: str = "./data/vectorstore",
    num_results: int = 3,
    num_retrieval_results: int = 5,
) -> List[Any]:
    """Execute RAG search and return retrieved external resources."""

    query_str = str(query)
    logger.info("Searching '%s' for external resources.", query_str)
    vectorstore = search_and_store(
        query_str,
        db_collection_name=db_collection_name,
        db_persist_directory=db_persist_directory,
        num_results=num_results,
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": num_retrieval_results})
    external_resources: List[Any] = retriever.invoke(query_str)
    logger.info("Found %d external resources.", len(external_resources))
    return external_resources


class LearningContentCreator(Agent):
    """Generate comprehensive learning content using optional external resources."""

    def __init__(self, llm: Any, use_search: bool = True) -> None:
        super().__init__("LearningContentCreator", llm=llm, json_output=True)
        self.use_search = use_search

    def create_content(
        self,
        input_dict: JSONDict,
        system_prompt: Optional[str] = None,
        task_prompt: Optional[str] = None,
    ) -> Any:
        """Create content with optional search-enhanced resources."""

        if system_prompt is None:
            system_prompt = learning_content_creator_system_prompt
        if task_prompt is None:
            task_prompt = learning_content_creator_task_prompt_content
        self.set_prompts(system_prompt, task_prompt)

        if "external_resources" not in input_dict:
            input_dict["external_resources"] = ""

        if self.use_search:
            input_dict["learning_session"] = _literal_eval_if_needed(
                input_dict["learning_session"]
            )  # type: ignore[assignment]
            learning_session = input_dict["learning_session"]
            if not isinstance(learning_session, dict):
                raise TypeError("learning_session must be a dictionary after parsing.")

            learning_session_title = str(learning_session.get("title", "learning_session"))
            if learning_session_title.isnumeric() or len(learning_session_title) < 3:
                learning_session_title = "learning_session"
            db_collection_name = sanitize_collection_name(learning_session_title)
            query = learning_session_title
            external_resources = search_enhanced_rag(
                query,
                db_collection_name=db_collection_name,
                db_persist_directory="./data/vectorstore",
                num_results=3,
                num_retrieval_results=5,
            )
            input_dict["external_resources"] += str(external_resources)
        return self.act(input_dict)

    def draft_section(self, input_dict: JSONDict) -> Any:
        """Draft a document section using search-enhanced external resources."""

        if self.use_search:
            session = input_dict.get("learning_session", {})
            if isinstance(session, str):
                session = _literal_eval_if_needed(session)
            if not isinstance(session, dict):
                raise TypeError("learning_session must be a dictionary for draft_section.")

            input_dict["learning_session"] = session
            session_title = str(session.get("title", "learning_session"))
            query = session_title + str(input_dict.get("document_section", ""))
            db_collection_name = sanitize_collection_name(session_title)
            external_resources = search_enhanced_rag(
                query,
                db_collection_name=db_collection_name,
                db_persist_directory="./data/vectorstore",
                num_results=3,
                num_retrieval_results=5,
            )
            input_dict["external_resources"] = str(external_resources)
        else:
            input_dict["external_resources"] = ""
        self.set_prompts(learning_content_creator_orag_system_prompt, learning_content_creator_task_prompt_draft)
        return self.act(input_dict)

    def create_content_with_outline(self, input_dict: JSONDict) -> List[Any]:
        """Create content based on a pre-defined outline."""

        document_outline = _literal_eval_if_needed(input_dict["document_outline"])
        if not isinstance(document_outline, dict):
            raise TypeError("document_outline must resolve to a dictionary.")

        document_title = document_outline["title"]
        document_sections: Sequence[Dict[str, Any]] = document_outline["sections"]
        document_content: List[Any] = [f"# {document_title}"]
        for section in document_sections:
            section_title = section["title"]
            input_dict["document_section"] = section_title
            input_dict_copy = copy.deepcopy(input_dict)
            section_draft = self.draft_section(input_dict_copy)
            document_content.append(section_draft)
        return document_content

    def prepare_outline(
        self,
        input_dict: JSONDict,
        system_prompt: Optional[str] = None,
        task_prompt: Optional[str] = None,
    ) -> Any:
        """Generate a learning content outline."""

        if system_prompt is None:
            system_prompt = learning_content_creator_orag_system_prompt
        if task_prompt is None:
            task_prompt = learning_content_creator_task_prompt_outline
        self.set_prompts(system_prompt, task_prompt)
        return self.act(input_dict)


class TailoredContentCreator(Agent):
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
    def __init__(self, llm: Any) -> None:
        super().__init__(
            "TailoredContentCreator",
            llm=llm,
            json_output=True,
            use_search=True,
            allow_parallel=True,
        )
        self.goal_oriented_knowledge_explorer = GoalOrientedKnowledgeExplorer(llm)
        self.search_enhanced_knowledge_drafter = SearchEnhancedKnowledgeDraftor(llm)
        self.learning_document_integrator = LearningDocumentIntegrator(llm)
        self.document_quiz_generator = DocumentQuizGenerator(llm)

    def create_content(
        self,
        input_dict: JSONDict,
        system_prompt: Optional[str] = None,
        task_prompt: Optional[str] = None,
    ) -> Any:
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
        if system_prompt is None:
            system_prompt = learning_content_creator_orag_system_prompt
        if task_prompt is None:
            task_prompt = learning_content_creator_task_prompt_content
        return self.act(input_dict, system_prompt=system_prompt, task_prompt=task_prompt)

    def prepare_outline(
        self,
        input_dict: JSONDict,
        system_prompt: Optional[str] = None,
        task_prompt: Optional[str] = None,
    ) -> Any:
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
        if system_prompt is None:
            system_prompt = learning_content_creator_orag_system_prompt
        if task_prompt is None:
            task_prompt = learning_content_creator_task_prompt_outline
        self.set_prompts(system_prompt, task_prompt)
        return self.act(input_dict)
        

    def goal_oriented_exploration(self, input_dict: JSONDict) -> Any:
        """Explore knowledge points for a learning session."""

        knowledge_points = self.goal_oriented_knowledge_explorer.explore_knowledges(input_dict)
        return knowledge_points

    def search_enhanced_drafting(self, input_dict: JSONDict) -> Any:
        """Draft knowledge content with search-enhanced insights."""

        knowledge_draft = self.search_enhanced_knowledge_drafter.draft_knowledge(input_dict)
        return knowledge_draft

    def integratation_and_refinement(self, input_dict: JSONDict) -> Any:
        """Integrate and refine knowledge drafts into a learning document."""

        learning_document = self.learning_document_integrator.integrate_document(input_dict)
        return learning_document

    def document_quiz_generation(self, input_dict: JSONDict) -> Any:
        """Generate quiz questions from the learning document."""

        quiz_questions = self.document_quiz_generator.generate_quiz(input_dict)
        return quiz_questions


class GoalOrientedKnowledgeExplorer(Agent):

    def __init__(self, llm: Any) -> None:
        super().__init__("GoalOrientedKnowledgeExploration", llm=llm, json_output=True)

    def check_json_output(self, output: Any, input_dict: JSONDict) -> bool:
        """Validate that knowledge exploration output is well-formed."""

        try:
            for knowledge_point in output:
                if knowledge_point.keys() == {"name", "type"}:
                    return True
            return False
        except Exception:  # noqa: BLE001
            return False

    def explore_knowledges(self, input_dict: JSONDict) -> Any:
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
        self.set_prompts(goal_oriented_knowledge_explorer_system_prompt, goal_oriented_knowledge_explorer_task_prompt)
        return self.act(input_dict)


class SearchEnhancedKnowledgeDraftor(Agent):
    
    def __init__(
            self,
            llm: Any,
            use_search: bool = True,
            num_search_results: int = 3,
            db_persist_directory: str = "./data/vectorstore",
            num_retrieval_results: int = 5,
    ) -> None:
        super().__init__("SearchEnhancedKnowledgeDraftor", llm=llm, json_output=True)
        self.use_search = use_search
        self.db_persist_directory = db_persist_directory
        self.num_search_results = num_search_results
        self.num_retrieval_results = num_retrieval_results

    def check_json_output(self, output: Any, input_dict: JSONDict) -> bool:
        """Validate the structure of drafter output."""

        try:
            return output.keys() == {"title", "content"}
        except Exception:  # noqa: BLE001
            return False

    def draft_knowledge(self, input_dict: JSONDict) -> Any:
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

        input_dict["learning_session"] = _literal_eval_if_needed(input_dict["learning_session"])  # type: ignore[assignment]
        input_dict["knowledge_point"] = _literal_eval_if_needed(input_dict["knowledge_point"])  # type: ignore[assignment]

        if self.use_search:
            learning_session = input_dict["learning_session"]
            knowledge_point = input_dict["knowledge_point"]
            if not isinstance(learning_session, dict) or not isinstance(knowledge_point, dict):
                raise TypeError("learning_session and knowledge_point must be dictionaries after parsing.")

            learning_session_title = str(learning_session.get("title", "learning_session"))
            knowledge_point_name = str(knowledge_point.get("name", ""))
            query = f"{learning_session_title} {knowledge_point_name}".strip()
            if learning_session_title.isnumeric() or len(learning_session_title) < 3:
                learning_session_title = "learning_session"
            db_collection_name = sanitize_collection_name(learning_session_title)
            external_resources = search_enhanced_rag(
                query,
                db_collection_name=db_collection_name,
                db_persist_directory=self.db_persist_directory,
                num_results=self.num_search_results,
                num_retrieval_results=self.num_retrieval_results,
            )
            input_dict["external_resources"] += str(external_resources)
        else:
            input_dict["external_resources"] += ""
        self.set_prompts(search_enhanced_knowledge_drafter_system_prompt, search_enhanced_knowledge_drafter_task_prompt)
        return self.act(input_dict)

class LearningDocumentIntegrator(Agent):

    def __init__(self, llm: Any, output_markdown: bool = True) -> None:
        super().__init__("LearningDocumentIntegrator", llm=llm, json_output=True)
        self.output_markdown = output_markdown

    def check_json_output(self, output: Any, input_dict: JSONDict) -> bool:
        """Validate the structure of the integrated document."""

        try:
            return output.keys() == {"title", "overview", "summary"}
        except Exception:  # noqa: BLE001
            return False

    def integrate_document(self, input_dict: JSONDict) -> Any:
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
        self.set_prompts(integrated_document_generator_system_prompt, integrated_document_generator_task_prompt)
        document_structure = self.act(input_dict)

        if not self.output_markdown:
            return document_structure
        logger.info("Preparing markdown document from structured content.")
        learning_document = prepare_markdown_document(
            document_structure,
            input_dict["knowledge_points"],
            input_dict["knowledge_drafts"],
        )
        return learning_document


class DocumentQuizGenerator(Agent):

    def __init__(self, llm: Any) -> None:
        super().__init__("DocumentQuizGenerator", llm=llm, json_output=True)

    def check_json_output(self, output: Any, input_dict: JSONDict) -> bool:
        """Validate quiz generation output structure."""

        try:
            return output.keys() == {
                "single_choice_questions",
                "multiple_choice_questions",
                "true_false_questions",
                "short_answer_questions",
            }
        except Exception:  # noqa: BLE001
            return False

    def generate_quiz(self, input_dict: JSONDict) -> Any:
        """
        Generates a quiz based on the provided input dictionary.

        Args:
            input_dict (dict): A dictionary containing the following keys:
                - learner_profile (str): The profile of the learner.
                - learning_document (str): The document used for the learning session.
                - single_choice_count (int, optional): The number of single choice questions. Defaults to 0.
                - multiple_choice_count (int, optional): The number of multiple choice questions. Defaults to 0.
                - true_false_count (int, optional): The number of true/false questions. Defaults to 0.
                - short_answer_count (int, optional): The number of short answer questions. Defaults to 0.

        Returns:
            dict: A dictionary containing the generated quiz questions.
        """
        if 'single_choice_count' not in input_dict:
            input_dict['single_choice_count'] = 0
        if 'multiple_choice_count' not in input_dict:
            input_dict['multiple_choice_count'] = 0
        if 'true_false_count' not in input_dict:
            input_dict['true_false_count'] = 0
        if 'short_answer_count' not in input_dict:
            input_dict['short_answer_count'] = 0
        self.set_prompts(document_quiz_generator_system_prompt, document_quiz_generator_task_prompt)
        return self.act(input_dict)


def explore_knowledge_points_with_llm(
    llm: Any,
    learner_profile: JSONDict,
    learning_path: JSONDict,
    learning_session: JSONDict,
) -> Any:
    """Explore knowledge points leveraging the provided language model."""

    input_dict = {
        'learner_profile': learner_profile,
        'learning_path': learning_path,
        'learning_session': learning_session
    }
    goal_oriented_explorer = GoalOrientedKnowledgeExplorer(llm)
    perspective_of_knowledge_point = goal_oriented_explorer.explore_knowledges(input_dict)
    return perspective_of_knowledge_point


def draft_knowledge_point_with_llm(
    llm: Any,
    learner_profile: JSONDict,
    learning_path: JSONDict,
    learning_session: JSONDict,
    knowledge_points: Union[str, Sequence[JSONDict]],
    knowledge_point: Union[str, JSONDict],
    use_search: bool = True,
) -> Any:
    """Draft a single knowledge point using the configured language model."""

    input_dict = {
        'learner_profile': learner_profile,
        'learning_path': learning_path,
        'learning_session': learning_session,
        'knowledge_points': knowledge_points,
        'knowledge_point': knowledge_point,
    }
    search_enhanced_drafter = SearchEnhancedKnowledgeDraftor(
        llm,
        num_search_results=3,
        num_retrieval_results=5,
        use_search=use_search,
    )
    return search_enhanced_drafter.draft_knowledge(input_dict)

def draft_knowledge_points_with_llm(
    llm: Any,
    learner_profile: JSONDict,
    learning_path: JSONDict,
    learning_session: JSONDict,
    knowledge_points: Union[str, Sequence[JSONDict]],
    allow_parallel: bool = True,
    use_search: bool = True,
    max_workers: int = 3,
) -> List[Any]:
    """Draft knowledge points sequentially or in parallel."""

    knowledge_points_resolved = _literal_eval_if_needed(knowledge_points)
    if not isinstance(knowledge_points_resolved, Sequence):
        raise TypeError("knowledge_points must resolve to a sequence.")

    def draft_single_knowledge(knowledge_point: Union[str, JSONDict]) -> Any:
        return draft_knowledge_point_with_llm(
            llm,
            learner_profile,
            learning_path,
            learning_session,
            knowledge_points_resolved,
            knowledge_point,
            use_search=use_search,
        )

    if allow_parallel:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            return list(executor.map(draft_single_knowledge, knowledge_points_resolved))

    knowledge_drafts: List[Any] = []
    for knowledge_point in knowledge_points_resolved:
        knowledge_drafts.append(
            draft_single_knowledge(knowledge_point)
        )
    return knowledge_drafts


def integrate_learning_document_with_llm(
    llm: Any,
    learner_profile: JSONDict,
    learning_path: JSONDict,
    learning_session: JSONDict,
    knowledge_points: Union[str, Sequence[JSONDict]],
    knowledge_drafts: Union[str, Sequence[JSONDict]],
    output_markdown: bool = True,
) -> Any:
    """Integrate drafts into a cohesive learning document."""

    knowledge_points_resolved = _literal_eval_if_needed(knowledge_points)
    knowledge_drafts_resolved = _literal_eval_if_needed(knowledge_drafts)
    if not isinstance(knowledge_points_resolved, Sequence) or not isinstance(knowledge_drafts_resolved, Sequence):
        raise TypeError("knowledge_points and knowledge_drafts must resolve to sequences.")

    logger.info(
        "Integrating learning document with %d knowledge points and %d drafts...",
        len(knowledge_points_resolved),
        len(knowledge_drafts_resolved),
    )
    input_dict = {
        'learner_profile': learner_profile,
        'learning_path': learning_path,
        'learning_session': learning_session,
        'knowledge_points': knowledge_points_resolved,
        'knowledge_drafts': knowledge_drafts_resolved
    }
    learning_document_integrator = LearningDocumentIntegrator(llm, output_markdown=output_markdown)
    learning_document = learning_document_integrator.integrate_document(input_dict)
    return learning_document

def generate_document_quizzes_with_llm(
    llm: Any,
    learner_profile: JSONDict,
    learning_document: Union[str, JSONDict],
    single_choice_count: int = 3,
    multiple_choice_count: int = 0,
    true_false_count: int = 0,
    short_answer_count: int = 0,
) -> Any:
    """Generate quizzes from the learning document using the language model."""

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
    llm: Any,
    learner_profile: JSONDict,
    learning_path: JSONDict,
    learning_session: JSONDict,
    document_outline: Optional[Union[str, JSONDict]] = None,
    allow_parallel: bool = True,
    with_quiz: bool = True,
    max_workers: int = 3,
    use_search: bool = True,
    output_markdown: bool = True,
    method_name: str = "genmentor",
) -> JSONDict:
    """Create complete learning content using the specified method."""

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
            max_workers=max_workers,
        )
        learning_document = integrate_learning_document_with_llm(
            llm,
            learner_profile,
            learning_path,
            learning_session,
            knowledge_points,
            knowledge_drafts,
            output_markdown=output_markdown,
        )
        learning_content: JSONDict = {'document': learning_document}
        if not with_quiz:
            return learning_content
        document_quiz = generate_document_quizzes_with_llm(
            llm,
            learner_profile,
            learning_document,
            single_choice_count=3,
            multiple_choice_count=0,
            true_false_count=0,
            short_answer_count=0,
        )
        learning_content['quizzes'] = document_quiz
        return learning_content

    learning_content_creator = LearningContentCreator(llm, use_search=use_search)
    outline_resolved = document_outline
    if outline_resolved is None:
        outline_resolved = prepare_content_outline_with_llm(llm, learner_profile, learning_path, learning_session)
    learning_content = learning_content_creator.create_content_with_outline({
        'learner_profile': learner_profile,
        'learning_path': learning_path,
        'learning_session': learning_session,
        'document_outline': outline_resolved
    })
    return learning_content


def prepare_markdown_document(
    document_structure: Union[str, JSONDict],
    knowledge_points: Union[str, Sequence[JSONDict]],
    knowledge_drafts: Union[str, Sequence[JSONDict]],
) -> str:
    """Convert structured document data into Markdown."""

    knowledge_points_resolved = _literal_eval_if_needed(knowledge_points)
    knowledge_drafts_resolved = _literal_eval_if_needed(knowledge_drafts)
    document_structure_resolved = _literal_eval_if_needed(document_structure)

    if not isinstance(document_structure_resolved, dict):
        raise TypeError("document_structure must resolve to a dictionary.")
    if not isinstance(knowledge_points_resolved, Sequence):
        raise TypeError("knowledge_points must resolve to a sequence.")
    if not isinstance(knowledge_drafts_resolved, Sequence):
        raise TypeError("knowledge_drafts must resolve to a sequence.")

    part_titles = {
        'foundational': "## Foundational Concepts",
        'practical': "## Practical Applications",
        'strategic': "## Strategic Insights"
    }

    learning_document = f"# {document_structure_resolved['title']}"
    learning_document += f"\n\n{document_structure_resolved['overview']}"
    for k_type, part_title in part_titles.items():
        learning_document += f"\n\n{part_title}\n"
        for k_id, knowledge_point in enumerate(knowledge_points_resolved):
            if not isinstance(knowledge_point, dict) or knowledge_point.get('type') != k_type:
                continue
            knowledge_draft = knowledge_drafts_resolved[k_id]
            learning_document += f"\n\n### {knowledge_draft['title']}\n"
            learning_document += f"\n\n{knowledge_draft['content']}\n"
    learning_document += f"\n\n## Summary\n\n{document_structure_resolved['summary']}"
    return learning_document


def prepare_content_outline_with_llm(
    llm: Any,
    learner_profile: JSONDict,
    learning_path: JSONDict,
    learning_session: JSONDict,
) -> Any:
    """Prepare a content outline using the tailored content creator."""

    input_dict = {
        'learner_profile': learner_profile,
        'learning_path': learning_path,
        'learning_session': learning_session
    }
    tailored_content_creator = TailoredContentCreator(llm)
    outline = tailored_content_creator.prepare_outline(input_dict)
    return outline
