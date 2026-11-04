#!/usr/bin/env python3
"""Score an archived DQN-FV prediction JSONL with the project's FEVER scorer."""

import argparse
import json
import sys
from pathlib import Path


def _install_six_compatibility_shim():
    """The scorer only uses six.string_types, so support stdlib-only installs."""
    try:
        import six  # noqa: F401
    except ImportError:
        class SixCompatibility:
            string_types = (str,)

        sys.modules["six"] = SixCompatibility()


def main():
    parser = argparse.ArgumentParser(
        description="Compute FEVER metrics for saved DQN-FV predictions."
    )
    parser.add_argument("predictions", help="Path to a saved predictions JSONL file")
    args = parser.parse_args()

    prediction_path = Path(args.predictions)
    if not prediction_path.is_file():
        parser.error("prediction file does not exist: {}".format(prediction_path))

    _install_six_compatibility_shim()
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from eval.scorer import fever_score

    rows = []
    seen_ids = set()
    with prediction_path.open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, 1):
            try:
                row = json.loads(line)
            except ValueError as error:
                parser.error("invalid JSON on line {}: {}".format(line_number, error))
            for field in ("id", "label", "evidence", "predicted_label", "predicted_evidence"):
                if field not in row:
                    parser.error("line {} is missing {!r}".format(line_number, field))
            if row["id"] in seen_ids:
                parser.error("duplicate prediction id on line {}: {}".format(line_number, row["id"]))
            seen_ids.add(row["id"])
            rows.append(row)

    if not rows:
        parser.error("prediction file is empty")

    strict, accuracy, precision, recall, f1 = fever_score(rows)
    print("Saved DQN-FV predictions: {}".format(prediction_path))
    print("Records: {}".format(len(rows)))
    print(
        "FEVER: {:.4f} | Label accuracy: {:.4f} | Evidence precision: {:.4f} | "
        "Evidence recall: {:.4f} | F1: {:.4f}".format(
            strict, accuracy, precision, recall, f1
        )
    )


if __name__ == "__main__":
    main()

