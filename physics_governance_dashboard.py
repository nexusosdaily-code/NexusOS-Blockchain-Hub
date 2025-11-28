"""
Physics Governance Dashboard — NexusOS

Interactive UI for the physics-based governance primitives.
Displays authority bands, constitutional clauses, multi-sig operations,
and security anomaly monitoring.

GPL v3.0 License — Community Owned, Physics Governed
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import pandas as pd

from physics_governance_primitives import (
    get_governance_engine,
    PhysicsGovernanceEngine,
    AuthorityBand,
    GovernanceEventType,
    AnomalyType,
    WaveformEventIdentity,
    EconomicStake,
    MultiSensorEndorsement,
    PlanckTimestamp,
    ConstitutionalClause,
    SecurityAnomaly
)

try:
    from governance.enforcer import (
        ConstitutionalEnforcer,
        EnforcementResult,
        EnforcementStatus,
        GLOBAL_ENFORCER,
        BAND_LEVEL_MAP
    )
    ENFORCER_AVAILABLE = True
except ImportError:
    ENFORCER_AVAILABLE = False
    GLOBAL_ENFORCER = None


def render_physics_governance_page():
    """Main entry point for Physics Governance dashboard"""
    
    st.markdown("""
    <style>
    .governance-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
        border: 1px solid rgba(0, 180, 255, 0.3);
    }
    .authority-card {
        background: rgba(0, 50, 80, 0.4);
        border-radius: 10px;
        padding: 15px;
        margin: 5px 0;
        border-left: 4px solid;
    }
    .constitution-box {
        background: rgba(100, 0, 100, 0.2);
        border: 1px solid rgba(180, 0, 180, 0.5);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    .anomaly-alert {
        background: rgba(255, 50, 50, 0.2);
        border: 1px solid rgba(255, 100, 100, 0.5);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    engine = get_governance_engine()
    
    st.markdown("""
    <div class="governance-header">
        <h2 style="color: #00d4ff; margin: 0;">⚛️ Physics Governance Primitives</h2>
        <p style="color: #888; margin: 5px 0 0 0;">
            "Constructing the rules of nature into the governance of civilization"
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    tabs = st.tabs([
        "🎚️ Authority Bands",
        "📜 Constitution",
        "✍️ Multi-Sig",
        "🚨 Security",
        "📊 Analytics"
    ])
    
    with tabs[0]:
        render_authority_bands_tab(engine)
    
    with tabs[1]:
        render_constitution_tab(engine)
    
    with tabs[2]:
        render_multi_sig_tab(engine)
    
    with tabs[3]:
        render_security_tab(engine)
    
    with tabs[4]:
        render_analytics_tab(engine)


def render_authority_bands_tab(engine: PhysicsGovernanceEngine):
    """Display the 7 authority bands with their properties"""
    
    st.subheader("Seven Authority Bands (Nano → Planck)")
    
    st.markdown("""
    Higher bands require more energy, more endorsements, and carry more authority weight.
    
    **Formula:** `E = h·f·n_cycles·authority²`
    """)
    
    band_colors = {
        'nano': '#00ff00',
        'pico': '#00ffff',
        'femto': '#0088ff',
        'atto': '#8800ff',
        'zepto': '#ff00ff',
        'yocto': '#ff8800',
        'planck': '#ff0000'
    }
    
    for band in AuthorityBand:
        color = band_colors.get(band.band_name, '#ffffff')
        
        base_cost = EconomicStake.calculate(band, cycles=1, staker_address="DEMO").total_cost_nxt
        
        st.markdown(f"""
        <div class="authority-card" style="border-left-color: {color};">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h4 style="color: {color}; margin: 0;">
                        Level {band.authority_level}: {band.band_name.upper()}
                    </h4>
                    <p style="color: #888; margin: 5px 0; font-size: 0.9em;">
                        {band.role}
                    </p>
                </div>
                <div style="text-align: right;">
                    <div style="color: #00d4ff; font-size: 1.2em;">
                        {base_cost:.6f} NXT
                    </div>
                    <div style="color: #888; font-size: 0.8em;">
                        {band.min_endorsements_required} endorsement(s) required
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    st.subheader("Cost Calculator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        operation = st.selectbox(
            "Operation Type",
            options=[
                'send_message',
                'create_wallet',
                'transfer_tokens',
                'stake_tokens',
                'create_proposal',
                'cast_vote',
                'enforce_policy',
                'emergency_override',
                'planetary_broadcast',
                'resolve_anomaly',
                'amend_constitution',
                'modify_bhls'
            ],
            key="gov_operation_select"
        )
    
    with col2:
        cycles = st.number_input("Wave Cycles", min_value=1, max_value=1000, value=1, key="gov_cycles_input")
    
    required_band = engine.get_required_authority_for_operation(operation)
    cost = engine.calculate_operation_cost(operation, cycles)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Required Band", required_band.band_name.upper())
    
    with col2:
        st.metric("Authority Level", required_band.authority_level)
    
    with col3:
        st.metric("Cost (NXT)", f"{cost:.6f}")


def render_constitution_tab(engine: PhysicsGovernanceEngine):
    """Display and manage constitutional clauses"""
    
    st.subheader("📜 NexusOS Constitution v1")
    
    if ENFORCER_AVAILABLE and GLOBAL_ENFORCER:
        enforcer = GLOBAL_ENFORCER
        constitution_hash = enforcer.get_constitution_hash()[:16]
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.info("The NexusOS Constitution defines inviolable rules for civilization governance. "
                    "Enforcement is automatic at the protocol level.")
        with col2:
            st.caption(f"Hash: `{constitution_hash}...`")
        
        formal_clauses = enforcer.get_all_clauses()
        
        st.markdown("### Formal Constitutional Clauses")
        
        for clause in formal_clauses:
            level = clause.get("level", "NANO")
            level_color = {
                "NANO": "#00ff88",
                "PICO": "#00ddff",
                "FEMTO": "#00aaff",
                "ATTO": "#ffaa00",
                "ZEPTO": "#ff8800",
                "YOCTO": "#ff00ff",
                "PLANCK": "#ff0000"
            }.get(level, "#ffffff")
            
            enforcement = clause.get("enforcement", {})
            enforcement_type = enforcement.get("type", "manual")
            required_attestations = enforcement.get("required_attestations", [])
            remedy = enforcement.get("remedy", "N/A")
            
            with st.expander(f"⚖️ {clause['id']}: {clause['title']}", expanded=True):
                st.markdown(f"""
                <div class="constitution-box">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                        <span style="color: {level_color}; font-weight: bold; font-size: 0.9em;">
                            Level: {level}
                        </span>
                        <span style="color: #888; font-size: 0.8em;">
                            Enforcement: {enforcement_type.upper()}
                        </span>
                    </div>
                    <div style="color: #ffffff; line-height: 1.8; font-size: 1.05em; margin: 15px 0;">
                        {clause['text']}
                    </div>
                    <div style="margin-top: 15px; padding-top: 10px; border-top: 1px solid rgba(180, 0, 180, 0.3);">
                        <div style="color: #888; font-size: 0.85em; margin-bottom: 5px;">
                            Required Attestations: 
                            <span style="color: #00d4ff;">{', '.join(required_attestations) if required_attestations else 'None'}</span>
                        </div>
                        <div style="color: #888; font-size: 0.85em;">
                            Remedy: <span style="color: #ffaa00;">{remedy}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        st.divider()
        st.markdown("### Enforcement Log")
        
        log_entries = enforcer.get_enforcement_log(limit=10)
        if log_entries:
            for entry in reversed(log_entries):
                status_color = {
                    "passed": "#00ff00",
                    "failed": "#ff0000",
                    "pending_attestation": "#ffaa00",
                    "quarantined": "#ff00ff"
                }.get(entry.get("status", ""), "#888888")
                
                st.markdown(f"""
                <div style="background: rgba(0, 50, 80, 0.3); border-left: 3px solid {status_color}; 
                     padding: 10px 15px; margin: 5px 0; border-radius: 5px;">
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: {status_color}; font-weight: bold;">
                            {entry.get('status', 'unknown').upper()}
                        </span>
                        <span style="color: #666; font-size: 0.8em;">
                            {entry.get('clause_id', 'N/A')}
                        </span>
                    </div>
                    <div style="color: #ccc; font-size: 0.9em; margin-top: 5px;">
                        {entry.get('message', '')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("No enforcement actions logged yet.")
    else:
        st.warning("Constitutional Enforcer module not loaded.")
    
    st.divider()
    st.markdown("### Engine-Level Clauses (Yocto-Encoded)")
    
    clauses = engine.get_constitutional_clauses()
    
    for clause in clauses:
        with st.expander(f"📋 {clause.title}", expanded=False):
            st.markdown(f"""
            <div class="constitution-box">
                <div style="color: #ff88ff; font-size: 0.8em; margin-bottom: 10px;">
                    Clause ID: {clause.clause_id}
                </div>
                <div style="color: #ffffff; line-height: 1.6;">
                    {clause.content}
                </div>
                <div style="margin-top: 15px; padding-top: 10px; border-top: 1px solid rgba(180, 0, 180, 0.3);">
                    <span style="color: #888;">Encoding Band:</span> 
                    <span style="color: #ff8800;">{clause.encoding_band.band_name.upper()}</span>
                    &nbsp;|&nbsp;
                    <span style="color: #888;">Amendments:</span> 
                    <span style="color: #00d4ff;">{len(clause.amendment_history)}</span>
                    &nbsp;|&nbsp;
                    <span style="color: #888;">Integrity:</span> 
                    <span style="color: {'#00ff00' if clause.verify_integrity() else '#ff0000'};">
                        {'✓ Verified' if clause.verify_integrity() else '✗ Compromised'}
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.divider()
    
    st.subheader("Propose New Constitutional Clause")
    
    with st.form("new_clause_form"):
        title = st.text_input("Clause Title", key="new_clause_title")
        content = st.text_area("Clause Content", height=100, key="new_clause_content")
        
        submitted = st.form_submit_button("Submit for Planck Consensus", type="primary")
        
        if submitted and title and content:
            new_clause = ConstitutionalClause.create(title, content)
            engine.constitutional_clauses[new_clause.clause_id] = new_clause
            st.success(f"Clause '{title}' submitted for Planck-level consensus approval.")
            st.rerun()


def render_multi_sig_tab(engine: PhysicsGovernanceEngine):
    """Display multi-signature endorsement operations"""
    
    st.subheader("✍️ Multi-Sensor Endorsement (Multi-Sig)")
    
    st.markdown("""
    High-authority operations require multiple independent sensor confirmations.
    This prevents fraud and ensures distributed consensus.
    """)
    
    pending = engine.get_pending_endorsements()
    
    if pending:
        st.warning(f"⏳ {len(pending)} pending endorsement(s)")
        
        for endorsement in pending:
            event_id = endorsement.event_id.hex()[:16] if endorsement.event_id else "Unknown"
            
            progress = endorsement.endorsement_count() / endorsement.required_threshold
            
            st.markdown(f"""
            <div style="background: rgba(0, 80, 120, 0.3); border-radius: 10px; padding: 15px; margin: 10px 0;">
                <div style="display: flex; justify-content: space-between;">
                    <div>
                        <strong style="color: #00d4ff;">Event: {event_id}...</strong>
                        <div style="color: #888; font-size: 0.9em;">
                            Authority: {endorsement.authority_band.band_name.upper()} (Level {endorsement.authority_band.authority_level})
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div style="color: #ffaa00; font-size: 1.2em;">
                            {endorsement.endorsement_count()} / {endorsement.required_threshold}
                        </div>
                        <div style="color: #888; font-size: 0.8em;">endorsements</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.progress(min(progress, 1.0))
            
            st.caption(f"Endorsers: {', '.join(endorsement.get_all_endorsers())}")
    else:
        st.success("✓ No pending multi-sig operations")
    
    st.divider()
    
    st.subheader("Create Multi-Sig Request")
    
    with st.form("multi_sig_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            event_type = st.selectbox(
                "Event Type",
                options=[e.value for e in GovernanceEventType],
                key="multi_sig_event_type"
            )
        
        with col2:
            band_name = st.selectbox(
                "Authority Band",
                options=[b.band_name.upper() for b in AuthorityBand],
                index=2,
                key="multi_sig_band"
            )
        
        payload = st.text_area("Event Payload", height=80, key="multi_sig_payload")
        
        submitted = st.form_submit_button("Create Multi-Sig Request", type="primary")
        
        if submitted and payload:
            band = next(b for b in AuthorityBand if b.band_name.upper() == band_name)
            event_type_enum = GovernanceEventType(event_type)
            
            event, stake = engine.create_governance_event(
                event_type=event_type_enum,
                payload=payload.encode(),
                authority_band=band
            )
            
            endorsement = engine.request_multi_sig_approval(event, band)
            
            st.success(f"Multi-sig request created. Event ID: {event.to_hex()[:16]}...")
            st.info(f"Requires {endorsement.required_threshold} endorsement(s) at {band.band_name.upper()} level")
            st.metric("Economic Stake", f"{stake.total_cost_nxt:.6f} NXT")


def render_security_tab(engine: PhysicsGovernanceEngine):
    """Display security anomalies and quarantine status"""
    
    st.subheader("🚨 Security Anomaly Detection")
    
    active_anomalies = engine.get_active_anomalies()
    
    if active_anomalies:
        st.error(f"⚠️ {len(active_anomalies)} active security anomalie(s)")
        
        for anomaly in active_anomalies:
            severity_color = '#ff0000' if anomaly.severity >= 8 else '#ffaa00' if anomaly.severity >= 5 else '#00ff00'
            
            st.markdown(f"""
            <div class="anomaly-alert">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong style="color: #ff6666;">
                            {anomaly.anomaly_type.code.upper().replace('_', ' ')}
                        </strong>
                        <div style="color: #888; font-size: 0.9em;">
                            ID: {anomaly.anomaly_id[:16]}...
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div style="color: {severity_color}; font-size: 1.5em; font-weight: bold;">
                            {anomaly.severity}/10
                        </div>
                        <div style="color: #888; font-size: 0.8em;">severity</div>
                    </div>
                </div>
                <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid rgba(255, 100, 100, 0.3);">
                    <span style="color: #888;">Quarantine:</span> 
                    <span style="color: {'#ff0000' if anomaly.quarantine_active else '#00ff00'};">
                        {'ACTIVE' if anomaly.quarantine_active else 'Inactive'}
                    </span>
                    &nbsp;|&nbsp;
                    <span style="color: #888;">Addresses:</span> 
                    <span style="color: #ffaa00;">{len(anomaly.quarantine_addresses)}</span>
                    &nbsp;|&nbsp;
                    <span style="color: #888;">Required Band:</span> 
                    <span style="color: #8800ff;">{anomaly.anomaly_type.required_band.band_name.upper()}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if anomaly.quarantine_addresses:
                with st.expander("View Quarantined Addresses"):
                    for addr in anomaly.quarantine_addresses:
                        st.code(addr)
    else:
        st.success("✓ No active security anomalies")
    
    st.divider()
    
    st.subheader("Simulate Anomaly Detection")
    
    with st.form("anomaly_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            anomaly_type = st.selectbox(
                "Anomaly Type",
                options=[a.code for a in AnomalyType],
                format_func=lambda x: x.upper().replace('_', ' '),
                key="anomaly_type_select"
            )
        
        with col2:
            severity = st.slider("Severity", 1, 10, 5, key="anomaly_severity")
        
        source_address = st.text_input("Source Address", value="NXS_SUSPECT_001", key="anomaly_source")
        auto_quarantine = st.checkbox("Auto-Quarantine (if severity >= 7)", value=True, key="auto_quarantine")
        
        submitted = st.form_submit_button("Trigger Anomaly Detection", type="primary")
        
        if submitted:
            anomaly_enum = next(a for a in AnomalyType if a.code == anomaly_type)
            
            anomaly = engine.detect_anomaly(
                anomaly_type=anomaly_enum,
                source_addresses=[source_address],
                evidence=f"Simulated anomaly: {anomaly_type}".encode(),
                severity=severity,
                auto_quarantine=auto_quarantine
            )
            
            if anomaly.quarantine_active:
                st.error(f"🚨 Anomaly detected and quarantine activated for {source_address}")
            else:
                st.warning(f"⚠️ Anomaly detected: {anomaly.anomaly_id[:16]}...")


def render_analytics_tab(engine: PhysicsGovernanceEngine):
    """Display governance analytics and statistics"""
    
    st.subheader("📊 Governance Analytics")
    
    stats = engine.get_governance_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Events", stats['total_events'])
    
    with col2:
        st.metric("Pending Multi-Sig", stats['pending_endorsements'])
    
    with col3:
        st.metric("Constitutional Clauses", stats['constitutional_clauses'])
    
    with col4:
        st.metric("Active Anomalies", stats['active_anomalies'])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Timestamp Chain", stats['timestamp_chain_length'])
    
    with col2:
        st.metric("Quarantined Addresses", stats['quarantined_addresses'])
    
    st.divider()
    
    st.subheader("Authority Band Distribution")
    
    band_data = []
    for band_name, props in stats['authority_bands'].items():
        band_data.append({
            'Band': band_name.upper(),
            'Level': props['level'],
            'Cost Multiplier': props['cost_multiplier'],
            'Min Endorsements': props['min_endorsements']
        })
    
    df = pd.DataFrame(band_data)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df['Band'],
        y=df['Cost Multiplier'],
        name='Cost Multiplier',
        marker_color=['#00ff00', '#00ffff', '#0088ff', '#8800ff', '#ff00ff', '#ff8800', '#ff0000']
    ))
    
    fig.update_layout(
        title="Authority Band Cost Multipliers",
        xaxis_title="Band",
        yaxis_title="Cost Multiplier (log scale)",
        yaxis_type="log",
        template="plotly_dark",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Physics-Governance Mapping Table")
    
    mapping_data = [
        {"Physics Primitive": "Waveform hash (physical_event_id)", "NexusOS Primitive": "Event identity", "Governance Semantic": "Single-source truth for action/event"},
        {"Physics Primitive": "Band used (nano..planck)", "NexusOS Primitive": "Authority tier", "Governance Semantic": "Higher band → higher authority weight & cost"},
        {"Physics Primitive": "Energy used (E = h·f·cycles)", "NexusOS Primitive": "Economic cost / stake", "Governance Semantic": "More energy = more commitment"},
        {"Physics Primitive": "Multi-sensor endorsement", "NexusOS Primitive": "Multi-sig attestation", "Governance Semantic": "Anti-fraud / higher threshold ops"},
        {"Physics Primitive": "Root timestamp (Planck-anchored)", "NexusOS Primitive": "Immutable time anchor", "Governance Semantic": "Final ordering and audit trail"},
        {"Physics Primitive": "Yocto-encoded declarations", "NexusOS Primitive": "Constitutional clause", "Governance Semantic": "Cannot override without Planck consensus"},
        {"Physics Primitive": "Anomaly patterns (atto/zepto)", "NexusOS Primitive": "Security alerts / quarantine", "Governance Semantic": "Auto-triggered emergency governance"},
    ]
    
    st.dataframe(pd.DataFrame(mapping_data), hide_index=True, use_container_width=True)


if __name__ == "__main__":
    st.set_page_config(page_title="Physics Governance", layout="wide")
    render_physics_governance_page()
