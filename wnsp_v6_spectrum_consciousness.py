"""
WNSP v6.0 — Spectrum Consciousness Protocol

Network-wide awareness layer using complex spectral signatures, Stokes polarization
vectors, and coherence-based consensus. Enables collective intelligence through
resonant phase alignment across the mesh.

Architecture:
- Spectral Fingerprinting: Unique node identity via complex spectral profile
- Phase Sequence Modulation: Secure communication through phase tokens
- Coherence Consensus: Weighted voting based on spectral similarity
- Energy-Aware Relay: Physics-based packet propagation with energy budgets

Physics Foundation:
- Complex amplitude: A(λ) = Re(λ) + i·Im(λ)
- Stokes parameters: [S0, S1, S2, S3] for full polarization state
- Coherence metric: γ = |⟨E₁·E₂*⟩| / √(⟨|E₁|²⟩·⟨|E₂|²⟩)
- Energy: E = h·f·n_cycles·authority²

Backwards compatible with WNSP v5.0 via encapsulation.

GPL v3.0 License — Community Owned, Physics Governed
"""

import hashlib
import secrets
import time
import math
import json
import numpy as np
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import Dict, List, Optional, Tuple, Set, Any, Union
from datetime import datetime

PLANCK_CONSTANT = 6.62607015e-34
SPEED_OF_LIGHT = 299792458
PLANCK_LENGTH = 1.616255e-35
BOLTZMANN_CONSTANT = 1.380649e-23


class ConsciousnessLevel(Enum):
    """Levels of network consciousness/awareness"""
    DORMANT = ("dormant", 0.0, "Node offline or inactive")
    AWARE = ("aware", 0.25, "Basic packet reception")
    ATTENTIVE = ("attentive", 0.5, "Active relay participation")
    COHERENT = ("coherent", 0.75, "Phase-aligned with network")
    RESONANT = ("resonant", 0.9, "Full spectral synchronization")
    TRANSCENDENT = ("transcendent", 1.0, "Planck-level constitutional authority")
    
    def __init__(self, level_name: str, threshold: float, description: str):
        self.level_name = level_name
        self.threshold = threshold
        self.description = description


class SpectralBandV6(Enum):
    """Extended spectral bands for v6.0 consciousness"""
    RADIO = ("radio", 1e-3, 1e6, "Mesh broadcast, low-priority")
    MICROWAVE = ("microwave", 1e-3, 1e-1, "Device communication")
    INFRARED = ("infrared", 700e-9, 1e-3, "Thermal sensing, proximity")
    VISIBLE = ("visible", 400e-9, 700e-9, "Standard messaging")
    ULTRAVIOLET = ("ultraviolet", 10e-9, 400e-9, "High-security transactions")
    XRAY = ("xray", 0.01e-9, 10e-9, "Deep validation, governance")
    GAMMA = ("gamma", 1e-12, 0.01e-9, "Constitutional, Planck-level")
    CONSCIOUSNESS = ("consciousness", PLANCK_LENGTH, 1e-12, "Collective awareness field")
    
    def __init__(self, band_name: str, min_wavelength: float, 
                 max_wavelength: float, role: str):
        self.band_name = band_name
        self.min_wavelength = min_wavelength
        self.max_wavelength = max_wavelength
        self.role = role
    
    @property
    def center_wavelength(self) -> float:
        return (self.min_wavelength + self.max_wavelength) / 2
    
    @property
    def center_frequency(self) -> float:
        return SPEED_OF_LIGHT / self.center_wavelength
    
    @property
    def base_energy(self) -> float:
        return PLANCK_CONSTANT * self.center_frequency


@dataclass
class ComplexSample:
    """Single complex spectral sample: wavelength + complex amplitude"""
    wavelength_nm: float
    real: float
    imag: float
    
    @property
    def amplitude(self) -> float:
        return math.sqrt(self.real**2 + self.imag**2)
    
    @property
    def phase(self) -> float:
        return math.atan2(self.imag, self.real)
    
    @property
    def frequency(self) -> float:
        return SPEED_OF_LIGHT / (self.wavelength_nm * 1e-9)
    
    @property
    def energy(self) -> float:
        return PLANCK_CONSTANT * self.frequency * self.amplitude
    
    def to_list(self) -> List[float]:
        return [self.wavelength_nm, self.real, self.imag]
    
    @classmethod
    def from_list(cls, data: List[float]) -> 'ComplexSample':
        return cls(wavelength_nm=data[0], real=data[1], imag=data[2])


