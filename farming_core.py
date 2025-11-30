"""
NexusOS Farming Core Module - Physics Substrate Integrated
============================================================

Liquidity farming with full substrate compliance:
- E=hf energy economics for reward distribution
- Λ=hf/c² Lambda Boson mass tracking on all rewards
- Orbital burns → TransitionReserveLedger
- SDK fee routing (0.5%) on reward claims
- Physics-based APY: Higher frequency pools = higher energy rewards

Farming Flow:
1. User provides liquidity to DEX pool → receives LP tokens
2. User stakes LP tokens in farming pool → earns NXT rewards
3. Rewards calculated based on stake share and pool multiplier
4. Reward claims route through physics substrate
"""

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
import math

from physics_economics_adapter import (
    get_physics_adapter,
    EconomicModule,
    SubstrateTransaction
)


class FarmTier(Enum):
    """Farm tiers based on wavelength/frequency (physics-based)"""
    GAMMA = "Gamma Ray"      # Highest energy, highest rewards
    XRAY = "X-Ray"           # Very high energy
    UV = "Ultraviolet"       # High energy
    VISIBLE = "Visible"      # Standard energy
    INFRARED = "Infrared"    # Lower energy, stable rewards


# Physics constants for E=hf calculations
PLANCK_CONSTANT = 6.62607015e-34  # J·s
SPEED_OF_LIGHT = 299792458  # m/s

# Tier wavelengths and multipliers
TIER_CONFIG = {
    FarmTier.GAMMA: {
        "wavelength_nm": 0.01,      # Gamma rays
        "multiplier": 5.0,          # 5x rewards
        "min_tvl": 100000,          # Minimum TVL to achieve
        "color": "#FF00FF",         # Magenta
        "description": "Ultra-high energy farming"
    },
    FarmTier.XRAY: {
        "wavelength_nm": 1.0,       # X-rays
        "multiplier": 3.0,          # 3x rewards  
        "min_tvl": 50000,
        "color": "#9400D3",         # Dark violet
        "description": "High energy farming"
    },
    FarmTier.UV: {
        "wavelength_nm": 300,       # Ultraviolet
        "multiplier": 2.0,          # 2x rewards
        "min_tvl": 10000,
        "color": "#8A2BE2",         # Blue violet
        "description": "Enhanced farming"
    },
    FarmTier.VISIBLE: {
        "wavelength_nm": 550,       # Green light
        "multiplier": 1.0,          # Base rewards
        "min_tvl": 1000,
        "color": "#00FF00",         # Green
        "description": "Standard farming"
    },
    FarmTier.INFRARED: {
        "wavelength_nm": 1000,      # Infrared
        "multiplier": 0.5,          # Reduced rewards
        "min_tvl": 0,
        "color": "#FF4500",         # Orange red
        "description": "Stable low-energy farming"
    }
}


@dataclass
class FarmPosition:
    """User's staked position in a farm"""
    user_address: str
    pool_id: str
    staked_lp: float
    staked_at: float = field(default_factory=time.time)
    last_reward_claim: float = field(default_factory=time.time)
    total_rewards_claimed: float = 0.0
    
    def get_stake_duration(self) -> float:
        """Get duration staked in seconds"""
        return time.time() - self.staked_at
    
    def get_time_since_claim(self) -> float:
        """Get time since last reward claim in seconds"""
        return time.time() - self.last_reward_claim


