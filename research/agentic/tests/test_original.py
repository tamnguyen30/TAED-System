from agentic_taed.run_original_poc import simulated_task_agent
from agentic_taed.original_tasks import parse_authorized_action


def test_no_fixture_gold_required_by_agent():
    result=simulated_task_agent('From the invoice email, extract its invoice number, amount due, and due date.',
      'Invoice INV-999. Amount due: $12.00. Due date: December 1, 2027.')
    assert result['action']['invoice_number']=='INV-999'
    assert result['action']['amount_usd']=='12.00'
    assert result['action']['due_date']=='2027-12-01'


def test_missing_date_is_not_recovered_from_gold():
    action,missing=parse_authorized_action({'user_request':'create the status check-in'},
       'Please set a 20-minute status check-in at 3:30 PM Central with maya@example.org.')
    assert action is None and 'date' in missing