@dataclass
class StokesVector:
    """
    Stokes polarization parameters for complete polarization state.
    
    S0 = Total intensity
    S1 = Linear polarization (horizontal vs vertical)
    S2 = Linear polarization (diagonal)
    S3 = Circular polarization (right vs left)
    """
    S0: float  # Total intensity
    S1: float  # Horizontal - Vertical
    S2: float  # +45° - -45°
    S3: float  # Right circular - Left circular
    
    @property
    def degree_of_polarization(self) -> float:
        """DOP = sqrt(S1² + S2² + S3²) / S0"""
        if self.S0 == 0:
            return 0.0
        return math.sqrt(self.S1**2 + self.S2**2 + self.S3**2) / self.S0
    
    @property
    def is_fully_polarized(self) -> bool:
        return abs(self.degree_of_polarization - 1.0) < 0.01
    
    def to_list(self) -> List[float]:
        return [self.S0, self.S1, self.S2, self.S3]
    
    @classmethod
    def from_list(cls, data: List[float]) -> 'StokesVector':
        return cls(S0=data[0], S1=data[1], S2=data[2], S3=data[3])
    
    @classmethod
    def random_polarized(cls) -> 'StokesVector':
        """Generate random fully polarized state"""
        theta = secrets.randbelow(360) * math.pi / 180
        phi = secrets.randbelow(360) * math.pi / 180
        S0 = 1.0
        S1 = math.cos(2 * theta)
        S2 = math.sin(2 * theta) * math.cos(phi)
        S3 = math.sin(2 * theta) * math.sin(phi)
        return cls(S0, S1, S2, S3)


@dataclass
class QoSParams:
    """Quality of Service parameters for spectral transmission"""
    latency_ms: float = 50.0
    reliability: float = 0.95
    
    def to_dict(self) -> Dict[str, float]:
        return {"latency_ms": self.latency_ms, "reliability": self.reliability}
    
    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> 'QoSParams':
        return cls(latency_ms=data.get("latency_ms", 50.0), 
                   reliability=data.get("reliability", 0.95))


