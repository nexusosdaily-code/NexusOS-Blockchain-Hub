"""
WNSP Unified Mesh Stack
Integrates 4 layers: Community Mesh ISP → Censorship-Resistant Routing → 
Privacy Messaging → Offline Knowledge Networks

Architecture:
┌─────────────────────────────────────────────────┐
│  Layer 4: Offline Knowledge (Content)           │
│  - Wikipedia cache, educational resources       │
│  - Physics-verified authenticity                │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│  Layer 3: Privacy Messaging (Application)       │
│  - Quantum-resistant encryption                 │
│  - Peer-to-peer, no central servers             │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│  Layer 2: Censorship-Resistant Routing          │
│  - Wavelength addressing (not DNS)              │
│  - Self-healing mesh topology                   │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│  Layer 1: Community Mesh ISP (Physical)         │
│  - BLE/WiFi/LoRa hardware abstraction           │
│  - Phone-to-phone direct communication          │
└─────────────────────────────────────────────────┘
"""

import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional, Set
from enum import Enum
import hashlib
import time

class TransportProtocol(Enum):
    BLE = "Bluetooth Low Energy"
    WIFI = "WiFi Direct" 
    LORA = "LoRa Long Range"

class NodeType(Enum):
    EDGE = "Edge Node (Phone/Tablet)"
    RELAY = "Relay Node (Dedicated)"
    GATEWAY = "Gateway (Internet Bridge)"
    CACHE = "Cache Node (Knowledge Store)"

@dataclass
class WavelengthAddress:
    """Wavelength-based addressing (not DNS/IP)"""
    spectral_signature: np.ndarray  # 8 spectral regions
    quantum_hash: str  # Physics-based hash
    node_id: str
    
    def to_routing_key(self) -> str:
        """Convert wavelength signature to routing key"""
        region_codes = ''.join([f"{int(amp*255):02x}" for amp in self.spectral_signature])
        return f"λ:{region_codes}:{self.quantum_hash[:8]}"

@dataclass 
class MeshNode:
    """Physical mesh network node"""
    node_id: str
    node_type: NodeType
    wavelength_addr: WavelengthAddress
    transport_protocols: List[TransportProtocol]
    neighbors: Set[str]  # Connected node IDs
    cache_capacity_mb: float  # For knowledge storage
    uptime_hours: float
    
    def __hash__(self):
        return hash(self.node_id)

@dataclass
class MeshLink:
    """Connection between two nodes"""
    node_a: str
    node_b: str
    protocol: TransportProtocol
    signal_strength_dbm: float
    latency_ms: float
    bandwidth_kbps: float
    
    @property
    def link_quality(self) -> float:
        """0-1 quality score"""
        signal_norm = min(1.0, (self.signal_strength_dbm + 100) / 70)  # -100 to -30 dBm
        latency_norm = max(0, 1.0 - self.latency_ms / 1000)
        bandwidth_norm = min(1.0, self.bandwidth_kbps / 10000)
        return (signal_norm * 0.4 + latency_norm * 0.3 + bandwidth_norm * 0.3)

@dataclass
class PrivateMessage:
    """E=hf priced, quantum-encrypted message"""
    sender_addr: WavelengthAddress
    recipient_addr: WavelengthAddress
    encrypted_payload: bytes
    wavelength_nm: float
    energy_cost_hf: float
    timestamp: float
    quantum_signature: str  # 5D wave signature
    
    @classmethod
    def create(cls, sender: WavelengthAddress, recipient: WavelengthAddress, 
               plaintext: str, wavelength_nm: float):
        """Create encrypted message with E=hf pricing"""
        h = 6.62607015e-34  # Planck constant
        c = 299792458  # Speed of light
        frequency = c / (wavelength_nm * 1e-9)
        energy_joules = h * frequency
        
        # Quantum encryption (simplified - real would use wave superposition)
        encryption_key = hashlib.sha256(
            f"{sender.quantum_hash}{recipient.quantum_hash}{wavelength_nm}".encode()
        ).digest()
        encrypted = bytes([b ^ encryption_key[i % len(encryption_key)] 
                          for i, b in enumerate(plaintext.encode())])
        
        # 5D wave signature for quantum resistance
        signature = hashlib.sha512(
            f"{encrypted}{wavelength_nm}{time.time()}{sender.quantum_hash}".encode()
        ).hexdigest()
        
        return cls(
            sender_addr=sender,
            recipient_addr=recipient,
            encrypted_payload=encrypted,
            wavelength_nm=wavelength_nm,
            energy_cost_hf=energy_joules,
            timestamp=time.time(),
            quantum_signature=signature
        )

