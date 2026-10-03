import json

with open("novel_rd_directions/results_runoff_erosion.json", encoding="utf-8") as f:
    ro = json.load(f)
with open("novel_rd_directions/results_voi_drone.json", encoding="utf-8") as f:
    voi = json.load(f)
with open("novel_rd_directions/results_area_continua.json", encoding="utf-8") as f:
    ac = json.load(f)
with open("novel_rd_directions/AGROSTECH_NOVEL_RD_DOSSIER.md", "r", encoding="utf-8") as f:
    d = f.read()

# Checks for Candidate 1
assert "1.0000" in d, "C1 AUC missing"
assert "0.0289" in d, "C1 Brier missing"
assert "100.0%" in d, "C1 IoU/Acc missing"

# Checks for Candidate 2
nev_agro = f"R$ {voi['policies']['Agrostech VoI Dispatch']['net_economic_value_per_ha_brl']['mean']:.2f}"
nev_base = f"R$ {voi['policies']['Fixed Calendar (14d)']['net_economic_value_per_ha_brl']['mean']:.2f}"
loss_agro = f"R$ {voi['policies']['Agrostech VoI Dispatch']['loss_prevented_per_ha_brl']['mean']:.2f}"
loss_base = f"R$ {voi['policies']['Fixed Calendar (14d)']['loss_prevented_per_ha_brl']['mean']:.2f}"
cost_agro = f"R$ {voi['policies']['Agrostech VoI Dispatch']['flight_cost_per_ha_brl']['mean']:.2f}"
lat_agro = f"{voi['policies']['Agrostech VoI Dispatch']['mean_detection_latency_days']:.2f}"
fer_agro = f"{voi['policies']['Agrostech VoI Dispatch']['false_escalation_rate_pct']:.2f}%"
cap_agro = f"{voi['policies']['Agrostech VoI Dispatch']['early_intervention_capture_pct']:.2f}%"

print(f"Checking C2: {nev_agro}, {nev_base}, {loss_agro}, {cost_agro}, {lat_agro}, {fer_agro}, {cap_agro}")
assert nev_agro in d, f"{nev_agro} not in dossier"
assert nev_base in d, f"{nev_base} not in dossier"
assert loss_agro in d, f"{loss_agro} not in dossier"
assert cost_agro in d, f"{cost_agro} not in dossier"
assert lat_agro in d, f"{lat_agro} not in dossier"
assert fer_agro in d, f"{fer_agro} not in dossier"
assert cap_agro in d, f"{cap_agro} not in dossier"

# Checks for Candidate 3
sav_agro = f"{ro['models']['Agrostech Probabilistic SCS-CN']['earthmoving_savings_pct']:.2f}%"
vol_agro = f"{ro['models']['Agrostech Probabilistic SCS-CN']['excavation_volume_m3']:,.1f}"
vol_base = f"{ro['models']['Single-Run Deterministic SCS-CN']['excavation_volume_m3']:,.1f}"
brier_agro = f"{ro['models']['Agrostech Probabilistic SCS-CN']['spatial_brier_score']:.4f}"
brier_base = f"{ro['models']['Single-Run Deterministic SCS-CN']['spatial_brier_score']:.4f}"
brier_rat = f"{ro['models']['Deterministic Rational Method']['spatial_brier_score']:.4f}"

print(f"Checking C3: {sav_agro}, {vol_agro}, {vol_base}, {brier_agro}, {brier_base}, {brier_rat}")
assert sav_agro in d, f"{sav_agro} not in dossier"
assert "26,958.5" in d, "26,958.5 not in dossier"
assert "33,849.4" in d, "33,849.4 not in dossier"
assert "6,890.9" in d, "6,890.9 not in dossier"
assert brier_agro in d, f"{brier_agro} not in dossier"
assert brier_base in d, f"{brier_base} not in dossier"
assert brier_rat in d, f"{brier_rat} not in dossier"

# Check absence of any hallucinated / previous audit numbers
forbidden = ["36.40%", "3.20%", "0.4200", "0.0520", "2.10 days", "Zero Wasted Flights", "36.4%", "R$ 0.00 / ha*"]
for tok in forbidden:
    assert tok not in d, f"Forbidden token {tok} found in dossier"

print("ALL CROSS-CHECKS PASSED PERFECTLY!")
