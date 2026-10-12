"""
registry.py: maps mutation names to their classes.
"""

from mutations.base import Mutation
from mutations.technical_quality import BlurMutation
from mutations.standard_presentation import RotateMutation
from mutations.visual_clarity import ClarityMutation
from mutations.functional_relevance import FunctionalRelevanceMutation
from mutations.text_image_coherence import TextImageCoherenceMutation
from mutations.fair_representation import FairRepresentationMutation
from mutations.no_op import NoOpMutation

MUTATIONS: dict[str, type] = {
    "funct_relevance_substitution": FunctionalRelevanceMutation,
    "rotate": RotateMutation,
    "blur": BlurMutation,
    "coherence_substitution": TextImageCoherenceMutation,
    "clarity_shapes": ClarityMutation,
    "fair_repr_swap": FairRepresentationMutation,
    "no_op_control": NoOpMutation,
}


def get_mutation(name: str, *args, **kwargs) -> Mutation:
    """
    Looks up a mutation class by name and constructs it.
    Raises ValueError if the name isn't registered.
    """
    if name not in MUTATIONS:
        raise ValueError(f"Unknown mutation: {name}")
    mutation_class = MUTATIONS[name]
    return mutation_class(*args, **kwargs)
