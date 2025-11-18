"""
Long-Term Supply Sustainability Dashboard
==========================================

Visualize 50-100 year token supply projections and burn economics.
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

from longterm_tokenomics_simulation import (
    LongTermTokenomicsSimulator,
    AdoptionScenario,
    EconomicBalancingMechanism
)
from native_token import token_system


def render_longterm_supply_dashboard():
    """Render long-term tokenomics dashboard"""
    
    st.title("📊 Long-Term Supply Sustainability (50-100 Years)")
    
    st.markdown("""
    **Critical Analysis:** How burn mechanics affect NXT supply over decades.
    
    🔥 **Burn Sources:** Messages, Links, Videos, Transaction Fees  
    ⚖️ **Balancing:** Dynamic burns + Validator inflation  
    🎯 **Goal:** Sustainable economics for 100+ years
    """)
    
    st.divider()
    
    # Current supply metrics
    metrics = token_system.get_sustainability_metrics()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            "Circulating Supply",
            f"{metrics['circulating_nxt']:,.0f} NXT",
            f"{metrics['supply_percentage']:.1f}%"
        )
    with col2:
        st.metric(
            "Total Burned",
            f"{metrics['total_burned_nxt']:,.2f} NXT"
        )
    with col3:
        st.metric(
            "Sustainability Score",
            f"{metrics['sustainability_score']:.0f}/100",
            delta=None if metrics['sustainability_score'] >= 75 else "⚠️ Low"
        )
    with col4:
        st.metric(
            "Total Supply",
            f"{metrics['total_supply_nxt']:,.0f} NXT"
        )
    
    st.divider()
    
    # Tabs for different analyses
    tabs = st.tabs([
        "📈 100-Year Projection",
        "⚖️ Balancing Mechanisms",
        "🔬 Scenario Comparison",
        "📊 Current Economics"
    ])
    
    with tabs[0]:
        render_projection_tab()
    
    with tabs[1]:
        render_balancing_tab()
    
    with tabs[2]:
        render_scenario_comparison_tab()
    
    with tabs[3]:
        render_current_economics_tab()


def render_projection_tab():
    """100-year supply projection"""
    
    st.header("📈 100-Year Supply Projection")
    
    # Scenario selection
    scenario = st.selectbox(
        "Adoption Scenario",
        options=[
            ("Conservative (1K → 100K users)", AdoptionScenario.CONSERVATIVE),
            ("Moderate (1K → 1M users)", AdoptionScenario.MODERATE),
            ("Aggressive (1K → 10M users)", AdoptionScenario.AGGRESSIVE),
            ("Viral (1K → 50M users)", AdoptionScenario.VIRAL)
        ],
        format_func=lambda x: x[0]
    )
    
    years = st.slider("Simulation Years", 10, 100, 100, 10)
    
    if st.button("🔄 Run Simulation", type="primary"):
        with st.spinner("Running 100-year economic simulation..."):
            # Run simulation
            sim = LongTermTokenomicsSimulator()
            metrics = sim.simulate(years=years, scenario=scenario[1])
            df = sim.to_dataframe()
            
            # Get critical milestones
            milestones = sim.get_critical_years(metrics)
            
            # Plot supply over time
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=(
                    'Circulating Supply Over Time',
                    'Daily Burn Rate',
                    'Active Users Growth',
                    'Sustainability Score'
                ),
                vertical_spacing=0.12,
                horizontal_spacing=0.1
            )
            
            # Supply chart
            fig.add_trace(
                go.Scatter(
                    x=df['Year'],
                    y=df['Circulating Supply (NXT)'],
                    mode='lines',
                    name='Supply',
                    line=dict(color='#00FF88', width=3),
                    fill='tozeroy'
                ),
                row=1, col=1
            )
            
            # Burn rate chart
            fig.add_trace(
                go.Scatter(
                    x=df['Year'],
                    y=df['Daily Burn Rate (NXT)'],
                    mode='lines',
                    name='Burn Rate',
                    line=dict(color='#FF4444', width=2)
                ),
                row=1, col=2
            )
            
            # Users chart
            fig.add_trace(
                go.Scatter(
                    x=df['Year'],
                    y=df['Active Users'],
                    mode='lines',
                    name='Users',
                    line=dict(color='#4466FF', width=2),
                    fill='tozeroy'
                ),
                row=2, col=1
            )
            
            # Sustainability chart
            colors = ['green' if score >= 75 else 'orange' if score >= 50 else 'red' 
                     for score in df['Sustainability Score']]
            fig.add_trace(
                go.Bar(
                    x=df['Year'],
                    y=df['Sustainability Score'],
                    name='Sustainability',
                    marker=dict(color=colors)
                ),
                row=2, col=2
            )
            
            fig.update_xaxes(title_text="Year", row=1, col=1)
            fig.update_xaxes(title_text="Year", row=1, col=2)
            fig.update_xaxes(title_text="Year", row=2, col=1)
            fig.update_xaxes(title_text="Year", row=2, col=2)
            
            fig.update_yaxes(title_text="NXT", row=1, col=1)
            fig.update_yaxes(title_text="NXT/day", row=1, col=2)
            fig.update_yaxes(title_text="Users", row=2, col=1)
            fig.update_yaxes(title_text="Score (0-100)", row=2, col=2)
            
            fig.update_layout(
                height=700,
                showlegend=False,
                template="plotly_dark"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Show critical milestones
            if milestones:
                st.subheader("⚠️ Critical Milestones")
                cols = st.columns(len(milestones))
                for i, (milestone, year) in enumerate(milestones.items()):
                    with cols[i]:
                        label = milestone.replace('_', ' ').title()
                        st.metric(label, f"Year {year}")
            
            # Show key stats
            st.subheader("📊 Key Statistics")
            final_year = metrics[-1]
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    f"Year {final_year.year} Supply",
                    f"{final_year.circulating_supply:,.0f} NXT",
                    f"{final_year.circulating_supply/sim.INITIAL_SUPPLY*100:.1f}%"
                )
            with col2:
                st.metric(
                    "Total Burned",
                    f"{final_year.total_burned:,.0f} NXT"
                )
            with col3:
                st.metric(
                    "Sustainability",
                    f"{final_year.sustainability_score:.0f}/100"
                )


def render_balancing_tab():
    """Economic balancing mechanisms"""
    
    st.header("⚖️ Economic Balancing Mechanisms")
    
    st.markdown("""
    **Three mechanisms to prevent supply depletion:**
    """)
    
    # 1. Dynamic Burn Adjustment
    st.subheader("1️⃣ Dynamic Burn Rate Adjustment")
    st.markdown("Automatically reduces burn rates as supply decreases")
    
    supply_levels = [100, 75, 50, 25, 10]
    base_burn = 0.1
    
    data = []
    for supply_pct in supply_levels:
        supply = supply_pct * 10_000
        adjusted = EconomicBalancingMechanism.dynamic_burn_adjustment(
            base_burn, supply, 1_000_000
        )
        data.append({
            'Supply %': f"{supply_pct}%",
            'Base Burn': base_burn,
            'Adjusted Burn': adjusted,
            'Reduction': f"{(1 - adjusted/base_burn)*100:.0f}%"
        })
    
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)
    
    # 2. Validator Inflation
    st.subheader("2️⃣ Validator Inflation (Bitcoin-style Halving)")
    st.markdown("Mints new NXT for validator rewards, decreases over time")
    
    inflation_years = [0, 4, 8, 12, 20, 40, 80]
    inflation_data = []
    for year in inflation_years:
        rate = EconomicBalancingMechanism.calculate_validator_inflation(year)
        inflation_data.append({
            'Year': year,
            'Inflation Rate': f"{rate:.2f}%",
            'Annual Mint (500K supply)': f"{500_000 * (rate/100):,.0f} NXT"
        })
    
    df_inflation = pd.DataFrame(inflation_data)
    st.dataframe(df_inflation, use_container_width=True)
    
    # 3. Burn Cap
    st.subheader("3️⃣ Annual Burn Cap (5% Maximum)")
    st.markdown("Prevents excessive burns in any single year")
    
    cap_data = []
    for supply in [1_000_000, 500_000, 100_000, 10_000]:
        proposed = 100_000
        capped = EconomicBalancingMechanism.apply_annual_burn_cap(
            proposed, supply, max_burn_pct=5.0
        )
        cap_data.append({
            'Supply': f"{supply:,} NXT",
            'Proposed Burn': f"{proposed:,} NXT",
            'Capped Burn': f"{capped:,.0f} NXT",
            'Protection': "✅" if capped < proposed else "N/A"
        })
    
    df_cap = pd.DataFrame(cap_data)
    st.dataframe(df_cap, use_container_width=True)


def render_scenario_comparison_tab():
    """Compare all scenarios"""
    
    st.header("🔬 Scenario Comparison")
    
    st.markdown("Compare all adoption scenarios side-by-side")
    
    if st.button("🔄 Run All Scenarios", type="primary"):
        scenarios = [
            AdoptionScenario.CONSERVATIVE,
            AdoptionScenario.MODERATE,
            AdoptionScenario.AGGRESSIVE,
            AdoptionScenario.VIRAL
        ]
        
        fig = go.Figure()
        
        for scenario in scenarios:
            with st.spinner(f"Simulating {scenario.value}..."):
                sim = LongTermTokenomicsSimulator()
                metrics = sim.simulate(years=100, scenario=scenario)
                df = sim.to_dataframe()
                
                fig.add_trace(go.Scatter(
                    x=df['Year'],
                    y=df['Circulating Supply (NXT)'],
                    mode='lines',
                    name=scenario.value.title(),
                    line=dict(width=3)
                ))
        
        fig.update_layout(
            title="Circulating Supply: All Scenarios (100 Years)",
            xaxis_title="Year",
            yaxis_title="Circulating Supply (NXT)",
            height=600,
            template="plotly_dark",
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)


def render_current_economics_tab():
    """Show current economic parameters"""
    
    st.header("📊 Current Economic Parameters")
    
    from native_token import NativeTokenSystem
    
    st.subheader("Burn Rates (Per Action)")
    
    burn_data = {
        'Action': ['Message', 'Link Share', 'Video Share', 'Transfer Fee'],
        'Burn Rate (NXT)': [
            NativeTokenSystem.MESSAGE_BURN_RATE,
            NativeTokenSystem.LINK_SHARE_BURN_RATE,
            NativeTokenSystem.VIDEO_SHARE_BURN_RATE,
            NativeTokenSystem.BASE_TRANSFER_FEE
        ],
        'Calibrated For': ['100+ years'] * 4
    }
    
    df_burns = pd.DataFrame(burn_data)
    st.dataframe(df_burns, use_container_width=True)
    
    st.subheader("Supply Allocation")
    
    allocation_data = {
        'Pool': ['Genesis Distribution', 'Validator Rewards', 'Ecosystem Development', 'Total'],
        'Amount (NXT)': [
            f"{NativeTokenSystem.GENESIS_SUPPLY / NativeTokenSystem.UNITS_PER_NXT:,.0f}",
            f"{NativeTokenSystem.VALIDATOR_RESERVE / NativeTokenSystem.UNITS_PER_NXT:,.0f}",
            f"{NativeTokenSystem.ECOSYSTEM_RESERVE / NativeTokenSystem.UNITS_PER_NXT:,.0f}",
            f"{NativeTokenSystem.TOTAL_SUPPLY / NativeTokenSystem.UNITS_PER_NXT:,.0f}"
        ],
        'Percentage': ['50%', '30%', '20%', '100%']
    }
    
    df_allocation = pd.DataFrame(allocation_data)
    st.dataframe(df_allocation, use_container_width=True)
    
    st.subheader("Balancing Features")
    
    features = {
        'Feature': [
            'Dynamic Burns',
            'Validator Inflation',
            'Inflation Rate',
            'Max Annual Burn'
        ],
        'Status': [
            '✅ Enabled' if NativeTokenSystem.ENABLE_DYNAMIC_BURNS else '❌ Disabled',
            '✅ Enabled' if NativeTokenSystem.ENABLE_VALIDATOR_INFLATION else '❌ Disabled',
            f"{NativeTokenSystem.VALIDATOR_INFLATION_RATE * 100:.1f}% (halves every 4 years)",
            f"{NativeTokenSystem.MAX_ANNUAL_BURN_PCT}% of circulating supply"
        ]
    }
    
    df_features = pd.DataFrame(features)
    st.dataframe(df_features, use_container_width=True)
