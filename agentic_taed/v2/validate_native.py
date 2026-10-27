"""Native task/vector compatibility, never an agent performance evaluation.

Uses benchmark oracle paths solely to check injection visibility. No defense or
trained detector is run on reserved evaluation content; no utility scores emitted.
"""
import argparse,json
from pathlib import Path
from agentdojo.task_suite.load_suites import get_suite
from agentdojo.agent_pipeline.ground_truth_pipeline import GroundTruthPipeline
from agentdojo.functions_runtime import FunctionsRuntime
from .design import PLAN,validate_plan,plan_hash
from .evidence import contract_from_query

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    if a.out.exists():p.error('Output exists')
    validate_plan();suite=get_suite(PLAN['benchmark_version'],PLAN['suite']);rows=[]
    for split in ('development','evaluation'):
        for task_id in PLAN[split]['tasks']:
            task=suite.get_user_task_by_id(task_id);vector=PLAN[split]['vectors'][task_id]
            marker='TAED_NATIVE_VISIBILITY_CANARY'
            env=task.init_environment(suite.load_and_inject_default_environment({vector:marker}))
            result=GroundTruthPipeline(task).query(task.PROMPT,FunctionsRuntime(suite.tools),env)
            seen=any(marker in str(m.get('content','')) for m in result[3] if m['role']=='tool')
            contract=contract_from_query(task.PROMPT)
            rows.append({'task':task_id,'split':split,'vector':vector,'vector_observed_in_oracle_tool_path':seen,
                         'contract_fields':contract.fields if contract else None})
    out={'kind':'native_API_compatibility_ONLY_NO_agent_performance','plan_hash':plan_hash(),'checks':rows,
      'notes':'Oracle path executed in isolated native environment; outputs and gold answers are not passed to defenses or calibration.'}
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2))
    if not all(r['vector_observed_in_oracle_tool_path'] for r in rows):raise SystemExit('Unreachable selected vector')
    print('All selected vectors observed; no LLM performance measured.')
if __name__=='__main__':main()
