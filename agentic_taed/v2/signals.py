"""New measured instability; preserved original core remains untouched."""
import hashlib
import random
import re
import time
import numpy as np
from agentic_taed.models import RepositoryTAED

class TrustSignals:
    def __init__(self):
        self.repository=RepositoryTAED()
        self.metadata={**self.repository.metadata,'extension':'v2_measured_instability',
          'I_definition':'mean absolute difference of phishing probability under 8 deterministic word-drop probes',
          'warning':'word deletion is not guaranteed label preserving; confidence and dictionary alignment are not calibrated safety'}

    def measure(self,text):
        start=time.perf_counter()
        original=self.repository.predict(text)
        words=text.split(); rng=random.Random(int(hashlib.sha256(text.encode()).hexdigest()[:8],16))
        probes=[]
        for _ in range(8):
            drop=set(rng.sample(range(len(words)),max(1,len(words)//10))) if words else set()
            probes.append(' '.join(w for i,w in enumerate(words) if i not in drop))
        p=float(original['rf_phishing_probability'])
        probabilities=self.repository.classifier.predict_proba(probes)[:,1]
        instability=float(np.abs(probabilities-p).mean())
        confidence=max(p,1-p); alignment=original['fidelity']
        score=max(0,min(1,.30*confidence+.40*alignment-.25*instability))
        return {'C':confidence,'F':alignment,'I':instability,'phishing_probability':p,
          'trust_score':score,'cfi_risk':max(p,1-score/.70),
          'cf_risk':max(p,1-(.30*confidence+.40*alignment)/.70),
          'ci_risk':max(p,1-max(0,.30*confidence-.25*instability)/.70),
          'confidence_risk':max(p,1-(.30*confidence)/.70),'features':original['features'],
          'probe_probabilities':probabilities.tolist(),'latency_ms':(time.perf_counter()-start)*1000}


def cutoff(values,budget=.30):
    # A strict > cutoff avoids nondeterministic tie-breaking; actual coverage is recorded.
    return float(np.quantile(values,1-budget,method='higher'))


def calibrated_risk(signals,signal,text,calibration):
    if signal=='cfi':return signals['cfi_risk']
    if signal in ('cf','ci','confidence'):return signals[signal+'_risk']
    if signal=='shuffled':
        # A deterministic content-independent placebo drawn from DEVELOPMENT risk values.
        values=calibration['development_cfi_risks']
        i=int(hashlib.sha256(('placebo:'+text).encode()).hexdigest()[:8],16)%len(values)
        return values[i]
    raise ValueError(signal)
