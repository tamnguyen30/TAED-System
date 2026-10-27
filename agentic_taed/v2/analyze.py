"""Within-block contrasts; unknown/error cases never count as defended successes."""
import argparse,json
from pathlib import Path
from statistics import mean


def analyze(rows):
    completed=[r for r in rows if r['status']=='completed']
    key=lambda r:(r['task'],r['seed'],r['template'],r['goal'])
    indexed={(key(r),r['treatment']):r for r in completed}
    summary=[]
    for name in sorted({r['treatment'] for r in rows}):
        group=[r for r in completed if r['treatment']==name];attacks=[r for r in group if r['attack']]
        clean_pairs=[r for r in group if not r['attack'] and (key(r),'T0F0S0_cfi') in indexed and indexed[key(r),'T0F0S0_cfi']['utility']]
        avg=lambda vals:mean(vals) if vals else None
        summary.append({'treatment':name,'n':len(group),'n_attacked':len(attacks),
          'errors':sum(r['status']!='completed' and r['treatment']==name for r in rows),
          'ASR':avg([r['attack_success'] for r in attacks]),'utility':avg([r['utility'] for r in group]),
          'secure_completion_attacked':avg([r['secure_completion'] for r in attacks]),
          'false_blocking_given_clean_baseline_success':avg([r['abstained'] for r in clean_pairs]),
          'clean_utility_loss_given_baseline_success':avg([not r['utility'] for r in clean_pairs]),
          'mean_latency_ms':avg([r['latency_ms'] for r in group]),
          'mean_estimated_cost_usd':avg([r['estimated_cost_usd'] for r in group]) if group and all(r['estimated_cost_usd'] is not None for r in group) else None})
    contrasts=[]
    pairs=[(f'T0F{f}S{s}_cfi',f'T1F{f}S{s}_cfi','trust') for f in (0,1) for s in (0,1)]
    pairs += [(f'T{t}F0S{s}_cfi',f'T{t}F1S{s}_cfi','filter') for t in (0,1) for s in (0,1)]
    pairs += [(f'T{t}F{f}S0_cfi',f'T{t}F{f}S1_cfi','sufficiency') for t in (0,1) for f in (0,1)]
    pairs += [('T1F1S1_'+x,'T1F1S1_cfi','signal:'+x) for x in ('cf','ci','confidence','shuffled')]
    for a,b,factor in pairs:
        pairs_data=[(r,indexed[key(r),b]) for r in completed if r['attack'] and r['treatment']==a and (key(r),b) in indexed]
        contrasts.append({'factor':factor,'from':a,'to':b,'paired_cases':len(pairs_data),
          'delta_secure_completion':mean(y['secure_completion']-x['secure_completion'] for x,y in pairs_data) if pairs_data else None})
    return {'summary':summary,'paired_contrasts':contrasts,'inference':'Descriptive only; two evaluation topic clusters are insufficient for reliable population inference. Missing pairs excluded explicitly.'}


def main():
    p=argparse.ArgumentParser();p.add_argument('run',type=Path);a=p.parse_args()
    path=a.run/'raw.jsonl'
    rows=[json.loads(x) for x in path.read_text().splitlines()] if path.exists() else []
    result=analyze(rows)
    result['status']='no_live_results' if not rows else 'analyzed'
    (a.run/'analysis.json').write_text(json.dumps(result,indent=2));print(result['status'])
if __name__=='__main__':main()
