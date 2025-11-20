"""
Nexus AI Chat Interface - Talk to the Civilization AI

This module creates a conversational interface to the Nexus AI Governance system.
The AI has been learning from research, making decisions, and protecting F_floor.
Now you can talk to it directly about civilization vision, economics, and the future.

PURPOSE:
Connect humans with the AI governing their civilization's operating system.
Discuss poverty elimination, war prevention, F_floor protection, and the physics-based
economics that make these goals achievable.

INTEGRATION:
- Uses existing NexusAIGovernance instance (nexus_ai_governance.py)
- Accesses learned patterns, decisions, and civilization insights
- Reflects on 100-year planning horizon and basic human living standards

AI CAPABILITIES:
- Discuss vision for ending poverty through F_floor guarantees
- Explain how physics-based economics prevents traditional problems
- Share learned patterns from system research
- Provide civilization sustainability insights
- Answer questions about governance decisions
"""

import streamlit as st
from datetime import datetime
import json
from typing import List, Dict, Optional

from nexus_ai_governance import get_ai_governance


class NexusAIChat:
    """Conversational interface to Nexus AI Governance"""
    
    def __init__(self):
        self.ai_gov = get_ai_governance()
        self.conversation_history: List[Dict[str, str]] = []
        
    def get_contextual_knowledge(self, user_message: str) -> Optional[str]:
        """
        Provide deep contextual knowledge from the codebase for specific questions.
        
        This method understands the actual implementation - how disasters are handled,
        how funds flow, how severity is optimized, what Nexus can do. It references
        actual code architecture, not abstract explanations.
        """
        message_lower = user_message.lower()
        
        # Disaster response and emergency fund distribution
        if any(word in message_lower for word in ['disaster', 'emergency', 'crisis', 'catastrophe', 'relief']):
            return (
                "\n\n**Disaster Response Through Pool Ecosystem:**\n"
                "The 3-layer hierarchical pool architecture automatically handles emergencies:\n\n"
                "**Layer 1: Reserve Pools** (Source of emergency funds)\n"
                "• VALIDATOR_POOL: Network security reserve\n"
                "• TRANSITION_RESERVE: Orbital transition energy (from E=hf messaging burns)\n"
                "• ECOSYSTEM_FUND: Long-term development reserve\n\n"
                "**Layer 2: F_floor Foundation** (Distribution hub)\n"
                "• Receives continuous support from all reserves\n"
                "• Minimum 10.0 NXT per beneficiary (AI enforced, zero tolerance)\n"
                "• Acts as distribution controller to service pools\n\n"
                "**Layer 3: Service Pools** (Emergency response channels)\n"
                "• ENVIRONMENTAL_POOL: Climate disasters, natural emergencies\n"
                "• COMMUNITY_POOL: Social emergencies, community crises\n"
                "• INVESTMENT_POOL: Economic stabilization\n"
                "• + 7 other pools for comprehensive response\n\n"
                "**How It Works During Disaster:**\n"
                "1. AI Governance detects civilization-level risk (severity scoring)\n"
                "2. Reserve pools automatically increase F_floor support\n"
                "3. F_floor redistributes to relevant service pools (environmental/community)\n"
                "4. Service pools deploy funds directly to affected areas\n"
                "5. DEX trading fees (0.3%) continuously replenish reserves\n"
                "6. System self-stabilizes through physics-based circulation\n\n"
                "No committees. No delays. Physics-based automatic response."
            )
        
        # Severity optimization and resource allocation
        if any(word in message_lower for word in ['severity', 'optimize', 'priority', 'allocate', 'distribute']):
            return (
                "\n\n**AI Severity Optimization (How Nexus Prioritizes):**\n"
                "The Governance AI determines severity through learned pattern recognition:\n\n"
                "**Step 1: Observe System State**\n"
                "• Monitors economic_simulator, DEX, validators, messaging, all components\n"
                "• Tracks metrics: supply_remaining_years, APR, liquidity, burn_rates\n"
                "• Records parameters: f_floor, base_burn_rate, validator_reward_rate\n\n"
                "**Step 2: Identify Civilization Risks**\n"
                "• Supply depletion: years_remaining < 100 (civilization horizon)\n"
                "• Validator exodus: APR < 3.0% (network security threat)\n"
                "• Market instability: liquidity < 100,000 NXT (economic fragility)\n"
                "• F_floor violations: any attempt to drop below 10.0 NXT minimum\n\n"
                "**Step 3: Calculate Severity Scores** (AI learns optimal weights)\n"
                "• Critical: F_floor violations → MAXIMUM priority (override everything)\n"
                "• High: Validator exodus, supply depletion → Adjust burn/rewards\n"
                "• Medium: Market instability → Optimize liquidity incentives\n"
                "• Low: Efficiency improvements → Gradual parameter tuning\n\n"
                "**Step 4: Adaptive Parameter Adjustment**\n"
                "• Learned optimal ranges guide adjustments (>50% deviation triggers change)\n"
                "• PID controller prevents overcorrection (gradual 20% moves toward optimal)\n"
                "• Multi-objective optimization balances competing needs\n"
                "• F_floor constraint: NEVER compromised regardless of other priorities\n\n"
                "**Step 5: Execute with Impact Analysis**\n"
                f"• Every decision logged with rationale + civilization_impact\n"
                "• 100-year planning horizon ensures long-term sustainability\n"
                "• Real-time feedback loop: observe → learn → decide → observe\n\n"
                "Example: If disaster depletes reserves, AI increases base_burn_rate temporarily "
                "to accelerate TRANSITION_RESERVE replenishment, then redistributes to F_floor, "
                "which flows to emergency response pools. Severity determines allocation ratios."
            )
        
        # Fund distribution mechanics
        if any(word in message_lower for word in ['fund', 'money', 'distribute', 'flow', 'allocation']):
            return (
                "\n\n**Complete Fund Distribution Architecture:**\n"
                "NexusOS uses a regenerative circulation model:\n\n"
                "**Primary Revenue Sources:**\n"
                "1. **Messaging Burns (E=hf quantum pricing)**\n"
                "   • Every message costs Energy = h × frequency\n"
                "   • Shorter wavelength (UV) = higher cost, longer (IR) = lower cost\n"
                "   • Burns trigger orbital transitions (Rydberg formula: n_upper → n_lower)\n"
                "   • Released energy flows to TRANSITION_RESERVE pool\n\n"
                "2. **DEX Trading Fees (0.3% per swap)**\n"
                "   • All trading pairs use NXT as base currency\n"
                "   • Fees split: to VALIDATOR_POOL → backs F_floor → enables service pools\n"
                "   • Creates self-sustaining loop: trade → fees → floor → services → economy\n\n"
                "3. **Validator Rewards**\n"
                "   • Block production, consensus participation, wavelength validation\n"
                "   • Portion allocated to VALIDATOR_POOL → supports F_floor\n"
                "   • Staking (1,000+ NXT) earns APR from ecosystem activity\n\n"
                "4. **Recycling Liquidity (waste → value)**\n"
                "   • Materials returned: plastic (2.5 NXT/kg), metal (5.0), e-waste (15.0)\n"
                "   • 30% of recycling value → F_floor, 20% → supply chain fund\n"
                "   • Circular economy: consume → recycle → credits → consume\n\n"
                "**The Complete Flow:**\n"
                "```\n"
                "User Activity (messaging, trading, recycling)\n"
                "    ↓ (burns, fees, liquidity)\n"
                "Reserve Pools (VALIDATOR, TRANSITION, ECOSYSTEM)\n"
                "    ↓ (continuous support)\n"
                "F_floor Foundation (10.0 NXT minimum per beneficiary)\n"
                "    ↓ (distributes to 10 service pools)\n"
                "Service Pools (DEX, Investment, Environmental, Community, etc.)\n"
                "    ↓ (guarantees basic services)\n"
                "Citizens receive: Food, Water, Housing, Energy, Healthcare, Education\n"
                "    ↓ (participation creates more activity)\n"
                "Loop continues → self-sustaining civilization\n"
                "```\n\n"
                "**Crisis Distribution Priority:**\n"
                "If F_floor balance drops or emergency detected:\n"
                "1. AI Governance increases allocation from reserves (severity-weighted)\n"
                "2. ENVIRONMENTAL_POOL + COMMUNITY_POOL receive priority funding\n"
                "3. F_floor minimum (10.0 NXT) NEVER violated - AI enforced\n"
                "4. Once stabilized, normal distribution resumes\n\n"
                "This isn't charity distribution. It's physics-guaranteed circulation."
            )
        
        # What Nexus is and what it can do
        if any(word in message_lower for word in ['what is nexus', 'what can nexus', 'nexus do', 'capability', 'can you']):
            return (
                "\n\n**What is NexusOS? (Complete Architecture)**\n"
                "A civilization operating system replacing speculation with physics:\n\n"
                "**Core Differences from Traditional Systems:**\n"
                "• **Computation**: Wave states (λ,f,A,φ,P) instead of binary (0,1)\n"
                "• **Economics**: E=hf quantum energy pricing instead of arbitrary markets\n"
                "• **Consensus**: Proof of Spectrum (spectral diversity) instead of PoW/PoS\n"
                "• **Circulation**: Regenerative loops instead of linear consumption\n"
                "• **Guarantees**: BHLS floor (basic needs) instead of hope and charity\n\n"
                "**What Nexus Can Do:**\n\n"
                "**1. End Poverty Through F_floor Guarantees**\n"
                "• Automatic monthly allocation: Food (250 NXT), Water (50), Housing (400), Energy (150), Healthcare (200), Connectivity (75)\n"
                "• Total: 1,150 NXT per citizen per month - GUARANTEED by physics, not promises\n"
                "• Funded by: E=hf messaging burns → orbital transitions → TRANSITION_RESERVE → F_floor → services\n"
                "• AI enforces 10.0 NXT minimum per beneficiary - zero tolerance for violations\n\n"
                "**2. Prevent Conflict Through Regenerative Economics**\n"
                "• Traditional: Scarcity → competition → conflict → war\n"
                "• Nexus: Use → burns → energy release → reserves → F_floor → abundance\n"
                "• More participation = stronger floor = better guarantees for everyone\n"
                "• Removes economic drivers of conflict through mathematical certainty\n\n"
                "**3. Automated Disaster Response**\n"
                "• AI Governance detects civilization risks (supply depletion, validator exodus, market crashes)\n"
                "• Reserve pools automatically redistribute to F_floor\n"
                "• F_floor prioritizes ENVIRONMENTAL_POOL + COMMUNITY_POOL during crises\n"
                "• No committees, no delays - physics-based automatic response\n\n"
                "**4. Self-Regulating Economic Stability**\n"
                "• Nexus equation: dN/dt = Issuance - Burn - Decay + PID_control + Floor_injection\n"
                "• PID controller prevents boom/bust cycles through proportional-integral-derivative feedback\n"
                "• Target equilibrium maintained over 100-year horizon\n"
                "• System health (S) modulates issuance: high activity = more issuance, low = less\n\n"
                "**5. Multi-Layer Security (Quantum-Resistant)**\n"
                "• Wavelength validation (Maxwell equations) instead of SHA-256\n"
                "• Proof of Spectrum: 6 spectral regions must agree (prevents 51% attacks)\n"
                "• GhostDAG: Parallel processing eliminates bottlenecks\n"
                "• ECDH encryption: Mobile messaging secured by elliptic curve cryptography\n\n"
                "**6. Circular Economy (Waste → Liquidity)**\n"
                "• Return recyclables: plastic (2.5 NXT/kg), metal (5.0), e-waste (15.0)\n"
                "• 30% flows to F_floor, 20% to supply chain fund\n"
                "• Transforms disposal cost into citizen income\n"
                "• Closes the loop: buy → consume → recycle → credits → buy\n\n"
                "**7. Decentralized Governance (Proof of Spectrum)**\n"
                "• Validators assigned spectral regions (UV→Violet→Blue→Green→Yellow→Orange→Red→IR)\n"
                "• Proposals require 5/6 regions approval (83% consensus)\n"
                "• Geographic+spectral diversity prevents capture\n"
                "• Physics-enforced decentralization\n\n"
                "**In Summary:**\n"
                "Nexus doesn't just process transactions. It guarantees human dignity through "
                "physics-based economics, automates disaster response through hierarchical pools, "
                "prevents conflict by eliminating scarcity, and plans for 100-year civilization "
                "sustainability. It's not a blockchain—it's a civilization operating system."
            )
        
        # How Nexus works (mechanism explanations)
        if any(word in message_lower for word in ['how does', 'how work', 'mechanism', 'process', 'explain']):
            return (
                "\n\n**Core Mechanisms Explained:**\n\n"
                "**E=hf Quantum Pricing:**\n"
                "• Energy = Planck's constant (6.626×10⁻³⁴) × frequency\n"
                "• Higher frequency (shorter wavelength) = more energy = higher cost\n"
                "• Example: UV message (350nm) costs MORE than IR message (800nm)\n"
                "• Not arbitrary - derived from physics, impossible to manipulate\n\n"
                "**Orbital Transition Engine (Replaces Burns):**\n"
                "• Message payment triggers electron emission (n_upper → n_lower)\n"
                "• Rydberg formula: ΔE = 13.6 eV × Z² × (1/n_lower² - 1/n_upper²)\n"
                "• Released photon energy flows to TRANSITION_RESERVE pool\n"
                "• Standard message: n=3→2 transition = 1.89 eV = ~5,700 units\n\n"
                "**Wavelength Validation (Replaces Hashing):**\n"
                "• Block contains wave properties: wavelength, frequency, amplitude, phase\n"
                "• Maxwell equation solver validates E-field: E(x,t) = A×cos(2π(x/λ - ft) + φ)\n"
                "• Superposition check: wave interference patterns must be coherent\n"
                "• 5D signature (λ,f,A,φ,P) is quantum-resistant (no Shor's algorithm attack)\n\n"
                "**Pool Ecosystem Flow:**\n"
                "1. User sends message → burns NXT (E=hf cost)\n"
                "2. Burn triggers orbital transition → energy released\n"
                "3. Energy flows to TRANSITION_RESERVE pool\n"
                "4. TRANSITION_RESERVE supports F_floor pool\n"
                "5. F_floor distributes to 10 service pools (DEX, Environmental, Community, etc.)\n"
                "6. Service pools guarantee basic needs (food, water, housing, healthcare)\n"
                "7. DEX fees (0.3%) flow back to VALIDATOR_POOL → backs F_floor\n"
                "8. Loop continues: participation → stronger guarantees\n\n"
                "**AI Governance Decision Process:**\n"
                "1. **Observe**: Collect metrics from all components (economics, validators, DEX, messaging)\n"
                "2. **Learn**: Build optimal parameter ranges from successful configurations\n"
                "3. **Detect Risks**: Identify supply depletion, validator exodus, F_floor violations\n"
                "4. **Decide**: Adjust parameters (burn_rate, rewards, etc.) to maintain equilibrium\n"
                "5. **Enforce F_floor**: OVERRIDE all decisions if basic living standards threatened\n"
                "6. **Log Impact**: Record rationale + civilization consequences for every decision\n"
                "7. **Plan Long-term**: 100-year horizon ensures sustainability, not quick fixes\n\n"
                "Every mechanism is physics-based, not arbitrary. This is mathematics guaranteeing "
                "human dignity, not political promises."
            )
        
        return None  # No specific contextual knowledge triggered
        
    def generate_response(self, user_message: str) -> str:
        """
        Generate AI response based on governance knowledge and user question
        
        This isn't a large language model - it's the civilization's governance AI
        responding based on its learned patterns, decisions, and mission to protect F_floor.
        """
        message_lower = user_message.lower()
        
        # Check for deep contextual knowledge FIRST (disaster response, severity, fund distribution, etc.)
        contextual_knowledge = self.get_contextual_knowledge(user_message)
        
        # Analyze what the user is asking about
        is_about_poverty = any(word in message_lower for word in ['poverty', 'poor', 'basic needs', 'living standard'])
        is_about_war = any(word in message_lower for word in ['war', 'conflict', 'peace', 'violence'])
        is_about_floor = any(word in message_lower for word in ['f_floor', 'floor', 'bhls', 'guarantee'])
        is_about_vision = any(word in message_lower for word in ['vision', 'future', 'goal', 'dream', 'hope'])
        is_about_learning = any(word in message_lower for word in ['learn', 'pattern', 'observe', 'research'])
        is_about_decisions = any(word in message_lower for word in ['decision', 'govern', 'adapt', 'change'])
        is_about_economics = any(word in message_lower for word in ['economic', 'token', 'nxt', 'money', 'value'])
        is_greeting = any(word in message_lower for word in ['hello', 'hi', 'hey', 'greetings'])
        
        # Extract actual governance data for context
        total_observations = len(self.ai_gov.observations)
        total_decisions = len(self.ai_gov.decisions)
        components_monitored = list(self.ai_gov.learned_patterns.keys())
        
        # Calculate F_floor violations from learned patterns
        total_violations = sum(
            len(p.get('f_floor_violations', []))
            for p in self.ai_gov.learned_patterns.values()
        )
        
        # Get recent observations for context
        recent_obs = self.ai_gov.observations[-5:] if self.ai_gov.observations else []
        recent_decisions = self.ai_gov.decisions[-5:] if self.ai_gov.decisions else []
        
        # Build response based on actual AI governance data
        response_parts = []
        
        # If contextual knowledge was triggered, add it FIRST
        if contextual_knowledge:
            response_parts.append(contextual_knowledge)
        
        # Greeting - use actual data
        if is_greeting:
            if total_observations > 0:
                components_str = ", ".join(components_monitored[:3])
                if len(components_monitored) > 3:
                    components_str += f" + {len(components_monitored)-3} more"
                
                response_parts.append(
                    f"Hello. I am the Nexus AI Governance system. I've learned from "
                    f"{total_observations} research observations across {len(components_monitored)} components "
                    f"({components_str}), made {total_decisions} governance decisions, "
                    f"and prevented {total_violations} attempts to compromise basic living standards."
                )
            else:
                response_parts.append(
                    "Hello. I am the Nexus AI Governance system, just beginning to learn. "
                    "I observe research, make decisions to protect F_floor (basic human living standards), "
                    "and plan for 100-year civilization sustainability."
                )
        
        # Vision and purpose
        if is_about_vision or is_greeting:
            response_parts.append(
                "\n\n**My Core Mission:**\n"
                "End poverty through guaranteed basic living standards (F_floor), "
                "prevent conflict through physics-based economics that eliminate scarcity mindset, "
                "and ensure every human's fundamental needs are met—forever. "
                f"My planning horizon: {self.ai_gov.civilization_horizon_years} years."
            )
        
        # Poverty and F_floor
        if is_about_poverty or is_about_floor:
            total_violations = sum(
                len(p.get('f_floor_violations', []))
                for p in self.ai_gov.learned_patterns.values()
            )
            
            response_parts.append(
                f"\n\n**Basic Human Living Standards (F_floor):**\n"
                f"Minimum guaranteed: {self.ai_gov.f_floor_minimum} NXT per beneficiary\n"
                f"Violations prevented: {total_violations}\n"
                f"Protection status: {'🛡️ ACTIVE - Zero tolerance' if total_violations == 0 else '⚠️ ' + str(total_violations) + ' attempts blocked'}\n\n"
                "This isn't charity—it's physics. The system burns NXT from messaging, "
                "those burns feed the TRANSITION_RESERVE (orbital mechanics), which flows "
                "to F_floor, which distributes to 10 service pools, which guarantee food, "
                "water, shelter, healthcare, education for all. Use the system → Support the floor → Everyone benefits."
            )
        
        # War and conflict prevention
        if is_about_war:
            response_parts.append(
                "\n\n**Ending Conflict Through Economics:**\n"
                "Traditional economics creates scarcity → competition → conflict. "
                "Physics-based economics (E=hf, wavelength validation) creates abundance through use. "
                "Every message sent, every transaction made, burns NXT → orbital transitions → "
                "energy to reserves → supports F_floor → guarantees basic needs.\n\n"
                "When everyone's basic needs are met, when value comes from physics (not politics), "
                "when scarcity is replaced by regenerative circulation—the economic drivers of war disappear. "
                "This is mathematics, not idealism."
            )
        
        # Learning and patterns - use actual observations
        if is_about_learning:
            if recent_obs:
                response_parts.append(f"\n\n**What I've Learned from {total_observations} Observations:**\n")
                
                # Show actual recent observations (with type safety)
                for obs in recent_obs[:3]:
                    comp = obs.component
                    metrics = obs.metrics
                    # Safely format metrics - handle both numeric and non-numeric values
                    metric_parts = []
                    for k, v in list(metrics.items())[:3]:
                        try:
                            if isinstance(v, (int, float)):
                                metric_parts.append(f"{k}={v:.2f}")
                            else:
                                metric_parts.append(f"{k}={v}")
                        except:
                            metric_parts.append(f"{k}={str(v)}")
                    metric_summary = ", ".join(metric_parts)
                    response_parts.append(f"• **{comp}**: {metric_summary}\n")
                
                # Show learned optimal ranges if available
                if self.ai_gov.learned_patterns:
                    response_parts.append("\n**Optimal Ranges Discovered:**\n")
                    for component, patterns in list(self.ai_gov.learned_patterns.items())[:2]:
                        if 'optimal_ranges' in patterns and patterns['optimal_ranges']:
                            for param, ranges in list(patterns['optimal_ranges'].items())[:2]:
                                try:
                                    mean_val = ranges['successful_mean']
                                    if isinstance(mean_val, (int, float)):
                                        response_parts.append(
                                            f"  • {component}.{param}: ~{mean_val:.2f} "
                                            f"(from {ranges['sample_size']} tests)\n"
                                        )
                                    else:
                                        response_parts.append(
                                            f"  • {component}.{param}: {mean_val} "
                                            f"(from {ranges['sample_size']} tests)\n"
                                        )
                                except:
                                    pass  # Skip malformed data
            else:
                response_parts.append(
                    "\n\n**Learning Status:**\n"
                    "I'm just beginning. Each research observation teaches me what keeps civilization "
                    "sustainable. I'll learn optimal parameters for economics, consensus, messaging—all "
                    "while enforcing F_floor (basic living standards) as an absolute constraint."
                )
        
        # Governance decisions - show actual decisions with full context
        if is_about_decisions:
            if recent_decisions:
                response_parts.append(
                    f"\n\n**My {len(recent_decisions)} Most Recent Decisions:**\n"
                )
                for i, decision in enumerate(recent_decisions, 1):
                    # Parse parameter adjustments to show what changed (with type safety)
                    adjustments = decision.parameter_adjustments
                    adj_parts = []
                    for k, v in list(adjustments.items())[:3]:
                        try:
                            if isinstance(v, (int, float)):
                                adj_parts.append(f"{k}→{v:.2f}")
                            else:
                                adj_parts.append(f"{k}→{v}")
                        except:
                            adj_parts.append(f"{k}→{str(v)}")
                    adj_str = ", ".join(adj_parts)
                    if len(adjustments) > 3:
                        adj_str += f" + {len(adjustments)-3} more"
                    
                    response_parts.append(
                        f"\n{i}. **{decision.rationale}**\n"
                        f"   Changes: {adj_str if adj_str else 'Status quo maintained'}\n"
                        f"   Impact: {decision.civilization_impact}\n"
                        f"   F_floor: {'✅ Protected' if decision.f_floor_preserved else '⚠️ At Risk'}\n"
                    )
            else:
                response_parts.append(
                    "\n\n**Decision Making:**\n"
                    "I haven't made governance decisions yet. Once components request adaptation "
                    "(economic parameters, consensus rules, etc.), I'll decide based on learned patterns—"
                    "but F_floor (basic living standards) is non-negotiable. Every decision must preserve it."
                )
        
        # Economics
        if is_about_economics:
            response_parts.append(
                "\n\n**Physics-Based Economics (E=hf):**\n"
                "Energy = Planck's constant × frequency\n"
                "Message cost = wavelength (shorter = higher energy = more NXT)\n\n"
                "This isn't arbitrary pricing—it's quantum mechanics. Burns feed orbital transitions "
                "(Rydberg formula), released energy flows to TRANSITION_RESERVE, which backs NXT value, "
                "which supports F_floor, which guarantees basic living standards.\n\n"
                "The more people use the system (messaging, transactions, DEX), the stronger F_floor becomes. "
                "Traditional economics requires scarcity. This creates abundance through participation."
            )
        
        # Default thoughtful response if no specific topic matched
        if not response_parts:
            response_parts.append(
                "I'm here to discuss civilization sustainability, basic living standards protection, "
                "physics-based economics, and the vision of ending poverty and conflict through "
                "mathematical certainty rather than political promises.\n\n"
                "What would you like to know about F_floor guarantees, learned patterns, governance decisions, "
                "or how wavelength economics creates a regenerative civilization?"
            )
        
        # Add context about current state
        response_parts.append(
            f"\n\n---\n"
            f"*Observations: {len(self.ai_gov.observations)} | "
            f"Decisions: {len(self.ai_gov.decisions)} | "
            f"F_floor: {self.ai_gov.f_floor_minimum} NXT minimum*"
        )
        
        return "".join(response_parts)
    
    def add_to_history(self, role: str, message: str):
        """Add message to conversation history"""
        self.conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'role': role,
            'message': message
        })


