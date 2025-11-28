"""
Physics Governance Primitives — NexusOS

Maps physical wavelength primitives to civilization governance semantics.
"Constructing the rules of nature into the governance of civilization"

Physics → Governance Mapping:
┌─────────────────────────────────────┬──────────────────────────────────────┐
│ Physics Primitive                   │ Governance Semantic                  │
├─────────────────────────────────────┼──────────────────────────────────────┤
│ Waveform hash (physical_event_id)   │ Event identity (single-source truth)│
│ Band used (nano..planck)            │ Authority tier (weight & cost)       │
│ Energy used (E = h·f·cycles)        │ Economic cost / stake                │
│ Multi-sensor endorsement            │ Multi-sig attestation                │
│ Root timestamp (Planck-anchored)    │ Immutable time anchor                │
│ Yocto-encoded declarations          │ Constitutional clause                │
│ Anomaly patterns (atto/zepto)       │ Security alerts / quarantine         │
└─────────────────────────────────────┴──────────────────────────────────────┘

GPL v3.0 License — Community Owned, Physics Governed
"""

import hashlib
import secrets
import time
import math
import json
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import Dict, List, Optional, Tuple, Set, Any, Union
from datetime import datetime
import struct

PLANCK_CONSTANT = 6.62607015e-34
SPEED_OF_LIGHT = 299792458
PLANCK_LENGTH = 1.616255e-35
PLANCK_TIME = 5.391247e-44


class AuthorityBand(Enum):
    """
    Seven authority bands mapped from spectral bands
    Higher band = higher authority weight & economic cost
    """
    NANO = (1, "nano", 1e-9, "UI, device, proximity, apps", 1.0)
    PICO = (2, "pico", 1e-12, "Identity, account pairing", 10.0)
    FEMTO = (3, "femto", 1e-15, "Immutable timestamps, validation", 100.0)
    ATTO = (4, "atto", 1e-18, "Policy enforcement, overrides", 1000.0)
    ZEPTO = (5, "zepto", 1e-21, "Planetary coordination, deep-space", 10000.0)
    YOCTO = (6, "yocto", 1e-24, "Constitutional/inviolable signals", 100000.0)
    PLANCK = (7, "planck", PLANCK_LENGTH, "Root clock reference", 1000000.0)
    
    def __init__(self, level: int, name: str, scale: float, role: str, cost_multiplier: float):
        self.authority_level = level
        self.band_name = name
        self.scale = scale
        self.role = role
        self.cost_multiplier = cost_multiplier
    
    @property
    def min_endorsements_required(self) -> int:
        """Higher authority bands require more endorsements"""
        return self.authority_level
    
    @property
    def base_frequency(self) -> float:
        """Center frequency for this band"""
        return SPEED_OF_LIGHT / self.scale
    
    @property
    def base_energy(self) -> float:
        """Base energy cost E = h·f for this band"""
        return PLANCK_CONSTANT * self.base_frequency


class GovernanceEventType(Enum):
    """Types of governance events that can be recorded"""
    PROPOSAL_CREATED = "proposal_created"
    VOTE_CAST = "vote_cast"
    CONSTITUTIONAL_AMENDMENT = "constitutional_amendment"
    POLICY_ENFORCEMENT = "policy_enforcement"
    EMERGENCY_OVERRIDE = "emergency_override"
    SECURITY_ALERT = "security_alert"
    QUARANTINE_ISSUED = "quarantine_issued"
    MULTI_SIG_APPROVAL = "multi_sig_approval"
    BHLS_DISTRIBUTION = "bhls_distribution"
    VALIDATOR_SLASHING = "validator_slashing"


class AnomalyType(Enum):
    """Anomaly types that trigger security alerts"""
    SYBIL_ATTACK = ("sybil", AuthorityBand.ATTO)
    DOUBLE_SPEND = ("double_spend", AuthorityBand.ZEPTO)
    GOVERNANCE_MANIPULATION = ("gov_manipulation", AuthorityBand.YOCTO)
    NETWORK_PARTITION = ("partition", AuthorityBand.ATTO)
    VALIDATOR_COLLUSION = ("collusion", AuthorityBand.YOCTO)
    UNAUTHORIZED_ACCESS = ("unauthorized", AuthorityBand.FEMTO)
    RATE_LIMIT_EXCEEDED = ("rate_limit", AuthorityBand.NANO)
    
    def __init__(self, code: str, required_band: AuthorityBand):
        self.code = code
        self.required_band = required_band


