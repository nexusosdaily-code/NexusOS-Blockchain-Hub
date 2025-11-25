"""
WNSP v4.0 Quick Start Example
============================

Simple example showing how to use Quantum Entanglement Consensus.
"""

from wnsp_quantum_entanglement_poc import (
    QuantumValidator,
    QuantumEnergyAwareConsensus,
    EPRPair,
    Transaction,
    HybridConsensus
)

def example_1_basic_consensus():
    """Example 1: Basic quantum consensus"""
    print("\n" + "="*70)
    print("Example 1: Basic Quantum Consensus")
    print("="*70)
    
    # Create 5 validator nodes
    validators = [
        QuantumValidator(f"validator_{i}", EPRPair(f"pair_{i}", 0, 0))
        for i in range(5)
    ]
    
    # Initialize quantum consensus engine
    qec = QuantumEnergyAwareConsensus(validators, threshold=0.67)
    qec.distribute_epr_pairs()
    
    # Create and validate a transaction
    tx = Transaction(
        tx_id="tx_example_1",
        sender="alice",
        receiver="bob",
        amount=50.0,
        timestamp=1732516800
    )
    
    is_valid, record = qec.validate_with_energy_awareness(tx)
    
    print(f"\nTransaction: {tx.tx_id}")
    print(f"Valid: {is_valid}")
    print(f"Bell Violation: {record['bell_violation']:.4f}")
    print(f"Energy Cost: {record['total_energy_nxt']:.2e} NXT")
    print(f"Validators: {record['validators_measured']}")


def example_2_byzantine_detection():
    """Example 2: Detect Byzantine nodes"""
    print("\n" + "="*70)
    print("Example 2: Byzantine Node Detection")
    print("="*70)
    
    validators = [
        QuantumValidator(f"val_{i}", EPRPair(f"pair_{i}", 0, 0))
        for i in range(7)
    ]
    
    qec = QuantumEnergyAwareConsensus(validators, threshold=0.65)
    qec.distribute_epr_pairs()
    
    # Validate multiple transactions to collect measurement data
    for i in range(3):
        tx = Transaction(
            tx_id=f"tx_byzantine_{i}",
            sender="alice",
            receiver="bob",
            amount=10.0 + i,
            timestamp=1732516800 + i
        )
        qec.validate_with_energy_awareness(tx)
    
    # Detect Byzantine nodes
    byzantine = qec.detect_byzantine_nodes()
    
    print(f"\nTransactions validated: 3")
    print(f"Byzantine nodes detected: {len(byzantine)}")
    if byzantine:
        print(f"Suspect nodes: {byzantine}")
    else:
        print("No Byzantine nodes detected - network is secure")


def example_3_energy_analysis():
    """Example 3: Analyze energy costs"""
    print("\n" + "="*70)
    print("Example 3: Energy Cost Analysis (E=hf)")
    print("="*70)
    
    validators = [
        QuantumValidator(f"validator_{i}", EPRPair(f"pair_{i}", 0, 0))
        for i in range(4)
    ]
    
    qec = QuantumEnergyAwareConsensus(validators, threshold=0.6)
    qec.distribute_epr_pairs()
    
    # Validate transactions with different sizes
    transactions = [
        Transaction("tx_001", "alice", "bob", 10.0, 1732516800),
        Transaction("tx_002", "bob", "charlie", 20.0, 1732516801),
        Transaction("tx_003", "charlie", "david", 30.0, 1732516802),
    ]
    
    print("\nTransaction Energy Costs:")
    print("-" * 70)
    
    total_energy = 0
    for tx in transactions:
        is_valid, record = qec.validate_with_energy_awareness(tx)
        energy = record['total_energy_nxt']
        total_energy += energy
        
        print(f"TX {tx.tx_id}:")
        print(f"  Amount: {tx.amount} NXT")
        print(f"  Energy: {energy:.2e} NXT")
        print(f"  Valid: {is_valid}")
        print()
    
    print(f"Total energy cost for 3 transactions: {total_energy:.2e} NXT")
    print(f"Average per transaction: {total_energy/3:.2e} NXT")


def example_4_wavelength_mapping():
    """Example 4: Show wavelength-energy mapping"""
    print("\n" + "="*70)
    print("Example 4: Wavelength-Energy Mapping")
    print("="*70)
    
    validators = [
        QuantumValidator(f"validator_{i}", EPRPair(f"pair_{i}", 0, 0))
        for i in range(7)
    ]
    
    qec = QuantumEnergyAwareConsensus(validators, threshold=0.65)
    qec.distribute_epr_pairs()
    
    print("\nValidator Wavelength Assignments:")
    print("-" * 70)
    print(f"{'Validator':<20} {'Wavelength (nm)':<20} {'Color':<15}")
    print("-" * 70)
    
    color_names = {
        400: "Violet",
        450: "Blue",
        500: "Cyan",
        550: "Green",
        600: "Yellow",
        650: "Red",
        700: "Dark Red"
    }
    
    for val_id, wavelength in qec.wavelengths.items():
        color = color_names.get(wavelength, "Unknown")
        print(f"{val_id:<20} {wavelength:<20} {color:<15}")


def example_5_hybrid_mode():
    """Example 5: Hybrid v3 + v4 consensus (conceptual)"""
    print("\n" + "="*70)
    print("Example 5: Hybrid WNSP v3 + v4 Consensus")
    print("="*70)
    
    # This is a conceptual example showing how v3 and v4 would coexist
    
    print("""
    Hybrid Consensus Architecture:
    
    Transaction arrives...
    
    ┌─────────────────────────────────────────────┐
    │ WNSP v3.0 (Proof of Spectrum)               │
    │ - Validates using wave interference         │
    │ - ~5 second confirmation                    │
    │ - 33% Byzantine tolerance                   │
    └──────────────────┬──────────────────────────┘
                       │
                       ↓
    ┌─────────────────────────────────────────────┐
    │ WNSP v4.0 (Proof of Entanglement)           │
    │ - Validates using Bell state measurements   │
    │ - ~10ms confirmation                        │
    │ - 50% Byzantine tolerance                   │
    └──────────────────┬──────────────────────────┘
                       │
                       ↓
    ┌─────────────────────────────────────────────┐
    │ Consensus Decision: BOTH must pass          │
    │ Result: Maximum security ✅                 │
    └─────────────────────────────────────────────┘
    
    Benefits:
    - Backward compatible with v3.0
    - Double-validation for high-value transactions
    - Gradual v3→v4 migration path
    - No disruption to existing deployments
    """)


if __name__ == "__main__":
    print("\n" + "🌐 WNSP v4.0 Quantum Entanglement Consensus - Examples" + "\n")
    
    # Run examples
    example_1_basic_consensus()
    example_2_byzantine_detection()
    example_3_energy_analysis()
    example_4_wavelength_mapping()
    example_5_hybrid_mode()
    
    print("\n" + "="*70)
    print("All examples completed!")
    print("="*70)
    print("\nNext Steps:")
    print("1. Run: streamlit run wnsp_v4_quantum_dashboard.py")
    print("2. Read: WNSP_v4_Integration_Guide.md")
    print("3. Explore: wiki/WNSP-Protocol.md (v4.0 section)")
