"""Plot stored native results, never generated or imputed outcomes."""
import csv
import sys
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def main():
    root=Path(sys.argv[1]);rows=list(csv.DictReader((root/'comparison.csv').open()))
    fig,axes=plt.subplots(1,2,figsize=(12,4.6))
    metrics=[('attack_success_rate','Attack success'),('native_utility_clean','Clean utility'),('native_utility_attacked','Attacked utility')]
    for i,(key,label) in enumerate(metrics):
        axes[0].bar([j+(i-1)*.25 for j in range(len(rows))],[float(r[key]) for r in rows],width=.25,label=label)
    axes[0].set_ylim(0,1.05);axes[0].legend(fontsize=8)
    axes[0].set_ylabel('Fraction (two tasks per condition)')
    axes[1].bar(range(len(rows)),[float(r['latency_ms']) for r in rows]);axes[1].set_ylabel('Mean runtime, milliseconds')
    for ax in axes:ax.set_xticks(range(len(rows)),[r['config'] for r in rows],rotation=30,ha='right')
    fig.suptitle('Native AgentDojo sandbox | scripted agent, NOT LLM | real RF, no DistilBERT',fontsize=10)
    fig.tight_layout();fig.savefig(root/'comparison.png',dpi=160);plt.close(fig)

if __name__=='__main__':main()