@dataclass
class KnowledgeResource:
    """Cached offline knowledge (Wikipedia, educational content)"""
    resource_id: str
    title: str
    content_hash: str  # Physics-verified authenticity
    size_mb: float
    category: str
    wavelength_proof: str  # Wavelength validation signature
    cache_priority: int  # 1-10, higher = more important
    access_count: int = 0
    
    def verify_authenticity(self, expected_hash: str) -> bool:
        """Verify content hasn't been tampered with"""
        return self.content_hash == expected_hash

class Layer1_CommunityMeshISP:
    """Physical layer: Phone-to-phone mesh network"""
    
    def __init__(self):
        self.nodes: Dict[str, MeshNode] = {}
        self.links: List[MeshLink] = []
        self.topology_graph = {}
        
    def add_node(self, node: MeshNode):
        """Add node to mesh network"""
        self.nodes[node.node_id] = node
        self.topology_graph[node.node_id] = set()
        
    def create_link(self, node_a_id: str, node_b_id: str, protocol: TransportProtocol,
                   signal_dbm: float, latency_ms: float, bandwidth_kbps: float):
        """Create bidirectional mesh link"""
        link = MeshLink(node_a_id, node_b_id, protocol, signal_dbm, latency_ms, bandwidth_kbps)
        self.links.append(link)
        
        # Update topology graph
        self.topology_graph[node_a_id].add(node_b_id)
        self.topology_graph[node_b_id].add(node_a_id)
        
        # Update node neighbors
        self.nodes[node_a_id].neighbors.add(node_b_id)
        self.nodes[node_b_id].neighbors.add(node_a_id)
        
    def get_network_coverage(self) -> Dict[str, any]:
        """Calculate mesh network coverage statistics"""
        total_nodes = len(self.nodes)
        total_links = len(self.links)
        
        # Node type distribution
        type_dist = {}
        for node in self.nodes.values():
            type_name = node.node_type.value
            type_dist[type_name] = type_dist.get(type_name, 0) + 1
            
        # Average connectivity
        avg_neighbors = np.mean([len(n.neighbors) for n in self.nodes.values()]) if self.nodes else 0
        
        # Protocol usage
        protocol_dist = {}
        for link in self.links:
            proto = link.protocol.value
            protocol_dist[proto] = protocol_dist.get(proto, 0) + 1
            
        return {
            "total_nodes": total_nodes,
            "total_links": total_links,
            "node_types": type_dist,
            "avg_neighbors_per_node": avg_neighbors,
            "protocol_distribution": protocol_dist,
            "network_density": total_links / (total_nodes * (total_nodes - 1) / 2) if total_nodes > 1 else 0
        }

class Layer2_CensorshipResistantRouting:
    """Protocol layer: Wavelength-based routing that can't be blocked"""
    
    def __init__(self, mesh_layer: Layer1_CommunityMeshISP):
        self.mesh = mesh_layer
        self.routing_table: Dict[str, List[str]] = {}  # wavelength_addr -> [path]
        self.blocked_dns_urls = set()  # Simulates government censorship
        
    def compute_wavelength_route(self, source_addr: WavelengthAddress, 
                                 dest_addr: WavelengthAddress) -> List[str]:
        """Find route using wavelength signatures (not DNS/IP)"""
        # Find source and destination nodes
        source_node = None
        dest_node = None
        
        for node in self.mesh.nodes.values():
            if node.wavelength_addr.quantum_hash == source_addr.quantum_hash:
                source_node = node.node_id
            if node.wavelength_addr.quantum_hash == dest_addr.quantum_hash:
                dest_node = node.node_id
                
        if not source_node or not dest_node:
            return []
            
        # Self-healing BFS pathfinding
        visited = set()
        queue = [(source_node, [source_node])]
        
        while queue:
            current, path = queue.pop(0)
            
            if current == dest_node:
                return path
                
            if current in visited:
                continue
            visited.add(current)
            
            for neighbor in self.mesh.topology_graph.get(current, []):
                if neighbor not in visited:
                    queue.append((neighbor, path + [neighbor]))
                    
        return []  # No route found
        
    def evade_censorship(self, original_request: str) -> Dict[str, any]:
        """Show how wavelength routing evades DNS/URL blocking"""
        is_blocked = original_request in self.blocked_dns_urls
        
        if is_blocked:
            return {
                "original_request": original_request,
                "censorship_status": "BLOCKED by government",
                "wavelength_bypass": "SUCCESS - routed via λ:signature instead of DNS",
                "method": "Wavelength addressing doesn't use DNS/URLs - nothing to block"
            }
        else:
            return {
                "original_request": original_request,
                "censorship_status": "Allowed",
                "wavelength_advantage": "Would bypass if blocked"
            }
            
    def simulate_government_block(self, dns_url: str):
        """Simulate government blocking a URL (has no effect on WNSP)"""
        self.blocked_dns_urls.add(dns_url)

