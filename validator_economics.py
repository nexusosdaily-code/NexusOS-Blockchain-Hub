"""
Validator Economics Module
Staking, delegation, reward distribution, slashing, and reputation system for blockchain validators
"""

import time
import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
import random


class SlashingType(Enum):
    """Types of slashable offenses"""
    DOWNTIME = "Extended Downtime"
    DOUBLE_SIGN = "Double Signing"
    MALICIOUS_BLOCK = "Malicious Block Proposal"
    BYZANTINE_BEHAVIOR = "Byzantine Behavior"
    NETWORK_ATTACK = "Network Attack Participation"


class DelegationStatus(Enum):
    """Status of a delegation"""
    ACTIVE = "active"
    UNBONDING = "unbonding"
    WITHDRAWN = "withdrawn"


@dataclass
class Delegation:
    """Delegator stake to a validator"""
    delegator_address: str
    validator_address: str
    amount: float
    status: DelegationStatus = DelegationStatus.ACTIVE
    delegated_at: float = field(default_factory=time.time)
    unbonding_started: Optional[float] = None
    unbonding_period: float = 604800.0  # 7 days in seconds
    
    # Rewards tracking
    accumulated_rewards: float = 0.0
    last_reward_claim: float = field(default_factory=time.time)
    total_rewards_claimed: float = 0.0
    
    def start_unbonding(self):
        """Start unbonding period"""
        self.status = DelegationStatus.UNBONDING
        self.unbonding_started = time.time()
    
    def can_withdraw(self) -> bool:
        """Check if unbonding period completed"""
        if self.status != DelegationStatus.UNBONDING or self.unbonding_started is None:
            return False
        return (time.time() - self.unbonding_started) >= self.unbonding_period
    
    def claim_rewards(self) -> float:
        """Claim accumulated rewards"""
        rewards = self.accumulated_rewards
        self.total_rewards_claimed += rewards
        self.accumulated_rewards = 0.0
        self.last_reward_claim = time.time()
        return rewards


