import pytest

import clean_data

# Dados sintéticos mínimos com resposta conhecida para cada flag e rótulo.
FIXTURE = {
    "accounts": """account_id,account_name,industry,country,signup_date,referral_source,plan_tier,seats,is_trial,churn_flag
A1,Co1,EdTech,US,2024-01-10,ads,Pro,5,False,False
A2,Co2,FinTech,UK,2024-01-01,organic,Basic,3,True,True
""",
    "subscriptions": """subscription_id,account_id,start_date,end_date,plan_tier,seats,mrr_amount,arr_amount,is_trial,upgrade_flag,downgrade_flag,churn_flag,billing_frequency,auto_renew_flag
S1,A1,2024-01-15,2024-03-01,Pro,5,100,1200,False,True,True,True,monthly,True
S2,A1,2024-02-01,,Pro,5,200,2400,False,False,False,False,annual,True
S3,A1,2024-02-01,,Pro,5,200,2400,False,False,False,False,annual,True
S4,A2,2024-01-05,,Basic,3,0,0,True,False,False,False,monthly,False
""",
    "feature_usage": """usage_id,subscription_id,usage_date,feature_name,usage_count,usage_duration_secs,error_count,is_beta_feature
U1,S1,2024-01-05,f1,3,100,0,False
U1,S2,2024-02-10,f2,4,200,1,False
U2,S3,2024-02-11,f1,0,0,0,True
U3,S1,2024-03-05,f1,2,50,0,False
""",
    "support_tickets": """ticket_id,account_id,submitted_at,closed_at,resolution_time_hours,priority,first_response_time_minutes,satisfaction_score,escalation_flag
T1,A1,2024-01-01,2024-01-01 05:00:00,5.0,high,10,,False
T2,A2,2024-02-01,2024-02-01 03:00:00,3.0,low,20,4.0,True
""",
    "churn_events": """churn_event_id,account_id,churn_date,reason_code,refund_amount_usd,preceding_upgrade_flag,preceding_downgrade_flag,is_reactivation,feedback_text
C1,A1,2024-03-01,pricing,0.0,False,False,True,too expensive
C2,A1,2024-04-01,competitor,10.5,False,False,False,too expensive
""",
}


@pytest.fixture
def raw_dir(tmp_path):
    d = tmp_path / "raw"
    d.mkdir()
    for name, text in FIXTURE.items():
        (d / f"ravenstack_{name}.csv").write_text(text)
    return d


@pytest.fixture
def clean_tables(raw_dir):
    return clean_data.clean(clean_data.read_raw(raw_dir))[0]

