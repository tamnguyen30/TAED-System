import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots(figsize=(9, 6))

intensities = [10, 30, 50]

models = {
    'Naive Bayes':          ([0.60, 8.03, 20.40],  '
    'Random Forest':        ([0.94, 9.83, 30.64],  '
    'XGBoost':              ([4.88, 20.33, 37.93], '
    'SVM':                  ([2.41, 25.69, 50.37], '
    'Logistic Regression':  ([2.54, 26.09, 53.24], '
    'DistilBERT (retrained)': ([0.40, 3.41, 17.86], '
    'TAED (Ours)':          ([0.60, 8.63, 25.35],  '
}

for label, (values, color, marker, linestyle) in models.items():
    lw = 3 if label == 'TAED (Ours)' else 1.5
    ms = 12 if label == 'TAED (Ours)' else 7
    ax.plot(intensities, values, 
            label=label, 
            color=color, 
            marker=marker,
            linestyle=linestyle,
            linewidth=lw,
            markersize=ms,
            zorder=5 if label == 'TAED (Ours)' else 3)

ax.axhline(y=10, color='gray', linestyle=':', linewidth=1.5, 
           label='10% Risk Threshold')

ax.set_xlabel('Perturbation Intensity (%)', fontsize=12)
ax.set_ylabel('Attack Success Rate (%)', fontsize=12)
ax.set_title('Attack Success Rate vs Perturbation Intensity', 
             fontsize=13, fontweight='bold')
ax.set_xticks(intensities)
ax.set_xticklabels(['Low (10%)', 'Medium (30%)', 'High (50%)'])
ax.set_ylim(0, 60)
ax.legend(loc='upper left', fontsize=9, framealpha=0.9)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('./results/figures/fig_attack_strength.png', 
            dpi=150, bbox_inches='tight')
plt.savefig('./results/figures/fig_attack_strength.pdf', 
            bbox_inches='tight')
print('Saved!')