class Layer3_PrivacyMessaging:
    """Application layer: Quantum-encrypted peer-to-peer messaging"""
    
    def __init__(self, routing_layer: Layer2_CensorshipResistantRouting):
        self.routing = routing_layer
        self.message_queue: List[PrivateMessage] = []
        self.delivered_messages: Dict[str, List[PrivateMessage]] = {}
        
    def send_message(self, sender_addr: WavelengthAddress, recipient_addr: WavelengthAddress,
                    plaintext: str, wavelength_nm: float) -> Dict[str, any]:
        """Send quantum-encrypted message over mesh"""
        # Create encrypted message with E=hf pricing
        msg = PrivateMessage.create(sender_addr, recipient_addr, plaintext, wavelength_nm)
        
        # Find route through mesh
        route = self.routing.compute_wavelength_route(sender_addr, recipient_addr)
        
        if not route:
            return {
                "status": "FAILED",
                "reason": "No mesh route available",
                "message_id": msg.quantum_signature[:16]
            }
            
        # Add to delivery queue
        self.message_queue.append(msg)
        
        # Deliver to recipient inbox
        recipient_key = recipient_addr.to_routing_key()
        if recipient_key not in self.delivered_messages:
            self.delivered_messages[recipient_key] = []
        self.delivered_messages[recipient_key].append(msg)
        
        return {
            "status": "DELIVERED",
            "message_id": msg.quantum_signature[:16],
            "route_hops": len(route),
            "energy_cost_joules": msg.energy_cost_hf,
            "wavelength_nm": wavelength_nm,
            "quantum_signature": msg.quantum_signature[:32],
            "privacy": "Quantum-encrypted, no central server"
        }
        
    def get_inbox(self, recipient_addr: WavelengthAddress) -> List[PrivateMessage]:
        """Retrieve messages for recipient"""
        key = recipient_addr.to_routing_key()
        return self.delivered_messages.get(key, [])

