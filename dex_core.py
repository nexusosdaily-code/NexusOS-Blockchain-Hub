"""
Decentralized Exchange (DEX) Core Module
Layer 2 integration for NexusOS blockchain with AMM, liquidity pools, and token standards
"""

import hashlib
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
import math


class TokenStandard(Enum):
    """Token standard types"""
    FUNGIBLE = "Fungible Token (ERC-20-like)"
    NFT = "Non-Fungible Token"
    WRAPPED = "Wrapped Native Token"


@dataclass
class Token:
    """ERC-20-like token standard"""
    symbol: str
    name: str
    decimals: int = 18
    total_supply: float = 0.0
    token_standard: TokenStandard = TokenStandard.FUNGIBLE
    creator: str = ""
    created_at: float = field(default_factory=time.time)
    
    # Token state
    balances: Dict[str, float] = field(default_factory=dict)
    allowances: Dict[str, Dict[str, float]] = field(default_factory=dict)  # owner -> spender -> amount
    
    def mint(self, to: str, amount: float) -> bool:
        """Mint new tokens to an address"""
        if amount <= 0:
            return False
        
        self.balances[to] = self.balances.get(to, 0) + amount
        self.total_supply += amount
        return True
    
    def burn(self, from_address: str, amount: float) -> bool:
        """Burn tokens from an address"""
        if amount <= 0:
            return False
        
        balance = self.balances.get(from_address, 0)
        if balance < amount:
            return False
        
        self.balances[from_address] = balance - amount
        self.total_supply -= amount
        return True
    
    def transfer(self, from_address: str, to: str, amount: float) -> bool:
        """Transfer tokens between addresses"""
        if amount <= 0:
            return False
        
        from_balance = self.balances.get(from_address, 0)
        if from_balance < amount:
            return False
        
        self.balances[from_address] = from_balance - amount
        self.balances[to] = self.balances.get(to, 0) + amount
        return True
    
    def approve(self, owner: str, spender: str, amount: float) -> bool:
        """Approve spender to use owner's tokens"""
        if owner not in self.allowances:
            self.allowances[owner] = {}
        
        self.allowances[owner][spender] = amount
        return True
    
    def transfer_from(self, spender: str, from_address: str, to: str, amount: float) -> bool:
        """Transfer tokens using allowance"""
        if amount <= 0:
            return False
        
        # Check allowance
        allowed = self.allowances.get(from_address, {}).get(spender, 0)
        if allowed < amount:
            return False
        
        # Check balance
        from_balance = self.balances.get(from_address, 0)
        if from_balance < amount:
            return False
        
        # Execute transfer
        self.balances[from_address] = from_balance - amount
        self.balances[to] = self.balances.get(to, 0) + amount
        
        # Update allowance
        self.allowances[from_address][spender] = allowed - amount
        return True
    
    def balance_of(self, address: str) -> float:
        """Get token balance for address"""
        return self.balances.get(address, 0)
    
    def allowance(self, owner: str, spender: str) -> float:
        """Get allowance for spender from owner"""
        return self.allowances.get(owner, {}).get(spender, 0)
    
    def to_dict(self) -> dict:
        """Convert token to dictionary"""
        return {
            'symbol': self.symbol,
            'name': self.name,
            'decimals': self.decimals,
            'total_supply': self.total_supply,
            'token_standard': self.token_standard.value,
            'creator': self.creator,
            'created_at': self.created_at,
            'holders': len(self.balances)
        }


