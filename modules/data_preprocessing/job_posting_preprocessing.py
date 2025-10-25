"""Utilities for extracting structured skill data from job postings via LLM agents."""

from __future__ import annotations

from typing import Any, Mapping, Sequence, TypedDict

import pandas as pd
from tqdm.auto import tqdm

from base import BaseAgent
from prompts import (
    goal2skill_cot_completor_system_prompt,
    goal2skill_cot_completor_task_prompt,
    job_posting_extractor_system_prompt,
    job_posting_extractor_task_prompt,
)


class SkillRequirement(TypedDict):
    """Structure describing a single skill requirement for a job posting."""

    name: str
    level: str


class Goal2SkillSample(TypedDict):
    """Output of the job posting extractor agent."""

    job_title: str
    job_type: str
    job_description: str
    skill_requirements: Sequence[SkillRequirement]


class Goal2SkillSampleWithTracks(TypedDict, total=False):
    """Extended Goal2Skill sample with reasoning tracks provided by the CoT completor."""

    job_title: str
    job_type: str
    job_description: str
    skill_requirements: Sequence[SkillRequirement]
    tracks: Sequence[Mapping[str, Any]]


class JobPostingExtractor(BaseAgent):
    """Agent responsible for turning free-form job postings into structured samples."""

    name: str = "JobPostingExtractor"

    def __init__(self, model: Any) -> None:
        """Create a job posting extractor with JSON output enforced."""

        super().__init__(model=model, jsonalize_output=True)

    def check_json_output(self, output: Mapping[str, Any]) -> bool:
        """Validate the JSON payload produced by the underlying LLM."""

        expected_fields = {"job_title", "job_type", "job_description", "skill_requirements"}
        if set(output.keys()) != expected_fields:
            raise ValueError(f"Unexpected output format. Expected keys {expected_fields}, got {output.keys()}")

        requirements = output.get("skill_requirements", [])
        if not isinstance(requirements, Sequence):
            raise ValueError("'skill_requirements' must be a sequence")

        for requirement in requirements:
            if not isinstance(requirement, Mapping):
                raise ValueError("Each skill requirement must be a mapping containing 'name' and 'level'")
            missing_fields = {"name", "level"} - set(requirement.keys())
            if missing_fields:
                raise ValueError(f"Skill requirement missing fields: {missing_fields}")

        return True

    def preprocess_posting(self, input_dict: Mapping[str, str]) -> Goal2SkillSample:
        """Extract a structured skill sample from a raw job posting string."""

        self.set_prompts(job_posting_extractor_system_prompt, job_posting_extractor_task_prompt)
        result: Goal2SkillSample = self.act(dict(input_dict))
        self.check_json_output(result)
        return result

    def extract_skills(self, job_posting: str) -> Goal2SkillSample:
        """Convenience wrapper that accepts a raw posting string and returns structured output."""

        return self.preprocess_posting({"job_posting": job_posting})


class Goal2SkillCotCompletor(BaseAgent):
    """Agent that enriches extracted samples with chain-of-thought tracks."""

    name: str = "Goal2SkillCotCompletor"

    def __init__(self, model: Any) -> None:
        super().__init__(model=model, jsonalize_output=True)

    def complete_tracks(self, input_dict: Mapping[str, Any]) -> Goal2SkillSampleWithTracks:
        """Generate reasoning tracks for an existing Goal2Skill sample."""

        self.set_prompts(goal2skill_cot_completor_system_prompt, goal2skill_cot_completor_task_prompt)
        result: Goal2SkillSampleWithTracks = self.act(dict(input_dict))
        tracks = result.get("tracks")
        if tracks is not None:
            if not isinstance(tracks, Sequence):
                raise ValueError("'tracks' must be a sequence of reasoning steps")
            for track in tracks:
                if not isinstance(track, Mapping):
                    raise ValueError("Each track must be a mapping describing the reasoning step")
        return result


