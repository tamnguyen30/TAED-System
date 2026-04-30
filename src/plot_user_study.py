import matplotlib.pyplot as plt
import numpy as np

fig, axes = plt.subplots(1, 2, figsize=(11, 5))
fig.suptitle('User Study Results: TAED vs No TAED (n=43)', 
             fontsize=13, fontweight='bold')


ax1 = axes[0]
categories = ['Legitimate', 'Clean\nPhishing', 'Adversarial', 'Overall']
no_taed = [0.827, 0.882, 0.958, 0.888]
with_taed = [0.815, 0.902, 0.980, 0.916]

x = np.arange(len(categories))
w = 0.35
bars1 = ax1.bar(x - w/2, no_taed, w, label='No TAED', 
                color='
bars2 = ax1.bar(x + w/2, with_taed, w, label='With TAED', 
                color='

ax1.set_ylabel('Classification Accuracy')
ax1.set_title('(a) Accuracy by Email Type')
ax1.set_xticks(x)
ax1.set_xticklabels(categories)
ax1.set_ylim(0.75, 1.02)
ax1.legend()
ax1.axhline(y=1.0, color='gray', linestyle='--', alpha=0.3)

for bar in bars1:
    ax1.text(bar.get_x() + bar.get_width()/2., 
             bar.get_height() + 0.005,
             f'{bar.get_height():.3f}', 
             ha='center', va='bottom', fontsize=8)
for bar in bars2:
    ax1.text(bar.get_x() + bar.get_width()/2., 
             bar.get_height() + 0.005,
             f'{bar.get_height():.3f}', 
             ha='center', va='bottom', fontsize=8)


ax2 = axes[1]
error_types = ['False Positives\n(Legit → Phishing)', 
               'False Negatives\n(Phishing → Legit)']
no_taed_errors = [13, 11]
with_taed_errors = [10, 8]

x2 = np.arange(len(error_types))
bars3 = ax2.bar(x2 - w/2, no_taed_errors, w, label='No TAED',
                color='
bars4 = ax2.bar(x2 + w/2, with_taed_errors, w, label='With TAED',
                color='

ax2.set_ylabel('Number of Errors')
ax2.set_title('(b) Classification Errors')
ax2.set_xticks(x2)
ax2.set_xticklabels(error_types)
ax2.set_ylim(0, 18)
ax2.legend()

for bar in bars3:
    ax2.text(bar.get_x() + bar.get_width()/2.,
             bar.get_height() + 0.2,
             str(int(bar.get_height())),
             ha='center', va='bottom', fontsize=10)
for bar in bars4:
    ax2.text(bar.get_x() + bar.get_width()/2.,
             bar.get_height() + 0.2,
             str(int(bar.get_height())),
             ha='center', va='bottom', fontsize=10)

plt.tight_layout()
plt.savefig('/tmp/fig_user_study.png', dpi=150, bbox_inches='tight')
plt.savefig('/tmp/fig_user_study.pdf', bbox_inches='tight')
print('Saved!')