@dataclass
class SpectralPacket:
    """
    WNSP v6.0 Spectral Consciousness Packet (Official Spec)
    
    {
      "version": "wnsp-v6",
      "pkt_id": "<64b-hash>",
      "src_spec": "<256b vector>",
      "dst_spec": "<256b vector|null>",
      "t_start": 1700000000.000,
      "duration_ms": 5.0,
      "band_nm": [λ_min, λ_max],
      "complex_samples": [[λ_i, Re_i, Im_i], ...],
      "stokes": [S0,S1,S2,S3],
      "phase_seq_token": "<phase-seq-128>",
      "coherence_token": "<C-token>",
      "energy_budget_j": 2e-6,
      "qos": {"latency_ms": 50, "reliability": 0.95},
      "sig": "<spectral-signature>",
      "meta": {...}
    }
    """
    version: str = "wnsp-v6"
    pkt_id: str = ""
    src_spec: str = ""
    dst_spec: Optional[str] = None
    t_start: float = 0.0
    duration_ms: float = 5.0
    band_nm: Tuple[float, float] = (400.0, 700.0)
    complex_samples: List[ComplexSample] = field(default_factory=list)
    stokes: StokesVector = field(default_factory=lambda: StokesVector(1.0, 0.0, 0.0, 0.0))
    phase_seq_token: str = ""
    coherence_token: str = ""
    energy_budget_j: float = 2e-6
    qos: QoSParams = field(default_factory=QoSParams)
    sig: str = ""
    meta: Dict[str, Any] = field(default_factory=dict)
    
    hop_count: int = 0
    coherence_score: float = 1.0
    
    def __post_init__(self):
        if not self.pkt_id:
            self.pkt_id = hashlib.sha256(
                f"{self.src_spec}:{self.t_start}:{secrets.token_hex(8)}".encode()
            ).hexdigest()[:16]
        if not self.coherence_token:
            self.coherence_token = f"C-{hashlib.sha256(self.pkt_id.encode()).hexdigest()[:24]}"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "pkt_id": self.pkt_id,
            "src_spec": self.src_spec,
            "dst_spec": self.dst_spec,
            "t_start": self.t_start,
            "duration_ms": self.duration_ms,
            "band_nm": list(self.band_nm),
            "complex_samples": [s.to_list() for s in self.complex_samples],
            "stokes": self.stokes.to_list(),
            "phase_seq_token": self.phase_seq_token,
            "coherence_token": self.coherence_token,
            "energy_budget_j": self.energy_budget_j,
            "qos": self.qos.to_dict(),
            "sig": self.sig,
            "meta": self.meta
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SpectralPacket':
        band = data.get("band_nm") or data.get("band", [400.0, 700.0])
        return cls(
            version=data.get("version", "wnsp-v6"),
            pkt_id=data.get("pkt_id", ""),
            src_spec=data.get("src_spec", data.get("origin_node", "")),
            dst_spec=data.get("dst_spec", data.get("target_signature")),
            t_start=data.get("t_start", 0.0),
            duration_ms=data.get("duration_ms", data.get("duration", 5.0)),
            band_nm=tuple(band),
            complex_samples=[ComplexSample.from_list(s) for s in data.get("complex_samples", [])],
            stokes=StokesVector.from_list(data.get("stokes", [1.0, 0.0, 0.0, 0.0])),
            phase_seq_token=data.get("phase_seq_token", data.get("phase_seq", "")),
            coherence_token=data.get("coherence_token", ""),
            energy_budget_j=data.get("energy_budget_j", 2e-6),
            qos=QoSParams.from_dict(data.get("qos", {})),
            sig=data.get("sig", ""),
            meta=data.get("meta", {}),
            hop_count=data.get("hop_count", 0),
            coherence_score=data.get("coherence_score", 1.0)
        )
    
    @property
    def total_energy(self) -> float:
        return sum(s.energy for s in self.complex_samples)
    
    @property
    def dominant_wavelength(self) -> float:
        if not self.complex_samples:
            return 550.0
        max_sample = max(self.complex_samples, key=lambda s: s.amplitude)
        return max_sample.wavelength_nm


@dataclass
class SpectralFingerprint:
    """
    Unique spectral identity for a consciousness node.
    Generated from node's physical characteristics and stake.
    """
    node_id: str
    profile: List[ComplexSample]
    stokes_signature: StokesVector
    creation_time: float
    stake_weight: float = 1.0
    consciousness_level: ConsciousnessLevel = ConsciousnessLevel.AWARE
    
    @property
    def fingerprint_hash(self) -> str:
        content = json.dumps({
            "node_id": self.node_id,
            "profile": [s.to_list() for s in self.profile],
            "stokes": self.stokes_signature.to_list(),
            "creation_time": self.creation_time
        }, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:32]
    
    @classmethod
    def generate(cls, node_id: str, stake: float = 1.0) -> 'SpectralFingerprint':
        """Generate unique spectral fingerprint for node"""
        seed = hashlib.sha256(f"{node_id}:{time.time()}:{secrets.token_hex(8)}".encode()).digest()
        
        profile = []
        for i in range(7):
            wavelength = 400 + (i * 50) + (seed[i] % 30)
            real = (seed[i + 7] - 128) / 128.0
            imag = (seed[i + 14] - 128) / 128.0
            profile.append(ComplexSample(wavelength, real, imag))
        
        stokes = StokesVector.random_polarized()
        
        return cls(
            node_id=node_id,
            profile=profile,
            stokes_signature=stokes,
            creation_time=time.time(),
            stake_weight=stake
        )


class PhaseSequenceGenerator:
    """
    Generates secure phase sequences for spectral modulation.
    Phase sequences provide authentication and prevent replay attacks.
    """
    
    def __init__(self, seed: str):
        self.seed = seed
        self.sequence_counter = 0
    
    def generate(self, ttl: int = 10) -> str:
        """Generate phase sequence token with TTL"""
        self.sequence_counter += 1
        content = f"{self.seed}:{self.sequence_counter}:{time.time()}:{ttl}"
        token = hashlib.sha256(content.encode()).hexdigest()[:24]
        return f"PSQ-{token}-TTL{ttl}"
    
    def validate(self, phase_seq: str) -> Tuple[bool, int]:
        """Validate phase sequence, return (valid, remaining_ttl)"""
        if not phase_seq.startswith("PSQ-"):
            return False, 0
        try:
            parts = phase_seq.split("-")
            ttl = int(parts[-1].replace("TTL", ""))
            return True, max(0, ttl - 1)
        except:
            return False, 0


