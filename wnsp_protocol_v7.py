"""
Wavelength-Native Signaling Protocol (WNSP) v7.0 - Lambda Boson Substrate
=========================================================================

Revolutionary encoding using oscillating wavelengths for 2+ characters per particle.
Built on Lambda Boson (Λ = hf/c²) physics substrate.

Key Features:
- Oscillating wavelength: λ₁ → λ₂ encodes 2 characters per particle
- Lambda mass validation: Λ = h(f₁+f₂)/2c² ensures physics compliance
- Energy authority: oscillation_cycles × Λ determines message weight
- Full NexusOS substrate integration

Encoding Density:
- v2.0: 1 character per particle (64 chars @ 6nm spacing)
- v7.0: 2+ characters per particle (4096 pairs @ oscillating wavelength)

Author: Te Rata Pou
License: GPL v3
"""

from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import time
import hashlib
import math

PLANCK_CONSTANT = 6.62607015e-34  # J·s
SPEED_OF_LIGHT = 2.99792458e8     # m/s
SDK_WALLET = "NXS5372697543A0FEF822E453DBC26FA044D14599E9"


class LambdaEncodingScheme(Enum):
    """WNSP v7.0 Lambda Boson encoding schemes."""
    DUAL_WAVELENGTH = "dual_wavelength"      # 2 chars per particle (λ₁→λ₂)
    TRIPLE_WAVELENGTH = "triple_wavelength"  # 3 chars per particle (λ₁→λ₂→λ₃)
    LAMBDA_BINARY = "lambda_binary"          # Binary via Λ mass quantization


class SpectralBand(Enum):
    """Spectral bands for Lambda encoding."""
    UV = ("ultraviolet", 200, 380)
    VIOLET = ("violet", 380, 450)
    BLUE = ("blue", 450, 495)
    GREEN = ("green", 495, 570)
    YELLOW = ("yellow", 570, 590)
    ORANGE = ("orange", 590, 620)
    RED = ("red", 620, 750)
    NIR = ("near_infrared", 750, 1000)
    
    @property
    def display_name(self) -> str:
        return self.value[0]
    
    @property
    def min_nm(self) -> float:
        return self.value[1]
    
    @property
    def max_nm(self) -> float:
        return self.value[2]


LAMBDA_CHAR_MAP = {
    'A': 380, 'B': 386, 'C': 392, 'D': 398, 'E': 404, 'F': 410,
    'G': 416, 'H': 422, 'I': 428, 'J': 434, 'K': 440, 'L': 446,
    'M': 452, 'N': 458, 'O': 464, 'P': 470, 'Q': 476, 'R': 482,
    'S': 488, 'T': 494, 'U': 500, 'V': 506, 'W': 512, 'X': 518,
    'Y': 524, 'Z': 530, '0': 536, '1': 542, '2': 548, '3': 554,
    '4': 560, '5': 566, '6': 572, '7': 578, '8': 584, '9': 590,
    ' ': 596, '.': 602, ',': 608, '!': 614, '?': 620, '-': 626,
    '_': 632, '+': 638, '=': 644, '*': 650, '/': 656, '@': 662,
    '#': 668, '$': 674, '%': 680, '&': 686, '(': 692, ')': 698,
    '[': 704, ']': 710, '{': 716, '}': 722, '<': 728, '>': 734,
    ':': 740, ';': 746, "'": 752, '"': 758, '\\': 764, '|': 770,
    'a': 380, 'b': 386, 'c': 392, 'd': 398, 'e': 404, 'f': 410,
    'g': 416, 'h': 422, 'i': 428, 'j': 434, 'k': 440, 'l': 446,
    'm': 452, 'n': 458, 'o': 464, 'p': 470, 'q': 476, 'r': 482,
    's': 488, 't': 494, 'u': 500, 'v': 506, 'w': 512, 'x': 518,
    'y': 524, 'z': 530,
}

WAVELENGTH_TO_CHAR = {v: k for k, v in LAMBDA_CHAR_MAP.items() if k.isupper() or k.isdigit() or not k.isalpha()}


def wavelength_to_frequency(wavelength_nm: float) -> float:
    """Convert wavelength (nm) to frequency (Hz)."""
    wavelength_m = wavelength_nm * 1e-9
    return SPEED_OF_LIGHT / wavelength_m


