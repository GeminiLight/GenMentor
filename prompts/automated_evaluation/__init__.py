from .goal2skill_mapping_evaluation import *
from .skill_gap_evaluation import *
from .learner_profile_evaluation import *
from .learning_path_evaluation import *
from .learning_content_evaluation import *

from ..basic_templetes import output_format_requirements_templete, batch_evaluation_requirements_prompt


# task_prompt_vars = [var_name for var_name in globals() if "task_prompt_batch" in var_name]
# for var_name in task_prompt_vars:
#     globals()[var_name] += batch_evaluation_requirements_prompt

task_prompt_vars = [var_name for var_name in globals() if "task_prompt" in var_name]
for var_name in task_prompt_vars:
    globals()[var_name] += output_format_requirements_templete