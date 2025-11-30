"""
NexusOS Active Intervention Engine
Real-time threat detection and automated response system

Philosophy: "Intervention is better than a cure"
- Detects attacks BEFORE they cause damage
- Automatically blocks/isolates threats
- Escalates based on severity
- Provides emergency kill-switches

Physics Substrate Integration:
- Emergency economic interventions route through PhysicsEconomicsAdapter
- Penalty slashing and compensation gated on settlement_success
- Crisis level coordination with supply chain and reserve modules
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Set, Any
from enum import Enum
from datetime import datetime, timedelta
import time

try:
    from physics_economics_adapter import (
        get_physics_adapter,
        PhysicsEconomicsAdapter,
        EconomicModule,
        CrisisLevel,
        SubstrateTransaction
    )
    SUBSTRATE_AVAILABLE = True
except ImportError:
    SUBSTRATE_AVAILABLE = False
    get_physics_adapter = None
    CrisisLevel = None


class ThreatLevel(Enum):
    """Threat severity levels with automated responses"""
    LOW = "low"              # Monitor only
    MEDIUM = "medium"        # Rate limit + warning
    HIGH = "high"            # Block + isolate
    CRITICAL = "critical"    # Emergency shutdown + alert


class InterventionAction(Enum):
    """Automated intervention actions"""
    MONITOR = "monitor"                    # Passive observation
    WARN = "warn"                          # Send warning notification
    RATE_LIMIT = "rate_limit"             # Increase rate limiting
    TEMPORARY_BAN = "temporary_ban"        # 1-hour ban
    PERMANENT_BAN = "permanent_ban"        # Permanent blacklist
    ISOLATE_VALIDATOR = "isolate_validator"  # Remove from consensus
    PAUSE_GOVERNANCE = "pause_governance"   # Freeze proposal/voting
    EMERGENCY_SHUTDOWN = "emergency_shutdown"  # System-wide halt
    ORACLE_BLACKLIST = "oracle_blacklist"   # Block data source


@dataclass
class ThreatDetection:
    """Detected threat with severity and context"""
    threat_id: str
    threat_type: str
    threat_level: ThreatLevel
    entity: str  # Address, validator, oracle, etc.
    evidence: str
    detected_at: float = field(default_factory=time.time)
    intervened: bool = False
    intervention_action: Optional[InterventionAction] = None


@dataclass
class InterventionRule:
    """Rule defining when and how to intervene"""
    rule_id: str
    threat_pattern: str
    threshold: float
    threat_level: ThreatLevel
    action: InterventionAction
    cooldown_seconds: int = 3600  # 1 hour default
    auto_execute: bool = True


class ActiveInterventionEngine:
    """
    Real-time threat detection and automated intervention system
    
    Monitors all NexusOS subsystems and intervenes automatically
    when attack patterns are detected, BEFORE damage occurs.
    """
    
    def __init__(self):
        # Threat tracking
        self.active_threats: Dict[str, ThreatDetection] = {}
        self.intervention_history: List[ThreatDetection] = []
        
        # Blacklists and bans
        self.permanent_bans: Set[str] = set()
        self.temporary_bans: Dict[str, float] = {}  # entity -> unban_time
        self.oracle_blacklist: Set[str] = set()
        self.isolated_validators: Set[str] = set()
        
        # Emergency controls
        self.governance_paused = False
        self.emergency_shutdown_active = False
        
        # Intervention rules
        self.rules = self._initialize_rules()
        
        # Statistics
        self.total_interventions = 0
        self.threats_blocked = 0
        self.false_positives = 0
    
    def _initialize_rules(self) -> List[InterventionRule]:
        """Initialize automated intervention rules"""
        return [
            # Oracle manipulation
            InterventionRule(
                rule_id="oracle_outlier_extreme",
                threat_pattern="oracle_price_deviation",
                threshold=0.50,  # 50% deviation
                threat_level=ThreatLevel.CRITICAL,
                action=InterventionAction.ORACLE_BLACKLIST,
                auto_execute=True
            ),
            InterventionRule(
                rule_id="oracle_outlier_high",
                threat_pattern="oracle_price_deviation",
                threshold=0.30,  # 30% deviation
                threat_level=ThreatLevel.HIGH,
                action=InterventionAction.WARN,
                auto_execute=True
            ),
            
            # Governance attacks
            InterventionRule(
                rule_id="governance_vote_spike",
                threat_pattern="sudden_vote_concentration",
                threshold=0.40,  # 40% of votes in 1 minute
                threat_level=ThreatLevel.HIGH,
                action=InterventionAction.PAUSE_GOVERNANCE,
                auto_execute=True
            ),
            InterventionRule(
                rule_id="governance_collusion_detected",
                threat_pattern="collusion_ring",
                threshold=0.80,  # 80% confidence
                threat_level=ThreatLevel.CRITICAL,
                action=InterventionAction.PAUSE_GOVERNANCE,
                auto_execute=True
            ),
            
            # Validator attacks
            InterventionRule(
                rule_id="validator_double_sign",
                threat_pattern="double_signing",
                threshold=1.0,  # Any occurrence
                threat_level=ThreatLevel.CRITICAL,
                action=InterventionAction.ISOLATE_VALIDATOR,
                auto_execute=True
            ),
            InterventionRule(
                rule_id="validator_censorship",
                threat_pattern="transaction_censorship",
                threshold=0.70,  # 70% rejection rate
                threat_level=ThreatLevel.HIGH,
                action=InterventionAction.ISOLATE_VALIDATOR,
                auto_execute=True
            ),
            
            # Network DDoS
            InterventionRule(
                rule_id="network_flood_critical",
                threat_pattern="request_flood",
                threshold=100.0,  # 100 req/sec from single IP
                threat_level=ThreatLevel.CRITICAL,
                action=InterventionAction.PERMANENT_BAN,
                auto_execute=True
            ),
            InterventionRule(
                rule_id="network_flood_high",
                threat_pattern="request_flood",
                threshold=50.0,  # 50 req/sec
                threat_level=ThreatLevel.HIGH,
                action=InterventionAction.TEMPORARY_BAN,
                auto_execute=True
            ),
            
            # Economic attacks
            InterventionRule(
                rule_id="wash_trading_extreme",
                threat_pattern="wash_trading",
                threshold=0.50,  # 50% of pair volume
                threat_level=ThreatLevel.CRITICAL,
                action=InterventionAction.PERMANENT_BAN,
                auto_execute=True
            ),
            InterventionRule(
                rule_id="flash_loan_attack",
                threat_pattern="same_block_borrow_repay",
                threshold=1.0,  # Any occurrence
                threat_level=ThreatLevel.CRITICAL,
                action=InterventionAction.PERMANENT_BAN,
                auto_execute=True
            )
        ]
    
    def detect_and_intervene(self, threat_type: str, entity: str, 
                            metric_value: float, evidence: str) -> Tuple[bool, Optional[InterventionAction]]:
        """
        Core intervention logic: detect threat and execute automated response
        
        Args:
            threat_type: Type of threat pattern
            entity: Entity being monitored (address, validator, oracle)
            metric_value: Measured value to compare against thresholds
            evidence: Context/proof of suspicious activity
        
        Returns:
            (threat_detected, action_taken)
        """
        # Check if entity is already banned
        if entity in self.permanent_bans:
            return True, InterventionAction.PERMANENT_BAN
        
        if entity in self.temporary_bans:
            if time.time() < self.temporary_bans[entity]:
                return True, InterventionAction.TEMPORARY_BAN
            else:
                # Unban expired
                del self.temporary_bans[entity]
        
        # Find matching rules (select highest severity match)
        threat_priority = {
            ThreatLevel.LOW: 0,
            ThreatLevel.MEDIUM: 1,
            ThreatLevel.HIGH: 2,
            ThreatLevel.CRITICAL: 3
        }
        
        matched_rule = None
        highest_priority = -1
        
        for rule in self.rules:
            if rule.threat_pattern == threat_type and metric_value >= rule.threshold:
                rule_priority = threat_priority[rule.threat_level]
                if rule_priority > highest_priority:
                    matched_rule = rule
                    highest_priority = rule_priority
        
        if matched_rule is None:
            return False, None
        
        # Create threat detection
        threat_id = f"{threat_type}_{entity}_{int(time.time())}"
        threat = ThreatDetection(
            threat_id=threat_id,
            threat_type=threat_type,
            threat_level=matched_rule.threat_level,
            entity=entity,
            evidence=evidence
        )
        
        # Execute intervention if auto_execute enabled
        if matched_rule.auto_execute:
            action = self._execute_intervention(threat, matched_rule.action)
            threat.intervened = True
            threat.intervention_action = action
            
            self.total_interventions += 1
            self.threats_blocked += 1
        
        # Record threat
        self.active_threats[threat_id] = threat
        self.intervention_history.append(threat)
        
        return True, matched_rule.action if matched_rule.auto_execute else None
    
    def _execute_intervention(self, threat: ThreatDetection, 
                             action: InterventionAction) -> InterventionAction:
        """Execute automated intervention action"""
        entity = threat.entity
        
        if action == InterventionAction.PERMANENT_BAN:
            self.permanent_bans.add(entity)
            print(f"🚨 PERMANENT BAN: {entity} - {threat.threat_type}")
            print(f"   Evidence: {threat.evidence}")
        
        elif action == InterventionAction.TEMPORARY_BAN:
            unban_time = time.time() + 3600  # 1 hour
            self.temporary_bans[entity] = unban_time
            print(f"⏱️ TEMPORARY BAN (1hr): {entity} - {threat.threat_type}")
        
        elif action == InterventionAction.ORACLE_BLACKLIST:
            self.oracle_blacklist.add(entity)
            print(f"📊 ORACLE BLACKLISTED: {entity}")
            print(f"   Evidence: {threat.evidence}")
        
        elif action == InterventionAction.ISOLATE_VALIDATOR:
            self.isolated_validators.add(entity)
            print(f"⚠️ VALIDATOR ISOLATED: {entity}")
            print(f"   Evidence: {threat.evidence}")
        
        elif action == InterventionAction.PAUSE_GOVERNANCE:
            self.governance_paused = True
            print(f"🛑 GOVERNANCE PAUSED - Attack detected: {threat.threat_type}")
            print(f"   Evidence: {threat.evidence}")
        
        elif action == InterventionAction.EMERGENCY_SHUTDOWN:
            self.emergency_shutdown_active = True
            print(f"🚨🚨 EMERGENCY SHUTDOWN ACTIVATED 🚨🚨")
            print(f"   Threat: {threat.threat_type}")
            print(f"   Evidence: {threat.evidence}")
        
        elif action == InterventionAction.WARN:
            print(f"⚠️ WARNING: {entity} - {threat.threat_type}")
            print(f"   Evidence: {threat.evidence}")
        
        return action
    
    def is_entity_blocked(self, entity: str) -> Tuple[bool, Optional[str]]:
        """Check if entity is blocked by any intervention"""
        if entity in self.permanent_bans:
            return True, "Permanently banned"
        
        if entity in self.temporary_bans:
            if time.time() < self.temporary_bans[entity]:
                remaining = int(self.temporary_bans[entity] - time.time())
                return True, f"Temporarily banned ({remaining}s remaining)"
            else:
                del self.temporary_bans[entity]
        
        if entity in self.oracle_blacklist:
            return True, "Oracle blacklisted"
        
        if entity in self.isolated_validators:
            return True, "Validator isolated"
        
        return False, None
    
    def manual_intervention(self, entity: str, action: InterventionAction, 
                          reason: str) -> bool:
        """Manual intervention by admin/governance"""
        threat = ThreatDetection(
            threat_id=f"manual_{entity}_{int(time.time())}",
            threat_type="manual_intervention",
            threat_level=ThreatLevel.HIGH,
            entity=entity,
            evidence=f"Manual intervention: {reason}"
        )
        
        self._execute_intervention(threat, action)
        threat.intervened = True
        threat.intervention_action = action
        
        self.intervention_history.append(threat)
        return True
    
    def unban_entity(self, entity: str, reason: str) -> bool:
        """Remove entity from all bans/blacklists"""
        removed = False
        
        if entity in self.permanent_bans:
            self.permanent_bans.remove(entity)
            removed = True
        
        if entity in self.temporary_bans:
            del self.temporary_bans[entity]
            removed = True
        
        if entity in self.oracle_blacklist:
            self.oracle_blacklist.remove(entity)
            removed = True
        
        if entity in self.isolated_validators:
            self.isolated_validators.remove(entity)
            removed = True
        
        if removed:
            print(f"✅ UNBANNED: {entity} - Reason: {reason}")
            self.false_positives += 1
        
        return removed
    
    def resume_governance(self, authorized_by: str) -> bool:
        """Resume governance after pause"""
        if self.governance_paused:
            self.governance_paused = False
            print(f"✅ GOVERNANCE RESUMED by {authorized_by}")
            return True
        return False
    
    def emergency_shutdown_override(self, authorized_by: str, 
                                   authorization_code: str) -> bool:
        """Override emergency shutdown (requires authorization)"""
        # In production, would verify cryptographic signature
        if authorization_code == "OVERRIDE_EMERGENCY":
            self.emergency_shutdown_active = False
            print(f"✅ EMERGENCY SHUTDOWN DEACTIVATED by {authorized_by}")
            return True
        return False
    
    def get_active_threats(self, min_level: Optional[ThreatLevel] = None) -> List[ThreatDetection]:
        """Get all active threats, optionally filtered by severity"""
        threats = list(self.active_threats.values())
        
        if min_level:
            level_priority = {
                ThreatLevel.LOW: 0,
                ThreatLevel.MEDIUM: 1,
                ThreatLevel.HIGH: 2,
                ThreatLevel.CRITICAL: 3
            }
            min_priority = level_priority[min_level]
            threats = [t for t in threats if level_priority[t.threat_level] >= min_priority]
        
        return sorted(threats, key=lambda t: t.detected_at, reverse=True)
    
    def slash_validator_stake(
        self,
        validator_address: str,
        slash_amount_nxt: float,
        reason: str
    ) -> Tuple[bool, str, Optional[Any]]:
        """
        Slash validator stake through physics substrate.
        
        Routes penalty slashing through PhysicsEconomicsAdapter.
        Slashed funds route to TRANSITION_RESERVE.
        Gated on settlement_success.
        
        Args:
            validator_address: Validator being slashed
            slash_amount_nxt: Amount to slash
            reason: Justification for slashing
            
        Returns:
            (success, message, substrate_transaction)
        """
        if not SUBSTRATE_AVAILABLE or get_physics_adapter is None:
            return False, "Physics substrate not available", None
        
        adapter = get_physics_adapter()
        
        substrate_tx = adapter.process_orbital_transfer(
            source_address=validator_address,
            recipient_address="TRANSITION_RESERVE",
            amount_nxt=slash_amount_nxt,
            wavelength_nm=380.0,
            module=EconomicModule.INTERVENTION,
            transfer_id=f"SLASH_{validator_address[:8]}_{int(time.time())}"
        )
        
        if not substrate_tx.settlement_success:
            return False, f"Slashing settlement failed: {substrate_tx.message}", substrate_tx
        
        return True, f"Slashed {slash_amount_nxt:.4f} NXT from {validator_address}: {reason}", substrate_tx
    
    def compensate_victim(
        self,
        victim_address: str,
        compensation_nxt: float,
        attacker_address: str,
        attack_type: str
    ) -> Tuple[bool, str, Optional[Any]]:
        """
        Compensate attack victim through physics substrate.
        
        Routes compensation from ECOSYSTEM_FUND to victim.
        Uses emergency liquidity primitives for immediate payout.
        
        Args:
            victim_address: Address of attack victim
            compensation_nxt: Compensation amount
            attacker_address: Who caused the damage
            attack_type: Type of attack
            
        Returns:
            (success, message, substrate_transaction)
        """
        if not SUBSTRATE_AVAILABLE or get_physics_adapter is None:
            return False, "Physics substrate not available", None
        
        adapter = get_physics_adapter()
        
        substrate_tx = adapter.process_emergency_liquidity(
            source_pool="ECOSYSTEM_FUND",
            recipient_address=victim_address,
            amount_nxt=compensation_nxt,
            crisis_level=CrisisLevel.WARNING,
            reason=f"COMPENSATION_{attack_type}: Victim of {attacker_address[:12]}",
            wavelength_nm=550.0
        )
        
        if not substrate_tx.settlement_success:
            return False, f"Compensation settlement failed: {substrate_tx.message}", substrate_tx
        
        return True, f"Compensated {victim_address}: {compensation_nxt:.4f} NXT", substrate_tx
    
    def trigger_economic_emergency(
        self,
        crisis_reason: str,
        emergency_fund_nxt: float,
        responder_address: str
    ) -> Tuple[bool, str, Optional[Any]]:
        """
        Trigger economic emergency response through physics substrate.
        
        Deploys emergency liquidity for crisis mitigation.
        Updates substrate crisis level to EMERGENCY.
        
        Args:
            crisis_reason: Description of the crisis
            emergency_fund_nxt: Amount to deploy
            responder_address: Who receives emergency funds
            
        Returns:
            (success, message, substrate_transaction)
        """
        if not SUBSTRATE_AVAILABLE or get_physics_adapter is None:
            return False, "Physics substrate not available", None
        
        adapter = get_physics_adapter()
        
        adapter.set_crisis_level(CrisisLevel.EMERGENCY, crisis_reason)
        
        substrate_tx = adapter.process_emergency_liquidity(
            source_pool="VALIDATOR_POOL",
            recipient_address=responder_address,
            amount_nxt=emergency_fund_nxt,
            crisis_level=CrisisLevel.EMERGENCY,
            reason=f"ECONOMIC_EMERGENCY: {crisis_reason}",
            wavelength_nm=380.0
        )
        
        if not substrate_tx.settlement_success:
            return False, f"Emergency response failed: {substrate_tx.message}", substrate_tx
        
        return True, f"Emergency deployed: {emergency_fund_nxt:.4f} NXT for {crisis_reason}", substrate_tx
    
    def sync_crisis_level_with_threat(self, threat: ThreatDetection) -> bool:
        """
        Sync physics substrate crisis level with current threat level.
        
        Maps threat levels to crisis levels for coordinated response.
        
        Args:
            threat: Current threat detection
            
        Returns:
            True if crisis level was updated
        """
        if not SUBSTRATE_AVAILABLE or get_physics_adapter is None:
            return False
        
        adapter = get_physics_adapter()
        
        threat_to_crisis = {
            ThreatLevel.LOW: CrisisLevel.NORMAL,
            ThreatLevel.MEDIUM: CrisisLevel.ELEVATED,
            ThreatLevel.HIGH: CrisisLevel.WARNING,
            ThreatLevel.CRITICAL: CrisisLevel.CRITICAL
        }
        
        new_level = threat_to_crisis.get(threat.threat_level, CrisisLevel.NORMAL)
        
        return adapter.set_crisis_level(
            level=new_level,
            reason=f"Threat: {threat.threat_type} from {threat.entity}"
        )
    
    def get_substrate_intervention_summary(self) -> Dict[str, Any]:
        """Get intervention stats with substrate integration status"""
        base_stats = self.get_intervention_stats()
        
        substrate_status = {
            "substrate_available": SUBSTRATE_AVAILABLE,
            "slashing_enabled": SUBSTRATE_AVAILABLE,
            "compensation_enabled": SUBSTRATE_AVAILABLE,
            "emergency_response_enabled": SUBSTRATE_AVAILABLE
        }
        
        if SUBSTRATE_AVAILABLE and get_physics_adapter:
            adapter = get_physics_adapter()
            crisis_status = adapter.get_crisis_status()
            substrate_status["current_crisis_level"] = crisis_status.get("current_crisis_level", "unknown")
            substrate_status["active_liquidity_locks"] = crisis_status.get("active_liquidity_locks", 0)
            substrate_status["total_emergency_deployed_nxt"] = crisis_status.get("total_emergency_deployed_nxt", 0)
        
        return {
            **base_stats,
            "substrate_integration": substrate_status
        }
    
    def get_intervention_stats(self) -> Dict:
        """Get intervention statistics"""
        recent_24h = [t for t in self.intervention_history 
                     if time.time() - t.detected_at < 86400]
        
        return {
            "total_interventions": self.total_interventions,
            "threats_blocked": self.threats_blocked,
            "false_positives": self.false_positives,
            "permanent_bans": len(self.permanent_bans),
            "temporary_bans": len(self.temporary_bans),
            "oracle_blacklist": len(self.oracle_blacklist),
            "isolated_validators": len(self.isolated_validators),
            "governance_paused": self.governance_paused,
            "emergency_shutdown": self.emergency_shutdown_active,
            "interventions_24h": len(recent_24h),
            "active_threats": len(self.active_threats)
        }


# Global singleton
_intervention_engine = None

def get_intervention_engine() -> ActiveInterventionEngine:
    """Get global intervention engine instance"""
    global _intervention_engine
    if _intervention_engine is None:
        _intervention_engine = ActiveInterventionEngine()
    return _intervention_engine
