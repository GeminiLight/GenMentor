from base import Agent
from prompts import learner_feedback_simulator_system_prompt, \
                    learner_feedback_simulator_task_prompt_path, \
                    learner_feedback_simulator_task_prompt_content


class LearnerFeedbackSimulator(Agent):

    def __init__(self, llm):
        super().__init__('LearnerFeedbackSimulator', llm=llm, json_output=True)

    def feedback_path(self, input_dict):
        """
        Simulate the learner feedback based on the provided learning path.

        Args:
            input_dict (dict):
                - learning_path (list): The learning path of the learner.
                - learner_profile (dict): The learner profile.

        Returns:
            dict: A dictionary containing the simulated learner feedback based on the provided learning path.
        """
        self.set_prompts(learner_feedback_simulator_system_prompt, learner_feedback_simulator_task_prompt_path)
        return self.act(input_dict)

    def feedback_content(self, input_dict):
        """
        Simulate the learner feedback based on the provided learning content.

        Args:
            input_dict (dict):
                - learning_content (str): The learning content of the learner.
                - learner_profile (dict): The learner profile.

        Returns:
            dict: A dictionary containing the simulated learner feedback based on the provided learning content.
        """
        self.set_prompts(learner_feedback_simulator_system_prompt, learner_feedback_simulator_task_prompt_content)
        return self.act(input_dict)