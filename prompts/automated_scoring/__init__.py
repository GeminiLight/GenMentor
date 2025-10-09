from .goal2skill_mapping_scoring import *
from .skill_gap_scoring import *
from .learner_profile_scoring import *
from .learning_path_scoring import *
from .learning_content_scoring import *

from ..basic_templetes import output_format_requirements_templete, batch_evaluation_requirements_prompt

# task_prompt_vars = [var_name for var_name in globals() if "task_prompt_batch" in var_name]
# for var_name in task_prompt_vars:
#     globals()[var_name] += batch_evaluation_requirements_prompt

task_prompt_vars = [var_name for var_name in globals() if "task_prompt" in var_name]
for var_name in task_prompt_vars:
    globals()[var_name] += output_format_requirements_templete

