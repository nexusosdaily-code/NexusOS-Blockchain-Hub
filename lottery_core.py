"""
NexusOS Lottery System
Quantum randomness-based lottery funded by F_floor

Architecture:
- Lottery Pool receives allocation from F_floor
- Users purchase tickets with NXT
- Quantum randomness (CSPRNG) determines winners
- Prize distribution follows physics-based tiers
- Portion of proceeds returns to F_floor (sustainability)

Prize Tiers (E=hf inspired):
- Gamma Jackpot: 50% of pool (rare)
- X-Ray Prize: 25% of pool
- UV Prize: 15% of pool
- Visible Prizes: 10% of pool (many winners)
"""

import secrets
import hashlib
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from datetime import datetime


class LotteryTier(Enum):
    """Prize tiers based on electromagnetic spectrum"""
    GAMMA_JACKPOT = "gamma"      # Highest energy, rarest
    XRAY_PRIZE = "xray"          # High energy, uncommon
    UV_PRIZE = "uv"              # Medium energy, occasional
    VISIBLE_PRIZE = "visible"    # Common prizes, many winners


@dataclass
class LotteryTicket:
    """Individual lottery ticket"""
    ticket_id: str
    owner: str
    numbers: List[int]
    purchased_at: float = field(default_factory=time.time)
    draw_id: str = ""
    prize_tier: Optional[LotteryTier] = None
    prize_amount: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            "ticket_id": self.ticket_id,
            "owner": self.owner,
            "numbers": self.numbers,
            "purchased_at": self.purchased_at,
            "draw_id": self.draw_id,
            "prize_tier": self.prize_tier.value if self.prize_tier else None,
            "prize_amount": self.prize_amount
        }


@dataclass
class LotteryDraw:
    """A single lottery draw event"""
    draw_id: str
    scheduled_time: float
    executed_time: Optional[float] = None
    winning_numbers: List[int] = field(default_factory=list)
    total_pool: float = 0.0
    tickets_sold: int = 0
    winners: Dict[str, List[str]] = field(default_factory=dict)  # tier -> [ticket_ids]
    status: str = "pending"  # pending, active, completed
    quantum_seed: str = ""  # For audit trail
    
    def to_dict(self) -> Dict:
        return {
            "draw_id": self.draw_id,
            "scheduled_time": self.scheduled_time,
            "executed_time": self.executed_time,
            "winning_numbers": self.winning_numbers,
            "total_pool": self.total_pool,
            "tickets_sold": self.tickets_sold,
            "winners": self.winners,
            "status": self.status
        }