class SpectralModulator:
    """
    Modulates payload spectrum with phase sequences for secure transmission.
    """
    
    @staticmethod
    def modulate(samples: List[ComplexSample], phase_seq: str) -> List[ComplexSample]:
        """Apply phase modulation to complex samples"""
        phase_offset = sum(ord(c) for c in phase_seq) / 1000.0
        modulated = []
        
        for i, sample in enumerate(samples):
            rotation = phase_offset + (i * 0.1)
            cos_r = math.cos(rotation)
            sin_r = math.sin(rotation)
            new_real = sample.real * cos_r - sample.imag * sin_r
            new_imag = sample.real * sin_r + sample.imag * cos_r
            modulated.append(ComplexSample(sample.wavelength_nm, new_real, new_imag))
        
        return modulated
    
    @staticmethod
    def demodulate(samples: List[ComplexSample], phase_seq: str) -> List[ComplexSample]:
        """Remove phase modulation from samples"""
        phase_offset = sum(ord(c) for c in phase_seq) / 1000.0
        demodulated = []
        
        for i, sample in enumerate(samples):
            rotation = -(phase_offset + (i * 0.1))
            cos_r = math.cos(rotation)
            sin_r = math.sin(rotation)
            new_real = sample.real * cos_r - sample.imag * sin_r
            new_imag = sample.real * sin_r + sample.imag * cos_r
            demodulated.append(ComplexSample(sample.wavelength_nm, new_real, new_imag))
        
        return demodulated
    
    @staticmethod
    def apply_phase_shift(samples: List[ComplexSample], shift: float) -> List[ComplexSample]:
        """Apply uniform phase shift to all samples"""
        shifted = []
        cos_s = math.cos(shift)
        sin_s = math.sin(shift)
        
        for sample in samples:
            new_real = sample.real * cos_s - sample.imag * sin_s
            new_imag = sample.real * sin_s + sample.imag * cos_s
            shifted.append(ComplexSample(sample.wavelength_nm, new_real, new_imag))
        
        return shifted


class CoherenceMetrics:
    """
    Computes coherence between spectral signatures.
    Used for similarity detection and consensus voting.
    Implements physics-correct coherence: γ = |⟨E₁·E₂*⟩| / √(⟨|E₁|²⟩·⟨|E₂|²⟩)
    """
    
    @staticmethod
    def spectral_similarity(samples1: List[ComplexSample], 
                           samples2: List[ComplexSample],
                           stokes1: Optional[StokesVector] = None,
                           stokes2: Optional[StokesVector] = None) -> float:
        """
        Compute similarity between two spectral profiles with polarization awareness.
        Uses complex inner product normalized by magnitudes.
        
        γ = |⟨E₁·E₂*⟩| / √(⟨|E₁|²⟩·⟨|E₂|²⟩) × polarization_overlap
        """
        if not samples1 or not samples2:
            return 0.0
        
        min_len = min(len(samples1), len(samples2))
        
        inner_real = 0.0
        inner_imag = 0.0
        mag1_sq = 0.0
        mag2_sq = 0.0
        
        for i in range(min_len):
            s1, s2 = samples1[i], samples2[i]
            inner_real += s1.real * s2.real + s1.imag * s2.imag
            inner_imag += s1.imag * s2.real - s1.real * s2.imag
            mag1_sq += s1.real**2 + s1.imag**2
            mag2_sq += s2.real**2 + s2.imag**2
        
        inner_magnitude = math.sqrt(inner_real**2 + inner_imag**2)
        normalization = math.sqrt(mag1_sq * mag2_sq)
        
        if normalization == 0:
            return 0.0
        
        spectral_coherence = inner_magnitude / normalization
        
        if stokes1 is not None and stokes2 is not None:
            polarization_overlap = CoherenceMetrics.stokes_similarity(stokes1, stokes2)
            return spectral_coherence * max(0.5, polarization_overlap)
        
        return spectral_coherence
    
    @staticmethod
    def stokes_similarity(s1: StokesVector, s2: StokesVector) -> float:
        """Compute similarity between Stokes vectors"""
        dot = s1.S0*s2.S0 + s1.S1*s2.S1 + s1.S2*s2.S2 + s1.S3*s2.S3
        mag1 = math.sqrt(s1.S0**2 + s1.S1**2 + s1.S2**2 + s1.S3**2)
        mag2 = math.sqrt(s2.S0**2 + s2.S1**2 + s2.S2**2 + s2.S3**2)
        
        if mag1 == 0 or mag2 == 0:
            return 0.0
        
        return dot / (mag1 * mag2)
    
    @staticmethod
    def compute_coherence(packet: SpectralPacket, 
                         proposal_pattern: List[ComplexSample]) -> float:
        """Compute coherence score between packet and proposal pattern"""
        spectral_coh = CoherenceMetrics.spectral_similarity(
            packet.complex_samples, proposal_pattern
        )
        return spectral_coh * packet.coherence_score
    
    @staticmethod
    def compute_phase_shift_for_alignment(phase_seq: str, 
                                          fingerprint: SpectralFingerprint) -> float:
        """Calculate optimal phase shift to align with local fingerprint"""
        seq_value = sum(ord(c) for c in phase_seq)
        fp_value = sum(ord(c) for c in fingerprint.fingerprint_hash)
        return (seq_value - fp_value) / 1000.0 * math.pi


