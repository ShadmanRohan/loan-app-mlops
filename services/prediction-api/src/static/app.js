const el = (id) => document.getElementById(id);

function payloadFromForm() {
  const ids = [
    'age','annual_income','credit_score','experience','loan_amount','loan_duration',
    'number_of_dependents','monthly_debt_payments','credit_card_utilization_rate',
    'number_of_open_credit_lines','number_of_credit_inquiries','debt_to_income_ratio',
    'bankruptcy_history','previous_loan_defaults','payment_history','length_of_credit_history',
    'savings_account_balance','checking_account_balance','total_assets','total_liabilities',
    'monthly_income','job_tenure','net_worth'
  ];

  const numeric = Object.fromEntries(ids.map(k => [k, Number(el(k).value)]));

  return {
    ...numeric,
    employment_status: el('employment_status').value,
    education_level: el('education_level').value,
    marital_status: el('marital_status').value,
    home_ownership_status: el('home_ownership_status').value,
    loan_purpose: el('loan_purpose').value,
  };
}

async function api(path, data) {
  const res = await fetch(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

function showStatus(html) { el('status').innerHTML = html; }
function showResult(obj) {
  el('result').style.display = 'block';
  el('result').textContent = JSON.stringify(obj, null, 2);
}

el('btnHealth').addEventListener('click', async () => {
  try {
    const res = await fetch('/health');
    const j = await res.json();
    const ok = j.status === 'healthy';
    showStatus(`<span class="badge ${ok ? 'ok' : 'warn'}">${ok ? 'HEALTHY' : 'ISSUE'}</span> SHAP: ${j.shap_available ? 'ON' : 'OFF'}`);
  } catch (e) {
    showStatus(`<span class="badge warn">ERROR</span> ${String(e)}`);
  }
});

el('btnPredict').addEventListener('click', async () => {
  try {
    const data = payloadFromForm();
    const res = await api('/predict', data);
    showResult(res);
  } catch (e) {
    showResult({ error: true, message: String(e) });
  }
});

el('btnExplain').addEventListener('click', async () => {
  try {
    const data = payloadFromForm();
    const res = await api('/predict/explain', data);
    showResult(res);
  } catch (e) {
    showResult({ error: true, message: String(e) });
  }
});


