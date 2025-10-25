from base import Agent
from base.search_rag import load_websites, split_docs, search_and_store
from prompts.backup.tailored_content_creation import *
from utils import sanitize_collection_name
from concurrent.futures import ThreadPoolExecutor
import ast


class TailoredContentCreator(Agent):

    def __init__(self, llm):
        super().__init__('TailoredContentCreator', llm=llm, json_output=True)
        self.set_prompts(learning_content_creator_system_prompt, learning_content_creator_task_prompt)

    def goal_oriented_exploration(self, input_dict):
        return self.act(input_dict)

    def search_enhanced_drafting(self, input_dict):
        return self.act(input_dict)

    def integratation(self, input_dict):
        return self.act(input_dict)


class GoalOrientedPerspectiveExplorer(Agent):

    def __init__(self, llm):
        super().__init__('GoalOrientedPerspectiveExploration', llm=llm, json_output=True)

    def explore_perspectives(self, input_dict):
        """
        - **Learner Profile**: {learner_profile}
        - **Learning Path**: {learning_path}
        - **Given Knowledge Point**: {knowledge_point}
        """
        self.set_prompts(goal_oriented_perspective_explorer_system_prompt, goal_oriented_perspective_explorer_task_prompt)
        return self.act(input_dict)


class SearchEnhancedPerspectiveDraftor(Agent):
    
    def __init__(self, llm, use_search=True, db_persist_directory='./data/vectorstore', num_search_results=3, num_retrieval_results=5):
        super().__init__('SearchEnhancedPerspectiveDraftor', llm=llm, json_output=True)
        self.use_search = use_search
        self.db_persist_directory = db_persist_directory
        self.num_search_results = num_search_results
        self.num_retrieval_results = num_retrieval_results


    def draft_perspective(self, input_dict):
        """
        - **Learner Profile**: {learner_profile}
        - **Learning Path**: {learning_path}
        - **Selected Knowledge Point**: {knowledge_point}
        - **Perspectives of This Knowledge Points**: {perspectives_of_knowledge_point}
        - **Selected Perspective for drafting**: {knowledge_perspective}
        - **External Resources**: {external_resources}
        """
        if self.use_search:
            query = input_dict['knowledge_point'] + ' ' + input_dict['knowledge_perspective']
            print(f'Searching {query} for external resources...')
            db_collection_name = sanitize_collection_name(input_dict['knowledge_point'])
            vectorstore = search_and_store(
                query, 
                db_collection_name=db_collection_name, 
                db_persist_directory=self.db_persist_directory, 
                num_results=self.num_search_results)
            retriever = vectorstore.as_retriever(search_kwargs={"k": self.num_retrieval_results})
            external_resources = retriever.invoke(input_dict['knowledge_point'])
            input_dict['external_resources'] = external_resources
            print(f'Found {len(external_resources)} external resources.')
            # print(external_resources)
        else:
            input_dict['external_resources'] = ""
        print('Drafting perspective section...')
        self.set_prompts(search_enhanced_perspective_drafter_system_prompt, search_enhanced_perspective_drafter_task_prompt)
        return self.act(input_dict)


class KnowledgeDocumentIntegrator(Agent):

    def __init__(self, llm):
        super().__init__('KnowledgeDocumentIntegrator', llm=llm, json_output=True)

    def integrate_document(self, input_dict):
        """
        - **Learner Profile**: {learner_profile}
        - **Learning Path**: {learning_path}
        - **Selected Knowledge Point**: {knowledge_point}
        - **Perspectives of This Knowledge Point**: {perspectives_of_knowledge_point}
        - **Drafts of These Perspectives**: {drafts_of_perspectives}
        """
        self.set_prompts(integrated_document_generator_system_prompt, integrated_document_generator_task_prompt)
        return self.act(input_dict)


