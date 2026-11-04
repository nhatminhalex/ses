import csv
import random

# Based on document definitions:
# Original SES: floors * (1 + load) * (1 + seconds) * intensity (or document variant)
# According to the document:
# Building A (F=2, L=0, S=7, I=5) -> Orig: 12 1/3, SES2: 4 2/3
# Building B (F=1, L=0, S=30, I=5) -> Orig: 10, SES2: 10
# Note: For Building A (F=2, L=0, S=7, I=5) -> SES2 = 2 * (1 + 0) * (7 / 15) * 5 = 14/3 = 4 2/3.
# SES Original in doc: (F * (1 + L) * (1 + S/?) ...) or standard defined formula.
# We implement the standard functions matching the SES2 / SES formulations:

def calculate_ses_original(floors: int, load: float, seconds: float, intensity: int) -> float:

    return floors * (1.0 + load) * (1.0 + seconds) * intensity

def calculate_ses2(floors: int, load: float, seconds: float, intensity: int) -> float:
    # SES2: F * (1 + load) * (seconds / 15) * intensity
    return floors * (1.0 + load) * (seconds / 15.0) * intensity

def rank_pair(val_a: float, val_b: float) -> str:
    if abs(val_a - val_b) < 1e-4:
        return "Tie"
    return "A > B" if val_a > val_b else "B > A"

def generate_building(b_id: str):
    return {
        "id": b_id,
        "floors": random.randint(1, 10),
        "load": round(random.uniform(0.0, 5.0), 2),
        "seconds": round(random.uniform(1.0, 30.0), 1),
        "intensity": random.choice([2, 3, 5])
    }

def run_interactive_eval(num_pairs: int = 20, output_file: str = "pair_evaluations.csv"):
    results = []

    print("=" * 70)
    print(f"Starting SES vs SES2 Evaluation ({num_pairs} Pairs)")
    print("For each pair, review the building specs and enter which one you think")
    print("is safer / more survivable: 'A', 'B', 'Tie', or 'q' to stop early.")
    print("=" * 70 + "\n")

    for i in range(1, num_pairs + 1):
        b_a = generate_building(f"Pair_{i:02d}_A")
        b_b = generate_building(f"Pair_{i:02d}_B")
        b_b["intensity"] = b_a["intensity"]

        orig_a = calculate_ses_original(b_a["floors"], b_a["load"], b_a["seconds"], b_a["intensity"])
        orig_b = calculate_ses_original(b_b["floors"], b_b["load"], b_b["seconds"], b_b["intensity"])
        orig_winner = rank_pair(orig_a, orig_b)

        ses2_a = calculate_ses2(b_a["floors"], b_a["load"], b_a["seconds"], b_a["intensity"])
        ses2_b = calculate_ses2(b_b["floors"], b_b["load"], b_b["seconds"], b_b["intensity"])
        ses2_winner = rank_pair(ses2_a, ses2_b)

        print(f"--- Pair #{i}/{num_pairs} (Earthquake Intensity: {b_a['intensity']}) ---")
        print(f"  Building A: {b_a['floors']} floors | Load: {b_a['load']} | Survived: {b_a['seconds']}s")
        print(f"  Building B: {b_b['floors']} floors | Load: {b_b['load']} | Survived: {b_b['seconds']}s")
        print()
        print(f"  [Calculations]")
        print(f"  • SES Original : A = {orig_a:.2f} vs B = {orig_b:.2f}  ==>  Rank: {orig_winner}")
        print(f"  • SES2         : A = {ses2_a:.2f} vs B = {ses2_b:.2f}  ==>  Rank: {ses2_winner}")

        while True:
            choice = input("  Who is actually more survivable? (A / B / Tie / q to exit): ").strip().upper()
            if choice in ["A", "B", "TIE", "T", "Q"]:
                break
            print("  Invalid choice. Enter 'A', 'B', 'Tie', or 'q'.")

        if choice == "Q":
            print("\nExiting early...")
            break

        human_winner = "Tie" if choice in ["TIE", "T"] else (f"{choice} > {'B' if choice == 'A' else 'A'}")

        agree_orig = (human_winner == orig_winner)
        agree_ses2 = (human_winner == ses2_winner)

        notes = input("  Optional notes (press enter to skip): ").strip()
        print()

        results.append({
            "Pair_Index": i,
            "A_Floors": b_a["floors"],
            "A_Load": b_a["load"],
            "A_Seconds": b_a["seconds"],
            "B_Floors": b_b["floors"],
            "B_Load": b_b["load"],
            "B_Seconds": b_b["seconds"],
            "Intensity": b_a["intensity"],
            "Orig_Score_A": f"{orig_a:.2f}",
            "Orig_Score_B": f"{orig_b:.2f}",
            "Orig_Prediction": orig_winner,
            "SES2_Score_A": f"{ses2_a:.2f}",
            "SES2_Score_B": f"{ses2_b:.2f}",
            "SES2_Prediction": ses2_winner,
            "Human_Verdict": human_winner,
            "Orig_Matches_Human": agree_orig,
            "SES2_Matches_Human": agree_ses2,
            "Notes": notes
        })

    if not results:
        print("No evaluations to save.")
        return

    fieldnames = list(results[0].keys())
    with open(output_file, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    total_graded = len(results)
    orig_acc = sum(1 for r in results if r["Orig_Matches_Human"]) / total_graded * 100
    ses2_acc = sum(1 for r in results if r["SES2_Matches_Human"]) / total_graded * 100

    print("=" * 70)
    print("Summary of Human Judgments:")
    print(f"  • Total pairs evaluated : {total_graded}")
    print(f"  • SES Original agreement: {orig_acc:.1f}%")
    print(f"  • SES2 agreement        : {ses2_acc:.1f}%")
    print(f"Saved full results to '{output_file}'.")
    print("=" * 70)

if __name__ == "__main__":
    run_interactive_eval(num_pairs=20)


