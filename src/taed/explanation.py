import lime.lime_text


def get_explanation_features(text, explainer, pipeline):
    """Extract top explanation features using LIME."""
    try:
        exp = explainer.explain_instance(
            text,
            pipeline.predict_proba,
            num_features=3
        )
        return [feature for feature, _ in exp.as_list()]
    except Exception:
        return []
