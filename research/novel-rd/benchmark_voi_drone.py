"""
benchmark_voi_drone.py
======================
Agrostech Novel R&D Directions — Candidate 2 Benchmark & PoC Engine
Value-of-Information (VoI) Trigger-Based Drone Dispatch vs Industry Baselines.

Compares:
1. Baseline 1: Fixed Calendar Policy (Bi-weekly rigid flight schedule every 14 days).
2. Baseline 2: Naive NDVI Threshold Policy (Reactive dispatch when optical NDVI < 0.65).
3. Agrostech Decision-Theoretic VoI Dispatch:
   - NVoI(t) = GVoI(t) - C_flight = [rho*(b_t) - E_Z[rho*(b_{t|Z})]] - C_flight.
   - Factors credit exposure, phenological vulnerability V(t), cloud Markov chains,
     action loss matrix, and marginal UAV flight logistics.

Zero-dependency implementation: Python 3.12 + numpy + scipy + pandas + matplotlib.
"""

import argparse
import json
import math
import os
import sys
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Tuple

import matplotlib
matplotlib.use("Agg")  # Headless backend
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class AgronomicRiskEvent:
    event_id: str
    event_type: str        # 'rust', 'caterpillar', 'waterlogging', 'grain_diversion'
    onset_dap: int         # Day After Planting when event initiates
    severity_fraction: float # Loss potential fraction of effective exposure [0, 1]
    critical_window_days: int # Days before damage becomes unmitigable (decay tau)
    is_active: bool = True
    resolved: bool = False
    detected_dap: Optional[int] = None


@dataclass
class DailyTelemetry:
    dap: int
    is_cloudy: bool
    cloud_prob_forecast: float
    satellite_optical_observed: bool
    days_since_clear_satellite: int
    true_latent_state: int  # 0: Healthy, 1: Early Stress, 2: Severe Failure, 3: Grain Diversion
    phenological_vulnerability: float
    ndvi_apparent: float


# =============================================================================
# 1. WEATHER & CROP CYCLE SIMULATORS
# =============================================================================

class CerradoWeatherSimulator:
    """
    Simulates daily cloud cover and rainfall for Sorriso/MT across 120-day cycle.
    Uses non-homogeneous Markov chain capturing the December-February rainy season surge.
    """
    def __init__(self, rng: np.random.Generator):
        self.rng = rng

    def simulate_season_weather(self, total_days: int = 120) -> Tuple[np.ndarray, np.ndarray]:
        """
        Returns:
            is_cloudy: boolean array (True if cloud cover blocks optical satellite).
            cloud_forecast: probability of cloud cover [0, 1].
        """
        is_cloudy = np.zeros(total_days, dtype=bool)
        cloud_forecast = np.zeros(total_days, dtype=float)

        curr_state = False  # Start clear in October planting
        for t in range(total_days):
            dap = t + 1
            # Seasonality transition matrix:
            if dap <= 44:
                # Early vegetative / transition season
                p_clear_to_cloud = 0.35
                p_cloud_to_cloud = 0.55
                forecast_base = 0.35
            elif dap <= 85:
                # Peak wet season surge (Dec/Jan) — 75% to 85% persistent cloud cover
                p_clear_to_cloud = 0.80
                p_cloud_to_cloud = 0.88
                forecast_base = 0.82
            else:
                # Late maturation / harvest
                p_clear_to_cloud = 0.40
                p_cloud_to_cloud = 0.58
                forecast_base = 0.45

            if not curr_state:
                curr_state = bool(self.rng.random() < p_clear_to_cloud)
            else:
                curr_state = bool(self.rng.random() < p_cloud_to_cloud)

            is_cloudy[t] = curr_state
            # Forecast has slight measurement noise around true probability
            cloud_forecast[t] = np.clip(forecast_base + self.rng.normal(0, 0.08), 0.05, 0.98)

        return is_cloudy, cloud_forecast


