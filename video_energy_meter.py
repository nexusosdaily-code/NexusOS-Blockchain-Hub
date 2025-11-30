"""
NexusOS Video Energy Meter - Deep Economic Integration
========================================================

Physics-based pricing for video/livestreaming using Lambda Boson substrate.
Fully integrated with economic_loop_controller, bhls_floor_system, and messaging_payment_adapter.

Video = photon streams at specific frequencies
- Frame rate × spectral bandwidth = oscillation frequency (f)
- Energy cost: E = hf × duration × quality_factor
- Lambda Boson: Λ = hf/c² (mass-equivalent of oscillation)

Integration Flow:
1. Video session starts → BHLSFloorSystem allocates from CONNECTIVITY budget
2. Metered energy → MessagingFlowController.process_message_burn → TransitionReserveLedger
3. Settlement → WalletPaymentAdapter.commit → NativeTokenSystem transfer
4. SDK fees → route to founder wallet
5. Escrow → persist to database when wallet not linked
"""

import time
import uuid
from typing import Dict, Optional, Tuple, Any, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

PLANCK_CONSTANT = 6.62607015e-34
SPEED_OF_LIGHT = 299_792_458
JOULES_PER_NXT = 1e-18
SDK_WALLET = "NXS5372697543A0FEF822E453DBC26FA044D14599E9"
SDK_FEE_PERCENT = 0.02


class VideoQuality(Enum):
    """Video quality tiers mapped to spectral frequencies"""
    AUDIO_ONLY = ("Audio Only", 16_000, 0.1, 300)
    LOW_240P = ("240p", 240 * 320 * 15, 0.3, 450)
    MEDIUM_480P = ("480p", 480 * 640 * 24, 0.5, 550)
    HD_720P = ("720p", 720 * 1280 * 30, 0.7, 600)
    FHD_1080P = ("1080p", 1080 * 1920 * 30, 1.0, 650)
    UHD_4K = ("4K", 2160 * 3840 * 60, 2.5, 700)
    
    def __init__(self, display_name: str, base_frequency: float, quality_factor: float, wavelength_nm: float):
        self.display_name = display_name
        self.base_frequency = base_frequency
        self.quality_factor = quality_factor
        self.wavelength_nm = wavelength_nm


class StreamType(Enum):
    """Types of video streams with different energy profiles"""
    VIDEO_CALL = ("Video Call", 1.0, "P2P bidirectional", "video")
    LIVESTREAM = ("Livestream", 1.5, "One-to-many broadcast", "video")
    CONFERENCE = ("Conference", 2.0, "Multi-party mesh", "video")
    SCREEN_SHARE = ("Screen Share", 0.8, "Lower frame rate", "image")
    
    def __init__(self, display_name: str, multiplier: float, description: str, message_type: str):
        self.display_name = display_name
        self.multiplier = multiplier
        self.description = description
        self.message_type = message_type


