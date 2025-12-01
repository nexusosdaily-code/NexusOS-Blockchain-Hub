"""
Physics Economics Adapter - Unified Substrate Layer Compliance
==============================================================

This adapter ensures ALL economic modules comply with NexusOS substrate:
- E=hf energy pricing (Planck's equation)
- Λ=hf/c² Lambda Boson mass-equivalence
- Orbital transition burns → TransitionReserveLedger
- BHLS floor allocation integration
- SDK fee routing to founder wallet

Every NXT transaction flows through this adapter for physics compliance.
"""

import time
from typing import Dict, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

PLANCK_CONSTANT = 6.62607015e-34
SPEED_OF_LIGHT = 2.99792458e8
SDK_WALLET = "NXS5372697543A0FEF822E453DBC26FA044D14599E9"
SDK_FEE_RATE = 0.005


class EconomicModule(Enum):
    """Economic modules requiring physics integration"""
    MESSAGING = "messaging"
    VIDEO = "video"
    DEX = "dex"
    VALIDATOR = "validator"
    GOVERNANCE = "governance"
    FARMING = "farming"
    LOTTERY = "lottery"
    SERVICE_POOLS = "service_pools"
    SUPPLY_CHAIN = "supply_chain"
    EMERGENCY = "emergency"
    RESERVE = "reserve"
    INTERVENTION = "intervention"
    WALLET = "wallet"
    MEDIA = "media"


class CrisisLevel(Enum):
    """Crisis severity levels for emergency liquidity coordination"""
    NORMAL = "normal"          # No crisis - standard operations
    ELEVATED = "elevated"      # Early warning - monitor closely
    WARNING = "warning"        # Active concern - prepare reserves
    CRITICAL = "critical"      # Immediate action required
    EMERGENCY = "emergency"    # System-wide emergency response


@dataclass
class LiquidityLock:
    """Lock on reserve funds during crisis coordination"""
    lock_id: str
    reserve_pool: str
    amount_locked_nxt: float
    crisis_level: CrisisLevel
    locked_at: float
    expires_at: float
    purpose: str
    released: bool = False
    release_recipient: Optional[str] = None


@dataclass
class PhysicsEnergyResult:
    """Result from E=hf energy calculation"""
    energy_joules: float
    energy_nxt: float
    lambda_boson_kg: float
    frequency_hz: float
    wavelength_nm: float
    sdk_fee_nxt: float
    net_to_reserve_nxt: float
    physics_formula: str


@dataclass
class SubstrateTransaction:
    """Transaction routed through substrate layer"""
    tx_id: str
    timestamp: float
    module: EconomicModule
    sender: str
    amount_nxt: float
    energy_joules: float
    lambda_boson_kg: float
    burned_to_reserve: float
    sdk_fee_routed: float
    bhls_category: Optional[str]
    bhls_deducted: float
    success: bool
    message: str
    recipient: Optional[str] = None
    net_payout_nxt: float = 0.0
    settlement_success: bool = False