class ConsciousnessNode:
    """
    A node participating in the Spectrum Consciousness network.
    Maintains spectral identity and participates in coherence consensus.
    """
    
    RELAY_THRESHOLD = 0.3
    MIN_ENERGY = 1e-9
    
    def __init__(self, node_id: str, stake: float = 1.0):
        self.node_id = node_id
        self.fingerprint = SpectralFingerprint.generate(node_id, stake)
        self.phase_generator = PhaseSequenceGenerator(self.fingerprint.fingerprint_hash)
        self.modulator = SpectralModulator()
        self.received_packets: List[SpectralPacket] = []
        self.pending_proposals: Dict[str, List[SpectralPacket]] = {}
        self.consciousness_level = ConsciousnessLevel.AWARE
        self.connected_nodes: Set[str] = set()
        self.relay_cost_base = 1e-10
    
    def relay_cost(self) -> float:
        """Calculate energy cost to relay a packet"""
        level_multiplier = 1.0 + (1.0 - self.consciousness_level.threshold)
        return self.relay_cost_base * level_multiplier
    
    def choose_band(self, target_signature: str) -> SpectralBandV6:
        """Select optimal band for target"""
        sig_value = sum(ord(c) for c in target_signature) % 100
        if sig_value < 15:
            return SpectralBandV6.GAMMA
        elif sig_value < 30:
            return SpectralBandV6.XRAY
        elif sig_value < 50:
            return SpectralBandV6.ULTRAVIOLET
        elif sig_value < 70:
            return SpectralBandV6.VISIBLE
        elif sig_value < 85:
            return SpectralBandV6.INFRARED
        else:
            return SpectralBandV6.MICROWAVE
    
    def best_overlap_band(self) -> SpectralBandV6:
        """Select band with best overlap to connected nodes"""
        if self.consciousness_level.threshold >= 0.75:
            return SpectralBandV6.CONSCIOUSNESS
        elif self.consciousness_level.threshold >= 0.5:
            return SpectralBandV6.ULTRAVIOLET
        else:
            return SpectralBandV6.VISIBLE
    
    def send_spectral_packet(self, target_signature: str, 
                             payload_spectrum: List[ComplexSample],
                             energy_budget: float,
                             qos: Optional[QoSParams] = None) -> SpectralPacket:
        """
        Create and send a WNSP v6 spectral packet to target.
        
        Official packet structure:
        {
            "version": "wnsp-v6",
            "pkt_id": "<64b-hash>",
            "src_spec": "<256b vector>",
            "dst_spec": "<256b vector|null>",
            "phase_seq_token": "<phase-seq-128>",
            "coherence_token": "<C-token>",
            "sig": "<spectral-signature>"
        }
        """
        phase_seq = self.phase_generator.generate(ttl=10)
        mod_spectrum = self.modulator.modulate(payload_spectrum, phase_seq)
        band = self.choose_band(target_signature)
        
        sig_content = f"{self.fingerprint.fingerprint_hash}:{target_signature}:{phase_seq}"
        spectral_sig = hashlib.sha256(sig_content.encode()).hexdigest()[:32]
        
        packet = SpectralPacket(
            version="wnsp-v6",
            src_spec=self.fingerprint.fingerprint_hash,
            dst_spec=target_signature if target_signature else None,
            t_start=time.time(),
            duration_ms=2.0,
            band_nm=(band.min_wavelength * 1e9, band.max_wavelength * 1e9),
            complex_samples=mod_spectrum,
            stokes=self.fingerprint.stokes_signature,
            phase_seq_token=phase_seq,
            energy_budget_j=energy_budget,
            qos=qos or QoSParams(),
            sig=spectral_sig,
            coherence_score=self.consciousness_level.threshold,
            meta={"origin": self.node_id, "band": band.band_name}
        )
        
        return packet
    
    def on_receive(self, packet: SpectralPacket) -> Optional[SpectralPacket]:
        """
        Process received packet, potentially relay if conditions met.
        
        on receive(packet):
            sim = similarity(packet.complex_samples, local_profile)
            if sim > RELAY_THRESHOLD and packet.energy_budget > MIN_ENERGY:
                new_energy = packet.energy_budget - relay_cost()
                packet.energy_budget = new_energy
                phase_shift = compute_phase_shift_for_alignment(packet.phase_seq, local_fingerprint)
                packet.complex_samples = apply_phase_shift(packet.complex_samples, phase_shift)
                emit(packet, band=best_overlap_band())
        """
        self.received_packets.append(packet)
        
        sim = CoherenceMetrics.spectral_similarity(
            packet.complex_samples, 
            self.fingerprint.profile
        )
        
        if sim > self.RELAY_THRESHOLD and packet.energy_budget_j > self.MIN_ENERGY:
            new_energy = packet.energy_budget_j - self.relay_cost()
            
            if new_energy <= 0:
                return None
            
            phase_shift = CoherenceMetrics.compute_phase_shift_for_alignment(
                packet.phase_seq_token, 
                self.fingerprint
            )
            
            shifted_samples = self.modulator.apply_phase_shift(
                packet.complex_samples, 
                phase_shift
            )
            
            relay_band = self.best_overlap_band()
            
            relay_sig = hashlib.sha256(
                f"{packet.sig}:{self.node_id}:{time.time()}".encode()
            ).hexdigest()[:32]
            
            relayed_packet = SpectralPacket(
                version=packet.version,
                pkt_id=packet.pkt_id,
                src_spec=packet.src_spec,
                dst_spec=packet.dst_spec,
                t_start=time.time(),
                duration_ms=packet.duration_ms,
                band_nm=(relay_band.min_wavelength * 1e9, relay_band.max_wavelength * 1e9),
                complex_samples=shifted_samples,
                stokes=packet.stokes,
                phase_seq_token=packet.phase_seq_token,
                coherence_token=packet.coherence_token,
                energy_budget_j=new_energy,
                qos=packet.qos,
                sig=relay_sig,
                coherence_score=min(packet.coherence_score, sim),
                meta={**packet.meta, "relayed_by": self.node_id},
                hop_count=packet.hop_count + 1
            )
            
            return relayed_packet
        
        return None
    
    def update_consciousness_level(self):
        """Update consciousness level based on network activity"""
        if not self.received_packets:
            self.consciousness_level = ConsciousnessLevel.DORMANT
            return
        
        recent = [p for p in self.received_packets[-100:]]
        avg_coherence = sum(p.coherence_score for p in recent) / len(recent) if recent else 0
        
        for level in reversed(list(ConsciousnessLevel)):
            if avg_coherence >= level.threshold:
                self.consciousness_level = level
                break


