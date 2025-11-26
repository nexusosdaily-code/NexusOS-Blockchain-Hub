"""
NexusOS Service Pools Dashboard
Unified interface for all service pools funded by F_floor

Displays:
- Pool Ecosystem Overview (Reserve → F_floor → Services)
- Real-World Supply Chain Pools
- Lottery System
- Bonus Pool Distribution
- Carbon Credits Trading
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import time

from pool_ecosystem import PoolEcosystem, PoolLayer, PoolType
from lottery_core import get_lottery_engine, LotteryTier
from bonus_pool_core import get_bonus_engine, BonusCategory
from nexus_native_wallet import get_token_system


def render_service_pools_page():
    """Main render function for Service Pools Dashboard"""
    
    st.title("Service Pools Dashboard")
    st.markdown("*All pools sustained by F_floor - Basic Human Living Standards*")
    
    # Get systems
    token_system = get_token_system()
    pool_ecosystem = PoolEcosystem()
    lottery_engine = get_lottery_engine(token_system)
    bonus_engine = get_bonus_engine(token_system)
    
    # Tabs for different sections
    tabs = st.tabs([
        "Pool Overview",
        "Supply Chains",
        "Lottery",
        "Bonus Rewards",
        "Carbon Credits"
    ])
    
    # Tab 1: Pool Overview
    with tabs[0]:
        render_pool_overview(pool_ecosystem)
    
    # Tab 2: Supply Chain Pools
    with tabs[1]:
        render_supply_chain_pools(pool_ecosystem, token_system)
    
    # Tab 3: Lottery
    with tabs[2]:
        render_lottery_section(lottery_engine)
    
    # Tab 4: Bonus Rewards
    with tabs[3]:
        render_bonus_section(bonus_engine)
    
    # Tab 5: Carbon Credits
    with tabs[4]:
        render_carbon_credits_section(pool_ecosystem, token_system)


def render_pool_overview(ecosystem: PoolEcosystem):
    """Render the pool hierarchy overview"""
    
    st.subheader("Pool Ecosystem Hierarchy")
    st.markdown("""
    The NexusOS economy flows in a clear hierarchy:
    **Reserve Pools** → **F_floor** → **Service Pools**
    
    This ensures Basic Human Living Standards are always funded before other activities.
    """)
    
    # Get verification data
    verification = ecosystem.verify_f_floor_support()
    
    # Display hierarchy status
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Layer 1: Reserve",
            f"{verification.get('reserve_total', 0):,.2f} NXT",
            "Supports F_floor"
        )
    
    with col2:
        st.metric(
            "Layer 2: F_floor",
            f"{verification.get('f_floor_balance', 0):,.2f} NXT",
            "Basic Living Standards"
        )
    
    with col3:
        st.metric(
            "Layer 3: Services",
            f"{verification.get('service_pool_count', 0)} Pools",
            "Enabled by F_floor"
        )
    
    # Hierarchy visualization
    st.markdown("---")
    st.subheader("Pool Structure")
    
    # Reserve pools
    reserve_pools = ecosystem.get_pools_by_layer(PoolLayer.RESERVE)
    with st.expander("Reserve Pools (Layer 1)", expanded=True):
        for pool in reserve_pools:
            st.markdown(f"- **{pool.name}**: {pool.description}")
    
    # F_floor
    f_floor = ecosystem.get_pool("F_FLOOR_POOL")
    if f_floor:
        with st.expander("F_floor Foundation (Layer 2)", expanded=True):
            st.markdown(f"**{f_floor.name}**")
            st.markdown(f"_{f_floor.description}_")
            st.markdown(f"Supports {len(f_floor.supports)} service pools")
    
    # Service pools
    service_pools = ecosystem.get_pools_by_layer(PoolLayer.SERVICE)
    with st.expander(f"Service Pools (Layer 3) - {len(service_pools)} pools", expanded=False):
        cols = st.columns(2)
        for i, pool in enumerate(service_pools):
            with cols[i % 2]:
                st.markdown(f"**{pool.name}**")
                st.caption(pool.description)


def render_supply_chain_pools(ecosystem: PoolEcosystem, token_system):
    """Render real-world supply chain pools"""
    
    st.subheader("Real-World Supply Chain Funding")
    st.markdown("""
    These pools fund real-world infrastructure and production,
    ensuring civilization runs on sustainable economics.
    """)
    
    # Define supply chain categories with actual allocation percentages from SupplyChainDemand
    supply_chains = {
        "Core Infrastructure (40%)": {
            "ELECTRICITY_POOL": ("Electricity & Energy", "12%"),
            "WATER_DESALINATION_POOL": ("Water Desalination", "8%"),
            "MANUFACTURING_POOL": ("Manufacturing", "12%"),
            "PRODUCT_SERVICE_POOL": ("Logistics & Transport", "8%"),
        },
        "Food & Agriculture (35%)": {
            "FOOD_SUPPLY_POOL": ("Food Supply Chain", "10%"),
            "AGRICULTURE_POOL": ("Sustainable Agriculture", "10%"),
            "HORTICULTURE_POOL": ("Horticulture", "8%"),
            "AQUACULTURE_POOL": ("Aquaculture & Fisheries", "7%"),
        },
        "Sustainability (25%)": {
            "ENVIRONMENTAL_POOL": ("Environmental Programs", "5%"),
            "RECYCLING_POOL": ("Circular Economy", "5%"),
            "CARBON_CREDITS_POOL": ("Carbon Credits", "5%"),
            "INNOVATION_POOL": ("Technology & Innovation", "5%"),
            "COMMUNITY_POOL": ("Services & Community", "5%"),
        }
    }
    
    for category, pools in supply_chains.items():
        st.markdown(f"### {category}")
        
        cols = st.columns(len(pools))
        for i, (pool_id, (name, allocation)) in enumerate(pools.items()):
            pool = ecosystem.get_pool(pool_id)
            with cols[i]:
                balance = pool.metrics.current_balance if pool else 0
                st.metric(
                    name,
                    f"{balance:,.2f} NXT",
                    f"Allocation: {allocation}"
                )
        
        st.markdown("---")
    
    # Investment form
    st.subheader("Invest in Supply Chain")
    
    col1, col2 = st.columns(2)
    with col1:
        all_pools = []
        for pools in supply_chains.values():
            all_pools.extend(pools.keys())
        selected_pool = st.selectbox("Select Pool", all_pools)
    
    with col2:
        invest_amount = st.number_input("Amount (NXT)", min_value=1.0, value=100.0)
    
    if st.button("Invest in Pool", type="primary"):
        user = st.session_state.get('active_address', st.session_state.get('user_address', ''))
        if not user:
            st.error("Please connect your wallet first")
        else:
            st.success(f"Invested {invest_amount} NXT in {selected_pool}")
            st.info("Your investment supports real-world infrastructure!")


def render_lottery_section(lottery_engine):
    """Render the lottery system interface"""
    
    st.subheader("Quantum Lottery")
    st.markdown("""
    **Fair, transparent lottery powered by cryptographic randomness.**
    
    15% of all ticket sales return to F_floor to sustain basic living standards.
    """)
    
    # Current draw info
    draw_info = lottery_engine.get_current_draw_info()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Current Pool", f"{draw_info.get('total_pool', 0):,.2f} NXT")
    
    with col2:
        st.metric("Tickets Sold", draw_info.get('tickets_sold', 0))
    
    with col3:
        st.metric("Ticket Price", f"{draw_info.get('ticket_price', 1)} NXT")
    
    with col4:
        remaining = draw_info.get('time_remaining_seconds', 0)
        hours = int(remaining // 3600)
        st.metric("Time Remaining", f"{hours}h")
    
    st.markdown("---")
    
    # Prize tiers
    st.subheader("Prize Tiers (E=hf)")
    
    tiers = [
        ("Gamma Jackpot", "6 matches", "40%", "Highest energy"),
        ("X-Ray Prize", "5 matches", "20%", "High energy"),
        ("UV Prize", "4 matches", "15%", "Medium energy"),
        ("Visible Prize", "3 matches", "10%", "Common wins"),
    ]
    
    tier_cols = st.columns(4)
    for i, (name, matches, share, desc) in enumerate(tiers):
        with tier_cols[i]:
            st.markdown(f"**{name}**")
            st.caption(f"{matches} | {share} of pool")
            st.caption(f"_{desc}_")
    
    st.markdown("---")
    
    # Buy ticket
    st.subheader("Buy Lottery Ticket")
    
    user = st.session_state.get('active_address', st.session_state.get('user_address', ''))
    
    pick_method = st.radio("Number Selection", ["Quick Pick (Random)", "Choose My Numbers"])
    
    custom_numbers = None
    if pick_method == "Choose My Numbers":
        cols = st.columns(6)
        custom_numbers = []
        for i in range(6):
            with cols[i]:
                num = st.number_input(f"#{i+1}", min_value=1, max_value=49, value=i+1, key=f"lotto_num_{i}")
                custom_numbers.append(num)
    
    if st.button("Purchase Ticket (1 NXT)", type="primary"):
        if not user:
            st.error("Please connect your wallet first")
        else:
            success, ticket, msg = lottery_engine.purchase_ticket(user, custom_numbers)
            if success:
                st.success(msg)
                st.balloons()
            else:
                st.error(msg)
    
    # User's tickets
    st.markdown("---")
    st.subheader("My Tickets")
    
    if user:
        tickets = lottery_engine.get_user_tickets(user)
        if tickets:
            for ticket in tickets[-5:]:  # Show last 5
                numbers_str = " ".join([f"**{n}**" for n in ticket['numbers']])
                prize_info = f" - Won {ticket['prize_tier']}!" if ticket.get('prize_tier') else ""
                st.markdown(f"Ticket `{ticket['ticket_id'][:12]}...`: {numbers_str}{prize_info}")
        else:
            st.info("No tickets yet. Buy your first ticket above!")
    else:
        st.info("Connect wallet to see your tickets")


def render_bonus_section(bonus_engine):
    """Render the bonus pool distribution interface"""
    
    st.subheader("Performance Bonus Pool")
    st.markdown("""
    **Earn rewards based on your contributions to the ecosystem.**
    
    Higher activity frequency = Higher energy rewards (E=hf principle)
    """)
    
    # Current period info
    period_info = bonus_engine.get_current_period_info()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Bonus Pool", f"{period_info.get('total_pool', 0):,.2f} NXT")
    
    with col2:
        st.metric("Participants", period_info.get('participants', 0))
    
    with col3:
        remaining = period_info.get('time_remaining_seconds', 0)
        days = int(remaining // 86400)
        st.metric("Period Ends In", f"{days} days")
    
    st.markdown("---")
    
    # Allocation breakdown
    st.subheader("Allocation by Category")
    
    allocation = period_info.get('allocation', {})
    
    categories = [
        ("Validator Performance", allocation.get('validator', 0.3), "Block validation uptime"),
        ("Community", allocation.get('community', 0.2), "Governance participation"),
        ("Trading Volume", allocation.get('trading', 0.2), "DEX activity"),
        ("Staking Loyalty", allocation.get('staking', 0.2), "Long-term staking"),
        ("Innovation", allocation.get('innovation', 0.05), "Development contributions"),
        ("Sustainability", allocation.get('sustainability', 0.05), "Environmental actions"),
    ]
    
    cols = st.columns(3)
    for i, (name, pct, desc) in enumerate(categories):
        with cols[i % 3]:
            st.metric(name, f"{pct*100:.0f}%")
            st.caption(desc)
    
    st.markdown("---")
    
    # User's performance
    user = st.session_state.get('active_address', st.session_state.get('user_address', ''))
    
    st.subheader("My Performance")
    
    if user:
        performance = bonus_engine.get_user_performance(user)
        if performance:
            for record in performance[-5:]:
                st.markdown(
                    f"- **{record['category']}**: Score {record['score']:.2f} | "
                    f"Bonus: {record['bonus']:.4f} NXT"
                )
        else:
            st.info("No performance records yet. Participate in the ecosystem to earn bonuses!")
    else:
        st.info("Connect wallet to see your performance")
    
    # Period history
    st.markdown("---")
    st.subheader("Recent Distribution History")
    
    history = bonus_engine.get_period_history(5)
    if history:
        for period in history:
            st.markdown(
                f"- Period `{period['period_id']}`: "
                f"Distributed {period['distributed']:,.2f} NXT to {period['participants']} participants"
            )
    else:
        st.info("No distribution history yet")


def render_carbon_credits_section(ecosystem: PoolEcosystem, token_system):
    """Render carbon credits and environmental sustainability section"""
    
    st.subheader("Carbon Credits & Environmental Offsets")
    st.markdown("""
    **Trade carbon credits and support environmental sustainability.**
    
    Part of NexusOS commitment to building a civilization that works with nature.
    """)
    
    # Pool status
    carbon_pool = ecosystem.get_pool("CARBON_CREDITS_POOL")
    env_pool = ecosystem.get_pool("ENVIRONMENTAL_POOL")
    
    col1, col2 = st.columns(2)
    
    with col1:
        balance = carbon_pool.metrics.current_balance if carbon_pool else 0
        st.metric(
            "Carbon Credits Pool",
            f"{balance:,.2f} NXT",
            "Available for offset trading"
        )
    
    with col2:
        balance = env_pool.metrics.current_balance if env_pool else 0
        st.metric(
            "Environmental Pool",
            f"{balance:,.2f} NXT",
            "Sustainability programs"
        )
    
    st.markdown("---")
    
    # Carbon offset categories
    st.subheader("Offset Categories")
    
    offset_types = [
        ("Reforestation", "1 NXT = 1 ton CO2", "Tree planting programs"),
        ("Renewable Energy", "0.5 NXT = 1 ton CO2", "Solar/wind projects"),
        ("Ocean Cleanup", "2 NXT = 1 ton CO2", "Marine conservation"),
        ("Methane Capture", "1.5 NXT = 1 ton CO2", "Agricultural emissions"),
    ]
    
    cols = st.columns(4)
    for i, (name, rate, desc) in enumerate(offset_types):
        with cols[i]:
            st.markdown(f"**{name}**")
            st.caption(rate)
            st.caption(f"_{desc}_")
    
    st.markdown("---")
    
    # Purchase carbon offsets
    st.subheader("Purchase Carbon Offsets")
    
    col1, col2 = st.columns(2)
    
    with col1:
        offset_category = st.selectbox(
            "Offset Type",
            ["Reforestation", "Renewable Energy", "Ocean Cleanup", "Methane Capture"]
        )
    
    with col2:
        tons_co2 = st.number_input("Tons CO2 to Offset", min_value=1, value=10)
    
    # Calculate cost based on category
    rates = {"Reforestation": 1.0, "Renewable Energy": 0.5, "Ocean Cleanup": 2.0, "Methane Capture": 1.5}
    cost = tons_co2 * rates.get(offset_category, 1.0)
    
    st.info(f"Cost: **{cost:.2f} NXT** for {tons_co2} tons CO2 offset")
    
    if st.button("Purchase Carbon Offset", type="primary"):
        user = st.session_state.get('active_address', st.session_state.get('user_address', ''))
        if not user:
            st.error("Please connect your wallet first")
        else:
            st.success(f"Purchased {tons_co2} tons CO2 offset via {offset_category}!")
            st.balloons()
            st.info("Thank you for supporting environmental sustainability!")
    
    st.markdown("---")
    
    # Environmental impact
    st.subheader("Ecosystem Environmental Impact")
    
    impact_metrics = [
        ("Total CO2 Offset", "1,250 tons", "Equivalent to 50 cars/year"),
        ("Trees Planted", "5,000", "Through reforestation"),
        ("Clean Energy Funded", "500 MWh", "Solar and wind"),
        ("Ocean Plastic Removed", "10 tons", "Marine conservation"),
    ]
    
    cols = st.columns(4)
    for i, (metric, value, note) in enumerate(impact_metrics):
        with cols[i]:
            st.metric(metric, value)
            st.caption(note)


if __name__ == "__main__":
    st.set_page_config(page_title="NexusOS Service Pools", layout="wide")
    render_service_pools_page()