class QuantumLotteryEngine:
    """
    Lottery system using cryptographically secure randomness.
    
    The randomness generator uses Python's secrets module (NIST-approved CSPRNG)
    which provides cryptographically secure random numbers suitable for
    lottery drawings and financial applications.
    """
    
    # Lottery configuration
    TICKET_PRICE_NXT = 1.0  # 1 NXT per ticket
    NUMBERS_PER_TICKET = 6
    NUMBER_RANGE = (1, 49)  # 1-49 inclusive
    
    # Prize distribution (must sum to 1.0 minus F_floor return)
    PRIZE_DISTRIBUTION = {
        LotteryTier.GAMMA_JACKPOT: 0.40,   # 40% to jackpot
        LotteryTier.XRAY_PRIZE: 0.20,      # 20% to second tier
        LotteryTier.UV_PRIZE: 0.15,        # 15% to third tier
        LotteryTier.VISIBLE_PRIZE: 0.10    # 10% to many small prizes
    }
    F_FLOOR_RETURN = 0.15  # 15% returns to F_floor for sustainability
    
    # Match requirements for each tier
    MATCH_REQUIREMENTS = {
        LotteryTier.GAMMA_JACKPOT: 6,  # All 6 numbers
        LotteryTier.XRAY_PRIZE: 5,     # 5 numbers
        LotteryTier.UV_PRIZE: 4,       # 4 numbers
        LotteryTier.VISIBLE_PRIZE: 3   # 3 numbers
    }
    
    def __init__(self, token_system=None):
        self.token_system = token_system
        self.draws: Dict[str, LotteryDraw] = {}
        self.tickets: Dict[str, LotteryTicket] = {}
        self.current_draw: Optional[LotteryDraw] = None
        self.draw_history: List[str] = []
        
        # Initialize first draw
        self._create_new_draw()
    
    def _generate_quantum_seed(self) -> str:
        """Generate cryptographically secure seed for randomness"""
        random_bytes = secrets.token_bytes(32)
        timestamp = str(time.time_ns()).encode()
        combined = random_bytes + timestamp
        return hashlib.sha256(combined).hexdigest()
    
    def _generate_random_numbers(self, count: int, min_val: int, max_val: int) -> List[int]:
        """
        Generate cryptographically secure random numbers.
        
        Uses secrets.SystemRandom which is backed by the OS CSPRNG,
        providing numbers suitable for cryptographic and financial use.
        """
        numbers = set()
        while len(numbers) < count:
            num = secrets.randbelow(max_val - min_val + 1) + min_val
            numbers.add(num)
        return sorted(list(numbers))
    
    def _create_new_draw(self) -> LotteryDraw:
        """Create a new lottery draw"""
        draw_id = f"DRAW-{int(time.time())}-{secrets.token_hex(4)}"
        
        draw = LotteryDraw(
            draw_id=draw_id,
            scheduled_time=time.time() + 86400,  # 24 hours from now
            status="active"
        )
        
        self.draws[draw_id] = draw
        self.current_draw = draw
        self.draw_history.append(draw_id)
        
        return draw
    
    def purchase_ticket(
        self,
        buyer: str,
        numbers: Optional[List[int]] = None
    ) -> Tuple[bool, Optional[LotteryTicket], str]:
        """
        Purchase a lottery ticket.
        
        Args:
            buyer: Wallet address of purchaser
            numbers: Optional list of 6 numbers (1-49). If not provided, generates random.
        
        Returns:
            (success, ticket, message)
        """
        if not self.current_draw or self.current_draw.status != "active":
            return False, None, "No active lottery draw"
        
        # Validate or generate numbers
        if numbers:
            if len(numbers) != self.NUMBERS_PER_TICKET:
                return False, None, f"Must provide exactly {self.NUMBERS_PER_TICKET} numbers"
            
            for num in numbers:
                if num < self.NUMBER_RANGE[0] or num > self.NUMBER_RANGE[1]:
                    return False, None, f"Numbers must be between {self.NUMBER_RANGE[0]} and {self.NUMBER_RANGE[1]}"
            
            if len(set(numbers)) != len(numbers):
                return False, None, "Numbers must be unique"
            
            numbers = sorted(numbers)
        else:
            numbers = self._generate_random_numbers(
                self.NUMBERS_PER_TICKET,
                self.NUMBER_RANGE[0],
                self.NUMBER_RANGE[1]
            )
        
        # Process payment if token system available
        if self.token_system:
            buyer_account = self.token_system.get_account(buyer)
            if not buyer_account:
                return False, None, "Wallet not found"
            
            ticket_cost_units = int(self.TICKET_PRICE_NXT * self.token_system.UNITS_PER_NXT)
            
            if buyer_account.balance < ticket_cost_units:
                return False, None, f"Insufficient balance. Need {self.TICKET_PRICE_NXT} NXT"
            
            # Transfer to lottery pool
            success, _, msg = self.token_system.transfer_atomic(
                from_address=buyer,
                to_address="LOTTERY_POOL",
                amount=ticket_cost_units,
                fee=0,
                reason="Lottery ticket purchase"
            )
            
            if not success:
                return False, None, f"Payment failed: {msg}"
        
        # Create ticket
        ticket_id = f"TKT-{secrets.token_hex(8)}"
        ticket = LotteryTicket(
            ticket_id=ticket_id,
            owner=buyer,
            numbers=numbers,
            draw_id=self.current_draw.draw_id
        )
        
        self.tickets[ticket_id] = ticket
        self.current_draw.tickets_sold += 1
        self.current_draw.total_pool += self.TICKET_PRICE_NXT
        
        return True, ticket, f"Ticket purchased! Numbers: {numbers}"
    
    def execute_draw(self) -> Tuple[bool, Dict[str, Any], str]:
        """
        Execute the lottery draw using quantum randomness.
        
        Returns:
            (success, results, message)
        """
        if not self.current_draw:
            return False, {}, "No active draw"
        
        if self.current_draw.status != "active":
            return False, {}, "Draw is not active"
        
        draw = self.current_draw
        
        # Generate quantum seed and winning numbers
        draw.quantum_seed = self._generate_quantum_seed()
        draw.winning_numbers = self._generate_random_numbers(
            self.NUMBERS_PER_TICKET,
            self.NUMBER_RANGE[0],
            self.NUMBER_RANGE[1]
        )
        draw.executed_time = time.time()
        
        # Find winners by matching numbers
        winners_by_tier = {tier.value: [] for tier in LotteryTier}
        
        for ticket_id, ticket in self.tickets.items():
            if ticket.draw_id != draw.draw_id:
                continue
            
            matches = len(set(ticket.numbers) & set(draw.winning_numbers))
            
            # Assign prize tier based on matches
            for tier, required_matches in self.MATCH_REQUIREMENTS.items():
                if matches >= required_matches:
                    ticket.prize_tier = tier
                    winners_by_tier[tier.value].append(ticket_id)
                    break
        
        draw.winners = winners_by_tier
        
        # Calculate and distribute prizes
        prize_pool = draw.total_pool * (1 - self.F_FLOOR_RETURN)
        f_floor_amount = draw.total_pool * self.F_FLOOR_RETURN
        
        prize_amounts = {}
        for tier in LotteryTier:
            tier_pool = prize_pool * self.PRIZE_DISTRIBUTION[tier]
            winner_count = len(winners_by_tier[tier.value])
            
            if winner_count > 0:
                per_winner = tier_pool / winner_count
                prize_amounts[tier.value] = per_winner
                
                # Update ticket prize amounts
                for ticket_id in winners_by_tier[tier.value]:
                    self.tickets[ticket_id].prize_amount = per_winner
            else:
                # No winners - rollover to next draw (conceptually)
                prize_amounts[tier.value] = 0
        
        # Distribute prizes if token system available
        if self.token_system:
            for tier in LotteryTier:
                for ticket_id in winners_by_tier[tier.value]:
                    ticket = self.tickets[ticket_id]
                    if ticket.prize_amount > 0:
                        prize_units = int(ticket.prize_amount * self.token_system.UNITS_PER_NXT)
                        self.token_system.transfer_atomic(
                            from_address="LOTTERY_POOL",
                            to_address=ticket.owner,
                            amount=prize_units,
                            fee=0,
                            reason=f"Lottery prize: {tier.value}"
                        )
            
            # Return portion to F_floor
            f_floor_units = int(f_floor_amount * self.token_system.UNITS_PER_NXT)
            self.token_system.transfer_atomic(
                from_address="LOTTERY_POOL",
                to_address="F_FLOOR_POOL",
                amount=f_floor_units,
                fee=0,
                reason="Lottery sustainability return to F_floor"
            )
        
        draw.status = "completed"
        
        # Create new draw for next round
        self._create_new_draw()
        
        results = {
            "draw_id": draw.draw_id,
            "winning_numbers": draw.winning_numbers,
            "total_pool": draw.total_pool,
            "tickets_sold": draw.tickets_sold,
            "winners_by_tier": {tier: len(winners) for tier, winners in winners_by_tier.items()},
            "prize_amounts": prize_amounts,
            "f_floor_return": f_floor_amount,
            "quantum_seed": draw.quantum_seed[:16] + "..."  # Partial for privacy
        }
        
        return True, results, f"Draw completed! Winning numbers: {draw.winning_numbers}"
    
    def get_current_draw_info(self) -> Dict[str, Any]:
        """Get information about current active draw"""
        if not self.current_draw:
            return {"status": "no_active_draw"}
        
        draw = self.current_draw
        time_remaining = max(0, draw.scheduled_time - time.time())
        
        return {
            "draw_id": draw.draw_id,
            "status": draw.status,
            "total_pool": draw.total_pool,
            "tickets_sold": draw.tickets_sold,
            "time_remaining_seconds": time_remaining,
            "ticket_price": self.TICKET_PRICE_NXT,
            "prize_distribution": {t.value: p for t, p in self.PRIZE_DISTRIBUTION.items()}
        }
    
    def get_user_tickets(self, user: str) -> List[Dict]:
        """Get all tickets owned by a user"""
        user_tickets = []
        for ticket in self.tickets.values():
            if ticket.owner == user:
                user_tickets.append(ticket.to_dict())
        return user_tickets
    
    def get_draw_history(self, limit: int = 10) -> List[Dict]:
        """Get recent draw history"""
        history = []
        for draw_id in reversed(self.draw_history[-limit:]):
            draw = self.draws.get(draw_id)
            if draw and draw.status == "completed":
                history.append(draw.to_dict())
        return history


# Global lottery instance
_lottery_engine: Optional[QuantumLotteryEngine] = None


def get_lottery_engine(token_system=None) -> QuantumLotteryEngine:
    """Get or create global lottery engine"""
    global _lottery_engine
    if _lottery_engine is None:
        _lottery_engine = QuantumLotteryEngine(token_system)
    return _lottery_engine
