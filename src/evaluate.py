"""Tahap evaluasi & validasi: bandingkan metrik model baru dengan ambang batas.

Exit code 1 kalau ada metrik `blocking` yang tidak lolos -> job GitHub Actions
gagal -> tahap registrasi model tidak dijalankan.
"""
import json
import os
import sys

import yaml

METRICS_PATH = "outputs/metrics.json"
THRESHOLDS_PATH = "config/thresholds.yaml"
EVALUATION_OUT = "outputs/evaluation.json"


def check_metrics(metrics, thresholds):
    """Kembalikan (lolos_semua_blocking, daftar_hasil_per_metrik)."""
    results = []
    for name, rule in thresholds.items():
        if name not in metrics:
            raise KeyError(f"Metrik '{name}' tidak ada di hasil training")
        value = metrics[name]
        if "min" in rule:
            passed, op, limit = value >= rule["min"], ">=", rule["min"]
        elif "max" in rule:
            passed, op, limit = value <= rule["max"], "<=", rule["max"]
        else:
            raise ValueError(f"Threshold '{name}' harus punya 'min' atau 'max'")
        results.append({
            "metric": name,
            "value": value,
            "rule": f"{op} {limit}",
            "blocking": bool(rule.get("blocking", True)),
            "passed": bool(passed),
        })
    all_blocking_passed = all(r["passed"] for r in results if r["blocking"])
    return all_blocking_passed, results


def status_label(r):
    if r["passed"]:
        return "PASS"
    return "FAIL" if r["blocking"] else "WARNING"


def render_markdown(run, results, passed):
    lines = [
        "## Tahap 3 - Model Evaluation & Validation",
        "",
        f"Run MLflow: `{run['run_id']}`  ",
        f"Hyperparameter: `{run['params']}`",
        "",
        "| Metrik | Nilai | Ambang | Blocking | Status |",
        "|---|---|---|---|---|",
    ]
    for r in results:
        lines.append(
            f"| {r['metric']} | {r['value']:.4f} | {r['rule']} | "
            f"{'ya' if r['blocking'] else 'tidak'} | {status_label(r)} |"
        )
    info = run["metrics"].get("R2_naive_baseline")
    if info is not None:
        lines += ["", f"Info: R2 baseline naif (harga hari ini = kemarin) = {info:.4f}"]
    lines += ["", f"**Hasil: {'LOLOS VALIDASI' if passed else 'GAGAL VALIDASI'}**"]
    return "\n".join(lines)


def main():
    with open(METRICS_PATH, encoding="utf-8") as f:
        run = json.load(f)
    with open(THRESHOLDS_PATH, encoding="utf-8") as f:
        thresholds = yaml.safe_load(f)["metrics"]

    passed, results = check_metrics(run["metrics"], thresholds)

    for r in results:
        print(f"[{status_label(r):7}] {r['metric']:22} = {r['value']:.4f}  (ambang {r['rule']}, blocking={r['blocking']})")
        if not r["passed"]:
            level = "error" if r["blocking"] else "warning"
            # Anotasi GitHub Actions supaya kelihatan jelas di halaman run
            print(f"::{level} title=Validasi {r['metric']}::{r['metric']}={r['value']:.4f} tidak memenuhi {r['rule']}")

    summary_path = os.getenv("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as f:
            f.write(render_markdown(run, results, passed) + "\n")

    os.makedirs(os.path.dirname(EVALUATION_OUT), exist_ok=True)
    with open(EVALUATION_OUT, "w", encoding="utf-8") as f:
        json.dump({"passed": passed, "results": results}, f, indent=2)

    print("HASIL:", "LOLOS VALIDASI" if passed else "GAGAL VALIDASI - model tidak akan didaftarkan")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