class CropCycleRiskSimulator:
    """
    120-day soybean cycle simulator with stochastic risk event injection
    and credit damage accumulation.
    """
    def __init__(
        self,
        rng: np.random.Generator,
        area_ha: float = 1000.0,
        credit_exposure: float = 3500000.0
    ):
        self.rng = rng
        self.area_ha = area_ha
        self.credit_exposure = credit_exposure

    @staticmethod
    def get_phenological_vulnerability(dap: int) -> float:
        """
        Crop sensitivity to yield loss and fraud risk across growth stages:
        - Emergence to V3 (1-20 DAP): V = 0.15 (resilient)
        - V4 to V8 (21-45 DAP): V = 0.40
        - Flowering & Pod Fill R1-R5 (46-85 DAP): V in [0.70, 1.00] (peak yield penalty)
        - Maturation R7-R8 (86-115 DAP): V = 0.85 (grain diversion risk)
        - Post-harvest (116-120 DAP): V = 0.05
        """
        if dap <= 20:
            return 0.15
        elif dap <= 45:
            return 0.40
        elif dap <= 85:
            return 0.40 + 0.60 * math.exp(- ((dap - 65) ** 2) / (2.0 * (15.0 ** 2)))
        elif dap <= 115:
            return 0.85
        else:
            return 0.05

    def generate_stochastic_events(self) -> List[AgronomicRiskEvent]:
        """Injects 1 to 3 realistic risk events per season."""
        events = []
        # Event 1: Early vegetative caterpillar defoliation (prob 0.65)
        if self.rng.random() < 0.65:
            onset = int(self.rng.integers(25, 42))
            events.append(AgronomicRiskEvent(
                event_id="EVT_CATERPILLAR",
                event_type="caterpillar",
                onset_dap=onset,
                severity_fraction=float(self.rng.uniform(0.12, 0.22)),
                critical_window_days=4
            ))

        # Event 2: Peak wet season Asian Soybean Rust (prob 0.80)
        if self.rng.random() < 0.80:
            onset = int(self.rng.integers(52, 75))
            events.append(AgronomicRiskEvent(
                event_id="EVT_SOYBEAN_RUST",
                event_type="rust",
                onset_dap=onset,
                severity_fraction=float(self.rng.uniform(0.28, 0.45)),
                critical_window_days=4
            ))

        # Event 3: Heavy rain soil waterlogging / terrace breach (prob 0.35)
        if self.rng.random() < 0.35:
            onset = int(self.rng.integers(65, 82))
            events.append(AgronomicRiskEvent(
                event_id="EVT_WATERLOGGING",
                event_type="waterlogging",
                onset_dap=onset,
                severity_fraction=float(self.rng.uniform(0.15, 0.30)),
                critical_window_days=5
            ))

        # Event 4: Grain diversion / unauthorized early harvest (prob 0.25)
        if self.rng.random() < 0.25:
            onset = int(self.rng.integers(98, 112))
            events.append(AgronomicRiskEvent(
                event_id="EVT_GRAIN_DIVERSION",
                event_type="grain_diversion",
                onset_dap=onset,
                severity_fraction=float(self.rng.uniform(0.40, 0.65)),
                critical_window_days=3
            ))

        return events


# =============================================================================
# 2. DISPATCH POLICY IMPLEMENTATIONS
# =============================================================================

class DroneFlightCostModel:
    """Marginal Drone Flight Cost Model under Brazilian Cerrado operational rates."""
    def __init__(
        self,
        mobilization_base: float = 1200.0,
        variable_cost_per_ha: float = 4.50
    ):
        self.c_mob = mobilization_base
        self.c_var = variable_cost_per_ha

    def compute_cost(self, area_ha: float) -> float:
        return self.c_mob + (self.c_var * area_ha)


class FixedCalendarPolicy:
    """Baseline 1: Dispatches drone every K days (default K=14 days)."""
    def __init__(self, interval_days: int = 14):
        self.interval = interval_days

    def should_dispatch(self, dap: int, **kwargs) -> bool:
        return (dap % self.interval) == 0


class NaiveNDVIPolicy:
    """
    Baseline 2: Dispatches drone when observed satellite NDVI drops below threshold.
    Susceptible to false alarms from cloud shadows, soil wetness, and atmospheric haze.
    """
    def __init__(self, ndvi_threshold: float = 0.65):
        self.threshold = ndvi_threshold
        self.last_dispatch_dap = -99

    def should_dispatch(self, dap: int, ndvi_apparent: float, optical_available: bool, **kwargs) -> bool:
        # Minimum 5-day cooldown between reactive dispatches
        if (dap - self.last_dispatch_dap) < 5:
            return False
        # If clear satellite shows drop, reactive dispatch
        if optical_available and (ndvi_apparent < self.threshold):
            self.last_dispatch_dap = dap
            return True
        return False