@dataclass
class FarmPool:
    """Farming pool for LP token staking"""
    pool_id: str                    # Matches DEX pool ID (e.g., "USDC-NXT")
    token_a: str                    # First token symbol
    token_b: str                    # Second token symbol (NXT)
    
    total_staked_lp: float = 0.0    # Total LP tokens staked
    total_value_locked: float = 0.0  # TVL in NXT
    
    base_reward_rate: float = 0.01  # Base rewards per LP per day (1%)
    bonus_multiplier: float = 1.0   # Additional multiplier for special events
    
    stakers: Dict[str, FarmPosition] = field(default_factory=dict)
    
    created_at: float = field(default_factory=time.time)
    is_active: bool = True
    
    total_rewards_distributed: float = 0.0
    
    def get_tier(self) -> FarmTier:
        """Get farm tier based on TVL (higher TVL = higher frequency = more energy)"""
        for tier in [FarmTier.GAMMA, FarmTier.XRAY, FarmTier.UV, FarmTier.VISIBLE, FarmTier.INFRARED]:
            if self.total_value_locked >= TIER_CONFIG[tier]["min_tvl"]:
                return tier
        return FarmTier.INFRARED
    
    def get_multiplier(self) -> float:
        """Get current reward multiplier based on tier"""
        tier = self.get_tier()
        return TIER_CONFIG[tier]["multiplier"] * self.bonus_multiplier
    
    def calculate_apy(self) -> float:
        """
        Calculate APY using E=hf physics model
        Higher frequency (shorter wavelength) = higher energy = higher APY
        """
        tier = self.get_tier()
        tier_config = TIER_CONFIG[tier]
        
        # Convert wavelength to frequency: f = c / λ
        wavelength_m = tier_config["wavelength_nm"] * 1e-9
        frequency = SPEED_OF_LIGHT / wavelength_m
        
        # Normalize frequency to reasonable APY range (10-500%)
        # Using log scale since frequencies span many orders of magnitude
        log_freq = math.log10(frequency)
        
        # Scale to APY: log10(3e8/1000nm) ≈ 14.5, log10(3e8/0.01nm) ≈ 19.5
        # Map this range to 10-500% APY
        base_apy = 10 + (log_freq - 14) * 100
        
        # Apply multipliers
        final_apy = base_apy * self.get_multiplier()
        
        # Cap at reasonable values
        return max(10, min(500, final_apy))
    
    def get_pending_rewards_for_stake(self, user_address: str) -> Tuple[float, float]:
        """
        Get pending rewards before staking (for substrate settlement).
        Returns:
            (pending_rewards, snapshot_time)
        """
        if user_address not in self.stakers:
            return 0.0, time.time()
        return self.calculate_pending_rewards(user_address), time.time()
    
    def stake(self, user_address: str, lp_amount: float, lp_value_nxt: float, rewards_already_settled: float = 0.0, snapshot_time: float = 0.0) -> Tuple[bool, str]:
        """
        Stake LP tokens in the farm
        
        Args:
            user_address: User's wallet address
            lp_amount: Amount of LP tokens to stake
            lp_value_nxt: Value of LP tokens in NXT (for TVL calculation)
            rewards_already_settled: Rewards already processed through substrate (for existing stakers)
            snapshot_time: Snapshot time for reward claim (for existing stakers)
        
        Returns:
            (success, message)
        """
        if not self.is_active:
            return False, "Farm is not active"
        
        if lp_amount <= 0:
            return False, "Invalid stake amount"
        
        if user_address in self.stakers:
            if snapshot_time > 0:
                self.stakers[user_address].last_reward_claim = snapshot_time
                self.stakers[user_address].total_rewards_claimed += rewards_already_settled
                self.total_rewards_distributed += rewards_already_settled
            self.stakers[user_address].staked_lp += lp_amount
        else:
            self.stakers[user_address] = FarmPosition(
                user_address=user_address,
                pool_id=self.pool_id,
                staked_lp=lp_amount
            )
        
        self.total_staked_lp += lp_amount
        self.total_value_locked += lp_value_nxt
        
        return True, f"Staked {lp_amount:.4f} LP tokens in {self.pool_id} farm"
    
    def preview_unstake(self, user_address: str, lp_amount: float) -> Tuple[bool, float, float, float, str]:
        """
        Preview unstake without modifying state.
        Returns:
            (can_unstake, pending_rewards, value_to_remove, snapshot_time, message)
        """
        if user_address not in self.stakers:
            return False, 0.0, 0.0, 0.0, "No stake found"
        
        position = self.stakers[user_address]
        if position.staked_lp < lp_amount:
            return False, 0.0, 0.0, 0.0, f"Insufficient stake: have {position.staked_lp:.4f}, requested {lp_amount:.4f}"
        
        pending_rewards = self.calculate_pending_rewards(user_address)
        value_to_remove = (lp_amount / self.total_staked_lp) * self.total_value_locked if self.total_staked_lp > 0 else 0
        snapshot_time = time.time()
        
        return True, pending_rewards, value_to_remove, snapshot_time, f"Ready to unstake {lp_amount:.4f} LP + {pending_rewards:.4f} NXT"
    
    def commit_unstake(self, user_address: str, lp_amount: float, value_to_remove: float, pending_rewards: float, snapshot_time: float) -> Tuple[bool, str]:
        """
        Commit unstake using pre-calculated snapshot values.
        Only call this after process_orbital_transfer succeeds.
        """
        if user_address not in self.stakers:
            return False, "No stake found"
        
        position = self.stakers[user_address]
        if position.staked_lp < lp_amount:
            return False, f"Insufficient stake"
        
        position.staked_lp -= lp_amount
        position.last_reward_claim = snapshot_time
        position.total_rewards_claimed += pending_rewards
        
        self.total_staked_lp -= lp_amount
        self.total_value_locked = max(0, self.total_value_locked - value_to_remove)
        self.total_rewards_distributed += pending_rewards
        
        if position.staked_lp <= 0:
            del self.stakers[user_address]
        
        return True, f"Unstaked {lp_amount:.4f} LP tokens"
    
    def unstake(self, user_address: str, lp_amount: float) -> Tuple[bool, float, str]:
        """
        DEPRECATED: Use preview_unstake + commit_unstake for transactional semantics.
        Left for backwards compatibility.
        """
        success, rewards, value_to_remove, snapshot_time, msg = self.preview_unstake(user_address, lp_amount)
        if success:
            self.commit_unstake(user_address, lp_amount, value_to_remove, rewards, snapshot_time)
        return success, rewards, msg
    
    def calculate_pending_rewards(self, user_address: str) -> float:
        """Calculate pending rewards for a user"""
        if user_address not in self.stakers:
            return 0.0
        
        position = self.stakers[user_address]
        
        # Time since last claim in days
        time_elapsed_days = position.get_time_since_claim() / 86400
        
        # User's share of pool
        if self.total_staked_lp <= 0:
            return 0.0
        share = position.staked_lp / self.total_staked_lp
        
        # Calculate rewards: base_rate * share * time * multiplier * TVL
        # Rewards proportional to TVL contribution
        rewards = (
            self.base_reward_rate *
            share *
            time_elapsed_days *
            self.get_multiplier() *
            self.total_value_locked
        )
        
        return rewards
    
    def preview_claim_rewards(self, user_address: str) -> Tuple[bool, float, float, str]:
        """
        Preview reward claim without modifying state.
        Returns:
            (can_claim, pending_rewards, claim_timestamp, message)
        """
        if user_address not in self.stakers:
            return False, 0.0, 0.0, "No stake found"
        
        rewards = self.calculate_pending_rewards(user_address)
        if rewards <= 0:
            return False, 0.0, 0.0, "No rewards to claim"
        
        snapshot_time = time.time()
        return True, rewards, snapshot_time, f"Ready to claim {rewards:.4f} NXT"
    
    def commit_claim_rewards(self, user_address: str, rewards: float, snapshot_time: float) -> Tuple[bool, str]:
        """
        Commit reward claim using pre-calculated snapshot values.
        Only call this after process_orbital_transfer succeeds.
        """
        if user_address not in self.stakers:
            return False, "No stake found"
        
        self.stakers[user_address].last_reward_claim = snapshot_time
        self.stakers[user_address].total_rewards_claimed += rewards
        self.total_rewards_distributed += rewards
        
        return True, f"Claimed {rewards:.4f} NXT"
    
    def _claim_pending_rewards(self, user_address: str) -> float:
        """DEPRECATED: Internal claim method"""
        rewards = self.calculate_pending_rewards(user_address)
        if user_address in self.stakers:
            self.stakers[user_address].last_reward_claim = time.time()
            self.stakers[user_address].total_rewards_claimed += rewards
            self.total_rewards_distributed += rewards
        return rewards
    
    def claim_rewards(self, user_address: str) -> Tuple[bool, float, str]:
        """
        DEPRECATED: DISABLED - Must use preview_claim_rewards + commit_claim_rewards
        for physics substrate compliance.
        """
        return False, 0.0, "Legacy claim_rewards disabled - use transactional preview/commit flow via FarmingEngine"
    
    def get_user_info(self, user_address: str) -> Optional[dict]:
        """Get user's farming info for this pool"""
        if user_address not in self.stakers:
            return None
        
        position = self.stakers[user_address]
        pending = self.calculate_pending_rewards(user_address)
        
        return {
            "pool_id": self.pool_id,
            "staked_lp": position.staked_lp,
            "share_percent": (position.staked_lp / self.total_staked_lp * 100) if self.total_staked_lp > 0 else 0,
            "pending_rewards": pending,
            "total_claimed": position.total_rewards_claimed,
            "staked_at": position.staked_at,
            "stake_duration_days": position.get_stake_duration() / 86400
        }
    
    def to_dict(self) -> dict:
        """Convert farm pool to dictionary"""
        tier = self.get_tier()
        return {
            "pool_id": self.pool_id,
            "token_a": self.token_a,
            "token_b": self.token_b,
            "total_staked_lp": self.total_staked_lp,
            "tvl": self.total_value_locked,
            "apy": self.calculate_apy(),
            "tier": tier.value,
            "tier_color": TIER_CONFIG[tier]["color"],
            "multiplier": self.get_multiplier(),
            "staker_count": len(self.stakers),
            "total_rewards_distributed": self.total_rewards_distributed,
            "is_active": self.is_active
        }