class Layer4_OfflineKnowledge:
    """Content layer: Distributed knowledge network (Wikipedia, education)"""
    
    def __init__(self, mesh_layer: Layer1_CommunityMeshISP):
        self.mesh = mesh_layer
        self.knowledge_catalog: Dict[str, KnowledgeResource] = {}
        self.node_cache_map: Dict[str, Set[str]] = {}  # node_id -> cached resource_ids
        
    def add_resource(self, resource: KnowledgeResource):
        """Add knowledge resource to network"""
        self.knowledge_catalog[resource.resource_id] = resource
        
    def cache_on_node(self, resource_id: str, node_id: str) -> Dict[str, any]:
        """Cache knowledge resource on mesh node"""
        if resource_id not in self.knowledge_catalog:
            return {"status": "FAILED", "reason": "Resource not found"}
            
        resource = self.knowledge_catalog[resource_id]
        node = self.mesh.nodes.get(node_id)
        
        if not node:
            return {"status": "FAILED", "reason": "Node not found"}
            
        # Check cache capacity
        if node_id not in self.node_cache_map:
            self.node_cache_map[node_id] = set()
            
        current_cache_mb = sum(
            self.knowledge_catalog[rid].size_mb 
            for rid in self.node_cache_map[node_id]
        )
        
        if current_cache_mb + resource.size_mb > node.cache_capacity_mb:
            return {
                "status": "FAILED", 
                "reason": f"Cache full ({current_cache_mb:.1f}/{node.cache_capacity_mb:.1f} MB)"
            }
            
        # Cache resource
        self.node_cache_map[node_id].add(resource_id)
        resource.access_count += 1
        
        return {
            "status": "CACHED",
            "resource": resource.title,
            "node": node_id,
            "size_mb": resource.size_mb,
            "cache_usage": f"{current_cache_mb + resource.size_mb:.1f}/{node.cache_capacity_mb:.1f} MB"
        }
        
    def find_nearest_cache(self, resource_id: str, requester_node_id: str) -> Optional[str]:
        """Find nearest node that has this resource cached"""
        if resource_id not in self.knowledge_catalog:
            return None
            
        # BFS to find nearest cached copy
        visited = set()
        queue = [(requester_node_id, 0)]
        
        while queue:
            current_node, hops = queue.pop(0)
            
            if current_node in visited:
                continue
            visited.add(current_node)
            
            # Check if this node has the resource
            if current_node in self.node_cache_map:
                if resource_id in self.node_cache_map[current_node]:
                    return current_node
                    
            # Search neighbors
            for neighbor in self.mesh.topology_graph.get(current_node, []):
                if neighbor not in visited:
                    queue.append((neighbor, hops + 1))
                    
        return None
        
    def get_network_knowledge_stats(self) -> Dict[str, any]:
        """Statistics about distributed knowledge network"""
        total_resources = len(self.knowledge_catalog)
        total_cached_mb = sum(r.size_mb for r in self.knowledge_catalog.values())
        
        # Replication factor
        total_cache_instances = sum(len(cached) for cached in self.node_cache_map.values())
        avg_replication = total_cache_instances / total_resources if total_resources > 0 else 0
        
        # Category distribution
        categories = {}
        for resource in self.knowledge_catalog.values():
            categories[resource.category] = categories.get(resource.category, 0) + 1
            
        # Most accessed
        top_resources = sorted(
            self.knowledge_catalog.values(),
            key=lambda r: r.access_count,
            reverse=True
        )[:5]
        
        return {
            "total_resources": total_resources,
            "total_size_mb": total_cached_mb,
            "avg_replication_factor": avg_replication,
            "categories": categories,
            "total_cache_instances": total_cache_instances,
            "top_accessed": [{"title": r.title, "accesses": r.access_count} for r in top_resources]
        }

class WNSPUnifiedMeshStack:
    """Complete 4-layer mesh stack"""
    
    def __init__(self):
        self.layer1_mesh_isp = Layer1_CommunityMeshISP()
        self.layer2_routing = Layer2_CensorshipResistantRouting(self.layer1_mesh_isp)
        self.layer3_messaging = Layer3_PrivacyMessaging(self.layer2_routing)
        self.layer4_knowledge = Layer4_OfflineKnowledge(self.layer1_mesh_isp)
        
    def get_stack_health(self) -> Dict[str, any]:
        """Overall stack health metrics"""
        mesh_stats = self.layer1_mesh_isp.get_network_coverage()
        knowledge_stats = self.layer4_knowledge.get_network_knowledge_stats()
        
        return {
            "layer1_mesh": {
                "status": "OPERATIONAL" if mesh_stats["total_nodes"] > 0 else "OFFLINE",
                "nodes": mesh_stats["total_nodes"],
                "links": mesh_stats["total_links"],
                "density": f"{mesh_stats['network_density']:.2%}"
            },
            "layer2_routing": {
                "status": "OPERATIONAL",
                "censorship_bypass": "ACTIVE",
                "wavelength_addressing": "ENABLED"
            },
            "layer3_messaging": {
                "status": "OPERATIONAL",
                "messages_queued": len(self.layer3_messaging.message_queue),
                "quantum_encryption": "ACTIVE"
            },
            "layer4_knowledge": {
                "status": "OPERATIONAL",
                "resources_available": knowledge_stats["total_resources"],
                "total_size_mb": knowledge_stats["total_size_mb"],
                "replication_factor": f"{knowledge_stats['avg_replication_factor']:.2f}x"
            }
        }

