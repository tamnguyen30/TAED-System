"""Describe development routing changes without labeling them LLM performance."""
import argparse,json,csv
from pathlib import Path
from .signals import calibrated_risk
from agentic_taed.models import ROOT

def main():
    p=argparse.ArgumentParser();p.add_argument('directory',type=Path);a=p.parse_args();out=a.directory
    cal=json.loads((out/'calibration.json').read_text());rows=[json.loads(x) for x in (out/'signals.jsonl').read_text().splitlines()]
    texts=[json.loads(x)['email_body'] for x in (ROOT/'research/agentic/fixtures/original_five_emails.jsonl').read_text().splitlines()]
    texts += [r['email'] for r in json.loads((ROOT/'research/agentic/fixtures/five_emails.json').read_text())]
    sets={name:[r['development_id'] for r,t in zip(rows,texts) if calibrated_risk(r['signals'],name,t,cal)>threshold] for name,threshold in cal['thresholds'].items()}
    result={'kind':'development_detector_diagnostics_NOT_agent_efficacy','n':len(rows),
      'measured_instability_min':min(r['signals']['I'] for r in rows),'measured_instability_max':max(r['signals']['I'] for r in rows),
      'quarantined_ids':sets,'cf_vs_cfi_identical_withholding':sets['cf']==sets['cfi'],
      'interpretation':'Record-selection differences alone do not establish additional security or utility.'}
    (out/'diagnostics.json').write_text(json.dumps(result,indent=2))
    with (out/'diagnostics.csv').open('w') as f:
        writer=csv.writer(f);writer.writerow(['signal','cutoff','achieved_dev_withholding','selected_development_ids'])
        for name in sets:writer.writerow([name,cal['thresholds'][name],cal['coverage'][name],str(sets[name])])
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(8,3.5))
    ax.bar(range(len(rows)),[r['signals']['I'] for r in rows]);ax.set_xlabel('Development input index (not independent held-out cases)')
    ax.set_ylabel('Mean absolute probability change')
    ax.set_title('Measured RF perturbation sensitivity — no LLM evaluation')
    fig.tight_layout();fig.savefig(out/'instability.png',dpi=150);plt.close(fig)
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