class PhysicsEconomicsAdapter:
    """
    Unified adapter for physics-based economics across all NexusOS modules.
    
    Ensures substrate compliance:
    1. E=hf energy calculation for all transactions
    2. Λ=hf/c² Lambda Boson mass tracking
    3. Orbital burns routed to TransitionReserveLedger
    4. BHLS allocations checked and deducted
    5. SDK fees routed to founder wallet
    
    Now integrated with WNSP v7.1 Substrate Coordinator and Consciousness Network.
    All layers above the substrate are governed by the substrate.
    """
    
    def __init__(self):
        self._token_system = None
        self._flow_controller = None
        self._bhls_system = None
        self._ledger = None
        self._substrate_coordinator = None
        self._consciousness_network = None
        self.transactions: list = []
        self.total_energy_processed_joules = 0.0
        self.total_lambda_mass_kg = 0.0
        self.total_sdk_fees_nxt = 0.0
        
        self.liquidity_locks: Dict[str, LiquidityLock] = {}
        self.current_crisis_level = CrisisLevel.NORMAL
        self.emergency_interventions: list = []
        self.total_emergency_liquidity_deployed_nxt = 0.0
    
    def _init_substrate(self):
        """Initialize connection to WNSP v7 Substrate Coordinator."""
        if self._substrate_coordinator is None:
            try:
                from wnsp_v7 import get_substrate_coordinator, get_consciousness_network
                self._substrate_coordinator = get_substrate_coordinator()
                self._consciousness_network = get_consciousness_network()
            except ImportError:
                pass
    
    def get_substrate_coordinator(self):
        """Get the unified substrate coordinator for direct access."""
        self._init_substrate()
        return self._substrate_coordinator
    
    def get_consciousness_network(self):
        """Get the consciousness network for node awareness tracking."""
        self._init_substrate()
        return self._consciousness_network
    
    def validate_via_substrate(
        self,
        sender: str,
        recipient: str,
        amount_nxt: float,
        module: EconomicModule,
        frequency_hz: float = 5e14
    ) -> Tuple[bool, str, Any]:
        """
        Validate a transaction via the unified substrate.
        
        All module operations should call this for Lambda mass conservation.
        """
        self._init_substrate()
        if not self._substrate_coordinator:
            return True, "Substrate not available, proceeding", None
        
        from wnsp_v7 import SubstrateTransaction as V7Transaction, OperationType
        
        op_map = {
            EconomicModule.MESSAGING: OperationType.MESSAGE_SEND,
            EconomicModule.VIDEO: OperationType.MEDIA_STREAM,
            EconomicModule.MEDIA: OperationType.MEDIA_STREAM,
            EconomicModule.DEX: OperationType.DEX_SWAP,
            EconomicModule.GOVERNANCE: OperationType.GOVERNANCE_VOTE,
            EconomicModule.WALLET: OperationType.WALLET_TRANSFER,
        }
        op_type = op_map.get(module, OperationType.MESSAGE_SEND)
        
        energy = PLANCK_CONSTANT * frequency_hz * amount_nxt
        lambda_in = energy / (SPEED_OF_LIGHT ** 2)
        fee_rate = 0.001
        lambda_fee = lambda_in * fee_rate
        lambda_out = lambda_in - lambda_fee
        
        tx = V7Transaction(
            operation_type=op_type,
            source_node=sender,
            target_node=recipient,
            nxt_amount=amount_nxt,
            frequency_hz=frequency_hz,
            energy_joules=energy,
            lambda_mass_in=lambda_in,
            lambda_mass_out=lambda_out,
            lambda_mass_fee=lambda_fee
        )
        
        valid, reason = self._substrate_coordinator.validate_transaction(tx)
        return valid, reason, tx
        
    def _lazy_init(self):
        """Lazy initialization of dependent systems"""
        if self._token_system is None:
            try:
                from native_token import NativeTokenSystem
                self._token_system = NativeTokenSystem()
                
                for acc_name in ["TRANSITION_RESERVE", SDK_WALLET, "DEX_FEES", "VALIDATOR_POOL"]:
                    if self._token_system.get_account(acc_name) is None:
                        self._token_system.create_account(acc_name, initial_balance=0)
            except Exception as e:
                print(f"Could not initialize token system: {e}")
                
        if self._flow_controller is None:
            try:
                from economic_loop_controller import (
                    MessagingFlowController,
                    TransitionReserveLedger,
                    get_transition_ledger
                )
                self._ledger = get_transition_ledger()
                if self._token_system:
                    self._flow_controller = MessagingFlowController(
                        self._token_system, self._ledger
                    )
            except Exception as e:
                print(f"Could not initialize flow controller: {e}")
                
        if self._bhls_system is None:
            try:
                from bhls_floor_system import BHLSFloorSystem
                self._bhls_system = BHLSFloorSystem()
            except Exception as e:
                print(f"Could not initialize BHLS system: {e}")
    
    def calculate_energy(
        self,
        wavelength_nm: float = 550.0,
        amount_nxt: float = 0.0,
        duration_seconds: float = 1.0
    ) -> PhysicsEnergyResult:
        """
        Calculate physics-based energy using E=hf and Λ=hf/c².
        
        Args:
            wavelength_nm: Wavelength in nanometers (default visible light)
            amount_nxt: Transaction amount in NXT
            duration_seconds: Duration for time-based services
            
        Returns:
            PhysicsEnergyResult with full energy breakdown
        """
        wavelength_m = wavelength_nm * 1e-9
        frequency_hz = SPEED_OF_LIGHT / wavelength_m
        
        energy_joules = PLANCK_CONSTANT * frequency_hz * duration_seconds
        lambda_boson_kg = PLANCK_CONSTANT * frequency_hz / (SPEED_OF_LIGHT ** 2)
        
        ENERGY_TO_NXT_SCALE = 1e21
        energy_nxt = max(amount_nxt, energy_joules * ENERGY_TO_NXT_SCALE / 1e6)
        
        sdk_fee_nxt = energy_nxt * SDK_FEE_RATE
        net_to_reserve = energy_nxt - sdk_fee_nxt
        
        return PhysicsEnergyResult(
            energy_joules=energy_joules,
            energy_nxt=energy_nxt,
            lambda_boson_kg=lambda_boson_kg,
            frequency_hz=frequency_hz,
            wavelength_nm=wavelength_nm,
            sdk_fee_nxt=sdk_fee_nxt,
            net_to_reserve_nxt=net_to_reserve,
            physics_formula=f"E = hf = {PLANCK_CONSTANT:.2e} × {frequency_hz:.2e} = {energy_joules:.2e} J; Λ = hf/c² = {lambda_boson_kg:.2e} kg"
        )
    
    def get_bhls_allocation(
        self,
        wallet_address: str,
        category: str
    ) -> Dict[str, Any]:
        """
        Get BHLS allocation for a category.
        
        Args:
            wallet_address: User's wallet address
            category: BHLS category (CONNECTIVITY, FOOD, ENERGY, etc.)
            
        Returns:
            Dict with allocation details
        """
        self._lazy_init()
        
        BHLS_DEFAULTS = {
            "CONNECTIVITY": 75.0,
            "FOOD": 250.0,
            "WATER": 50.0,
            "HOUSING": 400.0,
            "ENERGY": 150.0,
            "HEALTHCARE": 200.0,
            "RECYCLING": 25.0
        }
        
        monthly_allocation = BHLS_DEFAULTS.get(category.upper(), 0.0)
        used = 0.0
        
        if self._bhls_system:
            for cid, citizen in self._bhls_system.citizens.items():
                if citizen.wallet_address == wallet_address:
                    from bhls_floor_system import BHLSCategory
                    try:
                        cat_enum = BHLSCategory[category.upper()]
                        if cat_enum in citizen.bhls_allocations:
                            alloc = citizen.bhls_allocations[cat_enum]
                            monthly_allocation = alloc.monthly_allocation
                            used = alloc.usage_current_month
                    except (KeyError, AttributeError):
                        pass
                    break
        
        return {
            "category": category.upper(),
            "monthly_allocation_nxt": monthly_allocation,
            "used_nxt": used,
            "remaining_nxt": max(0, monthly_allocation - used),
            "wallet_address": wallet_address
        }
    
    def deduct_bhls(
        self,
        wallet_address: str,
        category: str,
        amount_nxt: float
    ) -> Tuple[bool, str]:
        """
        Deduct from BHLS allocation.
        
        Args:
            wallet_address: User's wallet address
            category: BHLS category
            amount_nxt: Amount to deduct
            
        Returns:
            (success, message)
        """
        self._lazy_init()
        
        allocation = self.get_bhls_allocation(wallet_address, category)
        
        if allocation["remaining_nxt"] < amount_nxt:
            return False, f"Insufficient BHLS {category}: {allocation['remaining_nxt']:.2f} remaining, need {amount_nxt:.2f}"
        
        if self._bhls_system:
            for cid, citizen in self._bhls_system.citizens.items():
                if citizen.wallet_address == wallet_address:
                    from bhls_floor_system import BHLSCategory
                    try:
                        cat_enum = BHLSCategory[category.upper()]
                        if cat_enum in citizen.bhls_allocations:
                            citizen.bhls_allocations[cat_enum].usage_current_month += amount_nxt
                            return True, f"Deducted {amount_nxt:.4f} NXT from BHLS {category}"
                    except (KeyError, AttributeError):
                        pass
                    break
        
        return True, f"BHLS {category} deduction recorded: {amount_nxt:.4f} NXT"
    
    def process_orbital_burn(
        self,
        sender_address: str,
        amount_nxt: float,
        wavelength_nm: float,
        module: EconomicModule,
        message_id: Optional[str] = None,
        bhls_category: Optional[str] = None
    ) -> SubstrateTransaction:
        """
        Process transaction through orbital transition burn.
        
        Complete flow:
        1. Calculate E=hf energy
        2. Check/deduct BHLS if applicable
        3. Execute orbital transition
        4. Route to TransitionReserveLedger
        5. Route SDK fee to founder wallet
        
        Args:
            sender_address: Wallet sending funds
            amount_nxt: Amount in NXT
            wavelength_nm: Wavelength for energy calculation
            module: Which economic module
            message_id: Optional transaction ID
            bhls_category: Optional BHLS category to deduct from
            
        Returns:
            SubstrateTransaction with full details
        """
        self._lazy_init()
        
        tx_id = f"SUBSTRATE_{module.value}_{int(time.time() * 1000)}"
        
        energy = self.calculate_energy(
            wavelength_nm=wavelength_nm,
            amount_nxt=amount_nxt
        )
        
        bhls_deducted = 0.0
        if bhls_category:
            success, msg = self.deduct_bhls(sender_address, bhls_category, amount_nxt)
            if success:
                bhls_deducted = amount_nxt
        
        orbital_success = False
        orbital_message = "Orbital transition pending"
        
        if self._flow_controller:
            try:
                success, msg, event = self._flow_controller.process_message_burn(
                    sender_address=sender_address,
                    message_id=message_id or tx_id,
                    burn_amount_nxt=energy.net_to_reserve_nxt,
                    wavelength_nm=wavelength_nm,
                    message_type=module.value
                )
                orbital_success = success
                orbital_message = msg
            except Exception as e:
                orbital_message = f"Orbital transition error: {e}"
        
        sdk_routed = self._route_sdk_fee(energy.sdk_fee_nxt, tx_id)
        
        self.total_energy_processed_joules += energy.energy_joules
        self.total_lambda_mass_kg += energy.lambda_boson_kg
        self.total_sdk_fees_nxt += energy.sdk_fee_nxt if sdk_routed else 0
        
        tx = SubstrateTransaction(
            tx_id=tx_id,
            timestamp=time.time(),
            module=module,
            sender=sender_address,
            amount_nxt=amount_nxt,
            energy_joules=energy.energy_joules,
            lambda_boson_kg=energy.lambda_boson_kg,
            burned_to_reserve=energy.net_to_reserve_nxt,
            sdk_fee_routed=energy.sdk_fee_nxt if sdk_routed else 0,
            bhls_category=bhls_category,
            bhls_deducted=bhls_deducted,
            success=orbital_success,
            message=orbital_message
        )
        
        self.transactions.append(tx)
        return tx
    
    def process_orbital_transfer(
        self,
        source_address: str,
        recipient_address: str,
        amount_nxt: float,
        wavelength_nm: float,
        module: EconomicModule,
        transfer_id: Optional[str] = None,
        bhls_category: Optional[str] = None
    ) -> SubstrateTransaction:
        """
        Process complete payout through physics substrate with settlement.
        
        Two-phase transfer:
        1. Burn phase: Track through substrate (E=hf, SDK fee, reserve)
        2. Settlement phase: Credit recipient only if burn succeeds
        
        Args:
            source_address: Pool/wallet sending funds
            recipient_address: Wallet receiving funds
            amount_nxt: Amount to transfer
            wavelength_nm: Wavelength for energy calculation
            module: Which economic module
            transfer_id: Optional transaction ID
            bhls_category: Optional BHLS category
            
        Returns:
            SubstrateTransaction with burn + settlement details
        """
        substrate_tx = self.process_orbital_burn(
            sender_address=source_address,
            amount_nxt=amount_nxt,
            wavelength_nm=wavelength_nm,
            module=module,
            message_id=transfer_id,
            bhls_category=bhls_category
        )
        
        substrate_tx.recipient = recipient_address
        
        if substrate_tx.success:
            net_payout = amount_nxt - substrate_tx.sdk_fee_routed
            substrate_tx.net_payout_nxt = net_payout
            
            if self._token_system:
                try:
                    payout_units = int(net_payout * self._token_system.UNITS_PER_NXT)
                    
                    if self._token_system.get_account(source_address) is None:
                        self._token_system.create_account(source_address, initial_balance=0)
                    if self._token_system.get_account(recipient_address) is None:
                        self._token_system.create_account(recipient_address, initial_balance=0)
                    
                    success, _, msg = self._token_system.transfer_atomic(
                        from_address=source_address,
                        to_address=recipient_address,
                        amount=payout_units,
                        fee=0,
                        reason=f"Substrate payout: {substrate_tx.tx_id}"
                    )
                    
                    substrate_tx.settlement_success = success
                    if success:
                        substrate_tx.message = f"{substrate_tx.message}; Settlement: {net_payout:.4f} NXT to {recipient_address[:12]}..."
                    else:
                        substrate_tx.message = f"{substrate_tx.message}; Settlement failed: {msg}"
                except Exception as e:
                    substrate_tx.settlement_success = False
                    substrate_tx.message = f"{substrate_tx.message}; Settlement error: {e}"
            else:
                substrate_tx.settlement_success = True
                substrate_tx.message = f"{substrate_tx.message}; Settlement recorded (no token system)"
        
        return substrate_tx
    
    def _route_sdk_fee(self, fee_nxt: float, tx_id: str) -> bool:
        """Route SDK fee to founder wallet"""
        if fee_nxt <= 0 or not self._token_system:
            return False
            
        try:
            if self._token_system.get_account("TRANSITION_RESERVE") is None:
                self._token_system.create_account("TRANSITION_RESERVE", initial_balance=0)
            if self._token_system.get_account(SDK_WALLET) is None:
                self._token_system.create_account(SDK_WALLET, initial_balance=0)
            
            fee_units = int(fee_nxt * self._token_system.UNITS_PER_NXT)
            
            reserve_account = self._token_system.get_account("TRANSITION_RESERVE")
            if reserve_account and hasattr(reserve_account, 'balance'):
                if reserve_account.balance >= fee_units:
                    success, tx, msg = self._token_system.transfer_atomic(
                        from_address="TRANSITION_RESERVE",
                        to_address=SDK_WALLET,
                        amount=fee_units,
                        fee=0,
                        reason=f"SDK fee: {tx_id}"
                    )
                    return success
            return False
        except Exception as e:
            print(f"SDK fee routing error: {e}")
            return False
    
    def set_crisis_level(self, level: CrisisLevel, reason: str) -> bool:
        """
        Update system-wide crisis level.
        
        Args:
            level: New crisis level
            reason: Justification for level change
            
        Returns:
            True if level changed
        """
        if level != self.current_crisis_level:
            previous_level = self.current_crisis_level
            self.current_crisis_level = level
            self.emergency_interventions.append({
                "type": "crisis_level_change",
                "from": previous_level.value,
                "to": level.value,
                "reason": reason,
                "timestamp": time.time()
            })
            return True
        return False
    
    def initiate_liquidity_lock(
        self,
        reserve_pool: str,
        amount_nxt: float,
        crisis_level: CrisisLevel,
        purpose: str,
        lock_duration_seconds: int = 3600
    ) -> Tuple[bool, Optional[LiquidityLock], str]:
        """
        Lock reserve funds for emergency coordination.
        
        Locks funds from reserve pool to prevent competing draws during crisis.
        Only releases to authorized recipient after settlement.
        
        Args:
            reserve_pool: Pool to lock from (VALIDATOR_POOL, TRANSITION_RESERVE, ECOSYSTEM_FUND)
            amount_nxt: Amount to lock
            crisis_level: Crisis severity
            purpose: Reason for lock
            lock_duration_seconds: How long to hold lock
            
        Returns:
            (success, lock_object, message)
        """
        self._lazy_init()
        
        lock_id = f"LOCK_{reserve_pool}_{int(time.time() * 1000)}"
        
        if self._token_system:
            pool_account = self._token_system.get_account(reserve_pool)
            if pool_account is None:
                return False, None, f"Reserve pool {reserve_pool} not found"
            
            pool_balance = pool_account.balance / self._token_system.UNITS_PER_NXT
            if pool_balance < amount_nxt:
                return False, None, f"Insufficient reserves: {pool_balance:.2f} NXT available, need {amount_nxt:.2f}"
        
        active_locks_amount = sum(
            lock.amount_locked_nxt 
            for lock in self.liquidity_locks.values() 
            if lock.reserve_pool == reserve_pool and not lock.released
        )
        
        if self._token_system:
            pool_account = self._token_system.get_account(reserve_pool)
            if pool_account:
                available = pool_account.balance / self._token_system.UNITS_PER_NXT - active_locks_amount
                if available < amount_nxt:
                    return False, None, f"Insufficient unlocked reserves: {available:.2f} NXT available after existing locks"
        
        lock = LiquidityLock(
            lock_id=lock_id,
            reserve_pool=reserve_pool,
            amount_locked_nxt=amount_nxt,
            crisis_level=crisis_level,
            locked_at=time.time(),
            expires_at=time.time() + lock_duration_seconds,
            purpose=purpose
        )
        
        self.liquidity_locks[lock_id] = lock
        
        return True, lock, f"Locked {amount_nxt:.2f} NXT from {reserve_pool} for {purpose}"
    
    def release_liquidity_lock(
        self,
        lock_id: str,
        recipient_address: str,
        wavelength_nm: float = 550.0
    ) -> SubstrateTransaction:
        """
        Release locked funds to authorized recipient through substrate.
        
        Args:
            lock_id: Lock to release
            recipient_address: Who receives the funds
            wavelength_nm: Wavelength for energy calculation
            
        Returns:
            SubstrateTransaction with settlement details
        """
        if lock_id not in self.liquidity_locks:
            return SubstrateTransaction(
                tx_id=f"RELEASE_FAILED_{lock_id}",
                timestamp=time.time(),
                module=EconomicModule.EMERGENCY,
                sender="SYSTEM",
                amount_nxt=0,
                energy_joules=0,
                lambda_boson_kg=0,
                burned_to_reserve=0,
                sdk_fee_routed=0,
                bhls_category=None,
                bhls_deducted=0,
                success=False,
                message=f"Lock {lock_id} not found"
            )
        
        lock = self.liquidity_locks[lock_id]
        
        if lock.released:
            return SubstrateTransaction(
                tx_id=f"RELEASE_FAILED_{lock_id}",
                timestamp=time.time(),
                module=EconomicModule.EMERGENCY,
                sender=lock.reserve_pool,
                amount_nxt=lock.amount_locked_nxt,
                energy_joules=0,
                lambda_boson_kg=0,
                burned_to_reserve=0,
                sdk_fee_routed=0,
                bhls_category=None,
                bhls_deducted=0,
                success=False,
                message=f"Lock {lock_id} already released"
            )
        
        substrate_tx = self.process_orbital_transfer(
            source_address=lock.reserve_pool,
            recipient_address=recipient_address,
            amount_nxt=lock.amount_locked_nxt,
            wavelength_nm=wavelength_nm,
            module=EconomicModule.EMERGENCY,
            transfer_id=f"EMERGENCY_RELEASE_{lock_id}"
        )
        
        if substrate_tx.settlement_success:
            lock.released = True
            lock.release_recipient = recipient_address
            self.total_emergency_liquidity_deployed_nxt += lock.amount_locked_nxt
        
        return substrate_tx
    
    def process_emergency_liquidity(
        self,
        source_pool: str,
        recipient_address: str,
        amount_nxt: float,
        crisis_level: CrisisLevel,
        reason: str,
        wavelength_nm: float = 380.0
    ) -> SubstrateTransaction:
        """
        Atomic emergency liquidity deployment through substrate.
        
        Combines lock + release for immediate emergency response.
        Uses UV wavelength (380nm) for high-energy emergency transactions.
        
        Args:
            source_pool: Reserve pool to draw from
            recipient_address: Emergency responder/beneficiary
            amount_nxt: Amount to deploy
            crisis_level: Crisis severity (affects validation)
            reason: Justification for emergency draw
            wavelength_nm: Wavelength (default UV for emergency)
            
        Returns:
            SubstrateTransaction with full details
        """
        lock_success, lock, lock_msg = self.initiate_liquidity_lock(
            reserve_pool=source_pool,
            amount_nxt=amount_nxt,
            crisis_level=crisis_level,
            purpose=reason,
            lock_duration_seconds=60
        )
        
        if not lock_success:
            return SubstrateTransaction(
                tx_id=f"EMERGENCY_FAILED_{int(time.time() * 1000)}",
                timestamp=time.time(),
                module=EconomicModule.EMERGENCY,
                sender=source_pool,
                amount_nxt=amount_nxt,
                energy_joules=0,
                lambda_boson_kg=0,
                burned_to_reserve=0,
                sdk_fee_routed=0,
                bhls_category=None,
                bhls_deducted=0,
                success=False,
                message=f"Emergency liquidity lock failed: {lock_msg}"
            )
        
        substrate_tx = self.release_liquidity_lock(
            lock_id=lock.lock_id,
            recipient_address=recipient_address,
            wavelength_nm=wavelength_nm
        )
        
        self.emergency_interventions.append({
            "type": "emergency_liquidity",
            "lock_id": lock.lock_id,
            "source": source_pool,
            "recipient": recipient_address,
            "amount_nxt": amount_nxt,
            "crisis_level": crisis_level.value,
            "reason": reason,
            "success": substrate_tx.settlement_success,
            "timestamp": time.time()
        })
        
        return substrate_tx
    
    def process_supply_chain_payment(
        self,
        payer_address: str,
        supplier_address: str,
        amount_nxt: float,
        resource_type: str,
        wavelength_nm: float = 550.0
    ) -> SubstrateTransaction:
        """
        Process supply chain payment through physics substrate.
        
        Routes supplier payments through E=hf pricing with SDK fees.
        
        Args:
            payer_address: Who is paying
            supplier_address: Resource supplier
            amount_nxt: Payment amount
            resource_type: Type of resource (FOOD, ENERGY, etc.)
            wavelength_nm: Wavelength for energy calculation
            
        Returns:
            SubstrateTransaction with details
        """
        bhls_category = None
        if resource_type.upper() in ["FOOD", "WATER", "ENERGY", "HEALTHCARE"]:
            bhls_category = resource_type.upper()
        
        return self.process_orbital_transfer(
            source_address=payer_address,
            recipient_address=supplier_address,
            amount_nxt=amount_nxt,
            wavelength_nm=wavelength_nm,
            module=EconomicModule.SUPPLY_CHAIN,
            transfer_id=f"SUPPLY_{resource_type}_{int(time.time() * 1000)}",
            bhls_category=bhls_category
        )
    
    def process_reserve_draw(
        self,
        reserve_pool: str,
        recipient_address: str,
        amount_nxt: float,
        purpose: str,
        wavelength_nm: float = 550.0
    ) -> SubstrateTransaction:
        """
        Draw from reserve pool through physics substrate.
        
        All reserve draws must route through substrate for tracking.
        
        Args:
            reserve_pool: Pool to draw from
            recipient_address: Recipient of funds
            amount_nxt: Amount to draw
            purpose: Reason for draw
            wavelength_nm: Wavelength for energy calculation
            
        Returns:
            SubstrateTransaction with details
        """
        return self.process_orbital_transfer(
            source_address=reserve_pool,
            recipient_address=recipient_address,
            amount_nxt=amount_nxt,
            wavelength_nm=wavelength_nm,
            module=EconomicModule.RESERVE,
            transfer_id=f"RESERVE_DRAW_{int(time.time() * 1000)}"
        )
    
    def get_crisis_status(self) -> Dict[str, Any]:
        """Get current crisis coordination status"""
        active_locks = [
            {
                "lock_id": lock.lock_id,
                "reserve_pool": lock.reserve_pool,
                "amount_nxt": lock.amount_locked_nxt,
                "crisis_level": lock.crisis_level.value,
                "purpose": lock.purpose,
                "expires_in_seconds": max(0, lock.expires_at - time.time())
            }
            for lock in self.liquidity_locks.values()
            if not lock.released
        ]
        
        return {
            "current_crisis_level": self.current_crisis_level.value,
            "active_liquidity_locks": len(active_locks),
            "total_locked_nxt": sum(l["amount_nxt"] for l in active_locks),
            "locks": active_locks,
            "total_emergency_deployed_nxt": self.total_emergency_liquidity_deployed_nxt,
            "recent_interventions": self.emergency_interventions[-10:]
        }
    
    def get_substrate_summary(self) -> Dict[str, Any]:
        """Get summary of substrate layer activity"""
        module_stats = {}
        for module in EconomicModule:
            module_txs = [t for t in self.transactions if t.module == module]
            module_stats[module.value] = {
                "transaction_count": len(module_txs),
                "total_nxt": sum(t.amount_nxt for t in module_txs),
                "total_energy_joules": sum(t.energy_joules for t in module_txs)
            }
        
        crisis_status = self.get_crisis_status()
        
        return {
            "total_transactions": len(self.transactions),
            "total_energy_processed_joules": self.total_energy_processed_joules,
            "total_lambda_mass_kg": self.total_lambda_mass_kg,
            "total_sdk_fees_nxt": self.total_sdk_fees_nxt,
            "sdk_wallet": SDK_WALLET,
            "module_breakdown": module_stats,
            "crisis_coordination": crisis_status,
            "physics_formulas": {
                "energy": "E = h × f (Planck 1900)",
                "lambda_boson": "Λ = hf/c² (Lambda Boson 2024)",
                "planck_constant": PLANCK_CONSTANT,
                "speed_of_light": SPEED_OF_LIGHT
            }
        }


_adapter_instance = None


def get_physics_adapter() -> PhysicsEconomicsAdapter:
    """Get singleton physics economics adapter"""
    global _adapter_instance
    if _adapter_instance is None:
        _adapter_instance = PhysicsEconomicsAdapter()
    return _adapter_instance