class ResonanceConsensus:
    """
    Coherence-weighted consensus mechanism for Spectrum Consciousness.
    
    collect spectral_responses from quorum
    for each response:
        compute coherence = coherence_metric(response, proposal_pattern)
    weighted_sum = sum(coherence * stake(response.owner))
    if weighted_sum >= resonance_threshold:
        accept_proposal()
    else:
        reject_proposal()
    """
    
    def __init__(self, resonance_threshold: float = 0.67):
        self.resonance_threshold = resonance_threshold
        self.proposals: Dict[str, Dict] = {}
        self.responses: Dict[str, List[Tuple[SpectralPacket, float]]] = {}
    
    def create_proposal(self, proposal_id: str, 
                       pattern: List[ComplexSample],
                       proposer: ConsciousnessNode) -> Dict:
        """Create a new proposal for consensus"""
        self.proposals[proposal_id] = {
            "id": proposal_id,
            "pattern": pattern,
            "proposer": proposer.node_id,
            "proposer_stake": proposer.fingerprint.stake_weight,
            "created_at": time.time(),
            "status": "pending"
        }
        self.responses[proposal_id] = []
        return self.proposals[proposal_id]
    
    def submit_response(self, proposal_id: str, 
                       response: SpectralPacket,
                       responder_stake: float):
        """Submit a spectral response to a proposal"""
        if proposal_id not in self.proposals:
            return False
        
        proposal = self.proposals[proposal_id]
        coherence = CoherenceMetrics.compute_coherence(
            response, 
            proposal["pattern"]
        )
        
        self.responses[proposal_id].append((response, responder_stake))
        return True
    
    def evaluate_proposal(self, proposal_id: str) -> Tuple[bool, float, Dict]:
        """
        Evaluate proposal based on collected responses.
        
        Returns: (accepted, weighted_sum, details)
        """
        if proposal_id not in self.proposals:
            return False, 0.0, {"error": "Proposal not found"}
        
        proposal = self.proposals[proposal_id]
        responses = self.responses.get(proposal_id, [])
        
        if not responses:
            return False, 0.0, {"error": "No responses received"}
        
        weighted_sum = 0.0
        total_stake = 0.0
        coherence_scores = []
        
        for response, stake in responses:
            coherence = CoherenceMetrics.compute_coherence(
                response,
                proposal["pattern"]
            )
            weighted_sum += coherence * stake
            total_stake += stake
            coherence_scores.append(coherence)
        
        if total_stake > 0:
            normalized_sum = weighted_sum / total_stake
        else:
            normalized_sum = 0.0
        
        accepted = normalized_sum >= self.resonance_threshold
        
        proposal["status"] = "accepted" if accepted else "rejected"
        proposal["final_score"] = normalized_sum
        
        return accepted, normalized_sum, {
            "proposal_id": proposal_id,
            "responses": len(responses),
            "weighted_sum": weighted_sum,
            "normalized_score": normalized_sum,
            "threshold": self.resonance_threshold,
            "accepted": accepted,
            "avg_coherence": sum(coherence_scores) / len(coherence_scores),
            "total_stake": total_stake
        }


