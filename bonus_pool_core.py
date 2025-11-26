"""
NexusOS Bonus Pool Distribution System
Performance-based rewards funded by F_floor

Architecture:
- Bonus Pool receives allocation from F_floor
- Rewards distributed based on performance metrics
- Categories: Validator performance, Community contribution, Trading volume, Staking loyalty

Distribution Model (E=hf inspired):
- Higher frequency activity = Higher energy rewards
- Validators: Based on uptime and block validation
- Community: Based on governance participation
- Traders: Based on DEX volume
- Stakers: Based on stake duration and amount
"""

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum


class BonusCategory(Enum):
    """Categories for bonus distribution"""
    VALIDATOR_PERFORMANCE = "validator"    # Block validation rewards
    COMMUNITY_CONTRIBUTION = "community"   # Governance participation
    TRADING_VOLUME = "trading"             # DEX activity
    STAKING_LOYALTY = "staking"            # Long-term staking
    INNOVATION_REWARD = "innovation"       # Development contributions
    SUSTAINABILITY_BONUS = "sustainability" # Environmental actions


@dataclass
class BonusAllocation:
    """Allocation of bonus pool to categories"""
    validator: float = 0.30      # 30% to validators
    community: float = 0.20      # 20% to community
    trading: float = 0.20        # 20% to traders
    staking: float = 0.20        # 20% to stakers
    innovation: float = 0.05     # 5% to innovators
    sustainability: float = 0.05 # 5% to sustainability


@dataclass
class PerformanceMetrics:
    """Performance metrics for bonus calculation"""
    user_address: str
    category: BonusCategory
    metric_value: float  # Raw performance metric
    normalized_score: float = 0.0  # 0-1 normalized score
    bonus_earned: float = 0.0
    period_start: float = field(default_factory=time.time)
    period_end: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            "user": self.user_address,
            "category": self.category.value,
            "metric": self.metric_value,
            "score": self.normalized_score,
            "bonus": self.bonus_earned
        }


@dataclass
class BonusPeriod:
    """A single bonus distribution period"""
    period_id: str
    start_time: float
    end_time: float
    total_pool: float = 0.0
    distributed: float = 0.0
    participants: int = 0
    status: str = "active"  # active, calculating, distributed
    distributions: Dict[str, float] = field(default_factory=dict)