@dataclass
class VideoSessionCost:
    """Cost calculation for a video session"""
    session_id: str
    wallet_address: Optional[str]
    stream_type: StreamType
    quality: VideoQuality
    duration_seconds: float
    frequency_hz: float
    energy_joules: float
    energy_nxt: float
    lambda_boson_kg: float
    sdk_fee_nxt: float
    bhls_covered_nxt: float
    overflow_charged_nxt: float
    transition_entry_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    is_escrowed: bool = False
    
    def to_dict(self) -> Dict:
        return {
            'session_id': self.session_id,
            'wallet_address': self.wallet_address,
            'stream_type': self.stream_type.display_name,
            'quality': self.quality.display_name,
            'duration_seconds': self.duration_seconds,
            'frequency_hz': self.frequency_hz,
            'energy_joules': self.energy_joules,
            'energy_nxt': self.energy_nxt,
            'lambda_boson_kg': self.lambda_boson_kg,
            'sdk_fee_nxt': self.sdk_fee_nxt,
            'bhls_covered_nxt': self.bhls_covered_nxt,
            'overflow_charged_nxt': self.overflow_charged_nxt,
            'transition_entry_id': self.transition_entry_id,
            'is_escrowed': self.is_escrowed,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class VideoEscrowEntry:
    """Escrowed video charges when wallet not linked - persisted to database"""
    escrow_id: str
    session_id: str
    user_identity: str
    energy_nxt: float
    sdk_fee_nxt: float
    created_at: datetime
    resolved: bool = False
    resolved_wallet: Optional[str] = None
    resolved_at: Optional[datetime] = None
    transition_entry_id: Optional[str] = None


class VideoEnergyMeter:
    """
    Physics-based energy metering for video streams with DEEP economic integration.
    
    Calculates costs using E = hf formula where:
    - h = Planck constant (6.626×10⁻³⁴ J·s)
    - f = effective frequency (frame_rate × resolution × quality_factor)
    
    Lambda Boson mass-equivalent: Λ = hf/c²
    
    INTEGRATION POINTS:
    - BHLSFloorSystem: Uses CONNECTIVITY allocation for video
    - MessagingFlowController: Records burns to TransitionReserveLedger
    - WalletPaymentAdapter: Handles settlement and rollback
    - NativeTokenSystem: Routes SDK fees to founder wallet
    """
    
    def __init__(self):
        self.active_sessions: Dict[str, Dict] = {}
        self.completed_sessions: List[VideoSessionCost] = []
        self.escrow_pool: Dict[str, VideoEscrowEntry] = {}
        self.total_energy_consumed_joules = 0.0
        self.total_energy_consumed_nxt = 0.0
        self.sdk_fees_collected_nxt = 0.0
        
        self._bhls_system = None
        self._flow_controller = None
        self._token_system = None
        self._payment_adapter = None
    
    def _get_bhls_system(self):
        """Lazy-load BHLS Floor System"""
        if self._bhls_system is None:
            try:
                from bhls_floor_system import BHLSFloorSystem
                self._bhls_system = BHLSFloorSystem()
            except ImportError:
                pass
        return self._bhls_system
    
    def _get_flow_controller(self):
        """Lazy-load Messaging Flow Controller with proper initialization"""
        if self._flow_controller is None:
            try:
                from economic_loop_controller import (
                    MessagingFlowController, 
                    TransitionReserveLedger,
                    get_transition_ledger
                )
                token_system = self._get_token_system()
                if token_system:
                    ledger = get_transition_ledger()
                    self._flow_controller = MessagingFlowController(token_system, ledger)
                    
                    if token_system.get_account("TRANSITION_RESERVE") is None:
                        token_system.create_account("TRANSITION_RESERVE", initial_balance=0)
                    if token_system.get_account(SDK_WALLET) is None:
                        token_system.create_account(SDK_WALLET, initial_balance=0)
            except Exception as e:
                print(f"Could not initialize flow controller: {e}")
        return self._flow_controller
    
    def _get_token_system(self):
        """Lazy-load Native Token System with account initialization"""
        if self._token_system is None:
            try:
                from native_token import NativeTokenSystem
                self._token_system = NativeTokenSystem()
                
                if self._token_system.get_account("TRANSITION_RESERVE") is None:
                    self._token_system.create_account("TRANSITION_RESERVE", initial_balance=0)
                if self._token_system.get_account(SDK_WALLET) is None:
                    self._token_system.create_account(SDK_WALLET, initial_balance=0)
            except Exception as e:
                print(f"Could not initialize token system: {e}")
        return self._token_system
    
    def _ensure_user_account(self, wallet_address: str):
        """Ensure user account exists in token system"""
        if not wallet_address:
            return False
        token_system = self._get_token_system()
        if token_system:
            try:
                if token_system.get_account(wallet_address) is None:
                    token_system.create_account(wallet_address, initial_balance=0)
                return True
            except Exception:
                pass
        return False
    
    def _get_db_session(self):
        """Get database session for escrow persistence"""
        try:
            from database import get_session
            return get_session()
        except Exception:
            return None
    
    def _ensure_escrow_table(self):
        """Create escrow table if it doesn't exist"""
        session = self._get_db_session()
        if session:
            try:
                from sqlalchemy import text
                session.execute(text("""
                    CREATE TABLE IF NOT EXISTS video_escrow (
                        escrow_id VARCHAR(64) PRIMARY KEY,
                        session_id VARCHAR(64) NOT NULL,
                        user_identity VARCHAR(256) NOT NULL,
                        energy_nxt DECIMAL(20, 8) NOT NULL,
                        sdk_fee_nxt DECIMAL(20, 8) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        resolved BOOLEAN DEFAULT FALSE,
                        resolved_wallet VARCHAR(128),
                        resolved_at TIMESTAMP,
                        transition_entry_id VARCHAR(64)
                    )
                """))
                session.commit()
                session.close()
                return True
            except Exception as e:
                session.close()
                print(f"Could not create escrow table: {e}")
        return False
    
    def _persist_escrow(self, escrow: VideoEscrowEntry) -> bool:
        """Persist escrow entry to database"""
        session = self._get_db_session()
        if session:
            try:
                self._ensure_escrow_table()
                from sqlalchemy import text
                session.execute(text("""
                    INSERT INTO video_escrow 
                    (escrow_id, session_id, user_identity, energy_nxt, sdk_fee_nxt, created_at, transition_entry_id)
                    VALUES (:escrow_id, :session_id, :user_identity, :energy_nxt, :sdk_fee_nxt, :created_at, :transition_entry_id)
                    ON CONFLICT (escrow_id) DO UPDATE SET
                        energy_nxt = EXCLUDED.energy_nxt,
                        sdk_fee_nxt = EXCLUDED.sdk_fee_nxt
                """), {
                    'escrow_id': escrow.escrow_id,
                    'session_id': escrow.session_id,
                    'user_identity': escrow.user_identity,
                    'energy_nxt': escrow.energy_nxt,
                    'sdk_fee_nxt': escrow.sdk_fee_nxt,
                    'created_at': escrow.created_at,
                    'transition_entry_id': escrow.transition_entry_id
                })
                session.commit()
                session.close()
                return True
            except Exception as e:
                session.close()
                print(f"Could not persist escrow: {e}")
        self.escrow_pool[escrow.escrow_id] = escrow
        return False
    
    def _load_user_escrows(self, user_identity: str) -> List[VideoEscrowEntry]:
        """Load unresolved escrow entries for user from database"""
        escrows = []
        session = self._get_db_session()
        if session:
            try:
                from sqlalchemy import text
                result = session.execute(text("""
                    SELECT escrow_id, session_id, user_identity, energy_nxt, sdk_fee_nxt, 
                           created_at, resolved, resolved_wallet, resolved_at, transition_entry_id
                    FROM video_escrow
                    WHERE user_identity = :user_identity AND resolved = FALSE
                """), {'user_identity': user_identity})
                for row in result.fetchall():
                    escrows.append(VideoEscrowEntry(
                        escrow_id=row[0],
                        session_id=row[1],
                        user_identity=row[2],
                        energy_nxt=float(row[3]),
                        sdk_fee_nxt=float(row[4]),
                        created_at=row[5],
                        resolved=row[6],
                        resolved_wallet=row[7],
                        resolved_at=row[8],
                        transition_entry_id=row[9]
                    ))
                session.close()
            except Exception as e:
                session.close()
                print(f"Could not load escrows: {e}")
        
        for eid, e in self.escrow_pool.items():
            if e.user_identity == user_identity and not e.resolved:
                if not any(x.escrow_id == eid for x in escrows):
                    escrows.append(e)
        
        return escrows
    
    def _resolve_escrow_in_db(self, escrow_id: str, wallet_address: str) -> bool:
        """Mark escrow as resolved in database"""
        session = self._get_db_session()
        if session:
            try:
                from sqlalchemy import text
                session.execute(text("""
                    UPDATE video_escrow
                    SET resolved = TRUE, resolved_wallet = :wallet_address, resolved_at = :resolved_at
                    WHERE escrow_id = :escrow_id
                """), {
                    'wallet_address': wallet_address,
                    'resolved_at': datetime.now(),
                    'escrow_id': escrow_id
                })
                session.commit()
                session.close()
                return True
            except Exception as e:
                session.close()
                print(f"Could not resolve escrow in DB: {e}")
        
        if escrow_id in self.escrow_pool:
            self.escrow_pool[escrow_id].resolved = True
            self.escrow_pool[escrow_id].resolved_wallet = wallet_address
            self.escrow_pool[escrow_id].resolved_at = datetime.now()
        return False
    
    def calculate_frequency(
        self,
        quality: VideoQuality,
        stream_type: StreamType
    ) -> float:
        """
        Calculate effective oscillation frequency for video stream.
        
        f_effective = base_frequency × quality_factor × stream_multiplier
        
        Returns frequency in Hz.
        """
        return quality.base_frequency * quality.quality_factor * stream_type.multiplier
    
    def calculate_energy_cost(
        self,
        quality: VideoQuality,
        stream_type: StreamType,
        duration_seconds: float
    ) -> Tuple[float, float, float]:
        """
        Calculate energy cost using E = hf × duration.
        
        Returns:
            Tuple of (energy_joules, energy_nxt, lambda_boson_kg)
        """
        frequency = self.calculate_frequency(quality, stream_type)
        energy_joules = PLANCK_CONSTANT * frequency * duration_seconds
        energy_nxt = energy_joules / JOULES_PER_NXT
        lambda_boson_kg = energy_joules / (SPEED_OF_LIGHT ** 2)
        
        return energy_joules, energy_nxt, lambda_boson_kg
    
    def validate_wallet_session(
        self,
        wallet_address: Optional[str],
        user_identity: str
    ) -> Tuple[bool, str]:
        """
        Validate wallet is properly linked for video session.
        
        Returns:
            Tuple of (is_valid, status_message)
        """
        if not wallet_address:
            return False, "WALLET_NOT_LINKED"
        
        if wallet_address.startswith("NXS_GUEST"):
            return False, "GUEST_WALLET"
        
        if not wallet_address.startswith("NXS"):
            return False, "INVALID_WALLET_FORMAT"
        
        token_system = self._get_token_system()
        if token_system:
            account = token_system.get_account(wallet_address)
            if account is None:
                return False, "WALLET_NOT_REGISTERED"
        
        return True, "WALLET_VALID"
    
    def get_bhls_video_budget(self, citizen_id: str) -> Tuple[float, float]:
        """
        Get BHLS video budget from floor system.
        
        Returns:
            Tuple of (remaining_budget, used_this_month)
        """
        bhls = self._get_bhls_system()
        if bhls and citizen_id in bhls.citizens:
            from bhls_floor_system import BHLSCategory
            citizen = bhls.citizens[citizen_id]
            if BHLSCategory.CONNECTIVITY in citizen.bhls_allocations:
                allocation = citizen.bhls_allocations[BHLSCategory.CONNECTIVITY]
                return allocation.remaining_balance(), allocation.usage_current_month
        return 75.0, 0.0
    
    def start_session(
        self,
        session_id: str,
        wallet_address: Optional[str],
        user_identity: str,
        quality: VideoQuality = VideoQuality.HD_720P,
        stream_type: StreamType = StreamType.VIDEO_CALL
    ) -> Dict[str, Any]:
        """
        Start metering a video session with BHLS integration.
        
        If wallet not linked, session proceeds but charges go to escrow.
        """
        is_valid, wallet_status = self.validate_wallet_session(wallet_address, user_identity)
        
        frequency = self.calculate_frequency(quality, stream_type)
        energy_per_second_j = PLANCK_CONSTANT * frequency
        energy_per_second_nxt = energy_per_second_j / JOULES_PER_NXT
        
        bhls_remaining, bhls_used = self.get_bhls_video_budget(user_identity)
        
        session = {
            'session_id': session_id,
            'wallet_address': wallet_address if is_valid else None,
            'user_identity': user_identity,
            'wallet_status': wallet_status,
            'is_escrowed': not is_valid,
            'quality': quality,
            'stream_type': stream_type,
            'frequency_hz': frequency,
            'wavelength_nm': quality.wavelength_nm,
            'energy_per_second_j': energy_per_second_j,
            'energy_per_second_nxt': energy_per_second_nxt,
            'start_time': time.time(),
            'accumulated_energy_j': 0.0,
            'accumulated_energy_nxt': 0.0,
            'accumulated_sdk_fee_nxt': 0.0,
            'bhls_used_nxt': 0.0,
            'overflow_charged_nxt': 0.0,
            'bhls_remaining': bhls_remaining,
            'last_meter_time': time.time(),
            'meter_ticks': 0
        }
        
        self.active_sessions[session_id] = session
        
        return {
            'success': True,
            'session_id': session_id,
            'wallet_status': wallet_status,
            'is_escrowed': not is_valid,
            'energy_rate_nxt_per_minute': energy_per_second_nxt * 60,
            'quality': quality.display_name,
            'stream_type': stream_type.display_name,
            'frequency_hz': frequency,
            'wavelength_nm': quality.wavelength_nm,
            'bhls_video_budget_remaining': bhls_remaining
        }
    
    def meter_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Update energy accumulation for active session.
        
        Processes burns through economic_loop_controller for DEEP integration.
        """
        if session_id not in self.active_sessions:
            return None
        
        session = self.active_sessions[session_id]
        current_time = time.time()
        elapsed = current_time - session['last_meter_time']
        
        if elapsed < 1.0:
            return None
        
        energy_j = session['energy_per_second_j'] * elapsed
        energy_nxt = energy_j / JOULES_PER_NXT
        sdk_fee = energy_nxt * SDK_FEE_PERCENT
        
        bhls_covered = 0.0
        overflow = 0.0
        
        if session['bhls_remaining'] > 0:
            bhls_covered = min(energy_nxt, session['bhls_remaining'])
            session['bhls_remaining'] -= bhls_covered
            session['bhls_used_nxt'] += bhls_covered
            overflow = energy_nxt - bhls_covered
        else:
            overflow = energy_nxt
        
        session['overflow_charged_nxt'] += overflow
        
        flow_controller = self._get_flow_controller()
        if flow_controller and session['wallet_address'] and overflow > 0:
            message_id = f"video_{session_id}_{session['meter_ticks']}"
            try:
                success, msg, event = flow_controller.process_message_burn(
                    sender_address=session['wallet_address'],
                    message_id=message_id,
                    burn_amount_nxt=overflow,
                    wavelength_nm=session['wavelength_nm'],
                    message_type=session['stream_type'].message_type
                )
                if success and event:
                    session['last_transition_entry_id'] = event.reserve_entry_id
            except Exception as e:
                print(f"Video burn processing error: {e}")
        
        session['accumulated_energy_j'] += energy_j
        session['accumulated_energy_nxt'] += energy_nxt
        session['accumulated_sdk_fee_nxt'] += sdk_fee
        session['last_meter_time'] = current_time
        session['meter_ticks'] += 1
        
        return {
            'session_id': session_id,
            'elapsed_seconds': current_time - session['start_time'],
            'interval_energy_nxt': energy_nxt,
            'total_energy_nxt': session['accumulated_energy_nxt'],
            'total_sdk_fee_nxt': session['accumulated_sdk_fee_nxt'],
            'bhls_covered_nxt': session['bhls_used_nxt'],
            'overflow_charged_nxt': session['overflow_charged_nxt'],
            'bhls_remaining': session['bhls_remaining'],
            'is_escrowed': session['is_escrowed']
        }
    
    def end_session(self, session_id: str) -> Optional[VideoSessionCost]:
        """
        End video session, finalize charges, and route SDK fees.
        
        If escrowed, persists escrow entry to database for later resolution.
        """
        if session_id not in self.active_sessions:
            return None
        
        self.meter_session(session_id)
        session = self.active_sessions.pop(session_id)
        
        duration = time.time() - session['start_time']
        energy_j, energy_nxt, lambda_kg = self.calculate_energy_cost(
            session['quality'],
            session['stream_type'],
            duration
        )
        
        sdk_fee = energy_nxt * SDK_FEE_PERCENT
        
        cost = VideoSessionCost(
            session_id=session_id,
            wallet_address=session['wallet_address'],
            stream_type=session['stream_type'],
            quality=session['quality'],
            duration_seconds=duration,
            frequency_hz=session['frequency_hz'],
            energy_joules=energy_j,
            energy_nxt=energy_nxt,
            lambda_boson_kg=lambda_kg,
            sdk_fee_nxt=sdk_fee,
            bhls_covered_nxt=session['bhls_used_nxt'],
            overflow_charged_nxt=session['overflow_charged_nxt'],
            transition_entry_id=session.get('last_transition_entry_id'),
            is_escrowed=session['is_escrowed']
        )
        
        if session['is_escrowed']:
            escrow_id = f"VE_{int(time.time() * 1000)}_{session_id[:8]}"
            escrow = VideoEscrowEntry(
                escrow_id=escrow_id,
                session_id=session_id,
                user_identity=session['user_identity'],
                energy_nxt=energy_nxt,
                sdk_fee_nxt=sdk_fee,
                created_at=datetime.now(),
                transition_entry_id=session.get('last_transition_entry_id')
            )
            self._persist_escrow(escrow)
        else:
            self._route_sdk_fee(sdk_fee, session['wallet_address'], session_id)
            self.total_energy_consumed_nxt += energy_nxt
            self.sdk_fees_collected_nxt += sdk_fee
        
        self.total_energy_consumed_joules += energy_j
        self.completed_sessions.append(cost)
        
        return cost
    
    def _route_sdk_fee(self, fee_nxt: float, from_wallet: str, session_id: str) -> bool:
        """Route SDK fee to founder wallet through NativeTokenSystem"""
        if fee_nxt <= 0:
            return True
            
        token_system = self._get_token_system()
        if not token_system:
            print(f"⚠️ Token system not available, SDK fee deferred: {fee_nxt:.8f} NXT")
            return False
            
        try:
            if token_system.get_account("TRANSITION_RESERVE") is None:
                token_system.create_account("TRANSITION_RESERVE", initial_balance=0)
            if token_system.get_account(SDK_WALLET) is None:
                token_system.create_account(SDK_WALLET, initial_balance=0)
            
            reserve_account = token_system.get_account("TRANSITION_RESERVE")
            if reserve_account and hasattr(reserve_account, 'balance'):
                fee_units = int(fee_nxt * token_system.UNITS_PER_NXT)
                
                if reserve_account.balance >= fee_units:
                    success, tx, msg = token_system.transfer_atomic(
                        from_address="TRANSITION_RESERVE",
                        to_address=SDK_WALLET,
                        amount=fee_units,
                        fee=0,
                        reason=f"SDK fee for video session: {session_id}"
                    )
                    
                    if success:
                        print(f"✅ SDK fee routed: {fee_nxt:.8f} NXT → {SDK_WALLET[:20]}...")
                        return True
                    else:
                        print(f"⚠️ SDK fee transfer failed: {msg}")
                else:
                    print(f"⚠️ Insufficient reserve balance for SDK fee")
            
            return False
        except Exception as e:
            print(f"SDK fee routing error: {e}")
            return False
    
    def link_wallet_to_escrow(
        self,
        user_identity: str,
        wallet_address: str
    ) -> Dict[str, Any]:
        """
        Resolve escrowed charges when wallet is linked.
        
        Finds all escrow entries for user from database and processes payment.
        """
        escrows = self._load_user_escrows(user_identity)
        
        resolved_entries = []
        total_resolved_nxt = 0.0
        total_sdk_fee_nxt = 0.0
        
        flow_controller = self._get_flow_controller()
        
        for escrow in escrows:
            if not escrow.resolved:
                if flow_controller:
                    try:
                        message_id = f"escrow_resolve_{escrow.escrow_id}"
                        success, msg, event = flow_controller.process_message_burn(
                            sender_address=wallet_address,
                            message_id=message_id,
                            burn_amount_nxt=escrow.energy_nxt,
                            wavelength_nm=600,
                            message_type="video"
                        )
                        if success:
                            escrow.transition_entry_id = event.reserve_entry_id if event else None
                    except Exception as e:
                        print(f"Escrow resolution burn error: {e}")
                
                self._route_sdk_fee(escrow.sdk_fee_nxt, wallet_address, escrow.session_id)
                self._resolve_escrow_in_db(escrow.escrow_id, wallet_address)
                
                total_resolved_nxt += escrow.energy_nxt
                total_sdk_fee_nxt += escrow.sdk_fee_nxt
                resolved_entries.append(escrow.escrow_id)
        
        if resolved_entries:
            self.total_energy_consumed_nxt += total_resolved_nxt
            self.sdk_fees_collected_nxt += total_sdk_fee_nxt
        
        return {
            'success': True,
            'wallet_address': wallet_address,
            'resolved_escrow_count': len(resolved_entries),
            'total_resolved_nxt': total_resolved_nxt,
            'total_sdk_fee_nxt': total_sdk_fee_nxt,
            'escrow_ids': resolved_entries
        }
    
    def get_bhls_video_status(self, wallet_address: str) -> Dict[str, Any]:
        """
        Get BHLS video budget status for wallet from floor system.
        """
        bhls = self._get_bhls_system()
        if bhls:
            for citizen_id, citizen in bhls.citizens.items():
                if citizen.wallet_address == wallet_address:
                    from bhls_floor_system import BHLSCategory
                    if BHLSCategory.CONNECTIVITY in citizen.bhls_allocations:
                        allocation = citizen.bhls_allocations[BHLSCategory.CONNECTIVITY]
                        return {
                            'wallet_address': wallet_address,
                            'citizen_id': citizen_id,
                            'bhls_video_budget_nxt': allocation.monthly_allocation,
                            'used_nxt': allocation.usage_current_month,
                            'remaining_nxt': allocation.remaining_balance(),
                            'is_over_budget': allocation.usage_current_month > allocation.monthly_allocation
                        }
        
        user_sessions = [
            s for s in self.completed_sessions 
            if s.wallet_address == wallet_address
        ]
        
        total_used = sum(s.energy_nxt for s in user_sessions)
        budget = 75.0
        remaining = max(0, budget - total_used)
        
        return {
            'wallet_address': wallet_address,
            'citizen_id': None,
            'bhls_video_budget_nxt': budget,
            'used_nxt': total_used,
            'remaining_nxt': remaining,
            'sessions_count': len(user_sessions),
            'is_over_budget': total_used > budget
        }
    
    def get_pending_escrows(self, user_identity: str) -> List[Dict]:
        """Get pending escrow entries for user"""
        escrows = self._load_user_escrows(user_identity)
        return [
            {
                'escrow_id': e.escrow_id,
                'session_id': e.session_id,
                'energy_nxt': e.energy_nxt,
                'sdk_fee_nxt': e.sdk_fee_nxt,
                'created_at': e.created_at.isoformat()
            }
            for e in escrows if not e.resolved
        ]
    
    def get_sdk_revenue_summary(self) -> Dict[str, Any]:
        """
        Get SDK revenue summary for founder wallet.
        """
        pending_escrow_fees = sum(
            e.sdk_fee_nxt for e in self.escrow_pool.values() 
            if not e.resolved
        )
        
        return {
            'sdk_wallet': SDK_WALLET,
            'total_fees_collected_nxt': self.sdk_fees_collected_nxt,
            'pending_escrow_fees_nxt': pending_escrow_fees,
            'total_sessions': len(self.completed_sessions),
            'active_sessions': len(self.active_sessions),
            'escrow_pending_count': len([
                e for e in self.escrow_pool.values() 
                if not e.resolved
            ])
        }
    
    def get_physics_formula(self) -> Dict[str, str]:
        """
        Return the physics formulas used for video energy pricing.
        """
        return {
            'energy_formula': "E = hf × t (Energy = Planck × frequency × time)",
            'lambda_boson': "Λ = hf/c² (Mass-equivalent of oscillation)",
            'frequency': "f = resolution × frame_rate × quality_factor × stream_multiplier",
            'planck_constant': f"h = {PLANCK_CONSTANT:.6e} J·s",
            'speed_of_light': f"c = {SPEED_OF_LIGHT:,} m/s",
            'nxt_conversion': f"1 NXT = {JOULES_PER_NXT:.0e} Joules",
            'sdk_fee': f"SDK Fee = {SDK_FEE_PERCENT * 100}% of energy cost",
            'sdk_wallet': SDK_WALLET
        }


video_energy_meter = VideoEnergyMeter()