class DocumentQuizGenerator(Agent):

    def __init__(self, llm):
        super().__init__('DocumentQuizGenerator', llm=llm, json_output=True)

    def generate_quiz(self, input_dict):
        """
        - **Learner Profile**: {learner_profile}
        - **Knowledge Document**: {knowledge_document}
        - **Number of Qiuzzes**:
            - Single Choice: {single_choice_count} questions
            - Multiple Choice: {multiple_choice_count} questions
            - True/False: {true_false_count} questions
            - Short Answer: {short_answer_count} questions
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


def explore_knowledge_perspectives_with_llm(llm, learner_profile, learning_path, knowledge_point):
    input_dict = {
        'learner_profile': learner_profile,
        'learning_path': learning_path,
        'knowledge_point': knowledge_point
    }
    goal_oriented_explorer = GoalOrientedPerspectiveExplorer(llm)
    perspective_of_knowledge_point = goal_oriented_explorer.explore_perspectives(input_dict)
    return perspective_of_knowledge_point


def draft_knowledge_perspective_with_llm(llm, learner_profile, learning_path, knowledge_point, perspectives_of_knowledge_point, knowledge_perspective, use_search=True):
    input_dict = {
        'learner_profile': learner_profile,
        'learning_path': learning_path,
        'knowledge_point': knowledge_point,
        'perspectives_of_knowledge_point': perspectives_of_knowledge_point,
        'knowledge_perspective': knowledge_perspective
    }
    search_enhanced_drafter = SearchEnhancedPerspectiveDraftor(llm, num_search_results=3, num_retrieval_results=5, use_search=use_search)
    return search_enhanced_drafter.draft_perspective(input_dict)

def draft_perspectives_of_knowledge_point_with_llm(llm, learner_profile, learning_path, knowledge_point, perspectives_of_knowledge_point, allow_parallel=True, use_search=True):
    if isinstance(perspectives_of_knowledge_point, str):
        perspectives_of_knowledge_point = ast.literal_eval(perspectives_of_knowledge_point)
    all_perspective_type_list = list(perspectives_of_knowledge_point.keys())
    perspective_list = [perspective for type in all_perspective_type_list for perspective in perspectives_of_knowledge_point[type]]
    perspective_draft_list = []

    def draft_single_perspective(knowledge_perspective):
        perspective_draft = draft_knowledge_perspective_with_llm(llm, learner_profile, learning_path, knowledge_point, perspectives_of_knowledge_point, knowledge_perspective, use_search=use_search)
        return perspective_draft["content"]
    
    if allow_parallel:
        with ThreadPoolExecutor() as executor:
            perspective_draft_list = list(executor.map(draft_single_perspective, perspective_list))
    else:
        for pid, knowledge_perspective in enumerate(perspective_list):
            print(f'*** {pid} - {knowledge_perspective} ***')
            perspective_draft = draft_knowledge_perspective_with_llm(llm, learner_profile, learning_path, knowledge_point, perspectives_of_knowledge_point, knowledge_perspective)
            perspective_draft_list.append(perspective_draft["content"])
    return perspective_draft_list

def integrate_knowledge_document_with_llm(llm, learner_profile, learning_path, knowledge_point, perspectives_of_knowledge_point, drafts_of_perspectives):
    input_dict = {
        'learner_profile': learner_profile,
        'learning_path': learning_path,
        'knowledge_point': knowledge_point,
        'perspectives_of_knowledge_point': perspectives_of_knowledge_point,
        'drafts_of_perspectives': drafts_of_perspectives
    }
    if isinstance(perspectives_of_knowledge_point, str):
        perspectives_of_knowledge_point = ast.literal_eval(perspectives_of_knowledge_point)
    if isinstance(drafts_of_perspectives, str):
        drafts_of_perspectives = ast.literal_eval(drafts_of_perspectives)
    print('integrate_knowledge_document_with_llm...')
    print("drafts_of_perspectives:", drafts_of_perspectives)
    print('----------------')
    import pprint
    # perspective_type_list = [p_type for p_type in all_perspective_type_list if perspectives_of_knowledge_point[p_type]]
    # for p_type, p_draft in zip(perspective_type_list, drafts_of_perspectives):
        # input_dict[p_type] = p_draft
    knowledge_document_integrator = KnowledgeDocumentIntegrator(llm)
    document_structure = knowledge_document_integrator.integrate_document(input_dict)

    section_titles = {
        'foundational': "## Foundational Concepts:",
        'practical': "## Practical Applications:",
        'strategic': "## Strategic Insights:"
    }


    knowledge_document = f"# {document_structure['title']}"
    knowledge_document += f"\n\n{document_structure['overview']}"
    all_perspective_type_list = list(perspectives_of_knowledge_point.keys())
    perspective_list = [perspective for type in all_perspective_type_list for perspective in perspectives_of_knowledge_point[type]]
    for p_type, title in section_titles.items():
        if p_type in perspectives_of_knowledge_point:
            knowledge_document += f"\n\n{title}\n"
            perspective_list_of_type = perspectives_of_knowledge_point[p_type]
            for perspective in perspective_list_of_type:
                perspective_idx = perspective_list.index(perspective)
                # print(perspective_idx, f"*** {perspective} ***")
                p_draft = drafts_of_perspectives[perspective_idx]
                # knowledge_document += f"\n\n### {perspective}\n\n{p_draft}"
                knowledge_document += f"\n\n{p_draft}"

    knowledge_document += f"\n\n## Summary\n\n{document_structure['summary']}"
    return knowledge_document

def generate_document_quizzes_with_llm(llm, learner_profile, knowledge_document, single_choice_count=3, multiple_choice_count=0, true_false_count=0, short_answer_count=0):
    input_dict = {
        'learner_profile': learner_profile,
        'knowledge_document': knowledge_document,
        'single_choice_count': single_choice_count,
        'multiple_choice_count': multiple_choice_count,
        'true_false_count': true_false_count,
        'short_answer_count': short_answer_count
    }
    document_quiz_generator = DocumentQuizGenerator(llm)
    return document_quiz_generator.generate_quiz(input_dict)


def tailor_knowledge_content_with_llm(llm, learning_path, learner_profile, knowledge_point, allow_parallel=True, with_quiz=True, max_wokrers=3):
    perspectives_of_knowledge_point = explore_knowledge_perspectives_with_llm(llm, learner_profile, learning_path, knowledge_point)
    all_perspective_type_list = list(perspectives_of_knowledge_point.keys())
    perspective_list = [perspective for type in all_perspective_type_list for perspective in perspectives_of_knowledge_point[type]]
    perspective_draft_list = []

    def draft_single_perspective(knowledge_perspective):
        return draft_knowledge_perspective_with_llm(llm, learner_profile, learning_path, knowledge_point, perspectives_of_knowledge_point, knowledge_perspective)

    if allow_parallel:
        with ThreadPoolExecutor(max_wokrers) as executor:
            perspective_draft_list = list(executor.map(draft_single_perspective, perspective_list))
    else:
        for pid, knowledge_perspective in enumerate(perspective_list):
            print(f'*** {pid} - {knowledge_perspective} ***')
            perspective_draft = draft_knowledge_perspective_with_llm(llm, learner_profile, learning_path, knowledge_point, perspectives_of_knowledge_point, knowledge_perspective)
            perspective_draft_list.append(perspective_draft)
    # print("perspective_draft_list:", perspective_draft_list)
    
    knowledge_document = integrate_knowledge_document_with_llm(llm, learner_profile, learning_path, knowledge_point, perspectives_of_knowledge_point, perspective_draft_list)
    if not with_quiz:
        return knowledge_document
    document_quiz = generate_document_quizzes_with_llm(llm, learner_profile, knowledge_document, single_choice_count=3, multiple_choice_count=0, true_false_count=0, short_answer_count=0)
    knowledge_document['quizzes'] = document_quiz
    return knowledge_document

