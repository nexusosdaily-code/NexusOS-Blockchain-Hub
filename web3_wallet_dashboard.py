"""
NexusOS Native Wallet Dashboard
================================

Mobile-first wallet interface for NXT tokens and WNSP messaging.
Accessible from any mobile phone browser - NO EXTERNAL WALLET NEEDED!
"""

import streamlit as st
import time
from typing import Dict, Optional
import json
from datetime import datetime

from nexus_native_wallet import NexusNativeWallet
from input_validators import validate_nxs_address, validate_amount


def init_wallet_session():
    """Initialize wallet in session state"""
    if 'nexus_wallet' not in st.session_state:
        st.session_state.nexus_wallet = NexusNativeWallet()
    if 'wallet_unlocked' not in st.session_state:
        st.session_state.wallet_unlocked = None
    if 'active_address' not in st.session_state:
        st.session_state.active_address = None


def render_web3_wallet_dashboard():
    """Main NexusOS Native Wallet dashboard - Mobile-first!"""
    
    init_wallet_session()
    wallet = st.session_state.nexus_wallet
    
    # Mobile-optimized CSS for better cursor display and readability
    st.markdown("""
        <style>
        /* Enhanced cursor pointer on interactive elements */
        button, a, img, [data-testid="stSelectbox"], 
        [data-testid="stExpander"], .stButton, select, 
        [data-testid="stTab"], input, textarea {
            cursor: pointer !important;
        }
        
        /* Make form inputs and buttons larger on mobile */
        input, textarea, select {
            font-size: 16px !important;
            padding: 12px !important;
            min-height: 48px !important;
        }
        
        button, [data-testid="stButton"] button {
            font-size: 16px !important;
            padding: 12px 24px !important;
            min-height: 48px !important;
        }
        
        /* Mobile-first responsive layout */
        @media (max-width: 768px) {
            input, textarea, select {
                font-size: 18px !important;
                padding: 14px !important;
                min-height: 52px !important;
            }
            
            button, [data-testid="stButton"] button {
                font-size: 18px !important;
                padding: 14px 28px !important;
                min-height: 52px !important;
            }
        }
        
        /* Hover effects for better interactivity */
        img:hover {
            cursor: pointer !important;
            opacity: 0.9;
            transform: scale(1.02);
            transition: all 0.2s ease;
        }
        
        button:hover, [data-testid="stButton"]:hover {
            cursor: pointer !important;
            transform: translateY(-2px);
            transition: all 0.2s ease;
        }
        
        [data-testid="stExpander"]:hover {
            cursor: pointer !important;
            background-color: rgba(255, 255, 255, 0.05);
            transition: all 0.2s ease;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("💎 NexusOS Native Wallet")
    st.markdown("""
    **Your Phone IS the Blockchain Node!** 🚀  
    📱 **Mobile-First** | ⚛️ **Quantum-Resistant** | 🌈 **Wavelength Security** | 💰 **NXT Tokens**
    """)
    
    # Show active wallet indicator
    if st.session_state.active_address:
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            st.success(f"🔓 Active Wallet: `{st.session_state.active_address[:20]}...`")
        with col2:
            balance = wallet.get_balance(st.session_state.active_address)
            st.metric("Balance", f"{balance['balance_nxt']:.2f} NXT")
        with col3:
            if st.button("🔒 Lock"):
                st.session_state.wallet_unlocked = None
                st.session_state.active_address = None
                st.rerun()
    
    st.divider()
    
    # Mobile-optimized tabs
    tabs = st.tabs([
        "🏠 Home",
        "➕ Create Wallet",
        "🔓 Unlock Wallet",
        "💸 Send NXT",
        "📨 Send Message",
        "📜 History"
    ])
    
    with tabs[0]:
        render_home_tab(wallet)
    
    with tabs[1]:
        render_create_wallet_tab(wallet)
    
    with tabs[2]:
        render_unlock_wallet_tab(wallet)
    
    with tabs[3]:
        render_send_nxt_tab(wallet)
    
    with tabs[4]:
        render_send_message_tab(wallet)
    
    with tabs[5]:
        render_history_tab(wallet)


def render_home_tab(wallet):
    """Home dashboard with wallet overview"""
    
    st.header("🏠 Welcome to NexusOS Wallet")
    
    st.info("""
    ### 📱 Mobile-First Blockchain Wallet
    
    Your phone is now a **full blockchain node**! No external wallets needed.
    
    **What makes this different:**
    - ✅ **Pure NexusOS** - No Ethereum, no MetaMask required
    - ✅ **Quantum-Resistant** - Multi-spectral wavelength encryption
    - ✅ **Mobile DAG** - Your messages create the mesh network
    - ✅ **NXT Native** - 1,000,000 NXT total supply
    - ✅ **Physics-Based** - E=hf energy costs for messages
    
    **Get Started:**
    1. 📝 Create a new wallet (or unlock existing)
    2. 💰 Check your NXT balance
    3. 📤 Send tokens to other addresses
    4. 📨 Send wavelength-encrypted messages
    5. 📊 View your transaction history
    """)
    
    st.divider()
    
    # Show all wallets
    st.subheader("📋 Your Wallets")
    wallets = wallet.list_wallets()
    
    if not wallets:
        st.warning("No wallets yet. Create one in the **Create Wallet** tab!")
    else:
        # Display as cards on mobile
        for w in wallets:
            with st.expander(f"💼 {w['address'][:30]}... ({w['balance_nxt']:.2f} NXT)"):
                col1, col2 = st.columns(2)
                with col1:
                    st.caption("**Address:**")
                    st.code(w['address'], language=None)
                    st.caption(f"**Created:** {w['created_at'][:10]}")
                with col2:
                    st.metric("Balance", f"{w['balance_nxt']:.2f} NXT")
                    
                    # Quick unlock from home
                    unlock_password = st.text_input(
                        "Password to unlock",
                        type="password",
                        key=f"pwd_{w['address'][:10]}",
                        placeholder="Enter password"
                    )
                    
                    if st.button(f"🔓 Unlock This Wallet", key=f"unlock_{w['address']}", type="primary"):
                        if not unlock_password:
                            st.error("Please enter password")
                        else:
                            try:
                                if wallet.unlock_wallet(w['address'], unlock_password):
                                    st.session_state.active_address = w['address']
                                    st.session_state.wallet_unlocked = w['address']
                                    st.success("✅ Wallet unlocked!")
                                    st.rerun()
                                else:
                                    st.error("❌ Invalid password")
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")


def render_create_wallet_tab(wallet):
    """Create new NexusOS wallet"""
    
    st.header("➕ Create New Wallet")
    
    st.markdown("""
    Create a **quantum-resistant** NXT wallet secured with:
    - 🔐 AES-256-GCM encryption
    - 🌈 Multi-spectral signatures (UV, Red, Green, IR)
    - 🔑 PBKDF2 key derivation (100K iterations)
    """)
    
    with st.form("create_wallet_form"):
        st.subheader("Wallet Setup")
        
        password = st.text_input(
            "Password",
            type="password",
            help="Minimum 8 characters - CANNOT BE RECOVERED!",
            placeholder="Enter secure password"
        )
        
        password_confirm = st.text_input(
            "Confirm Password",
            type="password",
            placeholder="Repeat password"
        )
        
        initial_balance = st.number_input(
            "Initial Balance (NXT)",
            min_value=0.0,
            max_value=10000.0,
            value=0.0,
            step=10.0,
            help="Starting NXT balance (for testing)"
        )
        
        submit = st.form_submit_button("🚀 Create Wallet", type="primary", width="stretch")
        
        if submit:
            if len(password) < 8:
                st.error("❌ Password must be at least 8 characters!")
            elif password != password_confirm:
                st.error("❌ Passwords don't match!")
            else:
                try:
                    with st.spinner("🔐 Creating quantum-resistant wallet..."):
                        result = wallet.create_wallet(password, initial_balance)
                        time.sleep(0.5)  # Show spinner
                    
                    st.success("✅ Wallet created successfully!")
                    
                    # Show wallet details
                    st.balloons()
                    
                    with st.container():
                        st.markdown("### 💎 Your New Wallet")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Balance", f"{result['balance_nxt']:.2f} NXT")
                        with col2:
                            st.metric("Spectral Regions", len(result['spectral_regions']))
                        
                        st.caption("**Your NexusOS Address:**")
                        st.code(result['address'], language=None)
                        
                        st.caption("**Quantum Spectral Signature:**")
                        st.text(", ".join(result['spectral_regions']))
                        
                        st.warning("⚠️ **SAVE YOUR PASSWORD!** It cannot be recovered if lost.")
                        
                        # Auto-unlock new wallet
                        st.session_state.active_address = result['address']
                        st.session_state.wallet_unlocked = result['address']
                
                except Exception as e:
                    st.error(f"❌ Error creating wallet: {str(e)}")


def render_unlock_wallet_tab(wallet):
    """Unlock existing wallet with scrollable wallet list"""
    
    st.header("🔓 Unlock Wallet")
    
    wallets = wallet.list_wallets()
    
    if not wallets:
        st.warning("No wallets found. Create one first!")
        return
    
    # Initialize selected wallet in session state
    if 'selected_unlock_wallet' not in st.session_state:
        st.session_state.selected_unlock_wallet = wallets[0]['address'] if wallets else None
    
    # Check if we need to unlock a specific wallet
    unlock_target = st.session_state.get('unlock_target')
    if unlock_target:
        st.session_state.selected_unlock_wallet = unlock_target
        st.session_state.unlock_target = None
    
    st.caption(f"📋 **{len(wallets)} wallet(s) found** - Select one to unlock")
    
    # Scrollable wallet container with CSS - LIGHT THEME
    st.markdown("""
        <style>
        .wallet-scroll-container {
            max-height: 300px;
            overflow-y: auto;
            padding: 10px;
            border: 2px solid rgba(102, 126, 234, 0.4);
            border-radius: 12px;
            background: rgba(255, 255, 255, 0.95);
            margin-bottom: 20px;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.15);
        }
        .wallet-card {
            background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
            border: 2px solid rgba(102, 126, 234, 0.3);
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 10px;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .wallet-card:hover {
            border-color: #667eea;
            transform: translateX(5px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.25);
        }
        .wallet-card.selected {
            border-color: #10b981 !important;
            background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
            box-shadow: 0 0 15px rgba(16, 185, 129, 0.3);
        }
        .wallet-address {
            font-family: monospace;
            font-size: 13px;
            color: #1B1B2F;
            word-break: break-all;
            background: rgba(102, 126, 234, 0.1);
            padding: 8px;
            border-radius: 6px;
            margin-top: 8px;
        }
        .wallet-balance {
            font-size: 18px;
            font-weight: bold;
            color: #047857;
        }
        .wallet-label {
            font-size: 14px;
            color: #1e3a5f;
            font-weight: 600;
            margin-bottom: 5px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Display wallets in scrollable container
    st.markdown('<div class="wallet-scroll-container">', unsafe_allow_html=True)
    
    for i, w in enumerate(wallets):
        is_selected = w['address'] == st.session_state.selected_unlock_wallet
        
        col1, col2 = st.columns([4, 1])
        with col1:
            # Display wallet info
            selected_marker = "✅ " if is_selected else "💼 "
            st.markdown(f"""
                <div class="wallet-card {'selected' if is_selected else ''}">
                    <div class="wallet-label">{selected_marker}Wallet {i+1}</div>
                    <div class="wallet-balance">{w['balance_nxt']:.4f} NXT</div>
                    <div class="wallet-address">{w['address']}</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Selection button
            if st.button("Select" if not is_selected else "Selected", key=f"select_wallet_{i}", disabled=is_selected):
                st.session_state.selected_unlock_wallet = w['address']
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Show currently selected wallet
    selected_address = st.session_state.selected_unlock_wallet
    if selected_address:
        selected_wallet = next((w for w in wallets if w['address'] == selected_address), None)
        if selected_wallet:
            st.success(f"🎯 **Selected:** {selected_address[:20]}...{selected_address[-10:]} ({selected_wallet['balance_nxt']:.4f} NXT)")
    
    st.divider()
    
    password = st.text_input(
        "Password",
        type="password",
        help="Enter your wallet password",
        key="unlock_password_input"
    )
    
    if st.button("🔓 Unlock Wallet", type="primary", width="stretch"):
        if not password:
            st.error("Please enter your password")
        elif not selected_address:
            st.error("Please select a wallet first")
        else:
            try:
                with st.spinner("🔐 Unlocking wallet..."):
                    if wallet.unlock_wallet(selected_address, password):
                        st.session_state.active_address = selected_address
                        st.session_state.wallet_unlocked = selected_address
                        
                        # IMMEDIATELY load friends from database on unlock
                        try:
                            from friend_manager import get_friend_manager
                            fm = get_friend_manager()
                            if fm:
                                db_friends = fm.get_friends(selected_address)
                                if db_friends:
                                    st.session_state.p2p_friends = db_friends
                                    st.success(f"✅ Wallet unlocked! {len(db_friends)} friends loaded.")
                                else:
                                    st.session_state.p2p_friends = []
                                    st.success("✅ Wallet unlocked!")
                        except Exception:
                            st.success("✅ Wallet unlocked!")
                        
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("❌ Invalid password")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")


def render_send_nxt_tab(wallet):
    """Send NXT tokens with physics-based cost preview"""
    
    st.header("💸 Send NXT Tokens")
    
    if not st.session_state.active_address:
        st.warning("🔒 Please unlock a wallet first!")
        return
    
    from_addr = st.session_state.active_address
    balance = wallet.get_balance(from_addr)
    
    st.info(f"💰 Available Balance: **{balance['balance_nxt']:.2f} NXT**")
    
    with st.form("send_nxt_form"):
        to_address = st.text_input(
            "Recipient Address",
            placeholder="NXS... (40+ characters)",
            help="NexusOS address starting with 'NXS'"
        )
        
        # Validate recipient address in real-time
        if to_address:
            is_valid, error_msg = validate_nxs_address(to_address)
            if not is_valid:
                st.error(f"⚠️ {error_msg}")
            else:
                st.success("✅ Valid NexusOS address")
        
        # Set default value based on balance (avoid max_value error)
        default_amount = min(1.0, float(balance['balance_nxt'])) if balance['balance_nxt'] > 0 else 0.01
        max_amount = max(0.01, float(balance['balance_nxt']))  # Ensure max >= min
        
        amount = st.number_input(
            "Amount (NXT)",
            min_value=0.01,
            max_value=max_amount,
            value=default_amount,
            step=0.01,
            help=f"Max: {balance['balance_nxt']:.2f} NXT",
            disabled=(balance['balance_nxt'] == 0)
        )
        
        password = st.text_input(
            "Confirm with Password",
            type="password",
            help="Your wallet password"
        )
        
        # Transaction cost preview with physics context
        st.divider()
        st.markdown("#### ⚡ Transaction Cost Preview")
        
        # Current fee structure
        network_fee = 0.01  # Flat network fee
        total_cost = amount + network_fee
        
        # Show actual costs
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("💸 Amount", f"{amount:.4f} NXT")
        with col2:
            st.metric("⚡ Network Fee", f"{network_fee:.4f} NXT")
        with col3:
            st.metric("📊 Total Cost", f"{total_cost:.4f} NXT")
        
        # Physics-based spectral classification (informational)
        PLANCK_CONSTANT = 6.62607015e-34  # J⋅s (CODATA 2018 exact value)
        
        # Classify transaction by spectral tier (for informational display)
        if amount >= 10000:
            spectral = ('GAMMA', 3e19, '🟣', 'Massive')
        elif amount >= 1000:
            spectral = ('X_RAY', 3e17, '🔵', 'Large')
        elif amount >= 100:
            spectral = ('ULTRAVIOLET', 1e16, '🟤', 'Medium')
        elif amount >= 10:
            spectral = ('VISIBLE', 5e14, '🟡', 'Small')
        else:
            spectral = ('INFRARED', 3e13, '🟠', 'Micro')
        
        region, frequency, icon, size = spectral
        energy_joules = PLANCK_CONSTANT * frequency
        
        with st.expander(f"{icon} Transaction Physics: {region} tier ({size} transaction)"):
            st.markdown(f"""
            **Quantum Energy Classification (E=hf)**
            - **Spectral Region:** {region}
            - **Frequency:** {frequency:.2e} Hz
            - **Energy:** {energy_joules:.2e} J
            - **Formula:** E = h × f = {PLANCK_CONSTANT:.2e} × {frequency:.2e}
            
            *Higher value transactions are classified at higher energy levels in the electromagnetic spectrum.*
            """)
        
        st.divider()
        
        submit = st.form_submit_button("📤 Send Transaction", type="primary", width="stretch")
        
        if submit:
            # Validate all inputs
            addr_valid = False
            if not to_address:
                st.error("Please enter recipient address")
            else:
                addr_valid, addr_error = validate_nxs_address(to_address)
                if not addr_valid:
                    st.error(f"❌ Invalid address: {addr_error}")
            
            if not addr_valid:
                pass  # Address error already shown
            elif not password:
                st.error("Please enter your password")
            elif amount <= 0:
                st.error("Amount must be positive")
            else:
                try:
                    # Generate/retrieve stable idempotency key for retry safety
                    # Key persists in session state across retries to prevent double-execution
                    import uuid
                    tx_key = f"tx_idempotency_{from_addr}_{to_address}_{amount}"
                    
                    if tx_key not in st.session_state:
                        # First attempt: Generate new key
                        st.session_state[tx_key] = uuid.uuid4().hex
                    
                    idempotency_key = st.session_state[tx_key]
                    
                    with st.spinner("🔐 Creating quantum-signed transaction..."):
                        tx = wallet.send_nxt(
                            from_addr, to_address, amount, password,
                            idempotency_key=idempotency_key
                        )
                        time.sleep(0.5)
                        
                        # Transaction succeeded! Clear the key for next transaction
                        del st.session_state[tx_key]
                    
                    st.success("✅ Transaction sent!")
                    st.balloons()
                    
                    with st.expander("📋 Transaction Details", expanded=True):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.caption("**TX ID:**")
                            st.code(tx['tx_id'], language=None)
                            st.caption(f"**Amount:** {tx['amount_nxt']:.2f} NXT")
                        with col2:
                            st.caption(f"**Fee:** {tx['fee_nxt']:.4f} NXT")
                            st.caption(f"**Quantum Proof:** {tx['quantum_proof']['interference_hash']}")
                        
                        # Show updated balance
                        new_balance = wallet.get_balance(from_addr)
                        st.metric(
                            "New Balance", 
                            f"{new_balance['balance_nxt']:.2f} NXT",
                            delta=f"-{amount + tx['fee_nxt']:.2f} NXT"
                        )
                
                except ValueError as e:
                    st.error(f"❌ {str(e)}")
                except Exception as e:
                    st.error(f"❌ Transaction failed: {str(e)}")


def render_send_message_tab(wallet):
    """Send WNSP quantum message"""
    
    st.header("📨 Send WNSP Message")
    
    if not st.session_state.active_address:
        st.warning("🔒 Please unlock a wallet first!")
        return
    
    from_addr = st.session_state.active_address
    balance = wallet.get_balance(from_addr)
    
    st.markdown("""
    Send **wavelength-encrypted** messages using WNSP v2.0 protocol:
    - 🌈 Spectral region selection (UV to Infrared)
    - ⚛️ Quantum-resistant cryptography
    - 📡 DAG mesh network linking
    - 💰 E=hf physics-based cost
    """)
    
    with st.form("send_message_form"):
        to_address = st.text_input(
            "Recipient (optional)",
            placeholder="NXS... or leave empty for broadcast",
            help="NexusOS address or empty for broadcast to network"
        )
        
        # Validate recipient address if provided
        if to_address:
            is_valid, error_msg = validate_nxs_address(to_address)
            if not is_valid:
                st.error(f"⚠️ {error_msg}")
            else:
                st.success("✅ Valid NexusOS address")
        
        content = st.text_area(
            "Message Content",
            placeholder="Type your message...",
            max_chars=280,
            help="Max 280 characters"
        )
        
        from wnsp_protocol_v2 import SpectralRegion
        region = st.selectbox(
            "Spectral Region",
            options=[
                ("Ultraviolet", SpectralRegion.UV),
                ("Violet", SpectralRegion.VIOLET),
                ("Blue", SpectralRegion.BLUE),
                ("Green", SpectralRegion.GREEN),
                ("Yellow", SpectralRegion.YELLOW),
                ("Orange", SpectralRegion.ORANGE),
                ("Red", SpectralRegion.RED),
                ("Infrared", SpectralRegion.IR)
            ],
            format_func=lambda x: f"{x[0]} ({x[1].value[1]*1e9:.0f}-{x[1].value[2]*1e9:.0f}nm)",
            help="Each region uses different wavelength encryption"
        )
        
        password = st.text_input(
            "Confirm with Password",
            type="password"
        )
        
        st.caption("💡 **Cost:** Based on E=hf (quantum energy)")
        
        submit = st.form_submit_button("📡 Send Message", type="primary", width="stretch")
        
        if submit:
            # Validate recipient if provided
            addr_valid = True
            if to_address:
                addr_valid, addr_error = validate_nxs_address(to_address)
                if not addr_valid:
                    st.error(f"❌ Invalid recipient: {addr_error}")
            
            if not addr_valid:
                pass  # Error already shown
            elif not content:
                st.error("Please enter a message")
            elif not password:
                st.error("Please enter your password")
            else:
                try:
                    with st.spinner("🌈 Creating wavelength-encrypted message..."):
                        msg = wallet.send_message(
                            from_addr,
                            content,
                            password,
                            to_address if to_address else None,
                            region[1]
                        )
                        time.sleep(0.5)
                    
                    st.success("✅ Message sent to DAG network!")
                    
                    with st.expander("📋 Message Details", expanded=True):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.caption("**Message ID:**")
                            st.code(msg['message_id'], language=None)
                            st.caption(f"**To:** {msg['to']}")
                        with col2:
                            st.caption(f"**Wavelength:** {msg['wavelength']*1e9:.1f} nm")
                            st.caption(f"**Cost:** {msg['cost_nxt']:.6f} NXT")
                
                except ValueError as e:
                    st.error(f"❌ {str(e)}")
                except Exception as e:
                    st.error(f"❌ Failed to send message: {str(e)}")


def render_history_tab(wallet):
    """Transaction and message history"""
    
    st.header("📜 Transaction History")
    
    if not st.session_state.active_address:
        st.warning("🔒 Please unlock a wallet first!")
        return
    
    address = st.session_state.active_address
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💸 NXT Transfers")
        tx_history = wallet.get_transaction_history(address)
        
        if not tx_history:
            st.info("No transactions yet")
        else:
            for tx in tx_history[:10]:  # Show last 10
                direction = "📤 Sent" if tx['from_address'] == address else "📥 Received"
                with st.expander(f"{direction} - {tx['amount_nxt']:.2f} NXT"):
                    st.caption(f"**TX ID:** `{tx['tx_id']}`")
                    st.caption(f"**From:** `{tx['from_address'][:30]}...`")
                    st.caption(f"**To:** `{tx['to_address'][:30]}...`")
                    st.caption(f"**Status:** {tx['status']}")
    
    with col2:
        st.subheader("📨 WNSP Messages")
        msg_history = wallet.get_message_history(address)
        
        if not msg_history:
            st.info("No messages yet")
        else:
            for msg in msg_history[:10]:  # Show last 10
                with st.expander(f"📡 {msg['spectral_region']} - {msg['content'][:20]}..."):
                    st.caption(f"**Message ID:** `{msg['message_id']}`")
                    st.caption(f"**To:** {msg['to_address'] or 'Broadcast'}")
                    st.caption(f"**Content:** {msg['content']}")
                    st.caption(f"**Cost:** {msg['cost_nxt']:.6f} NXT")
