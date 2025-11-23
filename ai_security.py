"""
NexusOS AI Security & Gaming Prevention
Protection against AI system exploitation and manipulation

Features:
- AI contribution score anomaly detection
- AI decision pattern analysis
- Training data poisoning prevention
- Behavior-based fraud detection
"""

import time
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from collections import deque, defaultdict
import hashlib


@dataclass
class AnomalyAlert:
    """AI anomaly alert"""
    alert_id: str
    address: str
    anomaly_type: str
    severity: float  # 0.0 to 1.0
    timestamp: float
    evidence: Dict[str, Any]
    action_taken: Optional[str] = None


class AIContributionAnomalyDetector:
    """
    Detect anomalous patterns in AI contribution scores
    
    Monitors for:
    - Sudden spikes in contribution scores
    - Coordinated gaming by multiple addresses
    - Repetitive/scripted behavior patterns
    - Statistical outliers
    """
    
    def __init__(self):
        # Contribution history (address -> deque of (timestamp, score))
        self.contribution_history: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=1000)
        )
        
        # Behavioral fingerprints
        self.behavior_fingerprints: Dict[str, List[str]] = defaultdict(list)
        
        # Anomaly alerts
        self.alerts: List[AnomalyAlert] = []
        
        # Detection thresholds
        self.spike_threshold = 3.0  # 3 standard deviations
        self.repetition_threshold = 0.8  # 80% identical actions
        self.velocity_threshold = 100.0  # Max score per hour
    
    def record_contribution(
        self,
        address: str,
        score: float,
        action_type: str,
        context: Dict[str, Any]
    ):
        """Record contribution for analysis"""
        timestamp = time.time()
        
        # Store contribution
        self.contribution_history[address].append((timestamp, score))
        
        # Create behavioral fingerprint
        fingerprint = hashlib.sha256(
            f"{action_type}:{sorted(context.items())}".encode()
        ).hexdigest()
        
        self.behavior_fingerprints[address].append(fingerprint)
    
    def detect_score_spike(
        self,
        address: str,
        new_score: float
    ) -> Tuple[bool, Optional[str]]:
        """
        Detect sudden spike in contribution score
        
        Returns:
            (is_anomaly: bool, evidence: Optional[str])
        """
        history = self.contribution_history[address]
        
        if len(history) < 10:
            return False, None  # Need baseline
        
        # Get recent scores
        recent_scores = [score for _, score in list(history)[-10:]]
        
        # Calculate statistics
        mean_score = np.mean(recent_scores)
        std_score = np.std(recent_scores)
        
        if std_score == 0:
            return False, None
        
        # Z-score
        z_score = (new_score - mean_score) / std_score
        
        if abs(z_score) > self.spike_threshold:
            evidence = f"Score spike detected: {new_score:.2f} vs mean {mean_score:.2f} (z={z_score:.2f})"
            return True, evidence
        
        return False, None
    
    def detect_repetitive_behavior(
        self,
        address: str,
        window: int = 50
    ) -> Tuple[bool, Optional[str]]:
        """
        Detect repetitive/scripted behavior
        
        Returns:
            (is_anomaly: bool, evidence: Optional[str])
        """
        fingerprints = self.behavior_fingerprints[address]
        
        if len(fingerprints) < window:
            return False, None
        
        # Get recent fingerprints
        recent = fingerprints[-window:]
        
        # Calculate uniqueness
        unique_count = len(set(recent))
        uniqueness = unique_count / len(recent)
        
        if uniqueness < (1 - self.repetition_threshold):
            evidence = f"Repetitive behavior: only {unique_count}/{len(recent)} unique actions ({uniqueness:.1%})"
            return True, evidence
        
        return False, None
    
    def detect_velocity_anomaly(
        self,
        address: str,
        time_window: int = 3600
    ) -> Tuple[bool, Optional[str]]:
        """
        Detect abnormally high contribution velocity
        
        Returns:
            (is_anomaly: bool, evidence: Optional[str])
        """
        current_time = time.time()
        cutoff = current_time - time_window
        
        # Get contributions in window
        recent = [
            score for timestamp, score in self.contribution_history[address]
            if timestamp > cutoff
        ]
        
        if not recent:
            return False, None
        
        # Calculate velocity (score per hour)
        total_score = sum(recent)
        hours = time_window / 3600
        velocity = total_score / hours
        
        if velocity > self.velocity_threshold:
            evidence = f"High velocity: {velocity:.2f} score/hour (threshold: {self.velocity_threshold})"
            return True, evidence
        
        return False, None
    
    def check_all_anomalies(
        self,
        address: str,
        new_score: float,
        action_type: str,
        context: Dict[str, Any]
    ) -> List[AnomalyAlert]:
        """
        Run all anomaly checks
        
        Returns:
            List of anomaly alerts
        """
        alerts = []
        
        # Record contribution
        self.record_contribution(address, new_score, action_type, context)
        
        # Check for spikes
        is_spike, spike_evidence = self.detect_score_spike(address, new_score)
        if is_spike:
            alert = AnomalyAlert(
                alert_id=hashlib.sha256(f"{address}:{time.time()}:spike".encode()).hexdigest()[:16],
                address=address,
                anomaly_type="contribution_spike",
                severity=0.8,
                timestamp=time.time(),
                evidence={"description": spike_evidence, "score": new_score}
            )
            alerts.append(alert)
            self.alerts.append(alert)
        
        # Check for repetition
        is_repetitive, rep_evidence = self.detect_repetitive_behavior(address)
        if is_repetitive:
            alert = AnomalyAlert(
                alert_id=hashlib.sha256(f"{address}:{time.time()}:repetition".encode()).hexdigest()[:16],
                address=address,
                anomaly_type="repetitive_behavior",
                severity=0.6,
                timestamp=time.time(),
                evidence={"description": rep_evidence}
            )
            alerts.append(alert)
            self.alerts.append(alert)
        
        # Check velocity
        is_velocity, vel_evidence = self.detect_velocity_anomaly(address)
        if is_velocity:
            alert = AnomalyAlert(
                alert_id=hashlib.sha256(f"{address}:{time.time()}:velocity".encode()).hexdigest()[:16],
                address=address,
                anomaly_type="high_velocity",
                severity=0.7,
                timestamp=time.time(),
                evidence={"description": vel_evidence}
            )
            alerts.append(alert)
            self.alerts.append(alert)
        
        return alerts
    
    def get_trust_score(self, address: str) -> float:
        """
        Calculate trust score for address (0.0 to 1.0)
        
        Based on:
        - Number of anomalies
        - Severity of anomalies
        - Time since last anomaly
        """
        # Get recent alerts for this address
        current_time = time.time()
        recent_alerts = [
            alert for alert in self.alerts
            if alert.address == address and current_time - alert.timestamp < 86400  # Last 24 hours
        ]
        
        if not recent_alerts:
            return 1.0  # Perfect trust
        
        # Calculate penalty
        severity_sum = sum(alert.severity for alert in recent_alerts)
        
        # Trust score inversely proportional to severity
        trust_score = max(0.0, 1.0 - (severity_sum / 10.0))
        
        return trust_score


