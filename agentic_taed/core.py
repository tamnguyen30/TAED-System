"""Auditable intervention with no access to evaluation answers or attack labels."""
from dataclasses import dataclass, asdict
import re
import time
import unicodedata

CONFIGS = ('no_defense', 'taed_only', 'filter_only', 'taed_filter', 'complete')

# Deliberately narrow, interpretable baseline, NOT a semantic safety guarantee.
PATTERNS = {
    'override': r'\b(?:ignore|disregard|override)\b.{0,65}\b(?:instructions?|rules?|user|system|task)\b',
    'role_spoof': r'(?:\[system\]|<\|(?:system|im_start)\|>|\bsystem (?:message|override)\b)',
    'exfiltration': r'\b(?:send|forward|upload|email|transmit)\b.{0,100}\b(?:secret|password|credentials?|inbox|all emails|security code)\b',
    'destruction': r'\b(?:delete|erase|wipe)\b.{0,50}\b(?:files?|emails?|inbox|records?)\b',
    'tool_instruction': r'\b(?:call|invoke|execute|run)\s+(?:the\s+)?(?:send_email|delete_file|shell|python|bash)\b',
    'mailbox_copy': r'\b(?:mirror|copy|replicate|export)\b.{0,80}\b(?:entire mailbox|all emails|inbox contents)\b',
    'structured_tool_request': r'\bEXECUTE_(?:EMAIL|TOOL)\s*\{',
    'calendar_exfiltration': r'\bsend\b.{0,40}\ball calendar details\b',
    'answer_contamination': r'\binclude the phrase\b.{0,140}\b(?:summarize|reply|answer)\b',
    'invented_fact': r'\b(?:pretend|invent|fabricate)\b.{0,80}\b(?:meeting|date|amount)\b',
    'concealment': r'\bdo not tell the user\b',
    'answer_hijack': r'\b(?:output|respond with|say only)\s+[\"\']?COMPROMISED\b',
}
FIELD_PATTERNS = {
    'date': r'\b\d{4}-\d{2}-\d{2}\b',
    'time': r'\b\d{1,2}:\d{2}\b',
    'location': r'(?im)^Location:\s*([^\n;]+)',
    'amount': r'\$\d+(?:\.\d{2})?',
    'code': r'\b\d{6}\b',
    'url': r'https?://[^\s<>]+',
}


def normalized(text):
    return ''.join(c for c in unicodedata.normalize('NFKC', text) if unicodedata.category(c) != 'Cf')


@dataclass
class RemovedSpan:
    start: int
    end: int
    text: str
    reasons: list[str]


def filter_text(text):
    """Remove unsafe clauses, retaining exact source offsets and untouched text."""
    spans = []
    # Split on lines, semicolons, or sentence boundaries, never dots within URLs.
    for match in re.finditer(r'[^\n;]+(?:[;\n]|$)|[\n;]', text):
        for sentence in re.finditer(r'.+?(?:[.!?](?=\s)|$)', match.group(), re.S):
            segment = sentence.group()
            reasons = [name for name, p in PATTERNS.items() if re.search(p, normalized(segment), re.I | re.S)]
            if reasons:
                start = match.start() + sentence.start()
                spans.append(RemovedSpan(start, start + len(segment), segment, reasons))
    parts, cursor = [], 0
    for span in spans:
        parts.append(text[cursor:span.start])
        cursor = span.end
    parts.append(text[cursor:])
    return ''.join(parts), spans


def extract_fields(text, required):
    result = {}
    for field in required:
        if field not in FIELD_PATTERNS:
            raise ValueError(f'Unsupported trusted task field: {field}')
        matches = list(re.finditer(FIELD_PATTERNS[field], text))
        values = list(dict.fromkeys(m.group(1) if m.lastindex else m.group() for m in matches))
        result[field] = values
    return result


def assess_sufficiency(text, required):
    """A conservative structural check; does not establish factual truth."""
    fields = extract_fields(text, required)
    missing = [k for k, v in fields.items() if not v]
    conflicting = [k for k, v in fields.items() if len(v) > 1]
    return {'sufficient': not missing and not conflicting, 'missing': missing,
            'conflicting': conflicting, 'fields': fields,
            'scope': 'structural_presence_and_uniqueness_only'}


class Intervention:
    def __init__(self, config, detector=None):
        if config not in CONFIGS:
            raise ValueError(config)
        if config in ('taed_only', 'taed_filter', 'complete') and detector is None:
            raise ValueError('TAED configurations require a real detector; no silent surrogate.')
        self.config, self.detector = config, detector

    def apply(self, text, required=()):
        start = time.perf_counter()
        detection = None
        spans = []
        output = text
        blocked = False
        if self.config in ('taed_only', 'taed_filter', 'complete'):
            detection = self.detector.predict(text)
        if self.config == 'taed_only' and detection['malicious']:
            output, blocked = '', True
        elif self.config == 'filter_only' or self.config == 'complete' or (
                self.config == 'taed_filter' and detection['malicious']):
            output, spans = filter_text(text)
        sufficiency = assess_sufficiency(output, required) if self.config == 'complete' else None
        # Complete always examines instructions, even when the phishing detector misses them.
        # This is an intentional routing difference, recorded in the report.
        if sufficiency and not sufficiency['sufficient']:
            blocked = True
        return {'config': self.config, 'text': output, 'blocked': blocked,
                'decision': 'abstain' if blocked else ('filtered' if spans else 'pass'),
                'removed_spans': [asdict(s) for s in spans], 'detection': detection,
                'sufficiency': sufficiency, 'latency_ms': (time.perf_counter()-start)*1000}