def frequency_to_wavelength(frequency_hz: float) -> float:
    """Convert frequency (Hz) to wavelength (nm)."""
    wavelength_m = SPEED_OF_LIGHT / frequency_hz
    return wavelength_m * 1e9


def calculate_lambda_mass(frequency_hz: float) -> float:
    """
    Calculate Lambda Boson mass from frequency.
    
    Λ = hf/c²
    
    This is the mass-equivalent of oscillation - not metaphor, but physics.
    """
    return (PLANCK_CONSTANT * frequency_hz) / (SPEED_OF_LIGHT ** 2)


def calculate_lambda_from_wavelength(wavelength_nm: float) -> float:
    """Calculate Lambda mass from wavelength."""
    freq = wavelength_to_frequency(wavelength_nm)
    return calculate_lambda_mass(freq)


def calculate_oscillating_lambda(wavelength_start: float, wavelength_end: float) -> float:
    """
    Calculate Lambda mass for oscillating wavelength (λ₁ → λ₂).
    
    Uses average frequency: Λ = h(f₁ + f₂) / 2c²
    """
    f1 = wavelength_to_frequency(wavelength_start)
    f2 = wavelength_to_frequency(wavelength_end)
    avg_freq = (f1 + f2) / 2
    return calculate_lambda_mass(avg_freq)


@dataclass
class LambdaFrame:
    """
    WNSP v7.0 Lambda Frame - Oscillating wavelength encoding.
    
    Encodes 2+ characters per particle via wavelength oscillation.
    Physics-validated via Λ = hf/c² substrate compliance.
    """
    wavelength_start_nm: float
    wavelength_end_nm: float
    intensity_level: int = 7
    oscillation_cycles: int = 1
    phase_shift: int = 0
    timestamp_ms: float = field(default_factory=lambda: time.time() * 1000)
    
    lambda_mass_kg: float = field(init=False)
    frequency_start_hz: float = field(init=False)
    frequency_end_hz: float = field(init=False)
    energy_joules: float = field(init=False)
    
    def __post_init__(self):
        """Calculate physics properties on initialization."""
        self.frequency_start_hz = wavelength_to_frequency(self.wavelength_start_nm)
        self.frequency_end_hz = wavelength_to_frequency(self.wavelength_end_nm)
        self.lambda_mass_kg = calculate_oscillating_lambda(
            self.wavelength_start_nm, 
            self.wavelength_end_nm
        )
        avg_freq = (self.frequency_start_hz + self.frequency_end_hz) / 2
        self.energy_joules = PLANCK_CONSTANT * avg_freq * self.oscillation_cycles
        
        if not (0 <= self.intensity_level <= 63):
            raise ValueError(f"intensity_level must be 0-63, got {self.intensity_level}")
        if not (0 <= self.phase_shift <= 3):
            raise ValueError(f"phase_shift must be 0-3, got {self.phase_shift}")
    
    @property
    def char_pair(self) -> Tuple[str, str]:
        """Decode the two characters from oscillating wavelength."""
        char1 = self._wavelength_to_char(self.wavelength_start_nm)
        char2 = self._wavelength_to_char(self.wavelength_end_nm)
        return (char1, char2)
    
    def _wavelength_to_char(self, wavelength: float) -> str:
        """Find closest character for wavelength."""
        closest_wl = min(WAVELENGTH_TO_CHAR.keys(), key=lambda w: abs(w - wavelength))
        return WAVELENGTH_TO_CHAR.get(closest_wl, '?')
    
    @property
    def energy_authority(self) -> float:
        """Calculate energy authority: Λ × cycles × intensity."""
        return self.lambda_mass_kg * self.oscillation_cycles * (self.intensity_level + 1)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize frame to dictionary."""
        return {
            'wavelength_start_nm': self.wavelength_start_nm,
            'wavelength_end_nm': self.wavelength_end_nm,
            'intensity_level': self.intensity_level,
            'oscillation_cycles': self.oscillation_cycles,
            'phase_shift': self.phase_shift,
            'timestamp_ms': self.timestamp_ms,
            'lambda_mass_kg': self.lambda_mass_kg,
            'frequency_start_hz': self.frequency_start_hz,
            'frequency_end_hz': self.frequency_end_hz,
            'energy_joules': self.energy_joules,
            'char_pair': self.char_pair,
            'energy_authority': self.energy_authority
        }


@dataclass
class LambdaMessage:
    """
    WNSP v7.0 Lambda Message - Complete message with physics substrate.
    
    Contains sequence of LambdaFrames encoding 2 chars each.
    Validates total Λ-mass conservation.
    """
    message_id: str
    sender_id: str
    recipient_id: str
    content: str
    frames: List[LambdaFrame] = field(default_factory=list)
    encoding_scheme: LambdaEncodingScheme = LambdaEncodingScheme.DUAL_WAVELENGTH
    created_at: float = field(default_factory=lambda: time.time() * 1000)
    
    total_lambda_mass_kg: float = field(init=False, default=0.0)
    total_energy_joules: float = field(init=False, default=0.0)
    total_energy_authority: float = field(init=False, default=0.0)
    characters_per_particle: float = field(init=False, default=2.0)
    
    def __post_init__(self):
        """Calculate aggregate physics properties."""
        self._recalculate_totals()
    
    def _recalculate_totals(self):
        """Recalculate totals from frames."""
        if self.frames:
            self.total_lambda_mass_kg = sum(f.lambda_mass_kg for f in self.frames)
            self.total_energy_joules = sum(f.energy_joules for f in self.frames)
            self.total_energy_authority = sum(f.energy_authority for f in self.frames)
            self.characters_per_particle = len(self.content) / len(self.frames) if self.frames else 0
    
    def add_frame(self, frame: LambdaFrame):
        """Add a frame and recalculate totals."""
        self.frames.append(frame)
        self._recalculate_totals()
    
    @property
    def efficiency_ratio(self) -> float:
        """Calculate encoding efficiency vs v2.0 (1 char/particle baseline)."""
        return self.characters_per_particle
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize message to dictionary."""
        return {
            'message_id': self.message_id,
            'sender_id': self.sender_id,
            'recipient_id': self.recipient_id,
            'content': self.content,
            'encoding_scheme': self.encoding_scheme.value,
            'created_at': self.created_at,
            'frame_count': len(self.frames),
            'content_length': len(self.content),
            'characters_per_particle': self.characters_per_particle,
            'efficiency_vs_v2': f"{self.efficiency_ratio:.1f}x",
            'total_lambda_mass_kg': self.total_lambda_mass_kg,
            'total_energy_joules': self.total_energy_joules,
            'total_energy_authority': self.total_energy_authority,
            'frames': [f.to_dict() for f in self.frames]
        }