def format_job_posting_content(title: Any, description: Any, skills_desc: Any) -> str:
    """Normalise the raw job posting fields into a single prompt string."""

    def _normalise_field(field: Any) -> str:
        if pd.isna(field):
            return ""
        if isinstance(field, str):
            return field.strip()
        return str(field).strip()

    title_text = _normalise_field(title) or "Unknown role"
    description_text = _normalise_field(description)
    skills_text = _normalise_field(skills_desc)

    components = [f"Job Title: {title_text}"]
    if description_text:
        components.append(description_text)
    if skills_text:
        components.append(skills_text)
    return "\n".join(components)


def preprocess_posting_with_llm(llm: Any, job_posting: str) -> Goal2SkillSample:
    """Run the job posting extractor for a single posting string."""

    job_posting_extractor = JobPostingExtractor(llm)
    return job_posting_extractor.extract_skills(job_posting)


def extract_skills_from_job_postings(llm: Any, raw_job_posting_dataset: pd.DataFrame) -> Sequence[Goal2SkillSample]:
    """Convert a tabular dataset containing job postings into structured samples."""

    required_columns = {"title", "description", "skills_desc"}
    missing_columns = required_columns - set(raw_job_posting_dataset.columns)
    if missing_columns:
        raise ValueError(f"Input dataset is missing required columns: {missing_columns}")

    dataset_size = len(raw_job_posting_dataset)
    job_posting_extractor = JobPostingExtractor(llm)
    goal2skill_dataset: list[Goal2SkillSample] = []

    with tqdm(total=dataset_size, desc="Extracting skills", unit="posting") as progress:
        for row in raw_job_posting_dataset.itertuples(index=False):
            job_posting_content = format_job_posting_content(
                getattr(row, "title", ""),
                getattr(row, "description", ""),
                getattr(row, "skills_desc", ""),
            )
            goal2skill_sample = job_posting_extractor.extract_skills(job_posting_content)
            goal2skill_dataset.append(goal2skill_sample)
            progress.update(1)

    return goal2skill_dataset


def complete_tracks_of_dataset(
    llm: Any, raw_goal2skill_dataset: pd.DataFrame
) -> Sequence[Goal2SkillSampleWithTracks]:
    """Augment a dataset of Goal2Skill samples with chain-of-thought tracks."""

    required_columns = {"job_title", "job_type", "job_description", "skill_requirements"}
    missing_columns = required_columns - set(raw_goal2skill_dataset.columns)
    if missing_columns:
        raise ValueError(f"Input dataset is missing required columns: {missing_columns}")

    dataset_size = len(raw_goal2skill_dataset)
    goal2skill_cot_completor = Goal2SkillCotCompletor(llm)
    completed_goal2skill_dataset: list[Goal2SkillSampleWithTracks] = []

    with tqdm(total=dataset_size, desc="Completing tracks", unit="sample") as progress:
        for row in raw_goal2skill_dataset.itertuples(index=False):
            sample_payload: Goal2SkillSample = {
                "job_title": getattr(row, "job_title", ""),
                "job_type": getattr(row, "job_type", ""),
                "job_description": getattr(row, "job_description", ""),
                "skill_requirements": getattr(row, "skill_requirements", []),
            }

            completed_tracks = goal2skill_cot_completor.complete_tracks(sample_payload)
            tracks = completed_tracks.get("tracks")
            if tracks is None:
                raise ValueError("LLM response missing required 'tracks' field")

            if not isinstance(tracks, Sequence):
                raise ValueError("'tracks' must be a sequence of reasoning steps")
            for track in tracks:
                if not isinstance(track, Mapping):
                    raise ValueError("Each track must be a mapping describing the reasoning step")

            sample_with_tracks: Goal2SkillSampleWithTracks = {
                "job_title": sample_payload["job_title"],
                "job_type": sample_payload["job_type"],
                "job_description": sample_payload["job_description"],
                "skill_requirements": sample_payload["skill_requirements"],
                "tracks": tracks,
            }

            completed_goal2skill_dataset.append(sample_with_tracks)
            progress.update(1)

    return completed_goal2skill_dataset