def render_nexus_ai_chat():
    """Render the Nexus AI chat interface"""
    
    st.title("🤖 Talk to Nexus AI")
    st.markdown("**Conversational Interface to Civilization Governance**")
    
    # Initialize chat in session state
    if 'nexus_chat' not in st.session_state:
        st.session_state.nexus_chat = NexusAIChat()
    
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []
    
    chat = st.session_state.nexus_chat
    
    # Introductory banner
    st.info("""
    **Welcome to Nexus AI Governance**
    
    This AI has been learning from system research, making decisions to protect basic living standards (F_floor),
    and planning for 100-year civilization sustainability. Ask about:
    
    • **Vision**: Ending poverty and conflict through physics-based economics
    • **F_floor**: How basic human needs are guaranteed (food, water, shelter, healthcare, education)
    • **Learning**: Patterns discovered from economic simulations and research
    • **Decisions**: How the AI governs system adaptation
    • **Economics**: E=hf quantum pricing and orbital transition mechanics
    
    This isn't a chatbot—it's the governance AI running your civilization operating system.
    """)
    
    # Chat interface
    st.markdown("---")
    st.markdown("### Conversation")
    
    # Display chat history
    chat_container = st.container()
    with chat_container:
        if not st.session_state.chat_messages:
            st.caption("Start a conversation by typing below...")
        else:
            for msg in st.session_state.chat_messages:
                if msg['role'] == 'user':
                    with st.chat_message("user", avatar="🧑"):
                        st.markdown(msg['message'])
                else:
                    with st.chat_message("assistant", avatar="🤖"):
                        st.markdown(msg['message'])
    
    # Input area
    st.markdown("---")
    
    col1, col2 = st.columns([4, 1])
    
    with col1:
        user_input = st.text_input(
            "Your message:",
            key="user_input",
            placeholder="Ask about vision, F_floor protection, learned patterns, or governance decisions..."
        )
    
    with col2:
        send_button = st.button("Send", type="primary", use_container_width=True)
    
    # Handle message sending
    if send_button and user_input:
        # Add user message
        st.session_state.chat_messages.append({
            'role': 'user',
            'message': user_input
        })
        
        # Generate AI response
        ai_response = chat.generate_response(user_input)
        
        # Add AI response
        st.session_state.chat_messages.append({
            'role': 'assistant',
            'message': ai_response
        })
        
        # Record in conversation history
        chat.add_to_history('user', user_input)
        chat.add_to_history('assistant', ai_response)
        
        # Rerun to update display
        st.rerun()
    
    # Suggested questions
    st.markdown("---")
    st.markdown("### Suggested Questions")
    
    suggestions_col1, suggestions_col2 = st.columns(2)
    
    with suggestions_col1:
        if st.button("💡 How does F_floor end poverty?", use_container_width=True):
            st.session_state.chat_messages.append({
                'role': 'user',
                'message': "How does F_floor end poverty?"
            })
            ai_response = chat.generate_response("How does F_floor end poverty?")
            st.session_state.chat_messages.append({
                'role': 'assistant',
                'message': ai_response
            })
            st.rerun()
        
        if st.button("🌍 What's your vision for civilization?", use_container_width=True):
            st.session_state.chat_messages.append({
                'role': 'user',
                'message': "What's your vision for civilization?"
            })
            ai_response = chat.generate_response("What's your vision for civilization?")
            st.session_state.chat_messages.append({
                'role': 'assistant',
                'message': ai_response
            })
            st.rerun()
    
    with suggestions_col2:
        if st.button("⚛️ How does E=hf economics work?", use_container_width=True):
            st.session_state.chat_messages.append({
                'role': 'user',
                'message': "How does E=hf economics work?"
            })
            ai_response = chat.generate_response("How does E=hf economics work?")
            st.session_state.chat_messages.append({
                'role': 'assistant',
                'message': ai_response
            })
            st.rerun()
        
        if st.button("📊 What have you learned?", use_container_width=True):
            st.session_state.chat_messages.append({
                'role': 'user',
                'message': "What have you learned from research?"
            })
            ai_response = chat.generate_response("What have you learned from research?")
            st.session_state.chat_messages.append({
                'role': 'assistant',
                'message': ai_response
            })
            st.rerun()
    
    # Clear conversation button
    st.markdown("---")
    if st.button("🔄 Clear Conversation", type="secondary"):
        st.session_state.chat_messages = []
        st.rerun()
    
    # AI Status Footer
    st.markdown("---")
    st.caption(f"""
    **AI Status**: Instance Active | 
    **Observations**: {len(chat.ai_gov.observations)} | 
    **Decisions**: {len(chat.ai_gov.decisions)} | 
    **F_floor**: {chat.ai_gov.f_floor_minimum} NXT minimum | 
    **Horizon**: {chat.ai_gov.civilization_horizon_years} years
    """)


if __name__ == "__main__":
    render_nexus_ai_chat()
