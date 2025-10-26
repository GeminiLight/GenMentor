import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from base.llm_factory import LLMFactory
# from base import BaseAgent  # Not used directly here; removed unused Agent import
from prompts import *

from modules.data_preprocessing.job_posting_preprocessing import JobPostingExtractor, extract_skills_from_job_postings, complete_tracks_of_dataset
from utils.preprocess import save_json

# Default to a local Ollama model for convenience; adjust as needed
llm = LLMFactory.create(model='llama-2-70b-chat', model_provider='ollama')

# df_job_postings = pd.read_csv('data/dataset/job_postings/postings.csv')
# print(len(df_job_postings))
# df_job_postings = df_job_postings.dropna(subset=['description'], how='any')
# df_job_postings = df_job_postings.dropna(subset=['title', 'description', 'skills_desc'], how='any')
# print(len(df_job_postings))
# key_columns = ['job_id', 'title', 'description', 'formatted_experience_level', 'skills_desc']
# df_job_postings = df_job_postings[key_columns]
# goal2skill_dataset = []
# job_posting_content_list = []

df_raw_goal2skill_dataset = pd.read_json('data/dataset/job_postings/goal2skill_dataset_0_2000.json')
goal2skill_with_tracks_dataset = complete_tracks_of_dataset(llm, df_raw_goal2skill_dataset[200:1000])
save_json('data/dataset/job_postings/goal2skill_with_tracks_dataset_200_1000.json', goal2skill_with_tracks_dataset)
# job_posting_proprocessor = JobPostingProprocessor(llm)
# start_idx = 0
# step = 200

# for dataset_id in range(1):
#     end_idx = start_idx + step
#     print(f"Processing dataset {start_idx} to {end_idx}")
#     num_samples = end_idx - start_idx
#     pbar = tqdm.tqdm(total=num_samples)

#     # Reset lists for each subset
#     job_posting_content_list = []
#     goal2skill_dataset = []
    
#     df_job_postings_subset = df_job_postings[start_idx:end_idx]
#     for i, job_posting in df_job_postings_subset.iterrows():
#         job_posting_content = f"Job Title: {job_posting['title']}.\n{job_posting['description']}. {job_posting['skills_desc']}"
#         job_posting_content_list.append(job_posting_content)
        
#         # Simulate agent's action to get goal-to-skill mapping
#         goal2skill_sample = job_posting_proprocessor.extract_skills({'job_posting': job_posting_content})
#         goal2skill_dataset.append(goal2skill_sample)
        
#         pbar.update(1)
    
#     # Save each subset to a separate JSON file
#     with open(f'data/dataset/job_postings/goal2skill_dataset_{start_idx}_{end_idx}.json', 'w') as f:
#         json.dump(goal2skill_dataset, f, indent=2)

#     # Close progress bar and update start index for the next range
#     pbar.close()
#     start_idx = end_idx