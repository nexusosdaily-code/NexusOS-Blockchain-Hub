"""
Long-Term Tokenomics Burn Simulation (50-100 Years)
====================================================

Critical Analysis: How burn mechanics affect NXT supply over decades.

Supply Model:
- Initial: 1,000,000 NXT (100M units)
- Burn Sources: Messages, Link Shares, Video Shares
- Validator Rewards: Inflationary pressure (optional)
- Target: Sustainable circulating supply for 100+ years
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from enum import Enum


class AdoptionScenario(Enum):
    """Network adoption scenarios"""
    CONSERVATIVE = "conservative"  # Slow growth
    MODERATE = "moderate"           # Steady growth
    AGGRESSIVE = "aggressive"       # Rapid adoption
    VIRAL = "viral"                 # Exponential growth


@dataclass
class BurnParameters:
    """Burn rate parameters - PRODUCTION VALUES (from native_token.py)"""
    # Bitcoin-style denomination: 100M units per NXT (like satoshis)
    # These match ACTUAL production burns in NativeTokenSystem
    message_burn: float = 0.000057   # 5,700 units = 0.000057 NXT per message
    link_burn: float = 0.0000285     # 2,850 units = 0.0000285 NXT per link
    video_burn: float = 0.000114     # 11,400 units = 0.000114 NXT per video
    transfer_fee: float = 0.00001    # 1,000 units = 0.00001 NXT per transaction
    
    # Activity ratios
    message_ratio: float = 0.7     # 70% of activity
    link_ratio: float = 0.2        # 20% of activity
    video_ratio: float = 0.1       # 10% of activity


@dataclass
class NetworkMetrics:
    """Network usage metrics"""
    year: int
    active_users: int
    daily_messages: int
    circulating_supply: float      # NXT
    total_burned: float            # NXT cumulative
    burn_rate_daily: float         # NXT per day
    supply_velocity: float         # Burns/Supply ratio
    years_until_depletion: float   # Estimated years remaining
    sustainability_score: float    # 0-100 health score


class LongTermTokenomicsSimulator:
    """
    Simulates NXT tokenomics over 50-100 years.
    
    Models:
    - User adoption curves
    - Daily burn rates
    - Circulating supply decay
    - Economic sustainability metrics
    """
    
    INITIAL_SUPPLY = 1_000_000.0  # NXT
    GENESIS_SUPPLY = 500_000.0    # Available at launch
    
    def __init__(self, burn_params: Optional[BurnParameters] = None):
        self.burn_params = burn_params or BurnParameters()
        self.metrics_history: List[NetworkMetrics] = []
    
    def estimate_active_users(
        self, 
        year: int, 
        scenario: AdoptionScenario
    ) -> int:
        """
        Estimate active users based on adoption scenario.
        
        CORRECTED Growth models (realistic startup curves):
        - Conservative: 1K → 100K over 100 years
        - Moderate: 1K → 1M over 50 years (S-curve)
        - Aggressive: 1K → 10M over 30 years
        - Viral: 1K → 50M over 20 years
        """
        if scenario == AdoptionScenario.CONSERVATIVE:
            # Linear: 1K + 990 users/year → 100K in 100 years
            return int(1_000 + (990 * year))
        
        elif scenario == AdoptionScenario.MODERATE:
            # Logistic S-curve: max 1M users, reaches 500K at year 25
            max_users = 1_000_000
            k = 0.15  # Growth rate
            midpoint = 25  # 50% adoption at year 25
            return int(max_users / (1 + np.exp(-k * (year - midpoint))))
        
        elif scenario == AdoptionScenario.AGGRESSIVE:
            # Exponential: doubles every 2.5 years
            initial = 1_000
            doubling_time = 2.5
            return min(int(initial * (2 ** (year / doubling_time))), 10_000_000)
        
        else:  # VIRAL
            # Super-exponential growth, capped at 50M
            return min(int(1_000 * (1.4 ** year)), 50_000_000)
    
    def estimate_daily_messages(
        self, 
        active_users: int
    ) -> int:
        """
        Estimate daily messaging activity.
        
        Assumptions:
        - Average user sends 5-10 messages/day
        - Power law: 20% users create 80% messages
        - Includes all activity types (messages, links, videos)
        """
        avg_messages_per_user = 7.5
        power_law_factor = 1.2  # Heavy users send more
        
        return int(active_users * avg_messages_per_user * power_law_factor)
    
    def calculate_daily_burn(
        self, 
        daily_messages: int
    ) -> float:
        """
        Calculate daily NXT burn from all activities.
        
        Breakdown:
        - 70% messages → 0.1 NXT each
        - 20% links → 0.05 NXT each
        - 10% videos → 0.2 NXT each
        """
        params = self.burn_params
        
        messages = daily_messages * params.message_ratio
        links = daily_messages * params.link_ratio
        videos = daily_messages * params.video_ratio
        
        burn = (
            messages * params.message_burn +
            links * params.link_burn +
            videos * params.video_burn
        )
        
        return burn
    
    def calculate_sustainability_score(
        self,
        circulating_supply: float,
        burn_rate_daily: float,
        years_until_depletion: float
    ) -> float:
        """
        Calculate economic sustainability score (0-100).
        
        Factors:
        - Supply remaining (50%)
        - Burn velocity (30%)
        - Years until depletion (20%)
        
        Thresholds:
        - 100: Perfect (100+ years remaining)
        - 75: Healthy (50-100 years)
        - 50: Warning (25-50 years)
        - 25: Critical (10-25 years)
        - 0: Emergency (<10 years)
        """
        # Supply health (0-50 points)
        supply_pct = circulating_supply / self.INITIAL_SUPPLY
        supply_score = min(50, supply_pct * 100)
        
        # Burn velocity health (0-30 points)
        # Lower burn rate relative to supply = healthier
        velocity = burn_rate_daily / max(circulating_supply, 1)
        velocity_score = max(0, 30 - (velocity * 10000))
        
        # Time until depletion (0-20 points)
        if years_until_depletion >= 100:
            time_score = 20
        elif years_until_depletion >= 50:
            time_score = 15
        elif years_until_depletion >= 25:
            time_score = 10
        elif years_until_depletion >= 10:
            time_score = 5
        else:
            time_score = 0
        
        total = supply_score + velocity_score + time_score
        return min(100, max(0, total))
    
    def simulate(
        self,
        years: int,
        scenario: AdoptionScenario
    ) -> List[NetworkMetrics]:
        """
        Run full tokenomics simulation for specified years.
        
        Returns:
            List of annual network metrics
        """
        circulating_supply = self.GENESIS_SUPPLY
        total_burned = 0.0
        metrics = []
        
        for year in range(1, years + 1):
            # Estimate network activity
            active_users = self.estimate_active_users(year, scenario)
            daily_messages = self.estimate_daily_messages(active_users)
            
            # Calculate burns
            burn_rate_daily = self.calculate_daily_burn(daily_messages)
            annual_burn = burn_rate_daily * 365
            
            # Update supply
            circulating_supply -= annual_burn
            total_burned += annual_burn
            
            # Prevent negative supply
            if circulating_supply <= 0:
                circulating_supply = 0
                years_remaining = 0
            else:
                # Estimate depletion time
                if burn_rate_daily > 0:
                    days_remaining = circulating_supply / burn_rate_daily
                    years_remaining = days_remaining / 365
                else:
                    years_remaining = 999  # Infinite
            
            # Calculate velocity
            supply_velocity = annual_burn / max(circulating_supply, 1)
            
            # Calculate sustainability
            sustainability = self.calculate_sustainability_score(
                circulating_supply,
                burn_rate_daily,
                years_remaining
            )
            
            # Record metrics
            metric = NetworkMetrics(
                year=year,
                active_users=active_users,
                daily_messages=daily_messages,
                circulating_supply=circulating_supply,
                total_burned=total_burned,
                burn_rate_daily=burn_rate_daily,
                supply_velocity=supply_velocity,
                years_until_depletion=years_remaining,
                sustainability_score=sustainability
            )
            metrics.append(metric)
            
            # Stop if supply depleted
            if circulating_supply <= 0:
                break
        
        self.metrics_history = metrics
        return metrics
    
    def get_critical_years(
        self,
        metrics: List[NetworkMetrics]
    ) -> Dict[str, int]:
        """
        Identify critical milestone years.
        
        Returns:
            Dictionary of milestone → year
        """
        milestones = {}
        
        for m in metrics:
            # 50% supply burned
            if m.circulating_supply <= self.INITIAL_SUPPLY * 0.5 and '50_percent_burned' not in milestones:
                milestones['50_percent_burned'] = m.year
            
            # 75% supply burned
            if m.circulating_supply <= self.INITIAL_SUPPLY * 0.25 and '75_percent_burned' not in milestones:
                milestones['75_percent_burned'] = m.year
            
            # 90% supply burned
            if m.circulating_supply <= self.INITIAL_SUPPLY * 0.1 and '90_percent_burned' not in milestones:
                milestones['90_percent_burned'] = m.year
            
            # Sustainability critical (<50 score)
            if m.sustainability_score < 50 and 'critical_sustainability' not in milestones:
                milestones['critical_sustainability'] = m.year
            
            # Complete depletion
            if m.circulating_supply <= 100 and 'supply_depleted' not in milestones:
                milestones['supply_depleted'] = m.year
        
        return milestones
    
    def to_dataframe(self) -> pd.DataFrame:
        """Convert metrics to pandas DataFrame for analysis"""
        if not self.metrics_history:
            return pd.DataFrame()
        
        data = []
        for m in self.metrics_history:
            data.append({
                'Year': m.year,
                'Active Users': m.active_users,
                'Daily Messages': m.daily_messages,
                'Circulating Supply (NXT)': m.circulating_supply,
                'Total Burned (NXT)': m.total_burned,
                'Daily Burn Rate (NXT)': m.burn_rate_daily,
                'Supply Velocity': m.supply_velocity,
                'Years Until Depletion': m.years_until_depletion,
                'Sustainability Score': m.sustainability_score
            })
        
        return pd.DataFrame(data)


class EconomicBalancingMechanism:
    """
    Proposed mechanisms to balance burn economics.
    
    Solutions:
    1. Dynamic Burn Rates - Reduce burns as supply decreases
    2. Validator Inflation - Mint new tokens for rewards
    3. Burn Caps - Maximum annual burn limits
    4. Fee Redistribution - Recycle burned tokens
    """
    
    @staticmethod
    def dynamic_burn_adjustment(
        base_burn: float,
        circulating_supply: float,
        initial_supply: float
    ) -> float:
        """
        Adjust burn rate based on remaining supply.
        
        Formula: burn = base_burn * (supply / initial)^0.5
        
        Example:
        - 100% supply → 100% burn rate
        - 50% supply → 70% burn rate
        - 25% supply → 50% burn rate
        - 10% supply → 30% burn rate
        """
        supply_ratio = circulating_supply / initial_supply
        adjustment = np.sqrt(supply_ratio)
        return base_burn * adjustment
    
    @staticmethod
    def calculate_validator_inflation(
        year: int,
        initial_rate: float = 2.0,
        halving_period: int = 4
    ) -> float:
        """
        Calculate annual validator reward inflation.
        
        Bitcoin-style halving:
        - Year 0-4: 2% annual inflation
        - Year 4-8: 1% annual inflation
        - Year 8-12: 0.5% annual inflation
        - Converges to 0%
        """
        halvings = year // halving_period
        inflation_rate = initial_rate / (2 ** halvings)
        return max(0.1, inflation_rate)  # Min 0.1% floor
    
    @staticmethod
    def apply_annual_burn_cap(
        proposed_burn: float,
        circulating_supply: float,
        max_burn_pct: float = 5.0
    ) -> float:
        """
        Cap annual burns to prevent rapid depletion.
        
        Args:
            proposed_burn: Calculated burn amount
            circulating_supply: Current supply
            max_burn_pct: Maximum % of supply to burn per year
        
        Returns:
            Capped burn amount
        """
        max_burn = circulating_supply * (max_burn_pct / 100)
        return min(proposed_burn, max_burn)


# Export key classes
__all__ = [
    'LongTermTokenomicsSimulator',
    'AdoptionScenario',
    'BurnParameters',
    'NetworkMetrics',
    'EconomicBalancingMechanism'
]