class AgrostechVoIPolicy:
    """
    Agrostech Patentable Engine: Decision-Theoretic Value-of-Information (VoI) Trigger.
    NVoI(t) = GVoI(t) - C_flight.
    Dispatches only when expected reduction in credit risk strictly exceeds marginal flight cost.
    """
    def __init__(
        self,
        cost_model: DroneFlightCostModel,
        area_ha: float,
        credit_exposure: float,
        threshold_brl: float = 0.0
    ):
        self.cost_model = cost_model
        self.area_ha = area_ha
        self.credit_exposure = credit_exposure
        self.threshold_brl = threshold_brl

        # Latent state belief: [b0: Healthy, b1: Stress/Pest, b2: Failure/Disease, b3: Fraud/Diversion]
        self.belief = np.array([0.94, 0.04, 0.01, 0.01], dtype=float)
        self.last_dispatch_dap = -99

        # UAV Confusion Matrix Pi_kj = P(Z=zk | theta=thetaj)
        self.Pi_uav = np.array([
            [0.96, 0.03, 0.01, 0.00],
            [0.02, 0.94, 0.04, 0.00],
            [0.01, 0.03, 0.95, 0.01],
            [0.01, 0.00, 0.00, 0.99]
        ], dtype=float)

    def update_daily_belief(
        self,
        dap: int,
        days_since_clear: int,
        optical_observed: bool,
        ndvi_apparent: float,
        v_t: float
    ):
        """Bayesian belief transition and satellite measurement update."""
        if optical_observed:
            # Satellite observed: update belief with optical signal
            if ndvi_apparent >= 0.72:
                # Strong healthy evidence: near-zero uncertainty
                likelihood = np.array([0.985, 0.010, 0.003, 0.002])
            elif ndvi_apparent >= 0.58:
                # Moderate stress observed from space
                likelihood = np.array([0.15, 0.72, 0.10, 0.03])
            else:
                # Severe vegetation drop
                likelihood = np.array([0.03, 0.20, 0.65, 0.12])
            self.belief = (self.belief * likelihood) / np.sum(self.belief * likelihood)
        else:
            # Persistent cloud cover: information decays dynamically
            # Hazard rate scales with phenological vulnerability V(t)
            hazard_stress = min(0.35, 0.015 + 0.022 * days_since_clear * v_t)
            hazard_failure = min(0.20, 0.005 + 0.015 * days_since_clear * v_t)
            hazard_fraud = 0.18 if (85 <= dap <= 115 and days_since_clear >= 7) else 0.01

            b_healthy = max(0.05, 1.0 - (hazard_stress + hazard_failure + hazard_fraud))
            diffuse_target = np.array([b_healthy, hazard_stress, hazard_failure, hazard_fraud])
            diffuse_target /= np.sum(diffuse_target)

            # Daily diffusion toward entropy
            alpha = min(0.45, 0.06 * days_since_clear)
            self.belief = (1.0 - alpha) * self.belief + alpha * diffuse_target
            self.belief /= np.sum(self.belief)

    def evaluate_voi(
        self,
        dap: int,
        v_t: float,
        cloud_prob_forecast: float
    ) -> Tuple[bool, float, float, float]:
        """
        Computes Gross VoI and Net VoI:
        NVoI = GVoI - C_flight.
        """
        # Minimum cooldown of 7 days between flights
        if (dap - self.last_dispatch_dap) < 7:
            return False, 0.0, 0.0, self.cost_model.compute_cost(self.area_ha)

        c_flight = self.cost_model.compute_cost(self.area_ha)
        e = self.credit_exposure * v_t

        # Canonical Action Loss Matrix (R$)
        # Actions: a0: Maintain, a1: Remediate, a2: Freeze Credit, a3: Forensic Seizure
        c_rem = 40.0 * self.area_ha  # R$ 40/ha targeted agronomic input
        c_fric = 0.03 * e           # Financial friction / interest margin foregone
        c_leg = 0.08 * e            # Legal and restructuring mobilization

        loss_matrix = np.array([
            [0.0, 0.25 * e, 0.65 * e, 0.85 * e],
            [c_rem, c_rem + 0.05 * e, 0.65 * e, 0.85 * e],
            [c_fric, c_fric + 0.20 * e, c_fric + 0.25 * e, c_fric + 0.40 * e],
            [c_leg, c_leg + 0.20 * e, c_leg + 0.15 * e, c_leg + 0.12 * e]
        ], dtype=float)

        # 1. Prior optimal expected loss
        prior_losses = [np.dot(loss_matrix[i, :], self.belief) for i in range(4)]
        prior_min_loss = min(prior_losses)

        # 2. Expected loss after drone flight observation
        p_z = np.dot(self.Pi_uav, self.belief)
        expected_post_loss = 0.0
        for k in range(4):
            if p_z[k] > 1e-9:
                post_b_k = (self.Pi_uav[k, :] * self.belief) / p_z[k]
                post_min_k = min([np.dot(loss_matrix[i, :], post_b_k) for i in range(4)])
                expected_post_loss += p_z[k] * post_min_k

        # 3. VoI Computation
        gvoi = max(0.0, prior_min_loss - expected_post_loss)
        nvoi = gvoi - c_flight

        should_dispatch = bool((nvoi > self.threshold_brl) and (v_t >= 0.20))
        if should_dispatch:
            self.last_dispatch_dap = dap
            # Reset belief upon sub-5cm drone inspection
            self.belief = np.array([0.98, 0.01, 0.005, 0.005])

        return should_dispatch, float(nvoi), float(gvoi), float(c_flight)