@dataclass
class ValidatorEconomics:
    """Extended validator with economic metrics"""
    address: str
    stake: float  # Self-bonded stake
    commission_rate: float = 0.10  # 10% commission
    
    # Delegation tracking
    total_delegated: float = 0.0
    delegations: List[Delegation] = field(default_factory=list)
    
    # Performance metrics
    blocks_proposed: int = 0
    blocks_validated: int = 0
    uptime_percentage: float = 100.0
    reputation_score: float = 100.0
    
    # Rewards
    total_rewards_earned: float = 0.0
    total_commission_earned: float = 0.0
    pending_rewards: float = 0.0
    
    # Slashing history
    slashing_events: List[dict] = field(default_factory=list)
    total_slashed: float = 0.0
    is_jailed: bool = False
    jail_until: Optional[float] = None
    
    # Timestamps
    activated_at: float = field(default_factory=time.time)
    last_active: float = field(default_factory=time.time)
    
    def get_total_stake(self) -> float:
        """Get total stake (self + delegated)"""
        return self.stake + self.total_delegated
    
    def get_voting_power(self, total_network_stake: float) -> float:
        """Calculate voting power as percentage of network"""
        if total_network_stake == 0:
            return 0.0
        return (self.get_total_stake() / total_network_stake) * 100
    
    def add_delegation(self, delegation: Delegation):
        """Add new delegation"""
        self.delegations.append(delegation)
        self.total_delegated += delegation.amount
    
    def remove_delegation(self, delegation: Delegation):
        """Remove delegation after unbonding"""
        if delegation in self.delegations:
            self.delegations.remove(delegation)
            self.total_delegated -= delegation.amount
    
    def distribute_rewards(self, block_reward: float):
        """Distribute block rewards to validator and delegators"""
        # Validator commission
        commission = block_reward * self.commission_rate
        self.total_commission_earned += commission
        self.total_rewards_earned += commission
        
        # Remaining rewards distributed proportionally
        remaining_rewards = block_reward - commission
        total_stake = self.get_total_stake()
        
        if total_stake > 0:
            # Validator's share based on self-bonded stake
            validator_share = (self.stake / total_stake) * remaining_rewards
            self.total_rewards_earned += validator_share
            self.pending_rewards += validator_share
            
            # Delegators' shares
            for delegation in self.delegations:
                if delegation.status == DelegationStatus.ACTIVE:
                    delegator_share = (delegation.amount / total_stake) * remaining_rewards
                    delegation.accumulated_rewards += delegator_share
    
    def slash(self, slash_type: SlashingType, slash_percentage: float, reason: str = ""):
        """Apply slashing penalty"""
        total_stake = self.get_total_stake()
        slash_amount = total_stake * (slash_percentage / 100)
        
        # Slash validator's stake first
        if self.stake >= slash_amount:
            self.stake -= slash_amount
        else:
            slash_amount -= self.stake
            self.stake = 0
            
            # Slash delegated stake proportionally
            if self.total_delegated > 0:
                for delegation in self.delegations:
                    if delegation.status == DelegationStatus.ACTIVE:
                        delegation_slash = (delegation.amount / self.total_delegated) * slash_amount
                        delegation.amount -= delegation_slash
        
        # Record slashing event
        self.slashing_events.append({
            'type': slash_type.value,
            'percentage': slash_percentage,
            'amount': slash_amount,
            'reason': reason,
            'timestamp': time.time()
        })
        
        self.total_slashed += slash_amount
        
        # Impact reputation
        self.reputation_score = max(0, self.reputation_score - (slash_percentage * 2))
    
    def jail(self, duration_seconds: float = 86400.0):
        """Jail validator temporarily (default 24 hours)"""
        self.is_jailed = True
        self.jail_until = time.time() + duration_seconds
    
    def unjail(self):
        """Release validator from jail if period expired"""
        if self.is_jailed and self.jail_until and time.time() >= self.jail_until:
            self.is_jailed = False
            self.jail_until = None
            return True
        return False
    
    def update_reputation(self, uptime_percentage: float, blocks_proposed: int):
        """Update reputation score based on performance"""
        self.uptime_percentage = uptime_percentage
        self.blocks_proposed = blocks_proposed
        
        # Reputation factors
        uptime_score = uptime_percentage  # 0-100
        performance_score = min(100, blocks_proposed * 2)  # More blocks = better score
        slashing_penalty = len(self.slashing_events) * 10  # Each slash reduces score
        
        # Weighted reputation
        self.reputation_score = max(0, min(100, 
            (uptime_score * 0.5) + 
            (performance_score * 0.3) - 
            slashing_penalty +
            20  # Base score
        ))
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'address': self.address[:10] + "...",
            'self_stake': self.stake,
            'total_delegated': self.total_delegated,
            'total_stake': self.get_total_stake(),
            'commission_rate': f"{self.commission_rate * 100:.1f}%",
            'delegators': len(self.delegations),
            'blocks_proposed': self.blocks_proposed,
            'uptime': f"{self.uptime_percentage:.1f}%",
            'reputation': f"{self.reputation_score:.1f}",
            'total_rewards': self.total_rewards_earned,
            'is_jailed': self.is_jailed,
            'slashing_events': len(self.slashing_events)
        }


