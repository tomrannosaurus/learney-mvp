import math
from typing import Any, Dict, Tuple

import numpy as np
from django.db import models

from accounts.models import User
from knowledge_maps.models import Concept
from learney_backend.base_models import UUIDModel
from questions.inference import GaussianParams


class QuestionBatch(UUIDModel):
    user = models.ForeignKey(
        User,
        related_name="question_batches",
        help_text="User whose question-answer batch this is",
        on_delete=models.CASCADE,
    )
    concept = models.ForeignKey(
        Concept,
        related_name="question_batches",
        help_text="The concept that the question batch corresponds to",
        on_delete=models.CASCADE,
    )

    time_started = models.DateTimeField(
        auto_now_add=True, help_text="Time that the question batch was started"
    )
    time_taken_to_complete = models.DateTimeField(
        null=True,
        default=None,
        help_text="Time after the question batch was started that it was completed",
    )
    completed = models.CharField(
        default="",
        max_length=28,
        help_text="Whether the user completed the batch and the type of completion",
    )
    initial_knowledge_mean = models.FloatField(
        help_text="Mean of the user's knowledge state when they started the question batch"
    )
    initial_knowledge_std_dev = models.FloatField(
        help_text="Standard deviation of the user's knowledge state when they started the question batch"
    )
    levels_progressed = models.IntegerField(
        default=0, help_text="How many levels the user progressed in this question batch"
    )
    concept_completed = models.BooleanField(
        default=False,
        help_text="Whether the highest level of the concept was achieved in this question batch",
    )
    session_id = models.TextField(help_text="session_id of the session the response was from")

    @property
    def initial_knowledge_level(self) -> int:
        return math.floor(
            GaussianParams(
                mean=self.initial_knowledge_mean, std_dev=self.initial_knowledge_std_dev
            ).level
        )

    @property
    def is_revision_batch(self) -> bool:
        return self.initial_knowledge_level > self.concept.max_difficulty_level

    @property
    def max_number_of_questions(self) -> int:
        return 5 if self.is_revision_batch else 10

    def json(self) -> Dict[str, Any]:
        responses = self.responses.all().select_related("question_template__concept")
        return {
            "id": self.id,
            "questions": [response.json for response in responses],
            "answers_given": [response.response for response in responses],
            "completed": self.completed,
            "concept_id": self.concept.cytoscape_id,
            "initial_knowledge_level": self.initial_knowledge_level,
            "max_num_questions": self.max_number_of_questions,
        }

    @property
    def training_data(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        answered_responses = self.responses.all().exclude(response=None)
        difficulties = np.array(
            [response.question_template.difficulty for response in answered_responses]
        )
        guess_probs = np.array(
            [1 / response.question_template.number_of_answers for response in answered_responses]
        )
        correct = np.array([response.correct for response in answered_responses])
        return difficulties, guess_probs, correct

    @property
    def initial_knowledge_state(self) -> GaussianParams:
        return GaussianParams(
            mean=self.initial_knowledge_mean, std_dev=self.initial_knowledge_std_dev
        )