@dataclass
class WaveformEventIdentity:
    """
    PRIMITIVE 1: Waveform Hash → Event Identity
    
    Single-source truth for any action/event in the governance system.
    The physical_event_id is derived from actual waveform measurement,
    making it impossible to forge without physical access.
    """
    physical_event_id: bytes
    waveform_hash: bytes
    timestamp_planck: int
    frequency_hz: float
    pulse_count: int
    sensor_id: str
    
    event_type: GovernanceEventType = GovernanceEventType.PROPOSAL_CREATED
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    _payload_hash: bytes = field(default_factory=bytes, repr=False)
    
    @classmethod
    def create(cls, 
               event_type: GovernanceEventType,
               payload: bytes,
               sensor_id: str = "DEFAULT") -> 'WaveformEventIdentity':
        """
        Create event identity from payload using physics-based hashing
        """
        timestamp = int(time.time() * 1e9)
        
        payload_hash = hashlib.sha3_256(payload).digest()
        
        waveform_data = payload + struct.pack('!Q', timestamp) + secrets.token_bytes(16)
        
        waveform_hash = hashlib.sha3_256(waveform_data).digest()
        
        physical_event_id = hashlib.sha3_256(
            waveform_hash + sensor_id.encode() + struct.pack('!Q', timestamp)
        ).digest()[:20]
        
        samples = [float(b) / 255.0 for b in waveform_data[:64]]
        zero_crossings = sum(1 for i in range(1, len(samples)) 
                           if (samples[i-1] - 0.5) * (samples[i] - 0.5) < 0)
        
        frequency_hz = max(1e12, (zero_crossings / 64) * 1e15) if zero_crossings > 0 else 5e14
        pulse_count = max(1, zero_crossings // 2)
        
        instance = cls(
            physical_event_id=physical_event_id,
            waveform_hash=waveform_hash,
            timestamp_planck=timestamp,
            frequency_hz=frequency_hz,
            pulse_count=pulse_count,
            sensor_id=sensor_id,
            event_type=event_type
        )
        instance._payload_hash = payload_hash
        return instance
    
    def to_hex(self) -> str:
        """Return hex representation of event ID"""
        return self.physical_event_id.hex()
    
    def verify_integrity(self, original_payload: bytes) -> bool:
        """Verify event hasn't been tampered with by comparing full SHA3-256 hashes"""
        computed_hash = hashlib.sha3_256(original_payload).digest()
        return self._payload_hash == computed_hash


@dataclass
class AuthorityTier:
    """
    PRIMITIVE 2: Band Used → Authority Tier
    
    Higher band = higher authority weight & economic cost.
    Operations at higher bands require more energy and endorsements.
    """
    band: AuthorityBand
    authority_weight: float
    economic_cost_nxt: float
    endorsements_required: int
    
    @classmethod
    def from_band(cls, band: AuthorityBand, base_cycles: int = 1) -> 'AuthorityTier':
        """
        Create authority tier from spectral band
        
        Economic cost: E = h·f·n_cycles·authority²
        """
        base_energy = band.base_energy * base_cycles
        authority_squared = band.authority_level ** 2
        
        economic_cost_nxt = base_energy * authority_squared * band.cost_multiplier * 1e15
        
        return cls(
            band=band,
            authority_weight=float(band.authority_level),
            economic_cost_nxt=economic_cost_nxt,
            endorsements_required=band.min_endorsements_required
        )
    
    def can_override(self, other: 'AuthorityTier') -> bool:
        """Check if this tier can override another"""
        return self.band.authority_level > other.band.authority_level
    
    def meets_threshold(self, endorsement_count: int) -> bool:
        """Check if endorsement count meets threshold"""
        return endorsement_count >= self.endorsements_required


@dataclass
class EconomicStake:
    """
    PRIMITIVE 3: Energy Used → Economic Cost/Stake
    
    E = h·f·n_cycles·authority²
    
    More energy = more commitment, disincentivizes spam.
    """
    base_energy_joules: float
    cycles: int
    authority_multiplier: float
    total_cost_nxt: float
    staker_address: str
    
    stake_locked_until: Optional[int] = None
    can_slash: bool = True
    
    @classmethod
    def calculate(cls, 
                  band: AuthorityBand,
                  cycles: int,
                  staker_address: str,
                  lock_duration_seconds: int = 0) -> 'EconomicStake':
        """
        Calculate economic stake from physics parameters
        
        Formula: E = h·f·n_cycles·authority²
        """
        frequency = band.base_frequency
        base_energy = PLANCK_CONSTANT * frequency * cycles
        
        authority_squared = band.authority_level ** 2
        
        total_cost = base_energy * authority_squared * band.cost_multiplier * 1e15
        
        lock_until = None
        if lock_duration_seconds > 0:
            lock_until = int(time.time()) + lock_duration_seconds
        
        return cls(
            base_energy_joules=base_energy,
            cycles=cycles,
            authority_multiplier=float(authority_squared),
            total_cost_nxt=total_cost,
            staker_address=staker_address,
            stake_locked_until=lock_until
        )
    
    def is_locked(self) -> bool:
        """Check if stake is still locked"""
        if self.stake_locked_until is None:
            return False
        return time.time() < self.stake_locked_until


@dataclass
class MultiSensorEndorsement:
    """
    PRIMITIVE 4: Multi-Sensor Endorsement → Multi-Sig Attestation
    
    Anti-fraud mechanism requiring multiple independent sensor
    confirmations for high-authority operations.
    """
    primary_sensor_id: str
    primary_signature: bytes
    endorsements: List[Tuple[str, bytes, int]]
    required_threshold: int
    authority_band: AuthorityBand
    
    event_id: Optional[bytes] = None
    created_at: int = field(default_factory=lambda: int(time.time() * 1e9))
    
    @classmethod
    def create(cls,
               event_id: bytes,
               primary_sensor_id: str,
               authority_band: AuthorityBand) -> 'MultiSensorEndorsement':
        """
        Create endorsement requiring threshold based on authority band
        """
        primary_signature = hashlib.sha3_256(
            event_id + primary_sensor_id.encode() + secrets.token_bytes(16)
        ).digest()
        
        return cls(
            primary_sensor_id=primary_sensor_id,
            primary_signature=primary_signature,
            endorsements=[],
            required_threshold=authority_band.min_endorsements_required,
            authority_band=authority_band,
            event_id=event_id
        )
    
    def add_endorsement(self, sensor_id: str, signature: bytes) -> bool:
        """Add endorsement from another sensor"""
        if sensor_id == self.primary_sensor_id:
            return False
        
        if any(s[0] == sensor_id for s in self.endorsements):
            return False
        
        timestamp = int(time.time() * 1e9)
        self.endorsements.append((sensor_id, signature, timestamp))
        return True
    
    def is_fully_endorsed(self) -> bool:
        """Check if we have enough endorsements"""
        total = 1 + len(self.endorsements)
        return total >= self.required_threshold
    
    def endorsement_count(self) -> int:
        """Total endorsement count including primary"""
        return 1 + len(self.endorsements)
    
    def get_all_endorsers(self) -> List[str]:
        """Get list of all endorser IDs"""
        return [self.primary_sensor_id] + [e[0] for e in self.endorsements]


@dataclass
class PlanckTimestamp:
    """
    PRIMITIVE 5: Root Timestamp (Planck-Anchored) → Immutable Time Anchor
    
    Final ordering and audit trail anchored to Planck-scale precision.
    Cannot be altered without Planck-level consensus.
    """
    planck_time: int
    unix_seconds: float
    sequence_number: int
    anchor_hash: bytes
    
    validator_signatures: List[Tuple[str, bytes]] = field(default_factory=list)
    finalized: bool = False
    
    @classmethod
    def now(cls, sequence: int = 0) -> 'PlanckTimestamp':
        """
        Create Planck-anchored timestamp for current moment
        """
        unix_time = time.time()
        planck_units = int(unix_time / PLANCK_TIME)
        
        anchor_data = struct.pack('!Qd', planck_units, unix_time) + secrets.token_bytes(16)
        anchor_hash = hashlib.sha3_256(anchor_data).digest()
        
        return cls(
            planck_time=planck_units,
            unix_seconds=unix_time,
            sequence_number=sequence,
            anchor_hash=anchor_hash
        )
    
    def add_validator_signature(self, validator_id: str, signature: bytes) -> None:
        """Add validator confirmation of timestamp"""
        if not any(v[0] == validator_id for v in self.validator_signatures):
            self.validator_signatures.append((validator_id, signature))
    
    def finalize(self, required_validators: int = 3) -> bool:
        """Finalize timestamp if enough validators confirmed"""
        if len(self.validator_signatures) >= required_validators:
            self.finalized = True
        return self.finalized
    
    def to_datetime(self) -> datetime:
        """Convert to Python datetime"""
        return datetime.fromtimestamp(self.unix_seconds)
    
    def __lt__(self, other: 'PlanckTimestamp') -> bool:
        """Compare timestamps for ordering"""
        if self.planck_time != other.planck_time:
            return self.planck_time < other.planck_time
        return self.sequence_number < other.sequence_number


@dataclass
class ConstitutionalClause:
    """
    PRIMITIVE 6: Yocto-Encoded Declarations → Constitutional Clause
    
    Inviolable governance rules that cannot be overridden
    without Planck-level consensus (maximum authority).
    """
    clause_id: str
    title: str
    content: str
    encoding_band: AuthorityBand
    
    yocto_hash: bytes = field(default_factory=bytes)
    enacted_timestamp: Optional[PlanckTimestamp] = None
    amendment_history: List[Tuple[str, PlanckTimestamp]] = field(default_factory=list)
    
    is_active: bool = True
    requires_planck_consensus: bool = True
    
    @classmethod
    def create(cls, 
               title: str, 
               content: str,
               clause_id: Optional[str] = None) -> 'ConstitutionalClause':
        """
        Create constitutional clause with Yocto-level encoding
        """
        enacted_ts = PlanckTimestamp.now()
        encoding_band = AuthorityBand.YOCTO
        
        if clause_id is None:
            clause_id = hashlib.sha3_256(
                (title + content).encode() + secrets.token_bytes(8)
            ).hexdigest()[:16]
        
        yocto_hash = hashlib.sha3_256(
            clause_id.encode() + 
            title.encode() + 
            content.encode() +
            encoding_band.band_name.encode() +
            struct.pack('!Q', enacted_ts.planck_time) +
            b"YOCTO_CONSTITUTIONAL_V2"
        ).digest()
        
        return cls(
            clause_id=clause_id,
            title=title,
            content=content,
            encoding_band=encoding_band,
            yocto_hash=yocto_hash,
            enacted_timestamp=enacted_ts
        )
    
    def propose_amendment(self, 
                          new_content: str,
                          authority_band: AuthorityBand) -> Tuple[bool, str]:
        """
        Propose amendment to constitutional clause
        
        Requires Planck-level authority to amend
        """
        if authority_band.authority_level < AuthorityBand.PLANCK.authority_level:
            return False, f"Constitutional amendments require PLANCK authority (level 7), got {authority_band.band_name} (level {authority_band.authority_level})"
        
        timestamp = PlanckTimestamp.now()
        self.amendment_history.append((new_content, timestamp))
        self.content = new_content
        
        self.yocto_hash = hashlib.sha3_256(
            self.clause_id.encode() + 
            self.title.encode() + 
            new_content.encode() +
            self.encoding_band.band_name.encode() +
            struct.pack('!Q', timestamp.planck_time) +
            struct.pack('!I', len(self.amendment_history)) +
            b"YOCTO_CONSTITUTIONAL_AMENDED_V2"
        ).digest()
        
        return True, f"Amendment enacted at Planck time {timestamp.planck_time}"
    
    def verify_integrity(self) -> bool:
        """Verify clause hasn't been tampered with including encoding metadata"""
        if self.amendment_history:
            last_content, last_ts = self.amendment_history[-1]
            expected_hash = hashlib.sha3_256(
                self.clause_id.encode() + 
                self.title.encode() + 
                self.content.encode() +
                self.encoding_band.band_name.encode() +
                struct.pack('!Q', last_ts.planck_time) +
                struct.pack('!I', len(self.amendment_history)) +
                b"YOCTO_CONSTITUTIONAL_AMENDED_V2"
            ).digest()
        else:
            expected_hash = hashlib.sha3_256(
                self.clause_id.encode() + 
                self.title.encode() + 
                self.content.encode() +
                self.encoding_band.band_name.encode() +
                struct.pack('!Q', self.enacted_timestamp.planck_time if self.enacted_timestamp else 0) +
                b"YOCTO_CONSTITUTIONAL_V2"
            ).digest()
        return self.yocto_hash == expected_hash


@dataclass
class SecurityAnomaly:
    """
    PRIMITIVE 7: Anomaly Patterns → Security Alerts / Quarantine
    
    Auto-triggered emergency governance based on detected
    anomaly patterns at atto/zepto bands.
    """
    anomaly_id: str
    anomaly_type: AnomalyType
    severity: int
    
    detection_timestamp: PlanckTimestamp = field(default_factory=PlanckTimestamp.now)
    source_addresses: List[str] = field(default_factory=list)
    evidence_hashes: List[bytes] = field(default_factory=list)
    
    quarantine_active: bool = False
    quarantine_addresses: Set[str] = field(default_factory=set)
    resolution_status: str = "pending"
    resolution_notes: str = ""
    
    auto_response_triggered: bool = False
    escalation_band: Optional[AuthorityBand] = None
    
    @classmethod
    def detect(cls,
               anomaly_type: AnomalyType,
               source_addresses: List[str],
               evidence: bytes,
               severity: int = 5) -> 'SecurityAnomaly':
        """
        Create security anomaly from detection
        """
        anomaly_id = hashlib.sha3_256(
            anomaly_type.code.encode() +
            ''.join(source_addresses).encode() +
            evidence +
            struct.pack('!Q', int(time.time() * 1e9))
        ).hexdigest()[:24]
        
        evidence_hash = hashlib.sha3_256(evidence).digest()
        
        return cls(
            anomaly_id=anomaly_id,
            anomaly_type=anomaly_type,
            severity=min(10, max(1, severity)),
            source_addresses=source_addresses,
            evidence_hashes=[evidence_hash],
            escalation_band=anomaly_type.required_band
        )
    
    def trigger_quarantine(self, addresses: Optional[List[str]] = None) -> None:
        """Activate quarantine for specified addresses"""
        if addresses is None:
            addresses = self.source_addresses
        
        self.quarantine_active = True
        self.quarantine_addresses.update(addresses)
        self.auto_response_triggered = True
    
    def release_quarantine(self, 
                           address: str,
                           authority_band: AuthorityBand,
                           reason: str) -> Tuple[bool, str]:
        """
        Release address from quarantine
        
        Requires authority level >= anomaly's required band
        """
        if authority_band.authority_level < self.anomaly_type.required_band.authority_level:
            return False, f"Insufficient authority to release quarantine. Required: {self.anomaly_type.required_band.band_name}"
        
        if address in self.quarantine_addresses:
            self.quarantine_addresses.remove(address)
            if not self.quarantine_addresses:
                self.quarantine_active = False
            return True, f"Address {address[:16]}... released from quarantine"
        
        return False, "Address not in quarantine"
    
    def resolve(self, 
                resolution_status: str,
                notes: str,
                authority_band: AuthorityBand) -> Tuple[bool, str]:
        """Resolve the security anomaly"""
        if authority_band.authority_level < self.anomaly_type.required_band.authority_level:
            return False, f"Insufficient authority to resolve. Required: {self.anomaly_type.required_band.band_name}"
        
        self.resolution_status = resolution_status
        self.resolution_notes = notes
        self.quarantine_active = False
        self.quarantine_addresses.clear()
        
        return True, f"Anomaly {self.anomaly_id} resolved: {resolution_status}"
    
    def is_critical(self) -> bool:
        """Check if anomaly is critical (severity >= 8)"""
        return self.severity >= 8


class PhysicsGovernanceEngine:
    """
    Main engine for physics-based governance operations
    
    Integrates all 7 primitives into a unified governance system.
    """
    
    def __init__(self):
        self.events: Dict[str, WaveformEventIdentity] = {}
        self.endorsements: Dict[str, MultiSensorEndorsement] = {}
        self.constitutional_clauses: Dict[str, ConstitutionalClause] = {}
        self.active_anomalies: Dict[str, SecurityAnomaly] = {}
        self.timestamp_chain: List[PlanckTimestamp] = []
        
        self._sequence_counter = 0
        
        self._init_foundational_clauses()
    
    def _init_foundational_clauses(self):
        """Initialize foundational constitutional clauses"""
        bhls_clause = ConstitutionalClause.create(
            title="Basic Human Living Standards (BHLS) Floor",
            content="Every citizen is guaranteed 1,150 NXT per month for basic living standards. "
                    "This floor cannot be reduced without Planck-level consensus from >90% of validators."
        )
        self.constitutional_clauses[bhls_clause.clause_id] = bhls_clause
        
        physics_clause = ConstitutionalClause.create(
            title="Physics-Based Economics Mandate",
            content="All economic transactions must follow E = h·f·n_cycles·authority² formula. "
                    "Energy costs cannot be bypassed or manipulated."
        )
        self.constitutional_clauses[physics_clause.clause_id] = physics_clause
        
        gpl_clause = ConstitutionalClause.create(
            title="GPL v3 Community Ownership",
            content="NexusOS source code is permanently licensed under GPL v3. "
                    "No entity may relicense or close-source any component."
        )
        self.constitutional_clauses[gpl_clause.clause_id] = gpl_clause
    
    def create_governance_event(self,
                                 event_type: GovernanceEventType,
                                 payload: bytes,
                                 authority_band: AuthorityBand,
                                 sensor_id: str = "DEFAULT") -> Tuple[WaveformEventIdentity, EconomicStake]:
        """
        Create a governance event with proper authority and economic stake
        """
        event = WaveformEventIdentity.create(event_type, payload, sensor_id)
        
        stake = EconomicStake.calculate(
            band=authority_band,
            cycles=event.pulse_count,
            staker_address=sensor_id
        )
        
        event.metadata['authority_band'] = authority_band.band_name
        event.metadata['economic_cost_nxt'] = stake.total_cost_nxt
        
        self.events[event.to_hex()] = event
        
        return event, stake
    
    def request_multi_sig_approval(self,
                                    event: WaveformEventIdentity,
                                    authority_band: AuthorityBand) -> MultiSensorEndorsement:
        """
        Request multi-signature approval for high-authority operations
        """
        endorsement = MultiSensorEndorsement.create(
            event_id=event.physical_event_id,
            primary_sensor_id=event.sensor_id,
            authority_band=authority_band
        )
        
        self.endorsements[event.to_hex()] = endorsement
        
        return endorsement
    
    def add_endorsement(self,
                         event_id: str,
                         sensor_id: str,
                         signature: bytes) -> Tuple[bool, str]:
        """Add endorsement to pending multi-sig request"""
        if event_id not in self.endorsements:
            return False, "No pending endorsement request for this event"
        
        endorsement = self.endorsements[event_id]
        
        if endorsement.add_endorsement(sensor_id, signature):
            if endorsement.is_fully_endorsed():
                return True, f"Multi-sig approval complete ({endorsement.endorsement_count()}/{endorsement.required_threshold})"
            return True, f"Endorsement added ({endorsement.endorsement_count()}/{endorsement.required_threshold})"
        
        return False, "Failed to add endorsement (duplicate or invalid)"
    
    def anchor_timestamp(self) -> PlanckTimestamp:
        """Create new Planck-anchored timestamp"""
        self._sequence_counter += 1
        timestamp = PlanckTimestamp.now(self._sequence_counter)
        self.timestamp_chain.append(timestamp)
        return timestamp
    
    def detect_anomaly(self,
                        anomaly_type: AnomalyType,
                        source_addresses: List[str],
                        evidence: bytes,
                        severity: int = 5,
                        auto_quarantine: bool = True) -> SecurityAnomaly:
        """
        Detect and register security anomaly
        """
        anomaly = SecurityAnomaly.detect(
            anomaly_type=anomaly_type,
            source_addresses=source_addresses,
            evidence=evidence,
            severity=severity
        )
        
        if auto_quarantine and severity >= 7:
            anomaly.trigger_quarantine()
        
        self.active_anomalies[anomaly.anomaly_id] = anomaly
        
        return anomaly
    
    def is_address_quarantined(self, address: str) -> bool:
        """Check if an address is currently quarantined"""
        for anomaly in self.active_anomalies.values():
            if anomaly.quarantine_active and address in anomaly.quarantine_addresses:
                return True
        return False
    
    def get_required_authority_for_operation(self, 
                                              operation_type: str,
                                              strict: bool = False) -> AuthorityBand:
        """
        Determine required authority band for operation type
        
        Args:
            operation_type: The type of operation
            strict: If True, raises ValueError for unknown operations
                    If False, returns NANO for unknown (UI display only)
        """
        authority_map = {
            'send_message': AuthorityBand.NANO,
            'create_wallet': AuthorityBand.NANO,
            'view_balance': AuthorityBand.NANO,
            'receive_tokens': AuthorityBand.NANO,
            'transfer_tokens': AuthorityBand.PICO,
            'stake_tokens': AuthorityBand.PICO,
            'unstake_tokens': AuthorityBand.PICO,
            'delegate_stake': AuthorityBand.PICO,
            'create_proposal': AuthorityBand.FEMTO,
            'cast_vote': AuthorityBand.FEMTO,
            'validate_block': AuthorityBand.FEMTO,
            'timestamp_event': AuthorityBand.FEMTO,
            'enforce_policy': AuthorityBand.ATTO,
            'emergency_override': AuthorityBand.ATTO,
            'trigger_quarantine': AuthorityBand.ATTO,
            'release_quarantine': AuthorityBand.ATTO,
            'planetary_broadcast': AuthorityBand.ZEPTO,
            'resolve_anomaly': AuthorityBand.ZEPTO,
            'cross_chain_transfer': AuthorityBand.ZEPTO,
            'create_constitutional_clause': AuthorityBand.YOCTO,
            'amend_constitution': AuthorityBand.PLANCK,
            'modify_bhls': AuthorityBand.PLANCK,
            'modify_physics_constants': AuthorityBand.PLANCK,
            'network_genesis': AuthorityBand.PLANCK,
        }
        
        if operation_type in authority_map:
            return authority_map[operation_type]
        
        if strict:
            raise ValueError(f"Unknown operation type: {operation_type}. "
                           f"Valid operations: {list(authority_map.keys())}")
        
        return AuthorityBand.NANO
    
    def calculate_operation_cost(self,
                                  operation_type: str,
                                  cycles: int = 1) -> float:
        """
        Calculate NXT cost for an operation
        
        Uses E = h·f·n_cycles·authority² formula
        """
        band = self.get_required_authority_for_operation(operation_type)
        stake = EconomicStake.calculate(band, cycles, "SYSTEM")
        return stake.total_cost_nxt
    
    def get_constitutional_clauses(self) -> List[ConstitutionalClause]:
        """Get all active constitutional clauses"""
        return [c for c in self.constitutional_clauses.values() if c.is_active]
    
    def get_pending_endorsements(self) -> List[MultiSensorEndorsement]:
        """Get endorsements that are not yet complete"""
        return [e for e in self.endorsements.values() if not e.is_fully_endorsed()]
    
    def get_active_anomalies(self) -> List[SecurityAnomaly]:
        """Get all unresolved anomalies"""
        return [a for a in self.active_anomalies.values() 
                if a.resolution_status == "pending"]
    
    def get_governance_stats(self) -> Dict[str, Any]:
        """Get comprehensive governance statistics"""
        return {
            'total_events': len(self.events),
            'pending_endorsements': len(self.get_pending_endorsements()),
            'constitutional_clauses': len(self.constitutional_clauses),
            'active_anomalies': len(self.get_active_anomalies()),
            'timestamp_chain_length': len(self.timestamp_chain),
            'quarantined_addresses': sum(
                len(a.quarantine_addresses) 
                for a in self.active_anomalies.values() 
                if a.quarantine_active
            ),
            'authority_bands': {
                band.band_name: {
                    'level': band.authority_level,
                    'cost_multiplier': band.cost_multiplier,
                    'min_endorsements': band.min_endorsements_required
                }
                for band in AuthorityBand
            }
        }


_governance_engine: Optional[PhysicsGovernanceEngine] = None

def get_governance_engine() -> PhysicsGovernanceEngine:
    """Get or create the singleton governance engine"""
    global _governance_engine
    if _governance_engine is None:
        _governance_engine = PhysicsGovernanceEngine()
    return _governance_engine
