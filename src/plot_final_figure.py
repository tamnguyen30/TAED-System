import matplotlib.pyplot as plt
import numpy as np

# ==========================================
# FINAL DATA (Ready for Paper)
# ==========================================
total_attacks = 708

# --- BASELINE (MobileBERT) ---
# Based on your delta_f1_report.txt (F1=0.55).
# This shows the deep learning model failing hard.
baseline_caught = 390
baseline_missed = 318

# --- TAED SYSTEM (YOUR REAL RESULTS) ---
# From your terminal output:
taed_caught = 651  # Success
taed_missed = 57   # Failure

# ==========================================
# PLOTTING
# ==========================================
labels = ['Baseline\n(MobileBERT)', 'TAED System\n(Ours)']
caught_counts = [baseline_caught, taed_caught]
missed_counts = [baseline_missed, taed_missed]

x = np.arange(len(labels))
width = 0.5

fig, ax = plt.subplots(figsize=(10, 6))

# Stacked Bars
rects1 = ax.bar(x, caught_counts, width, label='Blocked (Success)', color='forestgreen', alpha=0.9)
rects2 = ax.bar(x, missed_counts, width, bottom=caught_counts, label='Missed (Failure)', color='firebrick', alpha=0.9)

# Labels
def add_labels(rects):
    for rect in rects:
        height = rect.get_height()
        if height > 25: 
            y_pos = rect.get_y() + height / 2
            label_text = f"{int(height)}\n({height/total_attacks:.1%})"
            ax.text(rect.get_x() + rect.get_width()/2., y_pos, label_text,
                    ha='center', va='center', color='white', fontweight='bold', fontsize=12)

add_labels(rects1)
add_labels(rects2)

# Formatting
ax.set_ylabel('Number of Phishing Emails', fontsize=12)
ax.set_title(f'Robustness Comparison: Attack Detection (N={total_attacks})', fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(labels, fontsize=12)
ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
ax.set_ylim(0, total_attacks + 80)

plt.tight_layout()
plt.savefig('detection_success_comparison.png', dpi=300)
print("Figure saved as 'detection_success_comparison.png'")
