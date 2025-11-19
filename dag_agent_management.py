"""
DAG Agent Management Layer
AI-powered orchestration of DAG agents throughout the NexusOS ecosystem

Agents include:
- DAG messaging nodes
- Network validators
- Message routers
- Block validators
- Consensus participants
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any
from enum import Enum
from datetime import datetime
import time


class AgentType(Enum):
    """Types of agents in the ecosystem"""
    DAG_MESSAGE_NODE = "dag_message_node"
    VALIDATOR = "validator"
    MESSAGE_ROUTER = "message_router"
    BLOCK_VALIDATOR = "block_validator"
    CONSENSUS_PARTICIPANT = "consensus_participant"


class AgentStatus(Enum):
    """Agent operational status"""
    ACTIVE = "active"
    IDLE = "idle"
    DEGRADED = "degraded"
    OFFLINE = "offline"
    SUSPENDED = "suspended"


@dataclass
class AgentMetrics:
    """Performance metrics for an agent"""
    messages_processed: int = 0
    messages_routed: int = 0
    blocks_validated: int = 0
    consensus_votes: int = 0
    uptime_seconds: float = 0.0
    last_activity: float = field(default_factory=time.time)
    error_count: int = 0
    latency_ms_avg: float = 0.0
    throughput_tps: float = 0.0  # Transactions per second
    
    def calculate_performance_score(self) -> float:
        """Calculate overall performance score (0-100)"""
        # Simple scoring based on activity and reliability
        activity_score = min(100, (self.messages_processed + self.blocks_validated) / 10)
        reliability_score = max(0, 100 - self.error_count * 10)
        latency_score = max(0, 100 - self.latency_ms_avg / 10)
        
        return (activity_score + reliability_score + latency_score) / 3


@dataclass
class DAGAgent:
    """Represents an agent in the DAG ecosystem"""
    agent_id: str
    agent_type: AgentType
    status: AgentStatus
    metrics: AgentMetrics = field(default_factory=AgentMetrics)
    parameters: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    last_health_check: float = field(default_factory=time.time)
    
    def is_healthy(self) -> bool:
        """Check if agent is healthy"""
        if self.status == AgentStatus.OFFLINE:
            return False
        
        # Check if agent has been inactive for too long (5 minutes)
        time_since_activity = time.time() - self.metrics.last_activity
        if time_since_activity > 300:  # 5 minutes
            return False
        
        # Check error rate
        if self.metrics.error_count > 10:
            return False
        
        return True
    
    def update_metrics(self, **kwargs):
        """Update agent metrics"""
        for key, value in kwargs.items():
            if hasattr(self.metrics, key):
                setattr(self.metrics, key, value)
        
        self.metrics.last_activity = time.time()


class DAGAgentManager:
    """
    Manages DAG agents throughout the ecosystem
    Integrates with AI governance for adaptive orchestration
    """
    
    def __init__(self):
        self.agents: Dict[str, DAGAgent] = {}
        self.agent_groups: Dict[AgentType, Set[str]] = {
            agent_type: set() for agent_type in AgentType
        }
        self.orchestration_history: List[Dict] = []
        
    def register_agent(self, agent_id: str, agent_type: AgentType, 
                      parameters: Optional[Dict] = None) -> DAGAgent:
        """
        Register a new agent in the ecosystem
        
        Args:
            agent_id: Unique identifier for the agent
            agent_type: Type of agent
            parameters: Initial parameters for the agent
        
        Returns:
            Created DAGAgent
        """
        if agent_id in self.agents:
            return self.agents[agent_id]
        
        agent = DAGAgent(
            agent_id=agent_id,
            agent_type=agent_type,
            status=AgentStatus.ACTIVE,
            parameters=parameters or {}
        )
        
        self.agents[agent_id] = agent
        self.agent_groups[agent_type].add(agent_id)
        
        return agent
    
    def unregister_agent(self, agent_id: str) -> bool:
        """Remove an agent from the ecosystem"""
        if agent_id not in self.agents:
            return False
        
        agent = self.agents[agent_id]
        self.agent_groups[agent.agent_type].discard(agent_id)
        del self.agents[agent_id]
        
        return True
    
    def get_agent(self, agent_id: str) -> Optional[DAGAgent]:
        """Get agent by ID"""
        return self.agents.get(agent_id)
    
    def get_agents_by_type(self, agent_type: AgentType) -> List[DAGAgent]:
        """Get all agents of a specific type"""
        agent_ids = self.agent_groups.get(agent_type, set())
        return [self.agents[aid] for aid in agent_ids if aid in self.agents]
    
    def get_active_agents(self) -> List[DAGAgent]:
        """Get all active agents"""
        return [agent for agent in self.agents.values() 
                if agent.status == AgentStatus.ACTIVE]
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on all agents
        
        Returns:
            Health report with statistics
        """
        total_agents = len(self.agents)
        healthy_agents = 0
        degraded_agents = 0
        offline_agents = 0
        
        for agent in self.agents.values():
            if agent.is_healthy():
                if agent.status == AgentStatus.ACTIVE:
                    healthy_agents += 1
                else:
                    degraded_agents += 1
            else:
                offline_agents += 1
                # Auto-update status
                agent.status = AgentStatus.OFFLINE
        
        return {
            "total_agents": total_agents,
            "healthy": healthy_agents,
            "degraded": degraded_agents,
            "offline": offline_agents,
            "health_percentage": (healthy_agents / total_agents * 100) if total_agents > 0 else 0
        }
    
    def ai_orchestrate(self, governance_recommendations: Dict) -> List[str]:
        """
        AI-powered orchestration based on governance recommendations
        
        Args:
            governance_recommendations: Recommendations from AI governance system
        
        Returns:
            List of actions taken
        """
        actions_taken = []
        
        # Scale agents based on load
        if governance_recommendations.get("scale_validators"):
            target_count = governance_recommendations["target_validator_count"]
            current_count = len(self.get_agents_by_type(AgentType.VALIDATOR))
            
            if target_count > current_count:
                # Add validators
                for i in range(target_count - current_count):
                    agent_id = f"validator_{len(self.agents)}_{int(time.time())}"
                    self.register_agent(agent_id, AgentType.VALIDATOR)
                    actions_taken.append(f"Added validator {agent_id}")
        
        # Adjust routing parameters
        if governance_recommendations.get("optimize_routing"):
            routers = self.get_agents_by_type(AgentType.MESSAGE_ROUTER)
            for router in routers:
                router.parameters["routing_strategy"] = governance_recommendations.get("routing_strategy", "round_robin")
                actions_taken.append(f"Updated routing for {router.agent_id}")
        
        # Suspend underperforming agents
        if governance_recommendations.get("suspend_underperformers"):
            for agent in self.agents.values():
                if agent.metrics.calculate_performance_score() < 20:
                    agent.status = AgentStatus.SUSPENDED
                    actions_taken.append(f"Suspended underperforming agent {agent.agent_id}")
        
        # Reactivate suspended agents if conditions improve
        if governance_recommendations.get("reactivate_agents"):
            for agent in self.agents.values():
                if agent.status == AgentStatus.SUSPENDED and agent.is_healthy():
                    agent.status = AgentStatus.ACTIVE
                    actions_taken.append(f"Reactivated agent {agent.agent_id}")
        
        # Record orchestration event
        self.orchestration_history.append({
            "timestamp": datetime.now().isoformat(),
            "recommendations": governance_recommendations,
            "actions": actions_taken
        })
        
        return actions_taken
    
    def get_ecosystem_metrics(self) -> Dict:
        """Get aggregate metrics across all agents"""
        total_messages = sum(agent.metrics.messages_processed for agent in self.agents.values())
        total_blocks = sum(agent.metrics.blocks_validated for agent in self.agents.values())
        total_errors = sum(agent.metrics.error_count for agent in self.agents.values())
        
        avg_latency = 0
        active_agents = self.get_active_agents()
        if active_agents:
            avg_latency = sum(agent.metrics.latency_ms_avg for agent in active_agents) / len(active_agents)
        
        return {
            "total_agents": len(self.agents),
            "active_agents": len(active_agents),
            "total_messages_processed": total_messages,
            "total_blocks_validated": total_blocks,
            "total_errors": total_errors,
            "average_latency_ms": avg_latency,
            "agents_by_type": {
                agent_type.value: len(self.get_agents_by_type(agent_type))
                for agent_type in AgentType
            }
        }
    
    def detect_anomalies(self) -> List[str]:
        """Detect anomalies in agent behavior"""
        anomalies = []
        
        # Check for agents with high error rates
        for agent in self.agents.values():
            if agent.metrics.error_count > 5:
                anomalies.append(f"High error rate on {agent.agent_id}: {agent.metrics.error_count} errors")
        
        # Check for sudden performance drops
        ecosystem_metrics = self.get_ecosystem_metrics()
        if ecosystem_metrics["average_latency_ms"] > 1000:
            anomalies.append(f"High average latency: {ecosystem_metrics['average_latency_ms']:.1f}ms")
        
        # Check for agent concentration (single point of failure)
        for agent_type in AgentType:
            count = len(self.get_agents_by_type(agent_type))
            if count == 1 and agent_type in [AgentType.VALIDATOR, AgentType.MESSAGE_ROUTER]:
                anomalies.append(f"Single point of failure: only 1 {agent_type.value}")
        
        return anomalies


# Global agent manager instance
_agent_manager = None

def get_agent_manager() -> DAGAgentManager:
    """Get singleton DAG agent manager instance"""
    global _agent_manager
    if _agent_manager is None:
        _agent_manager = DAGAgentManager()
    return _agent_manager