# =============================================================================
# 3. BENCHMARK SIMULATION & EVALUATION ENGINE
# =============================================================================

class VoIBenchmarkEvaluator:
    """
    Simulates and evaluates all 3 policies across M Monte Carlo seasons:
    Computes:
    - Net Economic Value (NEV) in R$ and R$/ha
    - Total flight cost per hectare (R$/ha)
    - Detection latency (days from onset to detection)
    - False Escalation Rate (FER)
    - Early intervention capture rate (% caught within 4 days)
    """

    def __init__(
        self,
        area_ha: float = 1000.0,
        credit_exposure: float = 3500000.0,
        cost_model: Optional[DroneFlightCostModel] = None,
        seed: int = 42
    ):
        self.area_ha = area_ha
        self.credit_exposure = credit_exposure
        self.cost_model = cost_model or DroneFlightCostModel()
        self.rng = np.random.default_rng(seed)

    def run_single_season(
        self,
        season_idx: int,
        weather_sim: CerradoWeatherSimulator,
        risk_sim: CropCycleRiskSimulator
    ) -> Dict[str, Any]:
        total_days = 120
        is_cloudy, cloud_forecast = weather_sim.simulate_season_weather(total_days)
        events = risk_sim.generate_stochastic_events()

        # Telemetry timeline
        days_since_clear = 0
        telemetry_log = []

        # Baseline nominal NDVI trajectory
        t_steps = np.arange(1, total_days + 1)
        base_ndvi = 0.18 + 0.68 * (
            (1.0 / (1.0 + np.exp(-0.12 * (t_steps - 30)))) -
            (1.0 / (1.0 + np.exp(-0.10 * (t_steps - 95))))
        )

        for d in range(1, total_days + 1):
            cloud = is_cloudy[d - 1]
            if not cloud:
                days_since_clear = 0
                optical_seen = True
            else:
                days_since_clear += 1
                optical_seen = False

            v_t = risk_sim.get_phenological_vulnerability(d)

            # Active event impact on ground
            active_events = [e for e in events if e.onset_dap <= d and not e.resolved]
            max_sev = max([e.severity_fraction for e in active_events], default=0.0)

            # Apparent NDVI (with noise / cloud shadow artifacts)
            ndvi_val = base_ndvi[d - 1] * (1.0 - 0.7 * max_sev)
            if self.rng.random() < 0.08:  # 8% false haze/shadow dip
                ndvi_val -= self.rng.uniform(0.12, 0.25)
            ndvi_val = float(np.clip(ndvi_val, 0.10, 0.92))

            # Latent state
            if max_sev == 0.0:
                l_state = 0
            elif any(e.event_type == "grain_diversion" for e in active_events):
                l_state = 3
            elif max_sev > 0.25:
                l_state = 2
            else:
                l_state = 1

            telemetry_log.append(DailyTelemetry(
                dap=d,
                is_cloudy=cloud,
                cloud_prob_forecast=cloud_forecast[d - 1],
                satellite_optical_observed=optical_seen,
                days_since_clear_satellite=days_since_clear,
                true_latent_state=l_state,
                phenological_vulnerability=v_t,
                ndvi_apparent=ndvi_val
            ))

        # Instantiate policies
        pol_fixed = FixedCalendarPolicy(interval_days=14)
        pol_naive = NaiveNDVIPolicy(ndvi_threshold=0.62)
        pol_agrostech = AgrostechVoIPolicy(
            self.cost_model,
            self.area_ha,
            self.credit_exposure,
            threshold_brl=5000.0
        )

        policies = {
            "Agrostech VoI Dispatch": pol_agrostech,
            "Fixed Calendar (14d)": pol_fixed,
            "Naive NDVI Threshold": pol_naive
        }

        season_results = {}
        for pol_name, policy in policies.items():
            # Deep copy events for each policy evaluation
            pol_events = [
                AgronomicRiskEvent(
                    event_id=e.event_id,
                    event_type=e.event_type,
                    onset_dap=e.onset_dap,
                    severity_fraction=e.severity_fraction,
                    critical_window_days=e.critical_window_days
                ) for e in events
            ]

            flights_dap = []
            flight_costs_cum = 0.0
            daily_nvoi_trace = []
            c_flight = self.cost_model.compute_cost(self.area_ha)

            for tel in telemetry_log:
                d = tel.dap
                dispatch = False

                if pol_name == "Agrostech VoI Dispatch":
                    policy.update_daily_belief(
                        dap=d,
                        days_since_clear=tel.days_since_clear_satellite,
                        optical_observed=tel.satellite_optical_observed,
                        ndvi_apparent=tel.ndvi_apparent,
                        v_t=tel.phenological_vulnerability
                    )
                    dispatch, nvoi, gvoi, cost = policy.evaluate_voi(
                        dap=d,
                        v_t=tel.phenological_vulnerability,
                        cloud_prob_forecast=tel.cloud_prob_forecast
                    )
                    daily_nvoi_trace.append(nvoi)
                elif pol_name == "Fixed Calendar (14d)":
                    dispatch = policy.should_dispatch(dap=d)
                    daily_nvoi_trace.append(0.0)
                elif pol_name == "Naive NDVI Threshold":
                    dispatch = policy.should_dispatch(
                        dap=d,
                        ndvi_apparent=tel.ndvi_apparent,
                        optical_available=tel.satellite_optical_observed
                    )
                    daily_nvoi_trace.append(0.0)

                if dispatch:
                    flights_dap.append(d)
                    flight_costs_cum += c_flight
                    # Resolve active events detected by drone
                    for ev in pol_events:
                        if ev.onset_dap <= d and not ev.resolved:
                            ev.resolved = True
                            ev.detected_dap = d

            # Calculate damage and loss prevented
            total_potential_loss = 0.0
            total_realized_loss = 0.0
            latencies = []
            caught_early_count = 0

            for ev in pol_events:
                effective_exp = self.credit_exposure * risk_sim.get_phenological_vulnerability(ev.onset_dap)
                pot_loss = effective_exp * ev.severity_fraction
                total_potential_loss += pot_loss

                if ev.resolved and ev.detected_dap is not None:
                    latency = ev.detected_dap - ev.onset_dap
                    latencies.append(latency)
                    # Mitigability decay: M(dt) = exp(-dt / tau)
                    mitigability = max(0.0, math.exp(-latency / float(ev.critical_window_days)))
                    avoided = pot_loss * 0.85 * mitigability
                    realized = pot_loss - avoided
                    if latency <= ev.critical_window_days:
                        caught_early_count += 1
                else:
                    # Undetected: 100% loss realized
                    realized = pot_loss
                    latencies.append(30.0)  # Heavy penalty for unmonitored loss

                total_realized_loss += realized

            loss_prevented = total_potential_loss - total_realized_loss
            net_economic_value = loss_prevented - flight_costs_cum

            # False Escalations: flights dispatched when no active event existed
            false_escalations = 0
            for f_dap in flights_dap:
                had_event = any(e.onset_dap <= f_dap <= (e.onset_dap + 25) for e in events)
                if not had_event:
                    false_escalations += 1

            total_flights = len(flights_dap)
            fer = (false_escalations / total_flights * 100.0) if total_flights > 0 else 0.0
            early_capture_rate = (caught_early_count / len(pol_events) * 100.0) if pol_events else 100.0
            mean_latency = float(np.mean(latencies)) if latencies else 0.0

            season_results[pol_name] = {
                "total_flights": total_flights,
                "flight_cost_brl": flight_costs_cum,
                "flight_cost_per_ha_brl": flight_costs_cum / self.area_ha,
                "loss_prevented_brl": loss_prevented,
                "loss_prevented_per_ha_brl": loss_prevented / self.area_ha,
                "net_economic_value_brl": net_economic_value,
                "net_economic_value_per_ha_brl": net_economic_value / self.area_ha,
                "mean_latency_days": mean_latency,
                "false_escalation_rate_pct": fer,
                "early_capture_rate_pct": early_capture_rate,
                "flights_dap": flights_dap,
                "_daily_nvoi": daily_nvoi_trace
            }

        return {
            "season_idx": season_idx,
            "telemetry": telemetry_log,
            "events": events,
            "policies": season_results
        }

    def run_monte_carlo_benchmark(
        self,
        num_seasons: int = 100
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        print(f"[BENCHMARK 2] Running {num_seasons} Monte Carlo seasons (120-day Cerrado soybean cycle)...")
        weather_sim = CerradoWeatherSimulator(self.rng)
        risk_sim = CropCycleRiskSimulator(self.rng, self.area_ha, self.credit_exposure)

        all_season_results = []
        for s in range(num_seasons):
            res = self.run_single_season(s + 1, weather_sim, risk_sim)
            all_season_results.append(res)

        # Aggregate metrics across all seasons
        pol_names = ["Agrostech VoI Dispatch", "Fixed Calendar (14d)", "Naive NDVI Threshold"]
        summary = {}

        for p_name in pol_names:
            nev_ha = [s["policies"][p_name]["net_economic_value_per_ha_brl"] for s in all_season_results]
            cost_ha = [s["policies"][p_name]["flight_cost_per_ha_brl"] for s in all_season_results]
            prevented_ha = [s["policies"][p_name]["loss_prevented_per_ha_brl"] for s in all_season_results]
            latencies = [s["policies"][p_name]["mean_latency_days"] for s in all_season_results]
            fers = [s["policies"][p_name]["false_escalation_rate_pct"] for s in all_season_results]
            captures = [s["policies"][p_name]["early_capture_rate_pct"] for s in all_season_results]
            flights = [s["policies"][p_name]["total_flights"] for s in all_season_results]

            summary[p_name] = {
                "policy_name": p_name,
                "net_economic_value_per_ha_brl": {
                    "mean": round(float(np.mean(nev_ha)), 2),
                    "std": round(float(np.std(nev_ha)), 2),
                    "p10": round(float(np.percentile(nev_ha, 10)), 2),
                    "p90": round(float(np.percentile(nev_ha, 90)), 2)
                },
                "flight_cost_per_ha_brl": {
                    "mean": round(float(np.mean(cost_ha)), 2),
                    "std": round(float(np.std(cost_ha)), 2)
                },
                "loss_prevented_per_ha_brl": {
                    "mean": round(float(np.mean(prevented_ha)), 2)
                },
                "mean_flight_count": round(float(np.mean(flights)), 1),
                "mean_detection_latency_days": round(float(np.mean(latencies)), 2),
                "false_escalation_rate_pct": round(float(np.mean(fers)), 2),
                "early_intervention_capture_pct": round(float(np.mean(captures)), 2)
            }

        representative_season = all_season_results[0]
        return summary, representative_season


# =============================================================================
# 4. PLOTTING & VISUALIZATION ARTIFACTS
# =============================================================================

def render_voi_benchmark_plots(
    summary: Dict[str, Any],
    sample_season: Dict[str, Any],
    output_path: str
):
    """
    Renders 4-panel publication-grade figure:
    1. Cumulative Net Economic Value (NEV) Timeline (R$)
    2. Flight Cost vs Loss Prevented Breakdown
    3. Detection Latency & Early Capture Comparison
    4. Daily VoI Curve vs Cloud Probability & Phenological Vulnerability Window
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 11), dpi=300)
    plt.subplots_adjust(hspace=0.32, wspace=0.28)

    # 1. Net Economic Value Bar Chart with Error Bars
    ax1 = axes[0, 0]
    pol_names = ["Agrostech VoI Dispatch", "Fixed Calendar (14d)", "Naive NDVI Threshold"]
    short_names = ["Agrostech VoI", "Fixed Calendar", "Naive NDVI"]
    means = [summary[p]["net_economic_value_per_ha_brl"]["mean"] for p in pol_names]
    stds = [summary[p]["net_economic_value_per_ha_brl"]["std"] for p in pol_names]
    colors = ["#1b5e20", "#e65100", "#c62828"]

    bars = ax1.bar(short_names, means, yerr=stds, capsize=6, color=colors, alpha=0.85, edgecolor="black", linewidth=1.2)
    ax1.set_ylabel("Net Economic Value (R$/ha)", fontsize=11, fontweight="bold")
    ax1.set_title("A. Net Economic Value (NEV = Avoided Loss - Costs)", fontsize=12, fontweight="bold")
    ax1.axhline(0, color="black", linestyle="--", linewidth=1.0)
    ax1.grid(True, linestyle=":", alpha=0.6, axis="y")

    for bar in bars:
        h = bar.get_height()
        va = "bottom" if h >= 0 else "top"
        y_pos = h + 10.0 if h >= 0 else h - 25.0
        ax1.text(bar.get_x() + bar.get_width() / 2.0, y_pos, f"R$ {h:.1f}/ha", ha="center", va=va, fontsize=9, fontweight="bold")

    # 2. Cumulative Flight Cost vs Loss Prevented
    ax2 = axes[0, 1]
    cost_means = [summary[p]["flight_cost_per_ha_brl"]["mean"] for p in pol_names]
    prevented_means = [summary[p]["loss_prevented_per_ha_brl"]["mean"] for p in pol_names]

    x = np.arange(len(short_names))
    width = 0.32
    b1 = ax2.bar(x - width/2, cost_means, width, label="Flight Cost (R$/ha)", color="#ef5350", alpha=0.85)
    b2 = ax2.bar(x + width/2, prevented_means, width, label="Loss Prevented (R$/ha)", color="#43a047", alpha=0.85)

    ax2.set_xticks(x)
    ax2.set_xticklabels(short_names, fontsize=9.5, fontweight="bold")
    ax2.set_ylabel("Financial Scale (R$/ha)", fontsize=11, fontweight="bold")
    ax2.set_title("B. Drone Flight Cost vs Loss Prevented Breakdown", fontsize=12, fontweight="bold")
    ax2.legend(loc="upper left", frameon=True, fontsize=9)
    ax2.grid(True, linestyle=":", alpha=0.6, axis="y")

    # 3. Detection Latency & Early Intervention Capture Rate
    ax3 = axes[1, 0]
    latencies = [summary[p]["mean_detection_latency_days"] for p in pol_names]
    captures = [summary[p]["early_intervention_capture_pct"] for p in pol_names]

    b3 = ax3.bar(x - width/2, latencies, width, label="Mean Latency (Days)", color="#ff9800", alpha=0.85)
    ax3_twin = ax3.twinx()
    b4 = ax3_twin.bar(x + width/2, captures, width, label="Early Capture Rate (%)", color="#2e7d32", alpha=0.85)

    ax3.set_xticks(x)
    ax3.set_xticklabels(short_names, fontsize=9.5, fontweight="bold")
    ax3.set_ylabel("Detection Latency (Days)", fontsize=11, fontweight="bold", color="#e65100")
    ax3_twin.set_ylabel("Early Capture Rate (<= 4d) %", fontsize=11, fontweight="bold", color="#1b5e20")
    ax3_twin.set_ylim([0, 110])
    ax3.set_title("C. Operational Latency & Early Salvage Efficiency", fontsize=12, fontweight="bold")

    lines1, labels1 = ax3.get_legend_handles_labels()
    lines2, labels2 = ax3_twin.get_legend_handles_labels()
    ax3.legend(lines1 + lines2, labels1 + labels2, loc="upper right", frameon=True, fontsize=8.5)
    ax3.grid(True, linestyle=":", alpha=0.6, axis="y")

    # 4. Daily VoI Curve vs Cloud Probability & Phenological Vulnerability Window
    ax4 = axes[1, 1]
    telem = sample_season["telemetry"]
    daps = [t.dap for t in telem]
    v_ts = [t.phenological_vulnerability for t in telem]
    clouds = [t.cloud_prob_forecast for t in telem]
    nvoi_trace = sample_season["policies"]["Agrostech VoI Dispatch"]["_daily_nvoi"]
    flights_dap = sample_season["policies"]["Agrostech VoI Dispatch"]["flights_dap"]

    ax4.plot(daps, clouds, color="#78909c", linestyle="--", linewidth=1.5, label="Cloud Cover Probability")
    ax4.plot(daps, v_ts, color="#ab47bc", linewidth=2.0, label="Phenological Vulnerability V(t)")

    ax4_twin = ax4.twinx()
    ax4_twin.plot(daps, np.array(nvoi_trace) / 1000.0, color="#1b5e20", linewidth=2.2, label="Daily Net VoI (k R$)")
    ax4_twin.axhline(0, color="gray", linestyle=":", alpha=0.7)

    # Mark drone dispatch days
    for f_dap in flights_dap:
        ax4_twin.axvline(f_dap, color="#d32f2f", linestyle="-", alpha=0.7, linewidth=1.5)
        ax4_twin.scatter([f_dap], [nvoi_trace[f_dap - 1] / 1000.0], color="#d32f2f", s=45, zorder=5)

    ax4.set_xlabel("Days After Planting (DAP)", fontsize=11, fontweight="bold")
    ax4.set_ylabel("Probability / Vulnerability Scale", fontsize=11, fontweight="bold")
    ax4_twin.set_ylabel("Net VoI (R$ Thousand)", fontsize=11, fontweight="bold", color="#1b5e20")
    ax4.set_title("D. Agrostech Dynamic VoI Dispatch in 120-Day Cycle", fontsize=12, fontweight="bold")

    lines_a, labels_a = ax4.get_legend_handles_labels()
    lines_b, labels_b = ax4_twin.get_legend_handles_labels()
    ax4.legend(lines_a + lines_b, labels_a + labels_b, loc="upper left", frameon=True, fontsize=8)
    ax4.grid(True, linestyle=":", alpha=0.6)

    plt.suptitle("AGROSTECH R&D BENCHMARK — VALUE-OF-INFORMATION (VoI) DRONE DISPATCH\nSimulated Across M=100 Cerrado Soybean Crop Seasons (1,000 ha Parcel in Sorriso/MT)",
                 fontsize=14, fontweight="bold", y=0.98)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"[SUCCESS] VoI Benchmark visualization plot saved to: {output_path}")


# =============================================================================
# 5. MAIN EXECUTION PIPELINE
# =============================================================================

def run_voi_drone_benchmark(
    days: int = 120,
    area_ha: float = 1000.0,
    credit_exposure: float = 3500000.0,
    monte_carlo: int = 100,
    plot: bool = True,
    output_json: str = "results_voi_drone.json",
    output_png: str = "benchmark_voi_drone.png"
) -> Dict[str, Any]:
    print(f"[BENCHMARK 2] Initializing VoI Drone Benchmark: {area_ha} ha, Credit R$ {credit_exposure:,.2f}")
    evaluator = VoIBenchmarkEvaluator(
        area_ha=area_ha,
        credit_exposure=credit_exposure,
        seed=42
    )

    summary_metrics, sample_season = evaluator.run_monte_carlo_benchmark(num_seasons=monte_carlo)

    results_export = {
        "benchmark_name": "Value-of-Information Drone Trigger Dispatch",
        "farm_parameters": {
            "area_ha": area_ha,
            "credit_exposure_brl": credit_exposure,
            "crop_cycle_days": days,
            "monte_carlo_iterations": monte_carlo
        },
        "policies": summary_metrics
    }

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(results_export, f, indent=2)
    print(f"[SUCCESS] VoI Benchmark metrics exported to: {output_json}")

    if plot:
        render_voi_benchmark_plots(summary_metrics, sample_season, output_png)

    # Console summary table
    print("\n" + "=" * 95)
    print(f"{'Policy':<26} | {'NEV (R$/ha)':<14} | {'Flight Cost/ha':<15} | {'Latency (d)':<12} | {'FER %':<8} | {'Capture %':<10}")
    print("-" * 95)
    for p_name, m in summary_metrics.items():
        nev_str = f"R$ {m['net_economic_value_per_ha_brl']['mean']:.1f}"
        cost_str = f"R$ {m['flight_cost_per_ha_brl']['mean']:.1f}"
        lat_str = f"{m['mean_detection_latency_days']:.1f} d"
        fer_str = f"{m['false_escalation_rate_pct']:.1f}%"
        cap_str = f"{m['early_intervention_capture_pct']:.1f}%"
        print(f"{p_name:<26} | {nev_str:<14} | {cost_str:<15} | {lat_str:<12} | {fer_str:<8} | {cap_str:<10}")
    print("=" * 95 + "\n")

    return results_export


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agrostech Value-of-Information Drone Dispatch Benchmark")
    parser.add_argument("--days", type=int, default=120, help="Crop cycle duration in days")
    parser.add_argument("--area-ha", type=float, default=1000.0, help="Parcel area in hectares")
    parser.add_argument("--credit-exposure", type=float, default=3500000.0, help="Credit exposure in BRL")
    parser.add_argument("--monte-carlo", type=int, default=100, help="Number of Monte Carlo seasons")
    parser.add_argument("--plot", action="store_true", default=True, help="Render visual graphics")
    parser.add_argument("--output-json", type=str, default="results_voi_drone.json", help="Output JSON path")
    parser.add_argument("--output-png", type=str, default="benchmark_voi_drone.png", help="Output PNG path")
    args = parser.parse_args()

    run_voi_drone_benchmark(
        days=args.days,
        area_ha=args.area_ha,
        credit_exposure=args.credit_exposure,
        monte_carlo=args.monte_carlo,
        plot=args.plot,
        output_json=args.output_json,
        output_png=args.output_png
    )
