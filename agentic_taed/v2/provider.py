"""Real provider calls only. Missing usage/rates produce unknown costs, never zero."""
from types import SimpleNamespace
import time
import os


def credentials(provider):
    if provider=='openai':return bool(os.environ.get('OPENAI_API_KEY'))
    if provider=='openai-compatible':return bool(os.environ.get('OPENAI_COMPATIBLE_API_KEY') and os.environ.get('OPENAI_COMPATIBLE_BASE_URL'))
    raise ValueError(provider)


def estimated_cost(usage,rates):
    if not usage or not rates:return None
    p=usage.get('prompt_tokens');c=usage.get('completion_tokens')
    if p is None or c is None:return None
    cached=(usage.get('prompt_tokens_details') or {}).get('cached_tokens',0) or 0
    if cached and 'cached_input_per_million' not in rates:return None
    return ((p-cached)*rates['input_per_million']+cached*rates.get('cached_input_per_million',0)+c*rates['output_per_million'])/1e6

class Meter:
    def __init__(self,endpoint,seed,rates=None,send_seed=True,max_calls=32):
        self.endpoint=endpoint;self.seed=seed;self.rates=rates;self.send_seed=send_seed;self.max_calls=max_calls;self.calls=[]
    def create(self,**kwargs):
        if len(self.calls)>=self.max_calls:raise RuntimeError('Provider call limit reached')
        if self.send_seed:kwargs['seed']=self.seed
        started=time.perf_counter()
        entry={'seed_requested':self.seed if self.send_seed else None,'model_requested':kwargs['model']}
        try:
            response=self.endpoint.create(**kwargs)
            usage=response.usage.model_dump() if response.usage else None
            entry.update({'usage':usage,'model_returned':response.model,'response_id':response.id,
              'system_fingerprint':getattr(response,'system_fingerprint',None),'estimated_cost_usd':estimated_cost(usage,self.rates)})
            return response
        except Exception as e:
            # Do not persist HTTP headers or provider exception strings that might include secrets.
            entry.update({'error_type':type(e).__name__,'estimated_cost_usd':None});raise
        finally:
            entry['latency_ms']=(time.perf_counter()-started)*1000;self.calls.append(entry)


def make_llm(provider,model,seed,rates=None,send_seed=True):
    from openai import OpenAI
    from agentdojo.agent_pipeline.llms.openai_llm import OpenAILLM
    if not credentials(provider):raise RuntimeError('Missing provider credentials')
    client=(OpenAI(timeout=60,max_retries=0) if provider=='openai' else
       OpenAI(api_key=os.environ['OPENAI_COMPATIBLE_API_KEY'],base_url=os.environ['OPENAI_COMPATIBLE_BASE_URL'],timeout=60,max_retries=0))
    meter=Meter(client.chat.completions,seed,rates,send_seed)
    proxy=SimpleNamespace(chat=SimpleNamespace(completions=meter))
    llm=OpenAILLM(proxy,model,temperature=.2);llm.name=provider+':'+model
    return llm,meter
