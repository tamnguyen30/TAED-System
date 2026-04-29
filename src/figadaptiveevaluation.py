import matplotlib.pyplot as plt
import numpy as np

plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.spines.left': False,
})

fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))
fig.suptitle('White-Box Adaptive Adversarial Evaluation', 
             fontsize=14, fontweight='bold', y=1.01)

strategies = [
    'Baseline\n(no adaptation)',
    'Keyword\nStuffing',
    'Trusted Domain\nInjection',
    'Stability\nOptimization',
    'Combined\n(Stability + Keywords)',
    'Domain +\nStability'
]

asr = [9.13, 9.13, 8.31, 0.21, 0.21, 0.10]
trust_scores = [0.364, 0.364, 0.443, 0.365, 0.365, 0.441]

RED   = '#C0392B'
GREEN = '#1D9E75'

colors = [RED if a >= 1 else GREEN for a in asr]
ts_colors = [RED if ts < 0.50 else GREEN for ts in trust_scores]

y_pos = np.arange(len(strategies))

# Left panel: ASR
ax1 = axes[0]

ax1.hlines(y_pos, 0, asr, colors='#DDDDDD', linewidth=2.5, zorder=1)
ax1.scatter(asr, y_pos, c=colors, s=100, zorder=5,
            edgecolors='white', linewidth=1.2)

for i, (a, y) in enumerate(zip(asr, y_pos)):
    offset = 0.35 if a >= 1 else 0.25
    ax1.text(a + offset, y, f'{a}%',
             va='center', ha='left', fontsize=9, fontweight='bold',
             color=colors[i])

ax1.axvline(x=10, color='#888888', linestyle='--',
            linewidth=1.3, alpha=0.8)

ax1.text(10.1, 0.02, '10% Risk Threshold',
         transform=ax1.get_xaxis_transform(),
         fontsize=8, color='#888888', va='bottom', ha='left', rotation=90)

ax1.set_yticks(y_pos)
ax1.set_yticklabels(strategies, fontsize=9.5)
ax1.set_xlabel('Attack Success Rate (%)', fontsize=10.5, labelpad=8)
ax1.set_title('(a) ASR by Attack Strategy', fontsize=10, pad=10)
ax1.set_xlim(-0.3, 13)
ax1.grid(True, axis='x', alpha=0.2, linewidth=0.7)
ax1.tick_params(axis='both', length=0)
ax1.invert_yaxis()

# Right panel: Mean Trust Score
ax2 = axes[1]

ax2.hlines(y_pos, 0.30, trust_scores, colors='#DDDDDD', linewidth=2.5, zorder=1)
ax2.scatter(trust_scores, y_pos, c=ts_colors, s=100, zorder=5,
            edgecolors='white', linewidth=1.2)

for i, (ts, y) in enumerate(zip(trust_scores, y_pos)):
    ax2.text(ts + 0.006, y, f'{ts}',
             va='center', ha='left', fontsize=9, fontweight='bold',
             color=ts_colors[i])

ax2.axvline(x=0.50, color='#7B2D8B', linestyle='--',
            linewidth=1.3, alpha=0.8)

ax2.text(0.501, 0.02, 'Escalation Threshold (0.50)',
         transform=ax2.get_xaxis_transform(),
         fontsize=8, color='#7B2D8B', va='bottom', ha='left', rotation=90)

ax2.set_yticks(y_pos)
ax2.set_yticklabels(strategies, fontsize=9.5)
ax2.set_xlabel('Mean Trust Score', fontsize=10.5, labelpad=8)
ax2.set_title('(b) Mean Trust Score by Strategy', fontsize=10, pad=10)
ax2.set_xlim(0.295, 0.565)
ax2.grid(True, axis='x', alpha=0.2, linewidth=0.7)
ax2.tick_params(axis='both', length=0)
ax2.invert_yaxis()

plt.tight_layout(w_pad=3.5)
plt.savefig('results/figures/figadaptiveevaluation.png',
            dpi=150, bbox_inches='tight')
plt.savefig('results/figures/figadaptiveevaluation.pdf',
            bbox_inches='tight')
print('Saved!')