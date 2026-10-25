"""
train.py: Training, GroupKFold(5) Cross-Validation, and Gold Set Evaluation for Cyber Kavasam.
Writes metrics to models/metrics.json and persists trained model to models/kavasam.joblib.
"""

import os
import sys
import csv
import json
import numpy as np
from sklearn.model_selection import GroupKFold
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from app.engine import KavasamMLModel, check_message, MODEL_PATH, MESSAGES_CSV, MODEL_VERSION

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GOLD_CSV = os.path.join(BASE_DIR, "data", "gold_test.csv")
METRICS_JSON = os.path.join(BASE_DIR, "models", "metrics.json")

def load_data(path):
    texts, labels, groups, langs = [], [], [], []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            texts.append(row["text"])
            labels.append(row["label"])
            groups.append(row["group"])
            langs.append(row["lang"])
    return texts, labels, groups, langs

def run_group_kfold_cv(texts, labels, groups, n_splits=5):
    print(f"\n--- Running GroupKFold({n_splits}) Cross-Validation (by Template Group) ---")
    gkf = GroupKFold(n_splits=n_splits)
    y = np.array([1 if str(l).lower() == "scam" else 0 for l in labels])
    X = np.array(texts)
    groups_arr = np.array(groups)

    accuracies = []
    precisions = []
    recalls = []
    f1s = []

    fold = 1
    for train_idx, test_idx in gkf.split(X, y, groups=groups_arr):
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]

        model = KavasamMLModel()
        model.train(X_train, y_train)

        preds = [1 if model.predict_proba(t) >= 0.50 else 0 for t in X_test]

        acc = accuracy_score(y_test, preds)
        prec = precision_score(y_test, preds, zero_division=0)
        rec = recall_score(y_test, preds, zero_division=0)
        f1 = f1_score(y_test, preds, zero_division=0)

        accuracies.append(acc)
        precisions.append(prec)
        recalls.append(rec)
        f1s.append(f1)

        print(f"  Fold {fold}: Acc = {acc*100:.2f}%, Prec = {prec*100:.2f}%, Rec = {rec*100:.2f}%, F1 = {f1*100:.2f}%")
        fold += 1

    cv_results = {
        "mean_accuracy": float(np.mean(accuracies)),
        "mean_precision": float(np.mean(precisions)),
        "mean_recall": float(np.mean(recalls)),
        "mean_f1": float(np.mean(f1s))
    }
    print(f"CV Mean Accuracy: {cv_results['mean_accuracy']*100:.2f}%")
    print(f"CV Mean Precision: {cv_results['mean_precision']*100:.2f}%")
    print(f"CV Mean Recall:    {cv_results['mean_recall']*100:.2f}%")
    print(f"CV Mean F1-Score:  {cv_results['mean_f1']*100:.2f}%")
    return cv_results

def evaluate_gold_set(gold_path):
    print(f"\n--- Evaluating Full Hybrid Engine on Gold Test Set ({gold_path}) ---")
    texts, labels, groups, langs = load_data(gold_path)

    y_true = []
    y_pred = []
    misclassified = []

    for i, (text, true_label, gid, lang) in enumerate(zip(texts, labels, groups, langs)):
        res = check_message(text)
        verdict = res["verdict"]

        # Scam or Suspicious is treated as scam-positive detection
        pred_label = "scam" if verdict in ["Likely Scam", "Suspicious"] else "safe"

        true_num = 1 if true_label.lower() == "scam" else 0
        pred_num = 1 if pred_label == "scam" else 0

        y_true.append(true_num)
        y_pred.append(pred_num)

        if true_num != pred_num:
            misclassified.append({
                "index": i + 1,
                "group": gid,
                "lang": lang,
                "text": text,
                "expected": true_label,
                "verdict": verdict,
                "risk": res["risk"],
                "final_score": res["final_score"],
                "reasons": [r["en"] for r in res["reasons"]]
            })

    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)

    print(f"Gold Test Accuracy:  {acc*100:.2f}% ({len(y_true) - len(misclassified)}/{len(y_true)})")
    print(f"Gold Test Precision: {prec*100:.2f}%")
    print(f"Gold Test Recall:    {rec*100:.2f}%")
    print(f"Gold Test F1-Score:  {f1*100:.2f}%")

    if misclassified:
        print(f"\nMisclassified Gold Messages ({len(misclassified)}):")
        for m in misclassified:
            print(f"  [{m['index']}] ({m['lang']}) Expected: {m['expected']} | Got: {m['verdict']} (Risk: {m['risk']}%)")
            print(f"      Text: {m['text']}")
            print(f"      Reasons: {m['reasons']}")
    else:
        print("\nAll Gold Test Messages correctly classified!")

    return {
        "accuracy": float(acc),
        "precision": float(prec),
        "recall": float(rec),
        "f1": float(f1),
        "total_gold": len(y_true),
        "misclassified_count": len(misclassified),
        "misclassified": misclassified
    }

def main():
    print("=" * 60)
    print("CYBER KAVASAM - TRAINING & BENCHMARK SUITE")
    print("=" * 60)

    # 1. Load training data
    texts, labels, groups, langs = load_data(MESSAGES_CSV)
    print(f"Loaded {len(texts)} training samples across {len(set(groups))} template groups.")

    # 2. GroupKFold CV
    cv_metrics = run_group_kfold_cv(texts, labels, groups, n_splits=5)

    # 3. Fit final production model and save
    print(f"\n--- Fitting Final Production Model on All {len(texts)} Samples ---")
    final_model = KavasamMLModel()
    final_model.train(texts, labels)
    final_model.save(MODEL_PATH)
    print(f"Saved production model artifact to {MODEL_PATH}")

    # 4. Evaluate full hybrid engine on gold_test.csv
    gold_metrics = evaluate_gold_set(GOLD_CSV)

    # 5. Save all metrics
    metrics_data = {
        "model_version": MODEL_VERSION,
        "training_samples": len(texts),
        "template_groups": len(set(groups)),
        "cv_group_kfold_5": cv_metrics,
        "gold_test_set": {
            "total": gold_metrics["total_gold"],
            "accuracy": gold_metrics["accuracy"],
            "precision": gold_metrics["precision"],
            "recall": gold_metrics["recall"],
            "f1": gold_metrics["f1"],
            "misclassified_count": gold_metrics["misclassified_count"],
            "misclassified_samples": gold_metrics["misclassified"]
        }
    }

    os.makedirs(os.path.dirname(METRICS_JSON), exist_ok=True)
    with open(METRICS_JSON, "w", encoding="utf-8") as f:
        json.dump(metrics_data, f, indent=2)
    print(f"\nMetrics report saved to {METRICS_JSON}")
    print("=" * 60)

if __name__ == "__main__":
    main()