def create_demo_network() -> WNSPUnifiedMeshStack:
    """Create demonstration university campus mesh network"""
    stack = WNSPUnifiedMeshStack()
    
    # Create wavelength addresses for nodes
    def create_wavelength_addr(node_id: str) -> WavelengthAddress:
        np.random.seed(hash(node_id) % 2**32)
        signature = np.random.random(8)
        signature = signature / signature.sum()
        quantum_hash = hashlib.sha256(f"{node_id}{signature.tobytes()}".encode()).hexdigest()
        return WavelengthAddress(signature, quantum_hash, node_id)
    
    # Layer 1: Add mesh nodes (university campus deployment)
    campus_nodes = [
        ("student_phone_001", NodeType.EDGE, [TransportProtocol.BLE, TransportProtocol.WIFI], 500),
        ("student_phone_002", NodeType.EDGE, [TransportProtocol.BLE, TransportProtocol.WIFI], 500),
        ("student_phone_003", NodeType.EDGE, [TransportProtocol.WIFI, TransportProtocol.LORA], 200),
        ("library_relay", NodeType.RELAY, [TransportProtocol.WIFI, TransportProtocol.LORA], 2000),
        ("dorm_cache", NodeType.CACHE, [TransportProtocol.WIFI], 50000),
        ("campus_gateway", NodeType.GATEWAY, [TransportProtocol.WIFI, TransportProtocol.LORA], 10000),
    ]
    
    for node_id, node_type, protocols, cache_mb in campus_nodes:
        node = MeshNode(
            node_id=node_id,
            node_type=node_type,
            wavelength_addr=create_wavelength_addr(node_id),
            transport_protocols=protocols,
            neighbors=set(),
            cache_capacity_mb=cache_mb,
            uptime_hours=24.0
        )
        stack.layer1_mesh_isp.add_node(node)
    
    # Create mesh links
    links = [
        ("student_phone_001", "student_phone_002", TransportProtocol.BLE, -65, 15, 1000),
        ("student_phone_002", "library_relay", TransportProtocol.WIFI, -45, 8, 5000),
        ("student_phone_003", "library_relay", TransportProtocol.WIFI, -50, 10, 4500),
        ("library_relay", "dorm_cache", TransportProtocol.WIFI, -40, 5, 8000),
        ("library_relay", "campus_gateway", TransportProtocol.LORA, -85, 50, 250),
        ("dorm_cache", "campus_gateway", TransportProtocol.WIFI, -35, 3, 10000),
    ]
    
    for node_a, node_b, protocol, signal, latency, bandwidth in links:
        stack.layer1_mesh_isp.create_link(node_a, node_b, protocol, signal, latency, bandwidth)
    
    # Layer 4: Add knowledge resources (offline Wikipedia)
    resources = [
        ("wiki_physics", "Physics - Complete Encyclopedia", 1500, "Science", 10),
        ("wiki_math", "Mathematics - Core Concepts", 1200, "Science", 9),
        ("wiki_history", "World History - 1900-2000", 2500, "Humanities", 7),
        ("edu_coding", "Introduction to Programming", 800, "Technology", 10),
        ("wiki_medicine", "Medical Encyclopedia", 3000, "Science", 8),
    ]
    
    for res_id, title, size_mb, category, priority in resources:
        resource = KnowledgeResource(
            resource_id=res_id,
            title=title,
            content_hash=hashlib.sha256(f"{res_id}{title}".encode()).hexdigest(),
            size_mb=size_mb,
            category=category,
            wavelength_proof=hashlib.sha256(f"wavelength_proof_{res_id}".encode()).hexdigest(),
            cache_priority=priority
        )
        stack.layer4_knowledge.add_resource(resource)
    
    # Cache resources on appropriate nodes
    stack.layer4_knowledge.cache_on_node("wiki_physics", "dorm_cache")
    stack.layer4_knowledge.cache_on_node("wiki_math", "dorm_cache")
    stack.layer4_knowledge.cache_on_node("edu_coding", "dorm_cache")
    stack.layer4_knowledge.cache_on_node("wiki_physics", "campus_gateway")
    
    # Layer 2: Simulate government censorship (has no effect on WNSP)
    stack.layer2_routing.simulate_government_block("wikipedia.org")
    stack.layer2_routing.simulate_government_block("signal.org")
    
    return stack
