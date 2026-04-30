import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import warnings
warnings.filterwarnings('ignore')


plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 11,
    'axes.titlesize': 12,
    'axes.labelsize': 11,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'axes.spines.top': False,
    'axes.spines.right': False,
})

COLORS = {
    'taed': '
    'rf': '
    'nb': '
    'svm': '
    'lr': '
    'xgb': '
    'distilbert_v2': '
    'distilbert_v3': '
    'mobilebert': '
    'tinybert': '
    'clean': '
    'attack': '
    'degrade': '
    'bar_blue': '
    'bar_red': '
    'bar_green': '
    'gray': '
}

OUTPUT = 'results/figures/'
import os
os.makedirs(OUTPUT, exist_ok=True)





def fig_adversarial_robustness():
    models = [
        'Naive\nBayes', 'Random\nForest', 'XGBoost',
        'SVM', 'Logistic\nReg.', 'DistilBERT\nv2',
        'MobileBERT', 'TinyBERT', 'DistilBERT\nv3', 'TAED\n(Ours)'
    ]
    clean_acc = [99.83, 99.75, 99.45, 99.75, 99.37, 99.79, 99.00, 99.00, 99.79, 99.00]
    adv_acc   = [95.85, 94.13, 86.83, 88.81, 88.51, 51.56, 49.73, 51.31, 96.66, 85.95]
    asr       = [8.30,  11.78, 18.23, 22.90, 23.55, 99.45, 99.28, 99.98,  6.39,  9.79]

    x = np.arange(len(models))
    width = 0.28

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 9))
    fig.suptitle('Adversarial Robustness Evaluation Across Architectures\n(n = 16,836 adversarial samples, 8 attack types)',
                 fontsize=13, fontweight='bold', y=0.98)

    
    bars1 = ax1.bar(x - width/2, clean_acc, width, label='Clean Accuracy',
                    color=COLORS['bar_green'], alpha=0.85, edgecolor='white', linewidth=0.5)
    bars2 = ax1.bar(x + width/2, adv_acc, width, label='Adversarial Accuracy',
                    color=COLORS['bar_red'], alpha=0.85, edgecolor='white', linewidth=0.5)

    
    ax1.bar(x[-1] - width/2, clean_acc[-1], width,
            color=COLORS['bar_green'], alpha=1.0, edgecolor='
    ax1.bar(x[-1] + width/2, adv_acc[-1], width,
            color=COLORS['bar_red'], alpha=1.0, edgecolor='

    ax1.set_ylabel('Accuracy (%)')
    ax1.set_ylim(0, 105)
    ax1.set_xticks(x)
    ax1.set_xticklabels(models, fontsize=9.5)
    ax1.legend(loc='lower left')
    ax1.set_title('(a) Clean vs. Adversarial Accuracy', fontsize=11, pad=8)

    

    
    bar_colors = [COLORS['bar_blue']] * len(models)
    bar_colors[-1] = COLORS['taed']
    bar_colors[-2] = COLORS['bar_blue']

    bars3 = ax2.bar(x, asr, color=bar_colors, alpha=0.85,
                    edgecolor='white', linewidth=0.5)

    
    ax2.set_ylabel('Attack Success Rate (%)')
    ax2.set_ylim(0, 115)
    ax2.set_xticks(x)
    ax2.set_xticklabels(models, fontsize=9.5)
    ax2.set_title('(b) Attack Success Rate (ASR)', fontsize=11, pad=8)
    ax2.legend()

    
    for bar, val in zip(bars3, asr):
        ax2.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 1.5,
                f'{val:.1f}%', ha='center', va='bottom', fontsize=8.5,
                fontweight='bold' if val < 15 else 'normal',
                color=COLORS['taed'] if val == 9.79 else 'black')

    plt.tight_layout()
    plt.savefig(f'{OUTPUT}fig_adversarial_robustness.pdf')
    plt.savefig(f'{OUTPUT}fig_adversarial_robustness.png')
    print('✓ Figure 1: Adversarial Robustness saved')
    plt.close()





def fig_attack_strength():
    strengths = ['10%', '30%', '50%']
    x = np.arange(len(strengths))
    width = 0.13

    data = {
        'Naive Bayes':    [0.60,  8.03,  20.40],
        'Random Forest':  [0.94,  9.83,  30.64],
        'XGBoost':        [4.88,  20.33, 37.93],
        'SVM':            [2.41,  25.69, 50.37],
        'Log. Reg.':      [2.54,  26.09, 53.24],
        'DistilBERT v3':  [0.40,  3.41,  17.86],
        'TAED (Ours)':    [0.60,  8.63,  25.35],
    }

    colors = [COLORS['nb'], COLORS['rf'], COLORS['xgb'],
              COLORS['svm'], COLORS['lr'], COLORS['distilbert_v3'], COLORS['taed']]

    fig, ax = plt.subplots(figsize=(11, 6))
    fig.suptitle('Attack Success Rate by Perturbation Intensity\n(n = 3,000 samples per strength level)',
                 fontsize=13, fontweight='bold')

    offsets = np.linspace(-(len(data)-1)/2 * width, (len(data)-1)/2 * width, len(data))

    for i, ((label, values), color, offset) in enumerate(zip(data.items(), colors, offsets)):
        lw = 2.0 if label == 'TAED (Ours)' else 0.5
        ec = '
        alpha = 1.0 if label == 'TAED (Ours)' else 0.82
        bars = ax.bar(x + offset, values, width, label=label,
                     color=color, alpha=alpha, edgecolor=ec, linewidth=lw)

    ax.axhline(y=10, color='orange', linestyle='--', alpha=0.8,
               linewidth=1.2, label='_Threshold')
    ax.text(2.45, 11, 'Risk Threshold (10%)', color='orange',
            fontsize=9, va='bottom')

    ax.set_ylabel('Attack Success Rate (%)')
    ax.set_xlabel('Perturbation Intensity')
    ax.set_xticks(x)
    ax.set_xticklabels(['Low (10%)', 'Medium (30%)', 'High (50%)'], fontsize=11)
    ax.set_ylim(0, 62)
    ax.legend(loc='upper left', ncol=2, fontsize=9.5)

    
    taed_vals = data['TAED (Ours)']
    taed_offset = offsets[-1]
    for xi, val in zip(x, taed_vals):
        ax.text(xi + taed_offset, val + 1.2, f'{val:.1f}%',
               ha='center', fontsize=8.5, color=COLORS['taed'],
               fontweight='bold')

    plt.tight_layout()
    plt.savefig(f'{OUTPUT}fig_attack_strength.pdf')
    plt.savefig(f'{OUTPUT}fig_attack_strength.png')
    print('✓ Figure 2: Attack Strength Analysis saved')
    plt.close()





def fig_complexity_resilience():
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle('The Complexity-Resilience Paradox in Phishing Detection',
                 fontsize=13, fontweight='bold')

    
    ax = axes[0]
    models = ['Naive Bayes', 'Log. Reg.', 'SVM', 'Random Forest',
              'XGBoost', 'DistilBERT v2', 'MobileBERT', 'TinyBERT',
              'DistilBERT v3', 'TAED']
    clean_f1 = [0.9983, 0.9937, 0.9975, 0.9975, 0.9945,
                0.9979, 0.990, 0.990, 0.9979, 0.990]
    asr = [8.30, 23.55, 22.90, 11.78, 18.23,
           99.45, 99.28, 99.98, 6.39, 9.79]
    colors_scatter = [COLORS['nb'], COLORS['lr'], COLORS['svm'],
                      COLORS['rf'], COLORS['xgb'],
                      COLORS['distilbert_v2'], COLORS['mobilebert'],
                      COLORS['tinybert'], COLORS['distilbert_v3'],
                      COLORS['taed']]
    sizes = [120]*9 + [250]

    for i, (m, cf, a, c, s) in enumerate(zip(models, clean_f1, asr, colors_scatter, sizes)):
        ax.scatter(cf*100, a, color=c, s=s, zorder=5,
                  edgecolors='white' if m != 'TAED' else '
                  linewidth=1.5 if m == 'TAED' else 0.8)
        offset_x = 0.01
        offset_y = 2
        if m == 'TAED':
            offset_x = -0.25
            offset_y = 5
        elif m in ['DistilBERT v2', 'MobileBERT']:
            offset_y = -8
        elif m == 'TinyBERT':
            offset_x = -0.3
        ax.annotate(m, (cf*100 + offset_x, a + offset_y),
                   fontsize=8, ha='left')

    ax.axhline(y=10, color='orange', linestyle='--', alpha=0.7,
               linewidth=1.2, label='Risk threshold')
    ax.set_xlabel('Clean Data F1 Score (%)')
    ax.set_ylabel('Attack Success Rate (%)')
    ax.set_title('(a) Clean Performance vs. Adversarial Robustness\n(lower-right is ideal)',
                fontsize=10)
    ax.legend(fontsize=9)

    
    ax.text(99.3, 55, 'High accuracy\nLow robustness\n(Transformers)',
            fontsize=8.5, color=COLORS['bar_red'],
            ha='center', style='italic',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='
    ax.text(99.3, 5, 'High accuracy\nHigh robustness\n(Ideal)',
            fontsize=8.5, color=COLORS['taed'],
            ha='center', style='italic',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='

    
    ax2 = axes[1]
    model_names = ['NB', 'RF', 'XGB', 'SVM', 'LR',
                   'BERT\nv2', 'Mobile\nBERT', 'Tiny\nBERT',
                   'BERT\nv3', 'TAED']
    delta = [c - a for c, a in zip(clean_f1, asr)]
    
    clean_f1_vals = [0.9983, 0.9937, 0.9975, 0.9975, 0.9945,
                     0.9979, 0.990, 0.990, 0.9979, 0.990]
    adv_f1_vals   = [0.9585, 0.9413, 0.8683, 0.8881, 0.8851,
                     0.5156, 0.4973, 0.5131, 0.9666, 0.8595]
    delta_f1 = [(c - a)*100 for c, a in zip(clean_f1_vals, adv_f1_vals)]

    bar_colors2 = [COLORS['nb'], COLORS['rf'], COLORS['xgb'],
                   COLORS['svm'], COLORS['lr'],
                   COLORS['distilbert_v2'], COLORS['mobilebert'],
                   COLORS['tinybert'], COLORS['distilbert_v3'],
                   COLORS['taed']]

    xpos = np.arange(len(model_names))
    bars = ax2.bar(xpos, delta_f1, color=bar_colors2, alpha=0.85,
                   edgecolor='white', linewidth=0.5)
    bars[-1].set_edgecolor('
    bars[-1].set_linewidth(1.5)

    ax2.set_ylabel('F1 Degradation (clean → adversarial, %)')
    ax2.set_xlabel('Model')
    ax2.set_xticks(xpos)
    ax2.set_xticklabels(model_names, fontsize=9.5)
    ax2.set_title('(b) Performance Degradation Under Adversarial Attack\n(lower is better)',
                 fontsize=10)

    for bar, val in zip(bars, delta_f1):
        ax2.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.3,
                f'{val:.1f}%', ha='center', va='bottom', fontsize=8.5)

    ax2.axhline(y=5, color='orange', linestyle='--', alpha=0.7,
               linewidth=1.0, label='Acceptable degradation')
    ax2.legend(fontsize=9)

    plt.tight_layout()
    plt.savefig(f'{OUTPUT}fig_complexity_resilience.pdf')
    plt.savefig(f'{OUTPUT}fig_complexity_resilience.png')
    print('✓ Figure 3: Complexity-Resilience Paradox saved')
    plt.close()





def fig_adaptive_evaluation():
    attacks = [
        'Baseline\n(No Adaptation)',
        'Keyword\nStuffing',
        'Trusted Domain\nInjection',
        'Stability\nOptimization',
        'Combined\n(Stab. + KW)',
        'Domain +\nStability'
    ]
    asr = [9.13, 9.13, 8.31, 0.21, 0.21, 0.10]
    mean_ts = [0.3641, 0.3641, 0.4434, 0.3645, 0.3645, 0.4406]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle('White-Box Adaptive Adversarial Evaluation\n(Attacker has full knowledge of Trust Score formula)',
                 fontsize=13, fontweight='bold')

    
    bar_colors = [COLORS['gray'], COLORS['gray'], COLORS['bar_blue'],
                  COLORS['bar_green'], COLORS['bar_green'], COLORS['taed']]
    bars = ax1.bar(np.arange(len(attacks)), asr, color=bar_colors,
                   alpha=0.85, edgecolor='white', linewidth=0.5)

    ax1.axhline(y=9.79, color='gray', linestyle='--', alpha=0.8,
               linewidth=1.2, label='TAED Baseline (9.79%)')
    ax1.axhline(y=10, color='orange', linestyle=':', alpha=0.7,
               linewidth=1.0, label='Risk Threshold (10%)')

    ax1.set_ylabel('Attack Success Rate (%)')
    ax1.set_xticks(np.arange(len(attacks)))
    ax1.set_xticklabels(attacks, fontsize=9)
    ax1.set_ylim(0, 13)
    ax1.set_title('(a) ASR Under White-Box Adaptive Attacks\n(lower = TAED more robust)', fontsize=10)
    ax1.legend(fontsize=9)

    for bar, val in zip(bars, asr):
        ax1.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.1,
                f'{val:.2f}%', ha='center', va='bottom', fontsize=9, fontweight='bold')

    
    ax1.annotate('Stability optimization\ninadvertently aids TAED',
                xy=(3, 0.21), xytext=(3.8, 4),
                fontsize=8.5, color=COLORS['taed'],
                arrowprops=dict(arrowstyle='->', color=COLORS['taed'], lw=1.2))

    
    ts_colors = [COLORS['gray'], COLORS['gray'], COLORS['bar_blue'],
                 COLORS['bar_green'], COLORS['bar_green'], COLORS['taed']]
    bars2 = ax2.bar(np.arange(len(attacks)), mean_ts, color=ts_colors,
                    alpha=0.85, edgecolor='white', linewidth=0.5)

    ax2.axhline(y=0.50, color='red', linestyle='--', alpha=0.7,
               linewidth=1.2, label='Trust Gate Threshold (0.50)')
    ax2.set_ylabel('Mean Trust Score Assigned')
    ax2.set_xticks(np.arange(len(attacks)))
    ax2.set_xticklabels(attacks, fontsize=9)
    ax2.set_ylim(0, 0.65)
    ax2.set_title('(b) Mean Trust Score Assigned to Adversarial Samples\n(below threshold = escalated for review)', fontsize=10)
    ax2.legend(fontsize=9)

    for bar, val in zip(bars2, mean_ts):
        ax2.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.005,
                f'{val:.3f}', ha='center', va='bottom', fontsize=9)

    plt.tight_layout()
    plt.savefig(f'{OUTPUT}fig_adaptive_evaluation.pdf')
    plt.savefig(f'{OUTPUT}fig_adaptive_evaluation.png')
    print('✓ Figure 4: Adaptive Evaluation saved')
    plt.close()





def fig_dataset_overview():
    fig, axes = plt.subplots(1, 2, figsize=(11, 5))
    fig.suptitle('Dataset Composition and Adversarial Attack Distribution\n(Adversarial Evaluation Benchmark)',
                 fontsize=13, fontweight='bold')

    
    ax = axes[0]
    sources = ['ITASEC 2024\nPhishing', 'Nazario\nCorpus',
               'SpamAssassin\nHam', 'Synthetic\n(KD 2025)']
    sizes_clean = [2100, 900, 1200, 7632]
    colors_pie = ['
    wedges, texts, autotexts = ax.pie(sizes_clean, labels=sources,
                                       colors=colors_pie,
                                       autopct='%1.1f%%',
                                       startangle=140,
                                       pctdistance=0.75)
    for text in autotexts:
        text.set_fontsize(9)
    ax.set_title(f'(a) Clean Dataset Sources\n(n = 11,832 total, balanced)', fontsize=10)

    
    ax2 = axes[1]
    attack_types = ['URL\nShorten', 'Fake\nDomain', 'Paraphrase',
                    'Zero-Width', 'Leetspeak', 'Prompt\nInjection',
                    'Homoglyph', 'Noise\nInsertion']
    attack_counts = [322, 328, 2645, 2662, 2668, 2678, 2753, 2781]
    attack_colors = ['
                     '

    bars = ax2.barh(attack_types, attack_counts, color=attack_colors, alpha=0.85)
    ax2.set_xlabel('Number of Samples')
    ax2.set_title(f'(b) Adversarial Attack Distribution\n(n = 16,836 total, 8 attack types)', fontsize=10)
    for bar, count in zip(bars, attack_counts):
        ax2.text(bar.get_width() + 30, bar.get_y() + bar.get_height()/2.,
                f'{count:,}', va='center', fontsize=9)
    ax2.set_xlim(0, 3300)

    plt.tight_layout()
    plt.savefig(f'{OUTPUT}fig_dataset_overview.pdf')
    plt.savefig(f'{OUTPUT}fig_dataset_overview.png')
    print('✓ Figure 5: Dataset Overview saved')
    plt.close()





def fig_distilbert_comparison():
    fig, axes = plt.subplots(1, 2, figsize=(10, 5))
    fig.suptitle('Impact of Training Data Quality on DistilBERT Adversarial Robustness',
                 fontsize=13, fontweight='bold')

    strengths = ['10%', '30%', '50%', 'Full\nBenchmark']
    v2_asr = [99.45, 99.45, 99.45, 99.45]
    v3_asr = [0.40, 3.41, 17.86, 6.39]
    v2_acc = [51.56, 51.56, 51.56, 51.56]
    v3_acc = [99.77, 98.13, 90.87, 96.66]

    x = np.arange(len(strengths))
    w = 0.35

    ax1 = axes[0]
    ax1.bar(x - w/2, v2_asr, w, label='DistilBERT (original training data)',
            color=COLORS['distilbert_v2'], alpha=0.85)
    ax1.bar(x + w/2, v3_asr, w, label='DistilBERT (expanded training data)',
            color=COLORS['distilbert_v3'], alpha=0.85)
    ax1.set_ylabel('Attack Success Rate (%)')
    ax1.set_xticks(x)
    ax1.set_xticklabels(strengths)
    ax1.set_title('(a) ASR Comparison\n(lower is better)', fontsize=10)
    ax1.legend(fontsize=9)
    ax1.axhline(y=10, color='orange', linestyle='--', alpha=0.7, linewidth=1.0)

    ax2 = axes[1]
    ax2.bar(x - w/2, v2_acc, w, label='DistilBERT (original training data)',
            color=COLORS['distilbert_v2'], alpha=0.85)
    ax2.bar(x + w/2, v3_acc, w, label='DistilBERT (expanded training data)',
            color=COLORS['distilbert_v3'], alpha=0.85)
    ax2.set_ylabel('Adversarial Accuracy (%)')
    ax2.set_ylim(40, 105)
    ax2.set_xticks(x)
    ax2.set_xticklabels(strengths)
    ax2.set_title('(b) Adversarial Accuracy Comparison\n(higher is better)', fontsize=10)
    ax2.legend(fontsize=9)

    plt.tight_layout()
    plt.savefig(f'{OUTPUT}fig_distilbert_comparison.pdf')
    plt.savefig(f'{OUTPUT}fig_distilbert_comparison.png')
    print('✓ Figure 6: DistilBERT Comparison saved')
    plt.close()





if __name__ == '__main__':
    print('Generating publication figures...\n')
    fig_adversarial_robustness()
    fig_attack_strength()
    fig_complexity_resilience()
    fig_adaptive_evaluation()
    fig_dataset_overview()
    fig_distilbert_comparison()
    print(f'\n✅ All figures saved to {OUTPUT}')
    print('PDF and PNG versions generated for each figure.')