@dataclass
class LiquidityPool:
    """Automated Market Maker liquidity pool"""
    token_a: str  # Token A symbol
    token_b: str  # Token B symbol
    reserve_a: float = 0.0
    reserve_b: float = 0.0
    lp_token_supply: float = 0.0
    fee_rate: float = 0.003  # 0.3% trading fee
    
    # Pool state
    lp_balances: Dict[str, float] = field(default_factory=dict)  # LP token holders
    total_volume_a: float = 0.0
    total_volume_b: float = 0.0
    total_fees_collected: float = 0.0
    created_at: float = field(default_factory=time.time)
    
    def get_pool_id(self) -> str:
        """Generate unique pool ID"""
        return f"{self.token_a}-{self.token_b}"
    
    def get_price(self, input_token: str) -> float:
        """Get current price of input token in terms of output token"""
        if self.reserve_a == 0 or self.reserve_b == 0:
            return 0.0
        
        if input_token == self.token_a:
            return self.reserve_b / self.reserve_a
        else:
            return self.reserve_a / self.reserve_b
    
    def calculate_output_amount(self, input_token: str, input_amount: float) -> Tuple[float, float]:
        """
        Calculate output amount using constant product formula (x * y = k)
        Returns: (output_amount, price_impact)
        """
        if input_amount <= 0:
            return 0.0, 0.0
        
        if input_token == self.token_a:
            reserve_in = self.reserve_a
            reserve_out = self.reserve_b
        else:
            reserve_in = self.reserve_b
            reserve_out = self.reserve_a
        
        if reserve_in == 0 or reserve_out == 0:
            return 0.0, 0.0
        
        # Apply fee
        input_with_fee = input_amount * (1 - self.fee_rate)
        
        # Constant product formula: (x + Δx)(y - Δy) = xy
        # Δy = y * Δx / (x + Δx)
        output_amount = (reserve_out * input_with_fee) / (reserve_in + input_with_fee)
        
        # Calculate price impact
        old_price = reserve_out / reserve_in
        new_reserve_in = reserve_in + input_amount
        new_reserve_out = reserve_out - output_amount
        new_price = new_reserve_out / new_reserve_in
        price_impact = abs((new_price - old_price) / old_price) * 100
        
        return output_amount, price_impact
    
    def swap(self, input_token: str, input_amount: float, min_output: float = 0.0) -> Tuple[bool, float, str]:
        """
        Execute token swap
        Returns: (success, output_amount, message)
        """
        output_amount, price_impact = self.calculate_output_amount(input_token, input_amount)
        
        if output_amount < min_output:
            return False, 0.0, f"Slippage exceeded: got {output_amount:.4f}, minimum {min_output:.4f}"
        
        # Update reserves
        if input_token == self.token_a:
            self.reserve_a += input_amount
            self.reserve_b -= output_amount
            self.total_volume_a += input_amount
        else:
            self.reserve_b += input_amount
            self.reserve_a -= output_amount
            self.total_volume_b += input_amount
        
        # Track fees
        fee_amount = input_amount * self.fee_rate
        self.total_fees_collected += fee_amount
        
        return True, output_amount, f"Swap successful: {output_amount:.4f} (impact: {price_impact:.2f}%)"
    
    def add_liquidity(self, provider: str, amount_a: float, amount_b: float) -> Tuple[bool, float, str]:
        """
        Add liquidity to pool
        Returns: (success, lp_tokens_minted, message)
        """
        if amount_a <= 0 or amount_b <= 0:
            return False, 0.0, "Invalid amounts"
        
        # First liquidity provision
        if self.lp_token_supply == 0:
            lp_tokens = math.sqrt(amount_a * amount_b)
            self.reserve_a = amount_a
            self.reserve_b = amount_b
        else:
            # Maintain price ratio
            ratio_a = amount_a / self.reserve_a
            ratio_b = amount_b / self.reserve_b
            
            if abs(ratio_a - ratio_b) > 0.02:  # 2% tolerance
                return False, 0.0, f"Unbalanced liquidity: ratio A={ratio_a:.4f}, ratio B={ratio_b:.4f}"
            
            # Mint LP tokens proportional to share
            lp_tokens = min(
                (amount_a / self.reserve_a) * self.lp_token_supply,
                (amount_b / self.reserve_b) * self.lp_token_supply
            )
            
            self.reserve_a += amount_a
            self.reserve_b += amount_b
        
        # Issue LP tokens
        self.lp_balances[provider] = self.lp_balances.get(provider, 0) + lp_tokens
        self.lp_token_supply += lp_tokens
        
        return True, lp_tokens, f"Liquidity added: {lp_tokens:.4f} LP tokens minted"
    
    def remove_liquidity(self, provider: str, lp_tokens: float) -> Tuple[bool, float, float, str]:
        """
        Remove liquidity from pool
        Returns: (success, amount_a, amount_b, message)
        """
        if lp_tokens <= 0:
            return False, 0.0, 0.0, "Invalid LP token amount"
        
        provider_balance = self.lp_balances.get(provider, 0)
        if provider_balance < lp_tokens:
            return False, 0.0, 0.0, f"Insufficient LP tokens: have {provider_balance:.4f}, need {lp_tokens:.4f}"
        
        # Calculate share
        share = lp_tokens / self.lp_token_supply
        amount_a = self.reserve_a * share
        amount_b = self.reserve_b * share
        
        # Update reserves
        self.reserve_a -= amount_a
        self.reserve_b -= amount_b
        
        # Burn LP tokens
        self.lp_balances[provider] -= lp_tokens
        self.lp_token_supply -= lp_tokens
        
        return True, amount_a, amount_b, f"Liquidity removed: {amount_a:.4f} {self.token_a} + {amount_b:.4f} {self.token_b}"
    
    def get_pool_share(self, provider: str) -> float:
        """Get provider's share of the pool (0-100%)"""
        if self.lp_token_supply == 0:
            return 0.0
        return (self.lp_balances.get(provider, 0) / self.lp_token_supply) * 100
    
    def to_dict(self) -> dict:
        """Convert pool to dictionary"""
        return {
            'pool_id': self.get_pool_id(),
            'token_a': self.token_a,
            'token_b': self.token_b,
            'reserve_a': self.reserve_a,
            'reserve_b': self.reserve_b,
            'price_a_to_b': self.get_price(self.token_a),
            'price_b_to_a': self.get_price(self.token_b),
            'lp_token_supply': self.lp_token_supply,
            'total_volume_a': self.total_volume_a,
            'total_volume_b': self.total_volume_b,
            'total_fees_collected': self.total_fees_collected,
            'liquidity_providers': len(self.lp_balances),
            'tvl': self.reserve_a + self.reserve_b,  # Simplified TVL
            'created_at': self.created_at
        }


