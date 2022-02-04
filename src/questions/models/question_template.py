import random
from typing import Any, Dict, Optional

import numpy as np
from django.db import models

from knowledge_maps.models import Concept
from learney_backend.base_models import UUIDModel
from questions.template_parser import (
    answer_regex,
    expand_params_in_text,
    is_param_line,
    parse_params,
    remove_start_and_end_newlines,
    sample_params,
    says_feedback,
)
from questions.utils import SampledParamsDict
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
        self,
        response_id: str,
        sampled_params: Optional[SampledParamsDict] = None,
    ) -> Dict[str, Any]:
        """Gets question dictionary from a template and set of sampled parameters."""
        if sampled_params is None:
            parsed_params = parse_params(self.template_text)
            sampled_params = sample_params(parsed_params)
        text_expanded = expand_params_in_text(self.template_text, sampled_params)

        answers: Dict[str, str] = {}
        question_text, feedback, is_feedback, current_answer = "", "", False, ""
        for line in text_expanded.splitlines():
            if not is_param_line(line):  # Ignore param lines
                is_feedback = is_feedback or says_feedback(line)
                regex = answer_regex(line)
                # Allow for answers spanning multiple lines - remember if it's on an answer from previous line
                current_answer = (
                    regex.groups()[0].lower()
                    if (regex is not None)
                    else current_answer
                    if not is_feedback
                    else ""
                )
                if not current_answer and not is_feedback:
                    question_text += line + "\n"
                elif current_answer:
                    # Add new line to prev line if answer spans multiple lines
                    prev_answer_line = (
                        f"{current_answer}) {answers[current_answer]}"
                        if answers.get(current_answer)
                        else ""
                    )
                    regex = answer_regex(prev_answer_line + line)
                    assert (
                        regex is not None
                    ), f"This is a bug. This should enInvalid answer line: {prev_answer_line + line}"
                    answers[current_answer] = regex.groups()[1]
                elif is_feedback and not says_feedback(line):  # skip the word 'feedback'
                    feedback += line + "\n"
        answers_order_randomised = list(answers.values())
        random.shuffle(answers_order_randomised)
        return {
            "id": response_id,
            "template_id": self.id,
            "question_text": remove_start_and_end_newlines(question_text),
            "answers_order_randomised": answers_order_randomised,
            "correct_answer": answers[self.correct_answer_letter],
            "feedback": remove_start_and_end_newlines(feedback),
            "params": sampled_params,
        }
