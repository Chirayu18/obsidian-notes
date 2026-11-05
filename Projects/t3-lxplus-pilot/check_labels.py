from labels import count_labels


cases = [
    ([], {}),
    (["", "  "], {}),
    ([" ALPHA ", "alpha", "Beta", ""], {"alpha": 2, "beta": 1}),
    (["Straße", "STRASSE"], {"strasse": 2}),
]

for labels, expected in cases:
    actual = count_labels(labels)
    assert actual == expected, (labels, actual, expected)

print("PASS: empty input, blanks, whitespace and Unicode case folding")
