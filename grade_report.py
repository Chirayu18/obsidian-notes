"""Compute weighted course grades from per-assignment scores."""

WEIGHTS = {
    "homework": 0.30,
    "midterm": 0.30,
    "final": 0.40,
}


def weighted_average(scores, weights):
    """Combine category scores into a single 0-100 grade.

    Categories the student has no score for are excluded, and the
    remaining weights are renormalized so the result stays on 0-100.
    """
    total = 0.0
    weight_used = 0.0
    for category, weight in weights.items():
        if category not in scores:
            continue
        total += scores[category] * weight
        weight_used += weight
    return total / weight_used


def letter_grade(score):
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    return "F"


def build_report(students):
    report = []
    for name, scores in students.items():
        final = weighted_average(scores, WEIGHTS)
        report.append((name, round(final, 1), letter_grade(final)))
    report.sort(key=lambda row: row[1], reverse=True)
    return report


if __name__ == "__main__":
    students = {
        "Ada": {"homework": 95.0, "midterm": 88.0, "final": 92.0},
        "Grace": {"homework": 78.0, "midterm": 85.0, "final": 80.0},
        # Kim missed the midterm entirely.
        "Kim": {"homework": 90.0, "final": 85.0},
        # Sam enrolled late and has no graded work yet.
        "Sam": {},
    }

    for name, score, grade in build_report(students):
        print(f"{name:<8} {score:>6}  {grade}")
