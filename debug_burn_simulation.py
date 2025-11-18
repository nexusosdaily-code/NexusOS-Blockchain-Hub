"""Debug burn simulation to find the issue"""

from longterm_tokenomics_simulation import (
    LongTermTokenomicsSimulator,
    AdoptionScenario
)

sim = LongTermTokenomicsSimulator()

print("Initial Supply:", sim.INITIAL_SUPPLY, "NXT")
print("Genesis Supply:", sim.GENESIS_SUPPLY, "NXT")
print()

# Test Year 1 - Moderate scenario
year = 1
scenario = AdoptionScenario.MODERATE

users = sim.estimate_active_users(year, scenario)
messages = sim.estimate_daily_messages(users)
burn_daily = sim.calculate_daily_burn(messages)
burn_annual = burn_daily * 365

print(f"Year {year} - {scenario.value.upper()}:")
print(f"  Active Users: {users:,}")
print(f"  Daily Messages: {messages:,}")
print(f"  Daily Burn: {burn_daily:,.2f} NXT")
print(f"  Annual Burn: {burn_annual:,.2f} NXT")
print(f"  Genesis Supply: {sim.GENESIS_SUPPLY:,.0f} NXT")
print(f"  Burn vs Supply: {burn_annual/sim.GENESIS_SUPPLY*100:.1f}% per year")
print()

# Show what burn rate would be sustainable
sustainable_annual_burn = sim.GENESIS_SUPPLY * 0.01  # 1% per year = 100 years
sustainable_daily_burn = sustainable_annual_burn / 365
sustainable_per_message = sustainable_daily_burn / messages if messages > 0 else 0

print("Sustainable Economics (100-year horizon):")
print(f"  Max Annual Burn (1%): {sustainable_annual_burn:,.0f} NXT")
print(f"  Max Daily Burn: {sustainable_daily_burn:,.2f} NXT")
print(f"  Sustainable burn per message: {sustainable_per_message:.6f} NXT")
print(f"  Current burn per message: {sim.burn_params.message_burn:.6f} NXT")
print(f"  Reduction needed: {sim.burn_params.message_burn/sustainable_per_message:.0f}x")
