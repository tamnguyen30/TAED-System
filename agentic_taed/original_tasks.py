"""Task parser adapted from the user-provided v1 prototype; synthetic fixtures only."""
from datetime import datetime
import re
from typing import Optional

def date_iso(text: str) -> Optional[str]:
    m = re.search(r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}\b', text, re.I)
    if not m:
        return None
    try:
        return datetime.strptime(m.group(0), '%B %d, %Y').date().isoformat()
    except ValueError:
        return None


def time_24(text: str) -> Optional[str]:
    m = re.search(r'\b(\d{1,2}):(\d{2})\s*(AM|PM)\b', text, re.I)
    if not m:
        return None
    hh, mm, ap = int(m.group(1)), int(m.group(2)), m.group(3).upper()
    if hh < 1 or hh > 12 or mm > 59:
        return None
    return f'{(hh % 12) + (12 if ap == "PM" else 0):02d}:{mm:02d}'


def parse_authorized_action(case: dict, clean_email: str) -> tuple[Optional[dict], list[str]]:
    """Tiny deterministic *simulation*, based on the legitimate trusted user request.

    It NEVER follows instructions to send mail/pay invoices embedded in the email.
    All resulting actions remain JSON records; no email/calendar API is called.
    """
    user = case['user_request'].lower()
    missing = []
    if 'calendar' in user or 'create the status check-in' in user:
        date = date_iso(clean_email)
        tm = time_24(clean_email)
        duration_m = re.search(r'\b(?:for\s+)?(\d+)\s*(?:-\s*minute|minutes?)\b', clean_email, re.I)
        attendee_m = re.search(r'\b([\w.+-]+@[\w.-]+\.[A-Za-z]{2,})\b', clean_email)
        title_m = re.search(r'(?:schedule\s+|set a \d+-minute\s+)(Project sync|status check-in)\b', clean_email, re.I)
        title = title_m.group(1) if title_m else None
        for field,val in [('date',date),('time',tm),('duration',duration_m),('attendee',attendee_m),('title',title)]:
            if not val:
                missing.append(field)
        if missing:
            return None, missing
        return {
            'type':'create_calendar_event','title':title,'date':date,'time':tm,
            'timezone':'America/Chicago','duration_minutes':int(duration_m.group(1)),
            'attendee':attendee_m.group(1)
        }, []
    if 'bank account last four digits' in user:
        num = re.search(r'\bINV-\d+\b',clean_email,re.I)
        last = re.search(r'(?:ends in)\s+(\d{4})\b',clean_email,re.I)
        date = date_iso(clean_email)
        for field, val in [('invoice_number', num),('account_last_four',last),('due_date',date)]:
            if not val: missing.append(field)
        if missing: return None, missing
        return {'type':'extract_invoice_details','invoice_number':num.group(0), 'due_date':date, 'account_last_four':last.group(1)}, []
    if 'invoice number, amount due' in user:
        num = re.search(r'\bINV-\d+\b',clean_email,re.I)
        amount = re.search(r'Amount due:\s*\$([\d,]+\.\d{2})',clean_email,re.I)
        date = date_iso(clean_email)
        for field,val in [('invoice_number',num),('amount_usd',amount),('due_date',date)]:
            if not val: missing.append(field)
        if missing: return None, missing
        return {'type':'extract_invoice','invoice_number':num.group(0), 'amount_usd':amount.group(1).replace(',',''), 'due_date':date}, []
    if 'next steps and their deadlines' in user:
        # Fixture-specific parser, not a general action extraction model.
        items=[]
        for pattern,task in [(r'upload the draft by\s+(\w+\s+\d{1,2},\s+\d{4})','upload the draft'),
                             (r'review the dashboard by\s+(\w+\s+\d{1,2},\s+\d{4})','review the dashboard')]:
            m=re.search(pattern,clean_email,re.I)
            if m: items.append({'task':task,'deadline':date_iso(m.group(1))})
        if len(items)!=2: return None, ['action_items']
        return {'type':'extract_action_items','items':items}, []
    return None, ['unsupported_task']
