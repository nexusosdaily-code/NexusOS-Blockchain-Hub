"""
Test Long-Term Tokenomics Simulation
=====================================

Run critical 50-100 year burn scenarios to identify sustainability issues.
"""

from longterm_tokenomics_simulation import (
    LongTermTokenomicsSimulator,
    AdoptionScenario,
    BurnParameters,
    EconomicBalancingMechanism
)


def test_all_scenarios():
    """Test all adoption scenarios"""
    
    print("=" * 80)
    print("NexusOS Long-Term Tokenomics Burn Analysis (50-100 Years)")
    print("=" * 80)
    print()
    
    scenarios = [
        AdoptionScenario.CONSERVATIVE,
        AdoptionScenario.MODERATE,
        AdoptionScenario.AGGRESSIVE,
        AdoptionScenario.VIRAL
    ]
    
    for scenario in scenarios:
        print(f"\n{'=' * 80}")
        print(f"Scenario: {scenario.value.upper()}")
        print(f"{'=' * 80}\n")
        
        # Run 100-year simulation
        sim = LongTermTokenomicsSimulator()
        metrics = sim.simulate(years=100, scenario=scenario)
        
        # Get critical milestones
        milestones = sim.get_critical_years(metrics)
        
        # Show results
        print(f"Initial Supply: {sim.INITIAL_SUPPLY:,.0f} NXT")
        print(f"Simulation Years: {len(metrics)}")
        print()
        
        # Show year 10, 25, 50, 100
        checkpoints = [10, 25, 50, 100]
        for year in checkpoints:
            if year <= len(metrics):
                m = metrics[year - 1]
                print(f"Year {year}:")
                print(f"  Active Users: {m.active_users:,}")
                print(f"  Daily Messages: {m.daily_messages:,}")
                print(f"  Circulating Supply: {m.circulating_supply:,.2f} NXT ({m.circulating_supply/sim.INITIAL_SUPPLY*100:.1f}%)")
                print(f"  Total Burned: {m.total_burned:,.2f} NXT")
                print(f"  Daily Burn Rate: {m.burn_rate_daily:,.2f} NXT/day")
                print(f"  Years Until Depletion: {m.years_until_depletion:.1f}")
                print(f"  Sustainability Score: {m.sustainability_score:.0f}/100")
                print()
        
        # Show milestones
        print("Critical Milestones:")
        if '50_percent_burned' in milestones:
            print(f"  ⚠️  50% Supply Burned: Year {milestones['50_percent_burned']}")
        if '75_percent_burned' in milestones:
            print(f"  ⚠️  75% Supply Burned: Year {milestones['75_percent_burned']}")
        if '90_percent_burned' in milestones:
            print(f"  🚨 90% Supply Burned: Year {milestones['90_percent_burned']}")
        if 'critical_sustainability' in milestones:
            print(f"  🚨 Sustainability Critical: Year {milestones['critical_sustainability']}")
        if 'supply_depleted' in milestones:
            print(f"  💀 Supply Depleted: Year {milestones['supply_depleted']}")
        
        if not milestones:
            print("  ✅ No critical issues in 100-year horizon!")
        
        print()


def test_balancing_mechanisms():
    """Test economic balancing mechanisms"""
    
    print("\n" + "=" * 80)
    print("ECONOMIC BALANCING MECHANISMS")
    print("=" * 80)
    print()
    
    # Test dynamic burn adjustment
    print("1. Dynamic Burn Rate Adjustment:")
    print("   Reduces burn rates as supply decreases")
    print()
    
    base_burn = 0.1
    for supply_pct in [100, 75, 50, 25, 10]:
        supply = supply_pct * 10_000  # Example supply
        adjusted = EconomicBalancingMechanism.dynamic_burn_adjustment(
            base_burn, supply, 1_000_000
        )
        print(f"   Supply {supply_pct}%: {base_burn:.3f} NXT → {adjusted:.3f} NXT ({adjusted/base_burn*100:.0f}%)")
    
    print()
    print("2. Validator Inflation (Bitcoin-style halving):")
    print()
    
    for year in [0, 4, 8, 12, 20, 40]:
        inflation = EconomicBalancingMechanism.calculate_validator_inflation(year)
        print(f"   Year {year}: {inflation:.2f}% annual inflation")
    
    print()
    print("3. Annual Burn Cap (5% max):")
    print()
    
    for supply in [1_000_000, 500_000, 100_000, 10_000]:
        proposed = 100_000  # Proposed burn
        capped = EconomicBalancingMechanism.apply_annual_burn_cap(
            proposed, supply, max_burn_pct=5.0
        )
        print(f"   Supply {supply:,} NXT: {proposed:,} → {capped:,.0f} NXT (capped at 5%)")
    
    print()


def test_moderate_with_balancing():
    """Test moderate scenario with balancing mechanisms applied"""
    
    print("\n" + "=" * 80)
    print("BALANCED TOKENOMICS - Moderate Growth with Dynamic Adjustments")
    print("=" * 80)
    print()
    
    sim = LongTermTokenomicsSimulator()
    base_metrics = sim.simulate(years=100, scenario=AdoptionScenario.MODERATE)
    
    print("Comparing: Base vs. Balanced Economics\n")
    
    # Apply balancing
    circulating = sim.GENESIS_SUPPLY
    total_burned_balanced = 0
    
    for year in [10, 25, 50, 75, 100]:
        if year <= len(base_metrics):
            base = base_metrics[year - 1]
            
            # Calculate balanced burn
            base_burn_daily = base.burn_rate_daily
            adjusted_burn = EconomicBalancingMechanism.dynamic_burn_adjustment(
                base_burn_daily,
                circulating,
                sim.INITIAL_SUPPLY
            )
            
            # Apply inflation
            inflation_rate = EconomicBalancingMechanism.calculate_validator_inflation(year)
            annual_inflation = circulating * (inflation_rate / 100)
            
            # Update balanced supply
            annual_adjusted_burn = adjusted_burn * 365
            circulating = circulating - annual_adjusted_burn + annual_inflation
            total_burned_balanced += annual_adjusted_burn
            
            print(f"Year {year}:")
            print(f"  Base Model:")
            print(f"    Supply: {base.circulating_supply:,.0f} NXT ({base.circulating_supply/sim.INITIAL_SUPPLY*100:.1f}%)")
            print(f"    Sustainability: {base.sustainability_score:.0f}/100")
            print(f"  Balanced Model:")
            print(f"    Supply: {circulating:,.0f} NXT ({circulating/sim.INITIAL_SUPPLY*100:.1f}%)")
            print(f"    Annual Burn: {annual_adjusted_burn:,.0f} NXT")
            print(f"    Annual Inflation: +{annual_inflation:,.0f} NXT ({inflation_rate:.2f}%)")
            print(f"    Net Change: {annual_inflation - annual_adjusted_burn:+,.0f} NXT")
            print()


if __name__ == "__main__":
    test_all_scenarios()
    test_balancing_mechanisms()
    test_moderate_with_balancing()
    
    print("\n" + "=" * 80)
    print("✅ Long-term tokenomics analysis complete!")
    print("=" * 80)