class BonusPoolEngine:
    """
    Engine for calculating and distributing performance bonuses.
    
    Uses physics-inspired metrics where higher activity frequency
    corresponds to higher energy rewards (E=hf principle).
    """
    
    # Distribution period: 7 days
    PERIOD_DURATION = 7 * 24 * 60 * 60  # seconds
    
    # Minimum thresholds for bonus eligibility
    MIN_THRESHOLDS = {
        BonusCategory.VALIDATOR_PERFORMANCE: 0.95,  # 95% uptime
        BonusCategory.COMMUNITY_CONTRIBUTION: 1,     # At least 1 vote
        BonusCategory.TRADING_VOLUME: 10.0,          # 10 NXT volume
        BonusCategory.STAKING_LOYALTY: 7,            # 7 days staked
        BonusCategory.INNOVATION_REWARD: 1,          # 1 contribution
        BonusCategory.SUSTAINABILITY_BONUS: 1        # 1 action
    }
    
    def __init__(self, token_system=None):
        self.token_system = token_system
        self.allocation = BonusAllocation()
        self.current_period: Optional[BonusPeriod] = None
        self.period_history: List[BonusPeriod] = []
        self.performance_records: Dict[str, List[PerformanceMetrics]] = {}
        
        # Initialize first period
        self._create_new_period()
    
    def _create_new_period(self) -> BonusPeriod:
        """Create a new bonus distribution period"""
        period_id = f"BONUS-{int(time.time())}"
        start_time = time.time()
        
        period = BonusPeriod(
            period_id=period_id,
            start_time=start_time,
            end_time=start_time + self.PERIOD_DURATION
        )
        
        self.current_period = period
        return period
    
    def record_performance(
        self,
        user: str,
        category: BonusCategory,
        metric_value: float
    ) -> Tuple[bool, str]:
        """
        Record a performance metric for bonus calculation.
        
        Args:
            user: Wallet address
            category: Type of performance
            metric_value: Raw metric (varies by category)
        
        Returns:
            (success, message)
        """
        if not self.current_period or self.current_period.status != "active":
            return False, "No active bonus period"
        
        # Check minimum threshold
        min_threshold = self.MIN_THRESHOLDS.get(category, 0)
        if metric_value < min_threshold:
            return False, f"Below minimum threshold ({min_threshold}) for {category.value}"
        
        # Create performance record
        record = PerformanceMetrics(
            user_address=user,
            category=category,
            metric_value=metric_value,
            period_start=self.current_period.start_time
        )
        
        # Store record
        if user not in self.performance_records:
            self.performance_records[user] = []
        
        self.performance_records[user].append(record)
        self.current_period.participants += 1
        
        return True, f"Performance recorded: {category.value} = {metric_value}"
    
    def calculate_bonuses(self) -> Tuple[bool, Dict[str, Any], str]:
        """
        Calculate bonuses for all participants in current period.
        
        Returns:
            (success, results, message)
        """
        if not self.current_period:
            return False, {}, "No active period"
        
        period = self.current_period
        period.status = "calculating"
        
        # Get pool balance
        if self.token_system:
            pool_account = self.token_system.get_account("BONUS_POOL")
            if pool_account:
                period.total_pool = pool_account.balance / self.token_system.UNITS_PER_NXT
        else:
            period.total_pool = 10000.0  # Demo pool
        
        # Group records by category
        by_category: Dict[BonusCategory, List[PerformanceMetrics]] = {
            cat: [] for cat in BonusCategory
        }
        
        for user, records in self.performance_records.items():
            for record in records:
                if record.period_start == period.start_time:
                    by_category[record.category].append(record)
        
        # Calculate normalized scores and bonuses per category
        results = {
            "period_id": period.period_id,
            "total_pool": period.total_pool,
            "by_category": {},
            "top_performers": []
        }
        
        for category, records in by_category.items():
            if not records:
                continue
            
            # Get category allocation
            allocation_pct = getattr(self.allocation, category.value, 0.1)
            category_pool = period.total_pool * allocation_pct
            
            # Calculate total metric for normalization
            total_metric = sum(r.metric_value for r in records)
            
            # Normalize and assign bonuses
            category_results = []
            for record in records:
                if total_metric > 0:
                    record.normalized_score = record.metric_value / total_metric
                    record.bonus_earned = category_pool * record.normalized_score
                    
                    category_results.append({
                        "user": record.user_address,
                        "metric": record.metric_value,
                        "bonus": record.bonus_earned
                    })
                    
                    # Track in period distributions
                    if record.user_address in period.distributions:
                        period.distributions[record.user_address] += record.bonus_earned
                    else:
                        period.distributions[record.user_address] = record.bonus_earned
            
            results["by_category"][category.value] = {
                "pool": category_pool,
                "participants": len(records),
                "results": sorted(category_results, key=lambda x: x["bonus"], reverse=True)[:5]
            }
        
        # Get top performers overall
        top = sorted(period.distributions.items(), key=lambda x: x[1], reverse=True)[:10]
        results["top_performers"] = [{"user": u, "total_bonus": b} for u, b in top]
        
        return True, results, "Bonuses calculated"
    
    def distribute_bonuses(self) -> Tuple[bool, Dict[str, Any], str]:
        """
        Distribute calculated bonuses to participants.
        
        Returns:
            (success, results, message)
        """
        if not self.current_period:
            return False, {}, "No active period"
        
        period = self.current_period
        
        if period.status != "calculating":
            # Calculate first if not done
            success, _, msg = self.calculate_bonuses()
            if not success:
                return False, {}, msg
        
        distributed_count = 0
        total_distributed = 0.0
        
        # Distribute to each user
        for user, amount in period.distributions.items():
            if amount <= 0:
                continue
            
            if self.token_system:
                amount_units = int(amount * self.token_system.UNITS_PER_NXT)
                
                success, _, msg = self.token_system.transfer_atomic(
                    from_address="BONUS_POOL",
                    to_address=user,
                    amount=amount_units,
                    fee=0,
                    reason="Performance bonus distribution"
                )
                
                if success:
                    distributed_count += 1
                    total_distributed += amount
            else:
                distributed_count += 1
                total_distributed += amount
        
        period.distributed = total_distributed
        period.status = "distributed"
        
        # Archive and create new period
        self.period_history.append(period)
        self._create_new_period()
        
        return True, {
            "period_id": period.period_id,
            "recipients": distributed_count,
            "total_distributed": total_distributed
        }, f"Distributed {total_distributed:.2f} NXT to {distributed_count} participants"
    
    def get_current_period_info(self) -> Dict[str, Any]:
        """Get information about current bonus period"""
        if not self.current_period:
            return {"status": "no_active_period"}
        
        period = self.current_period
        time_remaining = max(0, period.end_time - time.time())
        
        # Count participants by category
        category_counts = {cat.value: 0 for cat in BonusCategory}
        for records in self.performance_records.values():
            for record in records:
                if record.period_start == period.start_time:
                    category_counts[record.category.value] += 1
        
        return {
            "period_id": period.period_id,
            "status": period.status,
            "start_time": period.start_time,
            "time_remaining_seconds": time_remaining,
            "total_pool": period.total_pool,
            "participants": period.participants,
            "by_category": category_counts,
            "allocation": {
                "validator": self.allocation.validator,
                "community": self.allocation.community,
                "trading": self.allocation.trading,
                "staking": self.allocation.staking,
                "innovation": self.allocation.innovation,
                "sustainability": self.allocation.sustainability
            }
        }
    
    def get_user_performance(self, user: str) -> List[Dict]:
        """Get performance records for a specific user"""
        records = self.performance_records.get(user, [])
        return [r.to_dict() for r in records]
    
    def get_period_history(self, limit: int = 5) -> List[Dict]:
        """Get recent period history"""
        history = []
        for period in reversed(self.period_history[-limit:]):
            history.append({
                "period_id": period.period_id,
                "total_pool": period.total_pool,
                "distributed": period.distributed,
                "participants": period.participants,
                "start_time": period.start_time,
                "end_time": period.end_time
            })
        return history


# Global bonus pool engine
_bonus_engine: Optional[BonusPoolEngine] = None


def get_bonus_engine(token_system=None) -> BonusPoolEngine:
    """Get or create global bonus pool engine"""
    global _bonus_engine
    if _bonus_engine is None:
        _bonus_engine = BonusPoolEngine(token_system)
    return _bonus_engine