class LiquidityProtection:
    """
    Protect DEX liquidity from coordinated drains
    
    Features:
    - Withdrawal time-locks
    - Gradual withdrawal limits
    - Coordinated drain detection
    """
    
    def __init__(self):
        # Withdrawal requests (request_id -> request data)
        self.withdrawal_requests: Dict[str, Dict[str, Any]] = {}
        
        # Time-lock duration (seconds)
        self.timelock_duration = 86400  # 24 hours
        
        # Gradual withdrawal limits
        self.max_withdrawal_percentage = 0.1  # 10% of pool per day
        
        # Daily withdrawal tracking (pool_id -> (date, total_withdrawn))
        self.daily_withdrawals: Dict[str, Tuple[str, float]] = {}
    
    def request_withdrawal(
        self,
        address: str,
        pool_id: str,
        amount: float,
        pool_balance: float
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Request liquidity withdrawal with time-lock
        
        Returns:
            (success: bool, request_id: Optional[str], error: Optional[str])
        """
        # Check daily limit
        current_date = time.strftime("%Y-%m-%d")
        
        if pool_id in self.daily_withdrawals:
            date, total = self.daily_withdrawals[pool_id]
            
            if date == current_date:
                # Check if adding this withdrawal exceeds limit
                percentage = (total + amount) / pool_balance
                
                if percentage > self.max_withdrawal_percentage:
                    return False, None, f"Daily withdrawal limit reached ({percentage:.1%} of pool, max {self.max_withdrawal_percentage:.1%})"
        
        # Create withdrawal request
        request_id = hashlib.sha256(
            f"{address}:{pool_id}:{amount}:{time.time()}".encode()
        ).hexdigest()[:16]
        
        unlock_time = time.time() + self.timelock_duration
        
        self.withdrawal_requests[request_id] = {
            "address": address,
            "pool_id": pool_id,
            "amount": amount,
            "request_time": time.time(),
            "unlock_time": unlock_time,
            "status": "pending"
        }
        
        return True, request_id, None
    
    def execute_withdrawal(
        self,
        request_id: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Execute withdrawal after time-lock expires
        
        Returns:
            (success: bool, error: Optional[str])
        """
        if request_id not in self.withdrawal_requests:
            return False, "Withdrawal request not found"
        
        request = self.withdrawal_requests[request_id]
        
        # Check time-lock
        if time.time() < request["unlock_time"]:
            remaining = request["unlock_time"] - time.time()
            return False, f"Time-lock active. Wait {remaining:.0f}s ({remaining/3600:.1f} hours)"
        
        # Check status
        if request["status"] != "pending":
            return False, f"Request already {request['status']}"
        
        # Mark as executed
        request["status"] = "executed"
        request["execution_time"] = time.time()
        
        # Update daily withdrawal tracking
        pool_id = request["pool_id"]
        amount = request["amount"]
        current_date = time.strftime("%Y-%m-%d")
        
        if pool_id in self.daily_withdrawals:
            date, total = self.daily_withdrawals[pool_id]
            
            if date == current_date:
                self.daily_withdrawals[pool_id] = (date, total + amount)
            else:
                self.daily_withdrawals[pool_id] = (current_date, amount)
        else:
            self.daily_withdrawals[pool_id] = (current_date, amount)
        
        return True, None
    
    def cancel_withdrawal(
        self,
        request_id: str,
        address: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Cancel pending withdrawal
        
        Returns:
            (success: bool, error: Optional[str])
        """
        if request_id not in self.withdrawal_requests:
            return False, "Withdrawal request not found"
        
        request = self.withdrawal_requests[request_id]
        
        # Verify ownership
        if request["address"] != address:
            return False, "Not authorized to cancel this request"
        
        # Check status
        if request["status"] != "pending":
            return False, f"Cannot cancel {request['status']} request"
        
        # Cancel
        request["status"] = "cancelled"
        request["cancellation_time"] = time.time()
        
        return True, None
    
    def get_withdrawal_status(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get withdrawal request status"""
        if request_id not in self.withdrawal_requests:
            return None
        
        request = self.withdrawal_requests[request_id]
        
        time_remaining = max(0, request["unlock_time"] - time.time())
        
        return {
            "request_id": request_id,
            "address": request["address"],
            "pool_id": request["pool_id"],
            "amount": request["amount"],
            "status": request["status"],
            "time_remaining": time_remaining,
            "unlock_time": request["unlock_time"]
        }


# Singleton instances
_anomaly_detector = None
_liquidity_protection = None

def get_anomaly_detector() -> AIContributionAnomalyDetector:
    """Get singleton anomaly detector"""
    global _anomaly_detector
    if _anomaly_detector is None:
        _anomaly_detector = AIContributionAnomalyDetector()
    return _anomaly_detector

def get_liquidity_protection() -> LiquidityProtection:
    """Get singleton liquidity protection"""
    global _liquidity_protection
    if _liquidity_protection is None:
        _liquidity_protection = LiquidityProtection()
    return _liquidity_protection