class LambdaEncoder:
    """
    WNSP v7.0 Lambda Encoder - Oscillating wavelength encoding.
    
    Encodes messages using dual-wavelength oscillation for 2 chars/particle.
    Full Lambda Boson substrate compliance with physics validation.
    """
    
    def __init__(self, 
                 encoding_scheme: LambdaEncodingScheme = LambdaEncodingScheme.DUAL_WAVELENGTH,
                 default_intensity: int = 32,
                 default_cycles: int = 1):
        """Initialize Lambda encoder."""
        self.encoding_scheme = encoding_scheme
        self.default_intensity = default_intensity
        self.default_cycles = default_cycles
        self.char_map = LAMBDA_CHAR_MAP
    
    def encode_message(self,
                       content: str,
                       sender_id: str,
                       recipient_id: str,
                       intensity: Optional[int] = None,
                       cycles: Optional[int] = None) -> LambdaMessage:
        """
        Encode content into Lambda message with oscillating wavelength frames.
        
        Each frame encodes 2 characters via λ₁ → λ₂ oscillation.
        """
        message_id = self._generate_message_id(content, sender_id)
        intensity = intensity or self.default_intensity
        cycles = cycles or self.default_cycles
        
        frames = self._encode_to_lambda_frames(content, intensity, cycles)
        
        message = LambdaMessage(
            message_id=message_id,
            sender_id=sender_id,
            recipient_id=recipient_id,
            content=content,
            frames=frames,
            encoding_scheme=self.encoding_scheme
        )
        
        return message
    
    def _encode_to_lambda_frames(self, 
                                  content: str, 
                                  intensity: int,
                                  cycles: int) -> List[LambdaFrame]:
        """Encode content to Lambda frames (2 chars per frame)."""
        frames = []
        base_time = time.time() * 1000
        frame_duration_ms = 50
        
        padded = content if len(content) % 2 == 0 else content + ' '
        
        for i in range(0, len(padded), 2):
            char1 = padded[i]
            char2 = padded[i + 1]
            
            wl1 = self.char_map.get(char1) or self.char_map.get(' ') or 596.0
            wl2 = self.char_map.get(char2) or self.char_map.get(' ') or 596.0
            
            frame = LambdaFrame(
                wavelength_start_nm=float(wl1),
                wavelength_end_nm=float(wl2),
                intensity_level=intensity,
                oscillation_cycles=cycles,
                phase_shift=i % 4,
                timestamp_ms=base_time + (i // 2 * frame_duration_ms)
            )
            frames.append(frame)
        
        return frames
    
    def _generate_message_id(self, content: str, sender_id: str) -> str:
        """Generate unique message ID using Lambda hash."""
        data = f"{content}{sender_id}{time.time()}"
        hash_hex = hashlib.sha256(data.encode('utf-8')).hexdigest()[:16]
        return f"wnsp7_{hash_hex}"
    
    def decode_message(self, message: LambdaMessage) -> str:
        """Decode Lambda message back to original content."""
        decoded = []
        for frame in message.frames:
            char1, char2 = frame.char_pair
            decoded.append(char1)
            decoded.append(char2)
        return ''.join(decoded).rstrip()


class LambdaValidator:
    """
    Physics validator for WNSP v7.0 Lambda frames.
    
    Ensures all frames comply with Λ = hf/c² substrate.
    """
    
    @staticmethod
    def validate_frame(frame: LambdaFrame) -> Tuple[bool, str]:
        """Validate a single Lambda frame for physics compliance."""
        expected_lambda = calculate_oscillating_lambda(
            frame.wavelength_start_nm,
            frame.wavelength_end_nm
        )
        
        tolerance = 1e-50
        if abs(frame.lambda_mass_kg - expected_lambda) > tolerance:
            return False, f"Lambda mass mismatch: {frame.lambda_mass_kg} vs {expected_lambda}"
        
        if not (200 <= frame.wavelength_start_nm <= 1000):
            return False, f"Start wavelength out of range: {frame.wavelength_start_nm}nm"
        
        if not (200 <= frame.wavelength_end_nm <= 1000):
            return False, f"End wavelength out of range: {frame.wavelength_end_nm}nm"
        
        expected_energy = PLANCK_CONSTANT * (
            (frame.frequency_start_hz + frame.frequency_end_hz) / 2
        ) * frame.oscillation_cycles
        
        if abs(frame.energy_joules - expected_energy) > tolerance:
            return False, f"Energy mismatch: {frame.energy_joules} vs {expected_energy}"
        
        return True, "Valid Lambda frame"
    
    @staticmethod
    def validate_message(message: LambdaMessage) -> Tuple[bool, str, Dict[str, Any]]:
        """Validate complete Lambda message."""
        report = {
            'frames_validated': 0,
            'frames_failed': 0,
            'total_lambda_kg': 0.0,
            'total_energy_j': 0.0,
            'encoding_efficiency': 0.0,
            'errors': []
        }
        
        for i, frame in enumerate(message.frames):
            valid, msg = LambdaValidator.validate_frame(frame)
            if valid:
                report['frames_validated'] += 1
                report['total_lambda_kg'] += frame.lambda_mass_kg
                report['total_energy_j'] += frame.energy_joules
            else:
                report['frames_failed'] += 1
                report['errors'].append(f"Frame {i}: {msg}")
        
        if message.frames:
            report['encoding_efficiency'] = len(message.content) / len(message.frames)
        
        all_valid = report['frames_failed'] == 0
        status = "All frames valid" if all_valid else f"{report['frames_failed']} frames failed"
        
        return all_valid, status, report


class LambdaSubstrateIntegration:
    """
    Integration layer connecting WNSP v7.0 to NexusOS substrate.
    
    Routes all Lambda transactions through physics economics adapter.
    """
    
    def __init__(self):
        self.encoder = LambdaEncoder()
        self.validator = LambdaValidator()
        self._physics_adapter = None
    
    @property
    def physics_adapter(self):
        """Lazy load physics economics adapter."""
        if self._physics_adapter is None:
            try:
                from physics_economics_adapter import PhysicsEconomicsAdapter
                self._physics_adapter = PhysicsEconomicsAdapter()
            except ImportError:
                self._physics_adapter = None
        return self._physics_adapter
    
    def create_message(self,
                       content: str,
                       sender_id: str,
                       recipient_id: str,
                       intensity: int = 32,
                       cycles: int = 1) -> Dict[str, Any]:
        """
        Create and validate Lambda message with full substrate integration.
        
        Returns message with physics economics calculations.
        """
        message = self.encoder.encode_message(
            content=content,
            sender_id=sender_id,
            recipient_id=recipient_id,
            intensity=intensity,
            cycles=cycles
        )
        
        valid, status, report = self.validator.validate_message(message)
        
        nxt_cost = self._calculate_nxt_cost(message)
        
        result = {
            'message': message.to_dict(),
            'validation': {
                'valid': valid,
                'status': status,
                'report': report
            },
            'economics': {
                'cost_nxt': nxt_cost,
                'sdk_fee_nxt': nxt_cost * 0.005,
                'net_cost_nxt': nxt_cost * 0.995,
                'lambda_mass_kg': message.total_lambda_mass_kg,
                'energy_joules': message.total_energy_joules
            },
            'efficiency': {
                'characters': len(content),
                'particles': len(message.frames),
                'chars_per_particle': message.characters_per_particle,
                'vs_v2_improvement': f"{message.efficiency_ratio:.1f}x"
            },
            'substrate': {
                'protocol': 'WNSP v7.0',
                'encoding': 'Lambda Boson Oscillating Wavelength',
                'formula': 'Λ = hf/c²',
                'sdk_wallet': SDK_WALLET
            }
        }
        
        return result
    
    def _calculate_nxt_cost(self, message: LambdaMessage) -> float:
        """Calculate NXT cost based on Lambda mass and energy."""
        base_cost_per_joule = 1e30
        return message.total_energy_joules * base_cost_per_joule


def encode_lambda_message(content: str, 
                          sender: str = "anonymous",
                          recipient: str = "broadcast",
                          intensity: int = 32,
                          cycles: int = 1) -> Dict[str, Any]:
    """
    Convenience function for Lambda message encoding.
    
    WNSP v7.0 - 2+ characters per particle via oscillating wavelength.
    """
    integration = LambdaSubstrateIntegration()
    return integration.create_message(
        content=content,
        sender_id=sender,
        recipient_id=recipient,
        intensity=intensity,
        cycles=cycles
    )


if __name__ == "__main__":
    print("=" * 70)
    print("WNSP v7.0 - Lambda Boson Substrate")
    print("Oscillating Wavelength Encoding: 2+ characters per particle")
    print("=" * 70)
    
    test_content = "LAMBDA BOSON IS REAL MASS FROM OSCILLATION"
    
    result = encode_lambda_message(
        content=test_content,
        sender="TeRataPou",
        recipient="NexusNetwork"
    )
    
    print(f"\nContent: {test_content}")
    print(f"Length: {len(test_content)} characters")
    print(f"\nEncoding Efficiency:")
    print(f"  Particles used: {result['efficiency']['particles']}")
    print(f"  Chars/particle: {result['efficiency']['chars_per_particle']:.1f}")
    print(f"  vs v2.0: {result['efficiency']['vs_v2_improvement']}")
    
    print(f"\nPhysics (Λ = hf/c²):")
    print(f"  Total Λ mass: {result['economics']['lambda_mass_kg']:.2e} kg")
    print(f"  Total energy: {result['economics']['energy_joules']:.2e} J")
    print(f"  Cost: {result['economics']['cost_nxt']:.4f} NXT")
    
    print(f"\nValidation: {result['validation']['status']}")
    print(f"Frames validated: {result['validation']['report']['frames_validated']}")
    
    print("\n" + "=" * 70)
    print("Λ = hf/c² — Oscillation IS mass")
    print("=" * 70)