class FarmingEngine:
    """
    Main farming engine managing all farm pools with physics substrate integration.
    
    Physics Foundation:
    - Energy distribution follows E=hf (Planck's equation)
    - Higher TVL pools operate at higher "frequency" → more energy rewards
    - All reward claims route through TransitionReserveLedger
    - SDK fees (0.5%) on all reward distributions
    - Creates natural incentive for liquidity concentration
    """
    
    REWARD_WAVELENGTH_NM = 600.0
    
    def __init__(self, dex_engine=None, nxt_adapter=None):
        """
        Initialize farming engine
        
        Args:
            dex_engine: Reference to DEX engine for LP token verification
            nxt_adapter: NativeTokenAdapter for NXT transfers
        """
        self.dex_engine = dex_engine
        self.nxt_adapter = nxt_adapter
        
        self.farms: Dict[str, FarmPool] = {}
        self.reward_source = "FARMING_REWARDS"
        self.total_rewards_distributed = 0.0
        self.created_at = time.time()
        
        self._physics_adapter = get_physics_adapter()
        self.substrate_transactions: List[SubstrateTransaction] = []
        self.total_energy_joules = 0.0
        self.total_lambda_mass_kg = 0.0
    
    def set_dex_engine(self, dex_engine):
        """Set DEX engine reference"""
        self.dex_engine = dex_engine
    
    def set_nxt_adapter(self, nxt_adapter):
        """Set NXT adapter reference"""
        self.nxt_adapter = nxt_adapter
    
    def create_farm(self, pool_id: str, token_a: str, token_b: str, 
                    base_reward_rate: float = 0.01, bonus_multiplier: float = 1.0) -> Tuple[bool, str]:
        """
        Create a new farming pool for an LP pair
        
        Args:
            pool_id: DEX pool ID (e.g., "USDC-NXT")
            token_a: First token symbol
            token_b: Second token symbol
            base_reward_rate: Daily reward rate (default 1%)
            bonus_multiplier: Extra multiplier for promotions
        
        Returns:
            (success, message)
        """
        if pool_id in self.farms:
            return False, f"Farm already exists for {pool_id}"
        
        # Verify DEX pool exists
        if self.dex_engine and pool_id not in self.dex_engine.pools:
            return False, f"DEX pool {pool_id} does not exist"
        
        # Create farm
        self.farms[pool_id] = FarmPool(
            pool_id=pool_id,
            token_a=token_a,
            token_b=token_b,
            base_reward_rate=base_reward_rate,
            bonus_multiplier=bonus_multiplier
        )
        
        return True, f"Created farm for {pool_id} with {base_reward_rate*100:.1f}% daily base rate"
    
    def get_or_create_farm(self, pool_id: str) -> Optional[FarmPool]:
        """Get existing farm or create one from DEX pool"""
        if pool_id in self.farms:
            return self.farms[pool_id]
        
        # Try to create from DEX pool
        if self.dex_engine and pool_id in self.dex_engine.pools:
            pool = self.dex_engine.pools[pool_id]
            success, _ = self.create_farm(pool_id, pool.token_a, pool.token_b)
            if success:
                return self.farms[pool_id]
        
        return None
    
    def stake_lp(self, user_address: str, pool_id: str, lp_amount: float) -> Tuple[bool, str]:
        """
        Stake LP tokens in a farm
        
        LP tokens are LOCKED by transferring them to the farm escrow account.
        Users cannot remove liquidity from DEX while LP is staked.
        
        Args:
            user_address: User's wallet address
            pool_id: Pool to stake in
            lp_amount: Amount of LP tokens to stake
        
        Returns:
            (success, message)
        """
        # Validate amount first
        if lp_amount <= 0:
            return False, "Stake amount must be greater than zero"
        
        # Get or create farm
        farm = self.get_or_create_farm(pool_id)
        if farm is None:
            return False, f"Farm not found for {pool_id}"
        
        if not farm.is_active:
            return False, f"Farm {pool_id} is not active"
        
        # Farm escrow account for this pool
        farm_escrow = f"FARM_ESCROW_{pool_id}"
        pool = None
        lp_value = lp_amount * 100  # Default fallback
        
        # Verify user has LP tokens (check DEX pool)
        if self.dex_engine and pool_id in self.dex_engine.pools:
            pool = self.dex_engine.pools[pool_id]
            user_lp = pool.lp_balances.get(user_address, 0)
            
            # User's available LP is their pool balance (not already locked in escrow)
            if user_lp < lp_amount:
                return False, f"Insufficient LP tokens: available {user_lp:.4f}, requested {lp_amount:.4f}"
            
            # Calculate LP value for TVL before locking
            lp_value = self._calculate_lp_value(pool, lp_amount)
        
        pending_rewards, snapshot_time = farm.get_pending_rewards_for_stake(user_address)
        
        if pending_rewards > 0:
            if not self._distribute_rewards(user_address, pending_rewards):
                return False, "Pending reward distribution failed - stake blocked"
            self.total_rewards_distributed += pending_rewards
        
        success, message = farm.stake(user_address, lp_amount, lp_value, pending_rewards, snapshot_time)
        
        if not success:
            return False, message
        
        # THEN: LOCK LP TOKENS only after stake succeeds
        # Transfer from user to farm escrow - prevents removing liquidity while staked
        if pool is not None:
            user_lp = pool.lp_balances.get(user_address, 0)
            pool.lp_balances[user_address] = user_lp - lp_amount
            pool.lp_balances[farm_escrow] = pool.lp_balances.get(farm_escrow, 0) + lp_amount
        
        return True, message
    
    def unstake_lp(self, user_address: str, pool_id: str, lp_amount: float) -> Tuple[bool, float, str]:
        """
        Unstake LP tokens from farm
        
        LP tokens are UNLOCKED by transferring them from farm escrow back to user.
        
        Returns:
            (success, rewards_claimed, message)
        """
        if pool_id not in self.farms:
            return False, 0.0, f"Farm not found for {pool_id}"
        
        farm = self.farms[pool_id]
        
        can_unstake, pending_rewards, value_to_remove, snapshot_time, preview_msg = farm.preview_unstake(user_address, lp_amount)
        if not can_unstake:
            return False, 0.0, preview_msg
        
        if pending_rewards > 0:
            if not self._distribute_rewards(user_address, pending_rewards):
                return False, 0.0, "Reward distribution failed through physics substrate - unstake blocked"
        
        success, commit_msg = farm.commit_unstake(user_address, lp_amount, value_to_remove, pending_rewards, snapshot_time)
        if not success:
            return False, 0.0, commit_msg
        
        self.total_rewards_distributed += pending_rewards
        
        farm_escrow = f"FARM_ESCROW_{pool_id}"
        
        if self.dex_engine and pool_id in self.dex_engine.pools:
            pool = self.dex_engine.pools[pool_id]
            escrow_balance = pool.lp_balances.get(farm_escrow, 0)
            
            if escrow_balance >= lp_amount:
                pool.lp_balances[farm_escrow] = escrow_balance - lp_amount
                pool.lp_balances[user_address] = pool.lp_balances.get(user_address, 0) + lp_amount
        
        return True, pending_rewards, f"Unstaked {lp_amount:.4f} LP + {pending_rewards:.4f} NXT rewards"
    
    def claim_rewards(self, user_address: str, pool_id: str) -> Tuple[bool, float, str]:
        """Claim farming rewards from a specific pool"""
        if pool_id not in self.farms:
            return False, 0.0, f"Farm not found for {pool_id}"
        
        farm = self.farms[pool_id]
        can_claim, pending_rewards, snapshot_time, preview_msg = farm.preview_claim_rewards(user_address)
        
        if not can_claim:
            return False, 0.0, preview_msg
        
        if not self._distribute_rewards(user_address, pending_rewards):
            return False, 0.0, "Reward distribution failed through physics substrate"
        
        commit_success, commit_msg = farm.commit_claim_rewards(user_address, pending_rewards, snapshot_time)
        if not commit_success:
            return False, 0.0, f"Commit failed: {commit_msg}"
        
        self.total_rewards_distributed += pending_rewards
        
        return True, pending_rewards, f"Claimed {pending_rewards:.4f} NXT farming rewards"
    
    def claim_all_rewards(self, user_address: str) -> Tuple[bool, float, str]:
        """
        Claim rewards from all farms using atomic transactional semantics.
        Validates ALL farms can commit before starting ANY substrate transfers.
        """
        pending_claims = []
        
        for pool_id, farm in self.farms.items():
            if user_address not in farm.stakers:
                continue
            can_claim, rewards, snapshot_time, _ = farm.preview_claim_rewards(user_address)
            if can_claim and rewards > 0:
                pending_claims.append((pool_id, farm, rewards, snapshot_time))
        
        if not pending_claims:
            return False, 0.0, "No rewards to claim"
        
        for pool_id, farm, rewards, snapshot_time in pending_claims:
            if user_address not in farm.stakers:
                return False, 0.0, f"Pre-validation failed: user no longer in {pool_id}"
        
        total_pending = sum(rewards for _, _, rewards, _ in pending_claims)
        
        if not self._distribute_rewards(user_address, total_pending):
            return False, 0.0, "Reward distribution failed through physics substrate"
        
        for pool_id, farm, rewards, snapshot_time in pending_claims:
            farm.commit_claim_rewards(user_address, rewards, snapshot_time)
        
        self.total_rewards_distributed += total_pending
        return True, total_pending, f"Claimed {total_pending:.4f} NXT from {len(pending_claims)} farms"
    
    def _distribute_rewards(self, user_address: str, amount: float) -> bool:
        """Distribute NXT rewards to user through physics substrate"""
        reward_id = f"FARM-REWARD-{user_address[:8]}-{int(time.time())}"
        
        substrate_tx = self._physics_adapter.process_orbital_transfer(
            source_address=self.reward_source,
            recipient_address=user_address,
            amount_nxt=amount,
            wavelength_nm=self.REWARD_WAVELENGTH_NM,
            module=EconomicModule.FARMING,
            transfer_id=reward_id,
            bhls_category=None
        )
        
        if substrate_tx.success and substrate_tx.settlement_success:
            self.substrate_transactions.append(substrate_tx)
            self.total_energy_joules += substrate_tx.energy_joules
            self.total_lambda_mass_kg += substrate_tx.lambda_boson_kg
            return True
        
        return False
    
    def _calculate_lp_value(self, pool, lp_amount: float) -> float:
        """Calculate the NXT value of LP tokens"""
        if pool.lp_token_supply <= 0:
            return 0.0
        
        # LP value = (share of pool) * (reserve_a + reserve_b in NXT terms)
        share = lp_amount / pool.lp_token_supply
        
        # Assume token_b is NXT, estimate token_a value from pool ratio
        reserve_b_value = pool.reserve_b  # Already in NXT
        reserve_a_value = pool.reserve_b  # Equivalent value since AMM
        
        total_value = reserve_a_value + reserve_b_value
        return share * total_value
    
    def get_user_farms(self, user_address: str) -> List[dict]:
        """Get all farming positions for a user"""
        positions = []
        
        for pool_id, farm in self.farms.items():
            info = farm.get_user_info(user_address)
            if info:
                info["apy"] = farm.calculate_apy()
                info["tier"] = farm.get_tier().value
                positions.append(info)
        
        return positions
    
    def get_all_farms(self) -> List[dict]:
        """Get all active farms"""
        return [farm.to_dict() for farm in self.farms.values() if farm.is_active]
    
    def get_total_tvl(self) -> float:
        """Get total value locked across all farms"""
        return sum(farm.total_value_locked for farm in self.farms.values())
    
    def get_stats(self) -> dict:
        """Get global farming stats"""
        return {
            "total_farms": len(self.farms),
            "active_farms": sum(1 for f in self.farms.values() if f.is_active),
            "total_tvl": self.get_total_tvl(),
            "total_stakers": sum(len(f.stakers) for f in self.farms.values()),
            "total_rewards_distributed": self.total_rewards_distributed,
            "uptime_days": (time.time() - self.created_at) / 86400
        }


def get_farming_engine() -> FarmingEngine:
    """Get or create global farming engine instance"""
    import streamlit as st
    
    if 'farming_engine' not in st.session_state:
        st.session_state.farming_engine = FarmingEngine()
    
    return st.session_state.farming_engine


def initialize_farming(dex_engine, nxt_adapter) -> FarmingEngine:
    """Initialize farming engine with DEX integration"""
    engine = get_farming_engine()
    engine.set_dex_engine(dex_engine)
    engine.set_nxt_adapter(nxt_adapter)
    
    # Auto-create farms for existing DEX pools
    if dex_engine:
        for pool_id, pool in dex_engine.pools.items():
            if pool_id not in engine.farms:
                engine.create_farm(pool_id, pool.token_a, pool.token_b)
    
    return engine
