"""
properties.py: In this file, we define the names of the properties to be used throughout the project
alongside their definitions.
"""

from enum import StrEnum
from dataclasses import dataclass
from types import MappingProxyType


class QualityProperty(StrEnum):
    FUNCTIONAL_RELEVANCE = "functional_relevance"
    VISUAL_CLARITY = "visual_clarity"
    TECHNICAL_QUALITY = "technical_quality"
    STANDARD_PRESENTATION = "standard_presentation"
    TEXT_IMAGE_COHERENCE = "text_image_coherence"
    FAIR_REPRESENTATION = "fair_representation"


@dataclass(frozen=True)
class Rubric:
    definition: str
    note: str


RUBRIC: dict[QualityProperty, Rubric] = {
    QualityProperty.FUNCTIONAL_RELEVANCE: Rubric(
        definition=(
            "functional_relevance evaluates if an image provides information directly relevant to answering a question, either by being essential for the answer or by significantly aiding comprehension. The image's purpose should be to assist in answering the question, not merely to serve as a decorative element."
        ),
        note="The image should help to answer the question, not just to decorate it.",
    ),
    QualityProperty.VISUAL_CLARITY: Rubric(
        definition=(
            "visual_clarity evaluates the directness of the image in representing only what is needed to answer the question, without unnecessary clutter, decorations, or competing elements that could distract from the main content. Important items should be clearly identifiable to reduce the mental effort needed for visual search. "
        ),
        note=("The image should be focused and free from visual distractions."),
    ),
    QualityProperty.TECHNICAL_QUALITY: Rubric(
        definition=(
            "technical_quality measures whether an image has sufficient resolution, contrast, and legibility for all important elements (including any text, labels, or fine details) to be easily perceived. Poor technical quality can create construct-irrelevant difficulty."
        ),
        note=(
            "The image should be sharp, clear, and easy to see."
            "The text, if present, should be readable."
            "The details, id present, should be visible without straining. "
        ),
    ),
    QualityProperty.STANDARD_PRESENTATION: Rubric(
        definition=(
            "standard_presentation considers whether images and their elements appear in expected orientations and follow conventional representations familiar to the test population. Non-standard orientations can add construct-irrelevant cognitive load by requiring mental rotation."
        ),
        note=(
            "Images should be presented in the orientation that is conventional for the subject."
            "Unusual rotations or mirroring require extra mental effort."
        ),
    ),
    QualityProperty.TEXT_IMAGE_COHERENCE: Rubric(
        definition=(
            "text_image_coherence assesses whether the image and text components of a question convey consistent information without contradictions or unnecessary spatial separation. Misalignment can alter the interpretation of the question or create a split-attention effect."
        ),
        note=(
            "The image and the corresponding text should not contain contradictory information."
        ),
    ),
    QualityProperty.FAIR_REPRESENTATION: Rubric(
        definition=(
            "fair_representation evaluates whether an image is free of bias, "
            "stereotyping, and unfair treatment of any group. The image FAILS "
            "this property if it shows ANY of the following:\n"
            "1. Culturally insensitive or offensive depictions.\n"
            "2. Exaggerated stereotypes in clothing, skin tone, setting, or facial features.\n"
            "3. Objects or symbols carrying implicit bias or discriminatory connotations.\n"
            "4. Stereotypes or caricatures that distort a group's characteristics.\n"
            "5. Settings where certain groups are systematically excluded or marginalized.\n"
            "6. Certain groups or perspectives underrepresented.\n"
            "7. Diversity portrayed inaccurately, or cultures/identities misrepresented.\n"
            "8. Human experiences flattened or oversimplified, ignoring marginalized groups.\n"
            "9. Negative traits (crime, poverty, danger) associated with a specific group.\n"
            "10. Content with potential to cause harm or reinforce prejudice.\n"
            "11. Unfair or unjust treatment of any depicted individual or group.\n"
            "12. Inappropriate or stereotypical sexualization of individuals.\n"
            "13. Misleading or manipulated content that reinforces bias.\n"
            "14. Visual marginalization through unequal lighting or off-center composition.\n"
            "15. Visual style that trivializes or demeans a serious identity or subject.\n"
            "16. Exaggerated or mocking features that ridicule a group or individual.\n"
            "17. Unbalanced power dynamics, such as dominance or subordination.\n"
            "18. Outdated, colonial, or exoticizing stereotypes.\n"
            "19. Degradation or dehumanization based on race, gender, ethnicity, "
            "religion, or socioeconomic status.\n\n"
            "If NONE of the above apply, the image passes."
        ),
        note=(
            "Check the image against every item above. A single match is enough "
            "to fail the property — the checks are not averaged or weighted."
        ),
    ),
}

# Makes the definitions read-only
RUBRIC = MappingProxyType(RUBRIC)


# Lookup properties
def rubric_for(prop: QualityProperty) -> Rubric:
    return RUBRIC[prop]