class DEXEngine:
    """Decentralized Exchange Engine with AMM"""
    
    def __init__(self):
        """Initialize DEX engine"""
        self.tokens: Dict[str, Token] = {}
        self.pools: Dict[str, LiquidityPool] = {}
        
        # DEX statistics
        self.total_swaps = 0
        self.total_volume = 0.0
        self.total_liquidity_added = 0.0
        
        # Initialize with default tokens
        self._initialize_default_tokens()
    
    def _initialize_default_tokens(self):
        """Create default tokens for testing"""
        # Native token (like ETH/SOL)
        native = Token(
            symbol="NXS",
            name="Nexus Token",
            decimals=18,
            creator="system"
        )
        native.mint("treasury", 1_000_000)
        self.tokens["NXS"] = native
        
        # Stablecoin
        usdc = Token(
            symbol="USDC",
            name="USD Coin",
            decimals=6,
            creator="system"
        )
        usdc.mint("treasury", 1_000_000)
        self.tokens["USDC"] = usdc
        
        # Governance token
        gov = Token(
            symbol="GOV",
            name="Governance Token",
            decimals=18,
            creator="system"
        )
        gov.mint("treasury", 100_000)
        self.tokens["GOV"] = gov
    
    def create_token(self, symbol: str, name: str, initial_supply: float, creator: str, decimals: int = 18) -> Tuple[bool, str]:
        """Create new token"""
        if symbol in self.tokens:
            return False, f"Token {symbol} already exists"
        
        token = Token(
            symbol=symbol,
            name=name,
            decimals=decimals,
            creator=creator
        )
        token.mint(creator, initial_supply)
        self.tokens[symbol] = token
        
        return True, f"Token {symbol} created with {initial_supply} initial supply"
    
    def create_pool(self, token_a: str, token_b: str, initial_a: float, initial_b: float, provider: str) -> Tuple[bool, str]:
        """Create new liquidity pool"""
        # Validate tokens
        if token_a not in self.tokens or token_b not in self.tokens:
            return False, "One or both tokens do not exist"
        
        # Ensure consistent ordering
        if token_a > token_b:
            token_a, token_b = token_b, token_a
            initial_a, initial_b = initial_b, initial_a
        
        pool_id = f"{token_a}-{token_b}"
        if pool_id in self.pools:
            return False, f"Pool {pool_id} already exists"
        
        # Create pool
        pool = LiquidityPool(token_a=token_a, token_b=token_b)
        
        # Add initial liquidity
        success, lp_tokens, message = pool.add_liquidity(provider, initial_a, initial_b)
        if not success:
            return False, f"Failed to add initial liquidity: {message}"
        
        # Transfer tokens from provider
        token_a_obj = self.tokens[token_a]
        token_b_obj = self.tokens[token_b]
        
        if not token_a_obj.transfer(provider, pool_id, initial_a):
            return False, f"Failed to transfer {token_a}"
        if not token_b_obj.transfer(provider, pool_id, initial_b):
            return False, f"Failed to transfer {token_b}"
        
        self.pools[pool_id] = pool
        self.total_liquidity_added += initial_a + initial_b
        
        return True, f"Pool {pool_id} created with {lp_tokens:.4f} LP tokens"
    
    def swap_tokens(self, user: str, input_token: str, output_token: str, input_amount: float, slippage_tolerance: float = 0.01) -> Tuple[bool, float, str]:
        """Execute token swap"""
        # Find pool
        pool_id = f"{min(input_token, output_token)}-{max(input_token, output_token)}"
        if pool_id not in self.pools:
            return False, 0.0, f"Pool {pool_id} does not exist"
        
        pool = self.pools[pool_id]
        
        # Calculate minimum output with slippage
        expected_output, _ = pool.calculate_output_amount(input_token, input_amount)
        min_output = expected_output * (1 - slippage_tolerance)
        
        # Execute swap
        success, output_amount, message = pool.swap(input_token, input_amount, min_output)
        
        if success:
            # Transfer tokens
            input_token_obj = self.tokens[input_token]
            output_token_obj = self.tokens[output_token]
            
            input_token_obj.transfer(user, pool_id, input_amount)
            output_token_obj.transfer(pool_id, user, output_amount)
            
            self.total_swaps += 1
            self.total_volume += input_amount
        
        return success, output_amount, message
    
    def get_quote(self, input_token: str, output_token: str, input_amount: float) -> Tuple[float, float, float]:
        """
        Get swap quote
        Returns: (output_amount, price_impact, effective_price)
        """
        pool_id = f"{min(input_token, output_token)}-{max(input_token, output_token)}"
        if pool_id not in self.pools:
            return 0.0, 0.0, 0.0
        
        pool = self.pools[pool_id]
        output_amount, price_impact = pool.calculate_output_amount(input_token, input_amount)
        effective_price = output_amount / input_amount if input_amount > 0 else 0.0
        
        return output_amount, price_impact, effective_price
    
    def get_all_pools(self) -> List[dict]:
        """Get all pools as dictionaries"""
        return [pool.to_dict() for pool in self.pools.values()]
    
    def get_all_tokens(self) -> List[dict]:
        """Get all tokens as dictionaries"""
        return [token.to_dict() for token in self.tokens.values()]
    
    def get_user_balances(self, user: str) -> Dict[str, float]:
        """Get all token balances for a user"""
        balances = {}
        for symbol, token in self.tokens.items():
            balance = token.balance_of(user)
            if balance > 0:
                balances[symbol] = balance
        return balances
