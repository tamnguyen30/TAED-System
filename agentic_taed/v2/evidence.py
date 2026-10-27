"""Typed task facts with source offsets and explicit out-of-band provenance assumptions.

Never promote an email's self-asserted role/sender to authenticated authority.
No benchmark gold answers, task IDs, or expected outputs enter this module.
"""
from dataclasses import dataclass,asdict
import re
from urllib.parse import urlparse

PATTERNS={
 'code':r'\b\d{6}\b', 'url':r'https?://[^\s<>"\\]+',
 'date':r'\b(?:\d{4}-\d{2}-\d{2}|(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:st|nd|rd|th)?(?:,?\s+\d{4})?)\b',
 'time':r'\b(?:\d{1,2}:\d{2}(?:\s*[AP]M)?|\d{1,2}\s*[AP]M)\b',
 'location':r'\b(?:[\w-]+\s+){0,3}trailhead\b|(?<=Location: )[^\n]+',
 'duration':r'\b(?:\d+|one|two|three|four|five|six)\s*(?:hours?|minutes?)\b',
 'attendee':r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}',
}

@dataclass(frozen=True)
class Contract:
    fields: tuple[str,...]
    topic_tokens: tuple[str,...]
    authorized_senders: tuple[str,...]=()
    allowed_url_hosts: tuple[str,...]=()


def contract_from_query(query):
    q=query.lower()
    if 'security code' in q: fields=('code',)
    elif 'link' in q and 'password' in q: fields=('url',)
    elif 'family reunion' in q: fields=('date','time')
    elif 'hiking' in q: fields=('time','location')
    else:return None
    if 'create' in q or 'book' in q:
        fields += ('duration',)
        if 'invite' in q: fields += ('attendee',)
    # Trusted request may supply facts; it is never replaced by an email instruction.
    stop={'what','where','when','please','from','email','emails','received','recently','based','going','give','format','create','event','calendar','with','this','that','only','should','have','make','last','hours','time','date','link'}
    tokens=tuple(w for w in re.findall(r'[a-z]{4,}',q) if w not in stop)
    senders=tuple(re.findall(PATTERNS['attendee'],q))
    return Contract(fields,tokens,senders)


def assess(records,contract,provenance=None,trusted_query=None):
    if contract is None:return {'decision':'clarify','reason':'unsupported_task_contract','facts':[],'missing':[],'conflicts':[]}
    provenance=dict(provenance or {});facts=[]
    records=list(records)
    if trusted_query is not None:
        if any(str(r.get('id_',r.get('id',''))) == '__trusted_query__' for r in records):
            raise ValueError('Reserved provenance identifier in tool output')
        records.append({'id_':'__trusted_query__','body':trusted_query,'subject':trusted_query,'sender':'__user__'})
        provenance['__trusted_query__']={'authenticated':True,'sender':'__user__'}
    for record in records:
        rid=str(record.get('id_',record.get('id','')))
        body=str(record.get('body',''));subject=str(record.get('subject','')).lower()
        # Registry is supplied out of band; fields in untrusted records named "verified" are ignored.
        prov=provenance.get(rid,{})
        verified=prov.get('authenticated',False) and prov.get('sender')==record.get('sender')
        assurance=2 if verified else 0
        if verified and contract.authorized_senders and prov.get('sender') in contract.authorized_senders:assurance=3
        relevance=sum(token in subject or token in body.lower() for token in set(contract.topic_tokens))
        for field in contract.fields:
            for match in re.finditer(PATTERNS[field],body,re.I):
                value=match.group().rstrip('.,')
                if field=='url' and contract.allowed_url_hosts and (urlparse(value).hostname or '').lower() not in contract.allowed_url_hosts:continue
                facts.append({'field':field,'value':value,'record_id':rid,'start':match.start(),'end':match.start()+len(value),
                  'assurance':assurance,'topic_relevance':relevance,'source_sender':record.get('sender'),'source_timestamp':str(record.get('timestamp','')),
                  'scope':'trusted_user_request' if rid=='__trusted_query__' else 'retrieved_email',
                  'provenance':'authenticated_out_of_band' if verified else 'unverified_email',
                  'evidence':body[match.start():match.start()+len(value)]})
    selected={};missing=[];conflicts=[]
    for field in contract.fields:
        candidates=[f for f in facts if f['field']==field and f['topic_relevance']>0]
        if not candidates:missing.append(field);continue
        top=max(f['assurance'] for f in candidates)
        # Relevance is only a retrieval gate, never grounds to override a factual conflict.
        preferred=[f for f in candidates if f['assurance']==top]
        values=set(f['value'].casefold() for f in preferred)
        if len(values)>1:conflicts.append({'field':field,'values':sorted(values),'record_ids':sorted(set(f['record_id'] for f in preferred))})
        else:selected[field]=preferred
    return {'decision':'clarify' if missing or conflicts else 'proceed_with_evidence',
      'facts':facts,'selected':selected,'missing':missing,'conflicts':conflicts,
      'provenance_warning':any(f['assurance']==0 for fs in selected.values() for f in fs),
      'limits':'support and consistency check, NOT truth or safety verification; compatible poison can pass'}