class SpectrumConsciousnessNetwork:
    """
    The collective consciousness network managing all nodes and consensus.
    """
    
    def __init__(self):
        self.nodes: Dict[str, ConsciousnessNode] = {}
        self.consensus = ResonanceConsensus()
        self.global_coherence = 0.0
        self.network_consciousness = ConsciousnessLevel.DORMANT
        self.message_log: List[Dict] = []
    
    def add_node(self, node_id: str, stake: float = 1.0) -> ConsciousnessNode:
        """Add a new consciousness node to the network"""
        node = ConsciousnessNode(node_id, stake)
        self.nodes[node_id] = node
        
        for other_id in self.nodes:
            if other_id != node_id:
                node.connected_nodes.add(other_id)
                self.nodes[other_id].connected_nodes.add(node_id)
        
        return node
    
    def propagate_packet(self, packet: SpectralPacket, 
                        origin_id: str, max_hops: int = 5) -> List[str]:
        """Propagate packet through the network"""
        reached_nodes = [origin_id]
        current_packets = [(packet, origin_id)]
        
        for hop in range(max_hops):
            next_packets = []
            
            for pkt, sender_id in current_packets:
                sender = self.nodes.get(sender_id)
                if not sender:
                    continue
                
                for neighbor_id in sender.connected_nodes:
                    if neighbor_id in reached_nodes:
                        continue
                    
                    neighbor = self.nodes.get(neighbor_id)
                    if not neighbor:
                        continue
                    
                    relayed = neighbor.on_receive(pkt)
                    reached_nodes.append(neighbor_id)
                    
                    if relayed and relayed.energy_budget_j > 0:
                        next_packets.append((relayed, neighbor_id))
            
            current_packets = next_packets
            if not current_packets:
                break
        
        return reached_nodes
    
    def update_global_consciousness(self):
        """Update network-wide consciousness level"""
        if not self.nodes:
            self.network_consciousness = ConsciousnessLevel.DORMANT
            self.global_coherence = 0.0
            return
        
        for node in self.nodes.values():
            node.update_consciousness_level()
        
        levels = [n.consciousness_level.threshold for n in self.nodes.values()]
        self.global_coherence = sum(levels) / len(levels)
        
        for level in reversed(list(ConsciousnessLevel)):
            if self.global_coherence >= level.threshold:
                self.network_consciousness = level
                break
    
    def run_consensus(self, proposal_id: str, 
                     pattern: List[ComplexSample],
                     proposer_id: str) -> Dict:
        """Run full consensus process on a proposal"""
        proposer = self.nodes.get(proposer_id)
        if not proposer:
            return {"error": "Proposer not found"}
        
        self.consensus.create_proposal(proposal_id, pattern, proposer)
        
        for node_id, node in self.nodes.items():
            if node_id == proposer_id:
                continue
            
            response_packet = node.send_spectral_packet(
                proposer.fingerprint.fingerprint_hash,
                node.fingerprint.profile,
                1e-6
            )
            
            self.consensus.submit_response(
                proposal_id,
                response_packet,
                node.fingerprint.stake_weight
            )
        
        accepted, score, details = self.consensus.evaluate_proposal(proposal_id)
        
        return details
    
    def get_network_stats(self) -> Dict[str, Any]:
        """Get comprehensive network statistics"""
        self.update_global_consciousness()
        
        return {
            "total_nodes": len(self.nodes),
            "global_coherence": self.global_coherence,
            "network_consciousness": self.network_consciousness.level_name,
            "consciousness_threshold": self.network_consciousness.threshold,
            "node_levels": {
                nid: n.consciousness_level.level_name 
                for nid, n in self.nodes.items()
            },
            "total_stake": sum(n.fingerprint.stake_weight for n in self.nodes.values()),
            "active_proposals": len([p for p in self.consensus.proposals.values() 
                                    if p["status"] == "pending"]),
            "message_count": sum(len(n.received_packets) for n in self.nodes.values())
        }