class StakingEconomy:
    """Blockchain staking economy manager"""
    
    def __init__(self, block_reward: float = 2.0, inflation_rate: float = 0.05):
        """
        Initialize staking economy
        
        Args:
            block_reward: Reward per block
            inflation_rate: Annual inflation rate (5% default)
        """
        self.block_reward = block_reward
        self.inflation_rate = inflation_rate
        
        # Validators and delegations
        self.validators: Dict[str, ValidatorEconomics] = {}
        self.delegations: Dict[str, List[Delegation]] = {}  # delegator -> [delegations]
        
        # Economic metrics
        self.total_staked = 0.0
        self.total_rewards_distributed = 0.0
        self.total_slashed = 0.0
        self.current_apy = 0.0
        
        # Slashing parameters
        self.slashing_params = {
            SlashingType.DOWNTIME: 1.0,  # 1% slash
            SlashingType.DOUBLE_SIGN: 5.0,  # 5% slash
            SlashingType.MALICIOUS_BLOCK: 10.0,  # 10% slash
            SlashingType.BYZANTINE_BEHAVIOR: 20.0,  # 20% slash
            SlashingType.NETWORK_ATTACK: 100.0,  # Complete slash
        }
    
    def register_validator(self, address: str, self_stake: float, commission_rate: float = 0.10) -> bool:
        """Register new validator"""
        if address in self.validators:
            return False
        
        validator = ValidatorEconomics(
            address=address,
            stake=self_stake,
            commission_rate=commission_rate
        )
        self.validators[address] = validator
        self.total_staked += self_stake
        
        return True
    
    def delegate(self, delegator: str, validator_address: str, amount: float) -> Tuple[bool, str]:
        """Delegate stake to validator"""
        if validator_address not in self.validators:
            return False, "Validator not found"
        
        if amount <= 0:
            return False, "Invalid amount"
        
        validator = self.validators[validator_address]
        
        if validator.is_jailed:
            return False, "Validator is jailed"
        
        # Create delegation
        delegation = Delegation(
            delegator_address=delegator,
            validator_address=validator_address,
            amount=amount
        )
        
        # Add to validator
        validator.add_delegation(delegation)
        
        # Track delegator's delegations
        if delegator not in self.delegations:
            self.delegations[delegator] = []
        self.delegations[delegator].append(delegation)
        
        self.total_staked += amount
        
        return True, f"Delegated {amount} to {validator_address[:10]}..."
    
    def undelegate(self, delegator: str, validator_address: str, amount: float) -> Tuple[bool, str]:
        """Start undelegation process"""
        if delegator not in self.delegations:
            return False, "No delegations found"
        
        # Find delegation
        delegation = None
        for d in self.delegations[delegator]:
            if d.validator_address == validator_address and d.status == DelegationStatus.ACTIVE:
                if d.amount >= amount:
                    delegation = d
                    break
        
        if not delegation:
            return False, "Insufficient delegated amount"
        
        # If unbonding partial amount, create new delegation
        if delegation.amount > amount:
            delegation.amount -= amount
            new_delegation = Delegation(
                delegator_address=delegator,
                validator_address=validator_address,
                amount=amount
            )
            new_delegation.start_unbonding()
            self.delegations[delegator].append(new_delegation)
        else:
            delegation.start_unbonding()
        
        return True, f"Unbonding {amount} (7 day unbonding period)"
    
    def withdraw_delegation(self, delegator: str, validator_address: str) -> Tuple[bool, float, str]:
        """Withdraw completed unbonded stake"""
        if delegator not in self.delegations:
            return False, 0.0, "No delegations found"
        
        total_withdrawn = 0.0
        delegations_to_remove = []
        
        for delegation in self.delegations[delegator]:
            if (delegation.validator_address == validator_address and 
                delegation.status == DelegationStatus.UNBONDING and 
                delegation.can_withdraw()):
                
                total_withdrawn += delegation.amount
                delegation.status = DelegationStatus.WITHDRAWN
                delegations_to_remove.append(delegation)
                
                # Remove from validator
                validator = self.validators[validator_address]
                validator.remove_delegation(delegation)
        
        # Remove withdrawn delegations
        for delegation in delegations_to_remove:
            self.delegations[delegator].remove(delegation)
        
        if total_withdrawn > 0:
            self.total_staked -= total_withdrawn
            return True, total_withdrawn, f"Withdrawn {total_withdrawn}"
        
        return False, 0.0, "No unbonded delegations ready for withdrawal"
    
    def distribute_block_reward(self, validator_address: str):
        """Distribute block reward to validator and delegators"""
        if validator_address not in self.validators:
            return
        
        validator = self.validators[validator_address]
        validator.distribute_rewards(self.block_reward)
        validator.blocks_proposed += 1
        validator.last_active = time.time()
        
        self.total_rewards_distributed += self.block_reward
    
    def apply_slashing(self, validator_address: str, slash_type: SlashingType, reason: str = ""):
        """Apply slashing penalty to validator"""
        if validator_address not in self.validators:
            return
        
        validator = self.validators[validator_address]
        slash_percentage = self.slashing_params.get(slash_type, 1.0)
        
        validator.slash(slash_type, slash_percentage, reason)
        self.total_slashed += validator.total_slashed
        
        # Jail for serious offenses
        if slash_type in [SlashingType.DOUBLE_SIGN, SlashingType.BYZANTINE_BEHAVIOR, SlashingType.NETWORK_ATTACK]:
            validator.jail(duration_seconds=86400.0)  # 24 hours
    
    def claim_rewards(self, delegator: str) -> Tuple[float, List[str]]:
        """Claim all accumulated rewards for delegator"""
        if delegator not in self.delegations:
            return 0.0, []
        
        total_claimed = 0.0
        claims = []
        
        for delegation in self.delegations[delegator]:
            if delegation.status == DelegationStatus.ACTIVE and delegation.accumulated_rewards > 0:
                rewards = delegation.claim_rewards()
                total_claimed += rewards
                claims.append(
                    f"{rewards:.4f} from {delegation.validator_address[:10]}..."
                )
        
        return total_claimed, claims
    
    def get_validator_rankings(self) -> List[ValidatorEconomics]:
        """Get validators ranked by total stake"""
        return sorted(
            self.validators.values(),
            key=lambda v: v.get_total_stake(),
            reverse=True
        )
    
    def calculate_apy(self) -> float:
        """Calculate current staking APY"""
        if self.total_staked == 0:
            return 0.0
        
        # Simplified APY calculation
        # Annual rewards = blocks per year * block reward
        blocks_per_year = (365 * 24 * 60 * 60) / 2.0  # Assuming 2s block time
        annual_rewards = blocks_per_year * self.block_reward
        
        self.current_apy = (annual_rewards / self.total_staked) * 100
        return self.current_apy
    
    def simulate_validator_profitability(
        self, 
        self_stake: float, 
        commission_rate: float, 
        delegated_stake: float,
        blocks_per_day: int
    ) -> dict:
        """Simulate validator profitability"""
        total_stake = self_stake + delegated_stake
        
        # Daily rewards
        daily_rewards = blocks_per_day * self.block_reward
        
        # Commission earnings
        commission_earnings = daily_rewards * commission_rate
        
        # Stake-based earnings (after commission)
        remaining_rewards = daily_rewards - commission_earnings
        stake_earnings = (self_stake / total_stake) * remaining_rewards if total_stake > 0 else 0
        
        # Total validator earnings
        total_daily_earnings = commission_earnings + stake_earnings
        
        # Annual extrapolation
        annual_earnings = total_daily_earnings * 365
        annual_roi = (annual_earnings / self_stake * 100) if self_stake > 0 else 0
        
        return {
            'daily_earnings': total_daily_earnings,
            'monthly_earnings': total_daily_earnings * 30,
            'annual_earnings': annual_earnings,
            'annual_roi': annual_roi,
            'commission_earnings_daily': commission_earnings,
            'stake_earnings_daily': stake_earnings,
            'effective_apy': self.calculate_apy()
        }
    
    def get_delegator_stats(self, delegator: str) -> dict:
        """Get comprehensive stats for a delegator"""
        if delegator not in self.delegations:
            return {
                'total_delegated': 0.0,
                'active_delegations': 0,
                'unbonding_delegations': 0,
                'pending_rewards': 0.0,
                'total_claimed': 0.0,
                'delegations': []
            }
        
        total_delegated = 0.0
        active = 0
        unbonding = 0
        pending_rewards = 0.0
        total_claimed = 0.0
        delegation_list = []
        
        for delegation in self.delegations[delegator]:
            if delegation.status == DelegationStatus.ACTIVE:
                total_delegated += delegation.amount
                active += 1
            elif delegation.status == DelegationStatus.UNBONDING:
                unbonding += 1
            
            pending_rewards += delegation.accumulated_rewards
            total_claimed += delegation.total_rewards_claimed
            
            delegation_list.append({
                'validator': delegation.validator_address[:10] + "...",
                'amount': delegation.amount,
                'status': delegation.status.value,
                'pending_rewards': delegation.accumulated_rewards,
                'total_claimed': delegation.total_rewards_claimed
            })
        
        return {
            'total_delegated': total_delegated,
            'active_delegations': active,
            'unbonding_delegations': unbonding,
            'pending_rewards': pending_rewards,
            'total_claimed': total_claimed,
            'delegations': delegation_list
        }
