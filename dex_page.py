"""
DEX (Decentralized Exchange) UI Module
Interactive dashboard for token swapping, liquidity provision, and pool analytics
Integrated with NativeTokenSystem (NXT) as exclusive base currency
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import time
from dex_core import DEXEngine, Token, LiquidityPool, NativeTokenAdapter
from native_token import NativeTokenSystem
from pool_ecosystem import get_pool_ecosystem, PoolLayer, PoolType


def initialize_dex():
    """Initialize or get DEX engine with NXT integration from session state"""
    # Initialize NativeTokenSystem if not already done
    if 'native_token_system' not in st.session_state:
        st.session_state.native_token_system = NativeTokenSystem()
    
    # Initialize DEX engine with NXT adapter
    if 'dex_engine' not in st.session_state:
        # Create NXT adapter
        nxt_adapter = NativeTokenAdapter(st.session_state.native_token_system)
        
        # Create DEX engine with adapter
        st.session_state.dex_engine = DEXEngine(nxt_adapter=nxt_adapter)
        
        dex = st.session_state.dex_engine
        token_system = st.session_state.native_token_system
        
        # Set up user address
        if 'user_address' not in st.session_state:
            st.session_state.user_address = "dex_user_1"
        
        user = st.session_state.user_address
        
        # Give user initial NXT tokens (from treasury)
        treasury = "TREASURY"
        token_system.transfer(treasury, user, 100000)  # 1000 NXT in units
        
        # Give user some ERC-20 tokens
        dex.tokens["USDC"].mint(user, 10000)
        dex.tokens["GOV"].mint(user, 100)
        
        # Give treasury some ERC-20 tokens for initial liquidity
        dex.tokens["USDC"].mint("treasury", 100000)
        dex.tokens["GOV"].mint("treasury", 10000)
        
        # Give treasury NXT for pools (already has genesis allocation)
        # Create initial pools (all must be TOKEN/NXT pairs)
        dex.create_pool("USDC", "NXT", 10000, 1000, "treasury")  # USDC/NXT pool
        dex.create_pool("GOV", "NXT", 1000, 200, "treasury")     # GOV/NXT pool
    
    return st.session_state.dex_engine


def render_swap_interface(dex: DEXEngine):
    """Render token swap interface"""
    st.subheader("💱 Swap Tokens")
    st.info("💡 All trades use NXT as base currency")
    
    user = st.session_state.user_address
    
    col1, col2 = st.columns(2)
    
    # Build full token list including NXT
    all_tokens = list(dex.tokens.keys()) + ["NXT"]
    
    with col1:
        st.markdown("**From**")
        input_token = st.selectbox("Token", all_tokens, key="swap_input_token")
        
        # Get balance from appropriate source
        if input_token == "NXT":
            balance = dex.nxt_adapter.get_balance(user) if dex.nxt_adapter else 0.0
        else:
            balance = dex.tokens[input_token].balance_of(user)
        st.caption(f"Balance: {balance:.4f} {input_token}")
        
        input_amount = st.number_input(
            "Amount",
            min_value=0.0,
            max_value=float(balance),
            value=0.0,
            step=0.1,
            key="swap_input_amount"
        )
    
    with col2:
        st.markdown("**To**")
        output_tokens = [t for t in all_tokens if t != input_token]
        output_token = st.selectbox("Token", output_tokens, key="swap_output_token")
        
        # Get balance from appropriate source
        if output_token == "NXT":
            output_balance = dex.nxt_adapter.get_balance(user) if dex.nxt_adapter else 0.0
        else:
            output_balance = dex.tokens[output_token].balance_of(user)
        st.caption(f"Balance: {output_balance:.4f} {output_token}")
        
        # Get quote
        if input_amount > 0:
            output_amount, price_impact, effective_price = dex.get_quote(
                input_token, output_token, input_amount
            )
            st.metric("You will receive", f"{output_amount:.4f} {output_token}")
            
            # Show price impact
            if price_impact > 5:
                st.warning(f"⚠️ High price impact: {price_impact:.2f}%")
            else:
                st.info(f"Price impact: {price_impact:.2f}%")
            
            st.caption(f"Effective price: {effective_price:.6f} {output_token}/{input_token}")
        else:
            st.metric("You will receive", "0.0000")
    
    # Slippage tolerance
    slippage = st.slider("Slippage Tolerance (%)", 0.1, 5.0, 1.0, 0.1) / 100
    
    # Swap button
    if st.button("🔄 Swap", type="primary", use_container_width=True):
        if input_amount <= 0:
            st.error("Please enter an amount")
        else:
            success, output, message = dex.swap_tokens(
                user, input_token, output_token, input_amount, slippage
            )
            if success:
                st.success(f"✅ {message}")
                st.rerun()
            else:
                st.error(f"❌ {message}")


def render_liquidity_interface(dex: DEXEngine):
    """Render liquidity provision interface"""
    st.subheader("💧 Manage Liquidity")
    
    user = st.session_state.user_address
    
    tab1, tab2 = st.tabs(["Add Liquidity", "Remove Liquidity"])
    
    with tab1:
        st.markdown("**Add Liquidity to Pool**")
        st.info("💡 All pools must include NXT as one token")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Only show ERC-20 tokens for token_a (NXT is always token_b)
            available_tokens = list(dex.tokens.keys())
            token_a = st.selectbox("Token", available_tokens, key="liq_token_a")
            balance_a = dex.tokens[token_a].balance_of(user)
            st.caption(f"Balance: {balance_a:.4f}")
            amount_a = st.number_input(
                f"Amount {token_a}",
                min_value=0.0,
                max_value=float(balance_a),
                value=0.0,
                step=0.1,
                key="liq_amount_a"
            )
        
        with col2:
            # Token B is always NXT
            token_b = "NXT"
            st.markdown(f"**{token_b} (Base Currency)**")
            balance_b = dex.nxt_adapter.get_balance(user) if dex.nxt_adapter else 0.0
            st.caption(f"Balance: {balance_b:.4f}")
            amount_b = st.number_input(
                f"Amount {token_b}",
                min_value=0.0,
                max_value=float(balance_b),
                value=0.0,
                step=0.1,
                key="liq_amount_b"
            )
        
        # Check if pool exists (always TOKEN-NXT format)
        pool_id = f"{token_a}-{token_b}"
        pool_exists = pool_id in dex.pools
        
        if pool_exists:
            pool = dex.pools[pool_id]
            current_price = pool.get_price(token_a)
            st.info(f"Current pool price: 1 {token_a} = {current_price:.6f} {token_b}")
        
        if st.button("💧 Add Liquidity", type="primary", use_container_width=True):
            if amount_a <= 0 or amount_b <= 0:
                st.error("Please enter valid amounts")
            else:
                # Use DEX create_pool which handles NXT properly
                if not pool_exists:
                    success, message = dex.create_pool(token_a, token_b, amount_a, amount_b, user)
                    if success:
                        st.success(f"✅ {message}")
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
                else:
                    # Add to existing pool
                    pool = dex.pools[pool_id]
                    success, lp_tokens, message = pool.add_liquidity(user, amount_a, amount_b)
                    
                    if success:
                        # Transfer ERC-20 token
                        if not dex.tokens[token_a].transfer(user, pool_id, amount_a):
                            st.error(f"Failed to transfer {token_a}")
                            return
                        
                        # Transfer NXT via adapter
                        if dex.nxt_adapter and not dex.nxt_adapter.transfer(user, pool_id, amount_b):
                            st.error(f"Failed to transfer NXT")
                            return
                        
                        st.success(f"✅ {message}")
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
    
    with tab2:
        st.markdown("**Remove Liquidity from Pool**")
        
        # Show user's LP positions
        user_pools = []
        for pool_id, pool in dex.pools.items():
            lp_balance = pool.lp_balances.get(user, 0)
            if lp_balance > 0:
                user_pools.append({
                    'Pool': pool_id,
                    'LP Tokens': lp_balance,
                    'Share': f"{pool.get_pool_share(user):.2f}%"
                })
        
        if user_pools:
            df = pd.DataFrame(user_pools)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            selected_pool = st.selectbox("Select Pool", [p['Pool'] for p in user_pools], key="remove_liq_pool")
            if selected_pool:
                pool = dex.pools[selected_pool]
                
                max_lp = pool.lp_balances.get(user, 0)
                lp_amount = st.number_input(
                    "LP Tokens to Remove",
                    min_value=0.0,
                    max_value=float(max_lp),
                    value=0.0,
                    step=0.1
                )
                
                if lp_amount > 0:
                    share = lp_amount / pool.lp_token_supply
                    expected_a = pool.reserve_a * share
                    expected_b = pool.reserve_b * share
                    
                    st.info(f"You will receive: {expected_a:.4f} {pool.token_a} + {expected_b:.4f} {pool.token_b}")
                
                if st.button("💧 Remove Liquidity", type="primary", use_container_width=True):
                    if lp_amount <= 0:
                        st.error("Please enter amount")
                    else:
                        success, amount_a, amount_b, message = pool.remove_liquidity(user, lp_amount)
                        if success:
                            # Transfer tokens back (pool.token_b is always NXT)
                            # Transfer ERC-20 token (token_a)
                            if pool.token_a in dex.tokens:
                                dex.tokens[pool.token_a].transfer(selected_pool, user, amount_a)
                            # Transfer NXT (token_b) via adapter
                            if dex.nxt_adapter:
                                dex.nxt_adapter.transfer(selected_pool, user, amount_b)
                            st.success(f"✅ {message}")
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
        else:
            st.info("You don't have any liquidity positions")


def render_pools_overview(dex: DEXEngine):
    """Render all pools overview"""
    st.subheader("🏊 Liquidity Pools")
    
    pools_data = []
    for pool in dex.pools.values():
        pools_data.append({
            'Pool': pool.get_pool_id(),
            f'{pool.token_a} Reserve': f"{pool.reserve_a:.2f}",
            f'{pool.token_b} Reserve': f"{pool.reserve_b:.2f}",
            'TVL': f"{pool.reserve_a + pool.reserve_b:.2f}",
            'Volume': f"{pool.total_volume_a + pool.total_volume_b:.2f}",
            'Fees Collected': f"{pool.total_fees_collected:.4f}",
            'LPs': pool.to_dict()['liquidity_providers']
        })
    
    if pools_data:
        df = pd.DataFrame(pools_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No liquidity pools created yet")


def render_user_portfolio(dex: DEXEngine):
    """Render user's token balances and positions"""
    st.subheader("👛 Your Portfolio")
    
    user = st.session_state.user_address
    
    # Token balances
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Token Balances**")
        balances = dex.get_user_balances(user)
        
        if balances:
            balance_data = [
                {'Token': symbol, 'Balance': f"{amount:.4f}"}
                for symbol, amount in balances.items()
            ]
            df = pd.DataFrame(balance_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No token balances")
    
    with col2:
        st.markdown("**LP Positions**")
        lp_positions = []
        
        for pool_id, pool in dex.pools.items():
            lp_balance = pool.lp_balances.get(user, 0)
            if lp_balance > 0:
                lp_positions.append({
                    'Pool': pool_id,
                    'LP Tokens': f"{lp_balance:.4f}",
                    'Share': f"{pool.get_pool_share(user):.2f}%"
                })
        
        if lp_positions:
            df = pd.DataFrame(lp_positions)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No LP positions")


def render_pool_ecosystem_tab(dex: DEXEngine):
    """Render Pool Ecosystem hierarchy and DEX integration"""
    st.subheader("🏛️ Pool Ecosystem Architecture")
    st.info("💡 The DEX is supported by the F_floor foundation, which is backed by reserve pools. All DEX trading fees flow back to support the BHLS floor and validators.")
    
    # Get pool ecosystem
    ecosystem = get_pool_ecosystem()
    
    # Show hierarchical structure
    st.markdown("### 3-Layer Hierarchical Structure")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 🔵 Layer 1: Reserve Pools")
        st.markdown("**Supports F_floor foundation**")
        reserve_pools = ecosystem.get_pools_by_layer(PoolLayer.RESERVE)
        for pool in reserve_pools:
            with st.expander(f"📦 {pool.name}"):
                st.write(f"**Type**: {pool.pool_type.value}")
                st.write(f"**Description**: {pool.description}")
                st.metric("Balance", f"{pool.metrics.current_balance:.2f} NXT")
                st.metric("Participants", pool.metrics.participant_count)
                health = "✅ Healthy" if pool.is_healthy() else "⚠️ Needs Attention"
                st.write(f"**Status**: {health}")
    
    with col2:
        st.markdown("#### 🟢 Layer 2: F_floor Foundation")
        st.markdown("**Enables all economic activities**")
        f_floor = ecosystem.get_pool("F_FLOOR_POOL")
        if f_floor:
            with st.expander(f"💎 {f_floor.name}"):
                st.write(f"**Description**: {f_floor.description}")
                st.write(f"**Supported by**: {f_floor.supported_by}")
                st.metric("Balance", f"{f_floor.metrics.current_balance:.2f} NXT")
                st.metric("Participants", f_floor.metrics.participant_count)
                st.write(f"**Supports {len(f_floor.supports)} service pools**:")
                for supported in f_floor.supports[:3]:
                    st.caption(f"• {supported}")
                if len(f_floor.supports) > 3:
                    st.caption(f"...and {len(f_floor.supports) - 3} more")
    
    with col3:
        st.markdown("#### 🟡 Layer 3: Service Pools")
        st.markdown("**All economic activities**")
        service_pools = ecosystem.get_pools_by_layer(PoolLayer.SERVICE)
        
        # Highlight DEX pool
        dex_pool = ecosystem.get_pool("DEX_POOL")
        if dex_pool:
            with st.expander(f"💱 {dex_pool.name} (YOU ARE HERE)", expanded=True):
                st.write(f"**Description**: {dex_pool.description}")
                st.write(f"**Supported by**: {dex_pool.supported_by}")
                st.metric("Balance", f"{dex_pool.metrics.current_balance:.2f} NXT")
                st.success("✅ DEX fees → F_floor → BHLS Support")
        
        st.caption(f"**{len(service_pools)} total service pools:**")
        for pool in service_pools[:5]:
            st.caption(f"• {pool.name}")
        if len(service_pools) > 5:
            st.caption(f"...and {len(service_pools) - 5} more")
    
    st.divider()
    
    # Flow diagram
    st.markdown("### 💰 Economic Flow")
    st.markdown("""
    ```
    Reserve Pools (VALIDATOR_POOL + TRANSITION_RESERVE + ECOSYSTEM_FUND)
            ⬇️ Support
    F_FLOOR_POOL (Basic Human Living Standards)
            ⬇️ Enables
    Service Pools (DEX + Investment + Staking + Environmental + 6 more)
            ⬆️ Fees flow back
    F_FLOOR_POOL (Strengthens foundation)
            ⬆️ Support flows
    Reserve Pools (Validator rewards + Ecosystem growth)
    ```
    """)
    
    st.divider()
    
    # All 10 Service Pools Dashboard
    st.markdown("### 🎯 All Service Pools (Enabled by F_floor)")
    
    service_pool_data = []
    for pool in service_pools:
        service_pool_data.append({
            'Pool Name': pool.name,
            'Type': pool.pool_type.value.replace('_', ' ').title(),
            'Balance': f"{pool.metrics.current_balance:.2f} NXT",
            'Participants': pool.metrics.participant_count,
            'Status': "✅ Healthy" if pool.is_healthy() else "⚠️ Attention",
            'Utilization': f"{pool.metrics.calculate_utilization():.1f}%"
        })
    
    if service_pool_data:
        df = pd.DataFrame(service_pool_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Service pool distribution chart
        st.markdown("### 📊 Service Pool Distribution")
        pool_balances = [ecosystem.get_pool(pid).metrics.current_balance for pid in ecosystem.hierarchy[PoolLayer.SERVICE] if ecosystem.get_pool(pid)]
        pool_names = [ecosystem.get_pool(pid).name for pid in ecosystem.hierarchy[PoolLayer.SERVICE] if ecosystem.get_pool(pid)]
        
        fig = go.Figure(data=[go.Pie(
            labels=pool_names,
            values=pool_balances,
            hole=0.4,
            marker=dict(colors=px.colors.qualitative.Set3)
        )])
        fig.update_layout(
            title="Distribution Across Service Pools",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Ecosystem Health Verification
    st.markdown("### 🔍 Ecosystem Health Verification")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # F_floor support verification
        support_report = ecosystem.verify_f_floor_support()
        
        st.metric("Reserve Total", f"{support_report.get('reserve_total', 0):.2f} NXT")
        st.metric("F_floor Balance", f"{support_report.get('f_floor_balance', 0):.2f} NXT")
        st.metric("Service Pools Total", f"{support_report.get('service_total', 0):.2f} NXT")
        st.metric("Service Pool Count", support_report.get('service_pool_count', 0))
        
        hierarchy_valid = support_report.get('hierarchy_valid', False)
        if hierarchy_valid:
            st.success("✅ Hierarchy Valid: Reserves → F_floor → Services")
        else:
            st.error("❌ Hierarchy needs attention")
    
    with col2:
        # Overall ecosystem health
        health_report = ecosystem.get_ecosystem_health()
        
        for layer_name, layer_health in health_report['by_layer'].items():
            st.markdown(f"**{layer_name.title()} Layer**")
            health_pct = layer_health['health_percentage']
            
            if health_pct == 100:
                st.success(f"✅ {layer_health['healthy_pools']}/{layer_health['total_pools']} pools healthy ({health_pct:.0f}%)")
            elif health_pct >= 75:
                st.info(f"ℹ️ {layer_health['healthy_pools']}/{layer_health['total_pools']} pools healthy ({health_pct:.0f}%)")
            else:
                st.warning(f"⚠️ {layer_health['healthy_pools']}/{layer_health['total_pools']} pools healthy ({health_pct:.0f}%)")
        
        st.divider()
        overall = health_report['overall']
        st.metric("Overall Ecosystem Health", f"{overall['health_percentage']:.1f}%")
        st.caption(f"{overall['healthy_pools']}/{overall['total_pools']} pools healthy")


def render_analytics(dex: DEXEngine):
    """Render DEX analytics and charts"""
    st.subheader("📊 Analytics")
    
    # Overall stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Pools", len(dex.pools))
    with col2:
        st.metric("Total Tokens", len(dex.tokens))
    with col3:
        st.metric("Total Swaps", dex.total_swaps)
    with col4:
        total_tvl = sum(p.reserve_a + p.reserve_b for p in dex.pools.values())
        st.metric("Total TVL", f"{total_tvl:.2f}")
    
    # Pool comparison
    if dex.pools:
        st.markdown("**Pool Comparison**")
        
        pool_data = []
        for pool in dex.pools.values():
            pool_data.append({
                'Pool': pool.get_pool_id(),
                'TVL': pool.reserve_a + pool.reserve_b,
                'Volume': pool.total_volume_a + pool.total_volume_b,
                'Fees': pool.total_fees_collected
            })
        
        df = pd.DataFrame(pool_data)
        
        # TVL comparison
        fig = px.bar(
            df,
            x='Pool',
            y='TVL',
            title='Total Value Locked by Pool',
            labels={'TVL': 'Total Value Locked'},
            color='TVL',
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Volume comparison
        fig2 = px.bar(
            df,
            x='Pool',
            y='Volume',
            title='Trading Volume by Pool',
            labels={'Volume': 'Total Volume'},
            color='Volume',
            color_continuous_scale='Greens'
        )
        st.plotly_chart(fig2, use_container_width=True)


def render_dex_page():
    """Main DEX page renderer"""
    st.title("🏦 DEX - Decentralized Exchange")
    st.markdown("**Automated Market Maker with Liquidity Pools**")
    
    # Initialize DEX
    dex = initialize_dex()
    
    # Navigation tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "💱 Swap",
        "💧 Liquidity",
        "🏊 Pools",
        "👛 Portfolio",
        "📊 Analytics",
        "🏛️ Pool Ecosystem"
    ])
    
    with tab1:
        render_swap_interface(dex)
    
    with tab2:
        render_liquidity_interface(dex)
    
    with tab3:
        render_pools_overview(dex)
    
    with tab4:
        render_user_portfolio(dex)
    
    with tab5:
        render_analytics(dex)
    
    with tab6:
        render_pool_ecosystem_tab(dex)
    
    # Nexus AI Research Report for Researchers
    st.divider()
    from nexus_ai import render_nexus_ai_button
    
    # Get sample DEX data for AI analysis
    pools = list(dex.pools.values())
    sample_pool = pools[0] if pools else None
    render_nexus_ai_button('dex', {
        'pair': f"{sample_pool.token_a}/{sample_pool.token_b}" if sample_pool else 'NXT/TOKEN',
        'liquidity': sample_pool.reserve_a + sample_pool.reserve_b if sample_pool else 0,
        'volume': sample_pool.total_volume_a + sample_pool.total_volume_b if sample_pool else 0,
        'price_impact': 0.5  # Sample value
    })


if __name__ == "__main__":
    render_dex_page()