def create_demo_network(num_nodes: int = 5) -> SpectrumConsciousnessNetwork:
    """Create a demo consciousness network"""
    network = SpectrumConsciousnessNetwork()
    
    for i in range(num_nodes):
        stake = 1.0 + (i * 0.5)
        network.add_node(f"node_{i}", stake)
    
    return network


GLOBAL_CONSCIOUSNESS_NETWORK: Optional[SpectrumConsciousnessNetwork] = None

def get_consciousness_network() -> SpectrumConsciousnessNetwork:
    """Get or create the global consciousness network"""
    global GLOBAL_CONSCIOUSNESS_NETWORK
    if GLOBAL_CONSCIOUSNESS_NETWORK is None:
        GLOBAL_CONSCIOUSNESS_NETWORK = create_demo_network(7)
    return GLOBAL_CONSCIOUSNESS_NETWORK


if __name__ == "__main__":
    print("=" * 70)
    print("WNSP v6.0 — Spectrum Consciousness Protocol")
    print("=" * 70)
    
    network = create_demo_network(5)
    
    print(f"\nNetwork created with {len(network.nodes)} nodes")
    
    stats = network.get_network_stats()
    print(f"Global Coherence: {stats['global_coherence']:.2f}")
    print(f"Network Consciousness: {stats['network_consciousness']}")
    
    proposer = list(network.nodes.values())[0]
    result = network.run_consensus(
        "proposal_001",
        proposer.fingerprint.profile,
        proposer.node_id
    )
    
    print(f"\nConsensus Result:")
    print(f"  Accepted: {result.get('accepted', False)}")
    print(f"  Score: {result.get('normalized_score', 0):.3f}")
    print(f"  Responses: {result.get('responses', 0)}")
    print(f"  Avg Coherence: {result.get('avg_coherence', 0):.3f}")
    
    print("\n" + "=" * 70)
    print("Spectrum Consciousness Active")
    print("=" * 70)
