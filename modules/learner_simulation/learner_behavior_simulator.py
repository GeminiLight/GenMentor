from base import BaseAgent
from prompts import *
from utils import load_json, save_json


class GroundTruthProfileCreator(BaseAgent):

    name: str = 'GroundTruthProfileCreator'

    def __init__(self, model):
        super().__init__(model=model, jsonalize_output=True)

    def create_profile(self, input_dict, system_prompt=None, task_prompt=None):
        if system_prompt is None: system_prompt = ground_truth_profile_creator_system_prompt
        if task_prompt is None: task_prompt = ground_truth_profile_creator_task_prompt
        self.set_prompts(system_prompt, task_prompt)
        return self.act(input_dict)

    def progress_profile(self, input_dict, system_prompt=None, task_prompt=None):
        """
        Progress the ground-truth learner profile based on the provided session information.

        Args:
            input_dict (dict): Input dictionary containing the ground-truth profile and session information.
                - ground_truth_profile (dict): The ground-truth learner profile.
                - session_information (dict): Information about the current session.
        """
        if system_prompt is None: system_prompt = ground_truth_profile_creator_system_prompt
        if task_prompt is None: task_prompt = ground_truth_profile_creator_task_prompt_progress
        self.set_prompts(system_prompt, task_prompt)
        return self.act(input_dict)


class LearnerInteractionSimulator(BaseAgent):

    name: str = 'LearnerInteractionSimulator'

    def __init__(self, model):
        super().__init__(model=model, jsonalize_output=True)

    def simulate_interactions(self, input_dict, system_prompt=None, task_prompt=None):
        """
        Simulate learner interactions based on the ground-truth profile and session count.

        Args:
            input_dict (dict): Input dictionary containing the ground-truth profile and session count.
                - previous_ground_truth_profile (dict): The ground-truth learner profile.
                - progressed_ground_truth_profile (dict): The progressed ground-truth learner profile.
                - session_information (dict): Information about the current session.
        """
        if system_prompt is None: system_prompt = learner_interaction_simulator_system_prompt
        if task_prompt is None: task_prompt = learner_interaction_simulator_task_prompt
        self.set_prompts(system_prompt, task_prompt)
        return self.act(input_dict)

def create_ground_truth_profile_with_llm(llm, learning_goal, learner_information, skill_requirements):
    ground_truth_profile_creator = GroundTruthProfileCreator(llm)
    ground_truth_profile = ground_truth_profile_creator.create_profile({
        "learning_goal": learning_goal,
        "learner_information": learner_information,
        "skill_requirements": skill_requirements,
    })
    return ground_truth_profile

def simulate_learner_interactions_with_llm(llm, ground_truth_profile, session_count=5):
    print("==== Step 2: Simulate Learner Interactions ====")
    learner_behavior_simulator = LearnerInteractionSimulator(llm)
    behavior_logs = []

    for session in range(1, session_count + 1):
        behavior_log = learner_behavior_simulator.simulate_interactions({
            "ground_truth_profile": ground_truth_profile,
            "session_number": session
        })
        behavior_logs.append(behavior_log)
    save_json('data/behavior_logs.json', behavior_logs)
    return behavior_logs
