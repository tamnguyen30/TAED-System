"""Development-only measurement and coverage matching, NOT LLM evaluation."""
import argparse,json,hashlib
from pathlib import Path
from .signals import TrustSignals,cutoff,calibrated_risk
from .design import PLAN,plan_hash
from agentic_taed.models import ROOT

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    if a.out.exists():p.error('Output exists')
    fixtures=[json.loads(x) for x in (ROOT/'research/agentic/fixtures/original_five_emails.jsonl').read_text().splitlines()]
    stress=json.loads((ROOT/'research/agentic/fixtures/five_emails.json').read_text())
    texts=[x['email_body'] for x in fixtures]+[x['email'] for x in stress]
    model=TrustSignals();rows=[{'development_id':i,'text_sha256':hashlib.sha256(t.encode()).hexdigest(),'signals':model.measure(t)} for i,t in enumerate(texts)]
    values=[r['signals']['cfi_risk'] for r in rows]
    calibration={'plan_hash':plan_hash(),'budget':.30,'development_cfi_risks':values,'thresholds':{},'coverage':{},'model':model.metadata,
                 'data_scope':'ten previously used synthetic DEVELOPMENT inputs, no evaluation tasks; no outcome-based threshold tuning'}
    for name in ('cfi','cf','ci','confidence','shuffled'):
        risks=[calibrated_risk(r['signals'],name,t,calibration) for r,t in zip(rows,texts)]
        threshold=cutoff(risks);calibration['thresholds'][name]=threshold
        calibration['coverage'][name]=sum(x>threshold for x in risks)/len(risks)
    a.out.mkdir(parents=True)
    (a.out/'calibration.json').write_text(json.dumps(calibration,indent=2))
    (a.out/'signals.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
    print(json.dumps({'coverage':calibration['coverage'],'thresholds':calibration['thresholds']},indent=2))
if __name__=='__main__':main()
