from typing import Any, Dict, Optional

import numpy as np
from django.db import models

from knowledge_maps.models import Concept
from learney_backend.base_models import UUIDModel
from questions.template_parser import (
    answer_regex,
    expand_params_in_text,
    parse_params,
    sample_params,
    says_feedback,
)
from questions.utils import SampledParamsDict, get_frontend_id
from questions.validators import integer_is_positive, not_null


class QuestionTemplate(UUIDModel):
    concept = models.ForeignKey(
        Concept,
        related_name="question_templates",
        help_text="Concept that the question corresponds to",
        on_delete=models.CASCADE,
    )
    difficulty = models.FloatField(
        help_text="Question difficulty for the concept. Initially set by an expert, but will "
        "subsequently be inferred from data. A relative scale, with 0 the lowest "
        "possible and as many difficulty levels as is deemed makes sense by the expert.",
        validators=[integer_is_positive],
    )
    question_type = models.TextField(
        help_text="Text for question template - generates full question",
        blank=False,
        validators=[not_null],
    )

    template_text = models.TextField(
        help_text="Text for question template - generates full questions",
        blank=False,
        validators=[not_null],
        max_length=16384,
    )
    correct_answer_letter = models.CharField(
        max_length=1,
        help_text="Answer option (a, b, c or d) which is the correct answer to the question",
        choices=[
            ("a", "Option a)"),
            ("b", "Option b)"),
            ("c", "Option c)"),
            ("d", "Option d)"),
        ],
        blank=False,
    )
    active = models.BooleanField(
        default=False,
        help_text="If questions from the template should be used onthe live site - "
        "broken questions should be deactivated until they're fixed!",
    )
    last_updated = models.DateTimeField(auto_now=True)

    @property
    def number_of_answers(self) -> int:
        num_answers = sum(
            answer_regex(line) is not None for line in self.template_text.splitlines()
        )
        assert num_answers in [
            2,
            4,
        ], f"Invalid number of answers ({num_answers}) for {self.id}. Template:\n{self.template_text}"
        return num_answers

    def to_question_json(
        self, sampled_params: Optional[SampledParamsDict] = None
    ) -> Dict[str, Any]:
        """Gets question dictionary from a template and set of sampled parameters."""
        parsed_params, remaining_text = parse_params(self.template_text)
        if sampled_params is None:
            sampled_params = sample_params(parsed_params)
        text_expanded = expand_params_in_text(remaining_text, sampled_params)

        question_text, answers, feedback, is_feedback = "", {}, "", False
        for index, line in enumerate(text_expanded.splitlines()):
            is_feedback = is_feedback or says_feedback(line)
            if line:
                regex = answer_regex(line)
                if not is_feedback and regex is not None:
                    answers[regex.groups()[0].lower()] = regex.groups()[1]
                elif not is_feedback:
                    question_text += line + "\n"
                elif not says_feedback(line):  # skip the word 'feedback'
                    feedback += line + "\n"

        answers_order_randomised = [a for a in answers.values()]
        np.random.shuffle(answers_order_randomised)

        return {
            "id": get_frontend_id(self.id, sampled_params),
            "question_text": question_text[:-1] if question_text else "",
            "answers_order_randomised": answers_order_randomised,
            "correct_answer": answers[self.correct_answer_letter],
            "feedback": feedback[:-1] if feedback else "",
            "params": sampled_params,
        }
