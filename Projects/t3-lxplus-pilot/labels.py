from collections import Counter


def count_labels(labels):
    """Count nonblank labels, ignoring surrounding whitespace and case."""
    cleaned = (label.strip() for label in labels)
    return dict(Counter(label for label in cleaned if label))
