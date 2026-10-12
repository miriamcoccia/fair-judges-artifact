from domain.properties import QualityProperty, rubric_for


def test_six_properties():
    """
    The number of properties must be exactly 6
    """
    assert len(QualityProperty) == 6


def test_properties_have_rubric():
    """
    Each property should have a rubric containing a definition and a note.
    """
    for prop in QualityProperty:
        rubric = rubric_for(prop)
        assert rubric.definition != ""
        assert rubric.note != ""
