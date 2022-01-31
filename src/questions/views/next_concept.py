from typing import Dict, List

import numpy as np
from django.db.models import QuerySet
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from goals.models import GoalModel
from knowledge_maps.models import Concept, KnowledgeMapModel
from learned.models import LearnedModel
from learney_web.settings import QUESTIONS_PREREQUISITE_DICT
from link_clicks.models import LinkClickModel
from questions.models.question_set import QuestionSet


class NextConceptView(APIView):
    def get(self, request: Request, format=None) -> Response:
        """Gets the concept that we suggest the user work on next.

        It first gets the concept of the previous question set you did (if that concept
        isn't completed already). Then it looks for valid next steps given your goals
        and what you've learned and picks based on content link clicks and if you haven't
        clicked any content - it picks randomly from these.

        If there is no goal set then it returns None.
        """
        try:
            user_id = request.GET["user_id"]

            # Set seed in case randomness is required (for reproducibility)
            np.random.seed(1)

            # Grab the concepts that are learned
            map = KnowledgeMapModel.objects.get(url_extension="questionsmap")
            learned_concepts_queryset: QuerySet[LearnedModel] = LearnedModel.objects.filter(
                user_id=user_id, map=map
            )
            learned_concepts: Dict[str, str] = (
                learned_concepts_queryset.latest("timestamp").learned_concepts
                if learned_concepts_queryset.count() > 0
                else {}
            )

            prev_question_sets: QuerySet[QuestionSet] = QuestionSet.objects.filter(
                user__id=user_id
            ).prefetch_related("concept__direct_prerequisites")
            if prev_question_sets.count() > 0:
                # [0] Get the most recent question set
                prev_question_set: QuestionSet = prev_question_sets.latest("time_started")

                if (
                    prev_question_set.concept.id not in learned_concepts
                ):  # [1.0] Concept is not learned
                    return Response(
                        {"concept_id": prev_question_set.concept.cytoscape_id},
                        status=status.HTTP_200_OK,
                    )
                # [2.0] Find valid concepts
                valid_next_concepts = get_valid_current_concept_ids(user_id, map, learned_concepts)
                if len(valid_next_concepts) == 0:
                    return Response({"concept_id": None}, status=status.HTTP_200_OK)
                # Prefer if a successor to the concept the previous question set was on
                valid_successors: List[Concept] = list(
                    Concept.objects.filter(
                        direct_prerequisites=prev_question_set.concept,
                        cytoscape_id__in=valid_next_concepts,
                    )
                )

                if len(valid_successors) == 1:
                    return Response(
                        {"concept_id": valid_successors[0].cytoscape_id},
                        status=status.HTTP_200_OK,
                    )
                elif len(valid_successors) > 2:
                    # [2.3] If multiple successors, go for the one which has had a content link clicked by this user before
                    return use_link_clicks_or_random(
                        map, user_id, [s.cytoscape_id for s in valid_successors]
                    )
                else:  # [2.4] Otherwise try other valid concepts
                    return use_link_clicks_or_random(map, user_id, valid_next_concepts)

            else:  # [3.0] No past question sets
                map = KnowledgeMapModel.objects.get(url_extension="questionsmap")
                valid_next_concepts = get_valid_current_concept_ids(user_id, map, learned_concepts)
                if len(valid_next_concepts) == 0:
                    return Response({"concept_id": None}, status=status.HTTP_200_OK)
                return use_link_clicks_or_random(map, user_id, valid_next_concepts)

            # Display an error if something goes wrong.
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)


def get_valid_current_concept_ids(
    user_id: str, map: KnowledgeMapModel, learned_concepts: Dict[str, str]
) -> List[str]:
    """Get concept ids of concepts which are potential next concepts for the user.

    This means they are both on the path to one of their goals and all prerequisites are set as
    learned.
    """
    # [2.1] Towards their goal
    goals_queryset = GoalModel.objects.filter(user_id=user_id, map=map)
    goals = goals_queryset.latest("timestamp").goal_concepts if goals_queryset.count() > 0 else {}
    is_towards_goal = [
        any(concept_id in QUESTIONS_PREREQUISITE_DICT[goal_id] for goal_id in goals)
        for concept_id in QUESTIONS_PREREQUISITE_DICT
    ]

    # [2.2] All prerequisites learned
    prereqs_learned = [
        all(
            learned_concepts.get(prereq, False)
            for prereq in QUESTIONS_PREREQUISITE_DICT[concept_id]
        )
        for concept_id in QUESTIONS_PREREQUISITE_DICT
    ]
    return [
        concept_id
        for count, concept_id in enumerate(QUESTIONS_PREREQUISITE_DICT)
        if prereqs_learned[count] and is_towards_goal[count]
    ]


def use_link_clicks_or_random(
    map: KnowledgeMapModel, user_id: str, possible_concept_ids: List[str]
):
    """From `possible_concept_ids`, pick the concept which has had a content link click clicked on
    it most recently if any have ever been clicked.

    Otherwise, pick randomly!
    """
    relevant_link_clicks = LinkClickModel.objects.filter(
        map=map, user_id=user_id, concept_id__in=possible_concept_ids
    )
    return Response(
        {
            "concept_id": relevant_link_clicks.latest("timestamp").concept_id
            if relevant_link_clicks.count() > 0
            else np.random.choice(possible_concept_ids)
        },
        status=status.HTTP_200_OK,
    )
