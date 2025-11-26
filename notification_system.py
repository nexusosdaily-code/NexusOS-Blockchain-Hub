"""
NexusOS In-App Notification System
===================================

Real-time notifications for connected nodes without SMS.
Supports: alerts, toasts, transaction updates, network events, governance notifications.

This system works through the web interface - all nodes connected via the website
receive notifications in real-time through session state and polling.
"""

import streamlit as st
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime
import time
import json
import hashlib


class NotificationType(Enum):
    """Types of notifications"""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    TRANSACTION = "transaction"
    GOVERNANCE = "governance"
    NETWORK = "network"
    REWARD = "reward"
    SECURITY = "security"
    MESSAGE = "message"


class NotificationPriority(Enum):
    """Priority levels for notifications"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


@dataclass
class Notification:
    """Individual notification"""
    id: str
    title: str
    message: str
    notification_type: NotificationType
    priority: NotificationPriority = NotificationPriority.NORMAL
    timestamp: float = field(default_factory=time.time)
    read: bool = False
    dismissed: bool = False
    action_url: Optional[str] = None
    action_label: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    expires_at: Optional[float] = None
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'title': self.title,
            'message': self.message,
            'type': self.notification_type.value,
            'priority': self.priority.value,
            'timestamp': self.timestamp,
            'read': self.read,
            'dismissed': self.dismissed,
            'action_url': self.action_url,
            'action_label': self.action_label,
            'data': self.data,
            'time_ago': self._time_ago()
        }
    
    def _time_ago(self) -> str:
        """Human-readable time ago"""
        seconds = time.time() - self.timestamp
        if seconds < 60:
            return "Just now"
        elif seconds < 3600:
            mins = int(seconds / 60)
            return f"{mins}m ago"
        elif seconds < 86400:
            hours = int(seconds / 3600)
            return f"{hours}h ago"
        else:
            days = int(seconds / 86400)
            return f"{days}d ago"
    
    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at


class NotificationCenter:
    """
    Central notification hub for NexusOS
    
    Manages all in-app notifications for connected nodes.
    Uses session state for real-time updates within the web interface.
    """
    
    MAX_NOTIFICATIONS = 100
    
    def __init__(self):
        self._init_session_state()
    
    def _init_session_state(self):
        """Initialize notification storage in session state"""
        if 'notifications' not in st.session_state:
            st.session_state.notifications = []
        if 'notification_settings' not in st.session_state:
            st.session_state.notification_settings = {
                'sound_enabled': True,
                'desktop_enabled': True,
                'transaction_alerts': True,
                'governance_alerts': True,
                'network_alerts': True,
                'reward_alerts': True,
                'security_alerts': True,
                'message_alerts': True
            }
        if 'unread_count' not in st.session_state:
            st.session_state.unread_count = 0
        if 'last_notification_check' not in st.session_state:
            st.session_state.last_notification_check = time.time()
    
    def _generate_id(self, title: str, message: str) -> str:
        """Generate unique notification ID"""
        content = f"{title}{message}{time.time()}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def notify(
        self,
        title: str,
        message: str,
        notification_type: NotificationType = NotificationType.INFO,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        action_url: Optional[str] = None,
        action_label: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        expires_in_seconds: Optional[int] = None
    ) -> Notification:
        """
        Send a notification to the user
        
        Args:
            title: Notification title
            message: Notification message
            notification_type: Type of notification
            priority: Priority level
            action_url: Optional URL/route for action button
            action_label: Optional label for action button
            data: Optional additional data
            expires_in_seconds: Optional expiry time
        
        Returns:
            The created Notification object
        """
        self._init_session_state()
        
        notification = Notification(
            id=self._generate_id(title, message),
            title=title,
            message=message,
            notification_type=notification_type,
            priority=priority,
            action_url=action_url,
            action_label=action_label,
            data=data,
            expires_at=time.time() + expires_in_seconds if expires_in_seconds else None
        )
        
        st.session_state.notifications.insert(0, notification)
        st.session_state.unread_count += 1
        
        if len(st.session_state.notifications) > self.MAX_NOTIFICATIONS:
            st.session_state.notifications = st.session_state.notifications[:self.MAX_NOTIFICATIONS]
        
        return notification
    
    def notify_transaction(
        self,
        tx_type: str,
        amount: float,
        from_addr: str,
        to_addr: str,
        tx_hash: str,
        status: str = "confirmed"
    ) -> Notification:
        """Notify about a transaction"""
        title = f"Transaction {status.title()}"
        message = f"{tx_type}: {amount:,.4f} NXT"
        
        return self.notify(
            title=title,
            message=message,
            notification_type=NotificationType.TRANSACTION,
            priority=NotificationPriority.HIGH,
            data={
                'tx_type': tx_type,
                'amount': amount,
                'from': from_addr,
                'to': to_addr,
                'tx_hash': tx_hash,
                'status': status
            }
        )
    
    def notify_reward(
        self,
        reward_type: str,
        amount: float,
        source: str
    ) -> Notification:
        """Notify about earned rewards"""
        return self.notify(
            title=f"Reward Earned!",
            message=f"+{amount:,.4f} NXT from {source}",
            notification_type=NotificationType.REWARD,
            priority=NotificationPriority.NORMAL,
            data={
                'reward_type': reward_type,
                'amount': amount,
                'source': source
            }
        )
    
    def notify_governance(
        self,
        event_type: str,
        proposal_title: str,
        proposal_id: str
    ) -> Notification:
        """Notify about governance events"""
        messages = {
            'new_proposal': f"New proposal: {proposal_title}",
            'vote_started': f"Voting open: {proposal_title}",
            'vote_ended': f"Voting closed: {proposal_title}",
            'proposal_passed': f"Proposal passed: {proposal_title}",
            'proposal_rejected': f"Proposal rejected: {proposal_title}"
        }
        
        return self.notify(
            title="Governance Update",
            message=messages.get(event_type, proposal_title),
            notification_type=NotificationType.GOVERNANCE,
            priority=NotificationPriority.HIGH,
            action_label="View Proposal",
            data={
                'event_type': event_type,
                'proposal_id': proposal_id,
                'proposal_title': proposal_title
            }
        )
    
    def notify_network(
        self,
        event_type: str,
        details: str
    ) -> Notification:
        """Notify about network events"""
        priority = NotificationPriority.NORMAL
        if event_type in ['validator_slashed', 'network_attack', 'consensus_failure']:
            priority = NotificationPriority.URGENT
        
        return self.notify(
            title="Network Alert",
            message=details,
            notification_type=NotificationType.NETWORK,
            priority=priority,
            data={'event_type': event_type}
        )
    
    def notify_security(
        self,
        event_type: str,
        details: str,
        severity: str = "medium"
    ) -> Notification:
        """Notify about security events"""
        priority_map = {
            'low': NotificationPriority.LOW,
            'medium': NotificationPriority.NORMAL,
            'high': NotificationPriority.HIGH,
            'critical': NotificationPriority.URGENT
        }
        
        return self.notify(
            title="Security Alert",
            message=details,
            notification_type=NotificationType.SECURITY,
            priority=priority_map.get(severity, NotificationPriority.HIGH),
            data={'event_type': event_type, 'severity': severity}
        )
    
    def notify_message(
        self,
        from_address: str,
        preview: str,
        message_id: str
    ) -> Notification:
        """Notify about new messages"""
        return self.notify(
            title="New Message",
            message=f"From {from_address[:10]}...: {preview[:50]}...",
            notification_type=NotificationType.MESSAGE,
            priority=NotificationPriority.NORMAL,
            action_label="View Message",
            data={
                'from_address': from_address,
                'message_id': message_id
            }
        )
    
    def get_notifications(
        self,
        unread_only: bool = False,
        notification_type: Optional[NotificationType] = None,
        limit: int = 50
    ) -> List[Notification]:
        """Get notifications with filters"""
        self._init_session_state()
        
        notifications = [n for n in st.session_state.notifications if not n.dismissed and not n.is_expired()]
        
        if unread_only:
            notifications = [n for n in notifications if not n.read]
        
        if notification_type:
            notifications = [n for n in notifications if n.notification_type == notification_type]
        
        return notifications[:limit]
    
    def get_unread_count(self) -> int:
        """Get count of unread notifications"""
        self._init_session_state()
        return len([n for n in st.session_state.notifications if not n.read and not n.dismissed])
    
    def mark_read(self, notification_id: str):
        """Mark a notification as read"""
        self._init_session_state()
        for notification in st.session_state.notifications:
            if notification.id == notification_id:
                notification.read = True
                break
        st.session_state.unread_count = self.get_unread_count()
    
    def mark_all_read(self):
        """Mark all notifications as read"""
        self._init_session_state()
        for notification in st.session_state.notifications:
            notification.read = True
        st.session_state.unread_count = 0
    
    def dismiss(self, notification_id: str):
        """Dismiss a notification"""
        self._init_session_state()
        for notification in st.session_state.notifications:
            if notification.id == notification_id:
                notification.dismissed = True
                break
    
    def clear_all(self):
        """Clear all notifications"""
        self._init_session_state()
        st.session_state.notifications = []
        st.session_state.unread_count = 0


def render_notification_bell():
    """Render the notification bell icon with unread count"""
    center = NotificationCenter()
    unread = center.get_unread_count()
    
    badge_html = ""
    if unread > 0:
        badge_html = f'<span class="notification-badge">{unread if unread < 100 else "99+"}</span>'
    
    st.markdown(f"""
        <style>
        .notification-bell {{
            position: relative;
            display: inline-block;
            cursor: pointer;
            font-size: 24px;
            padding: 8px;
        }}
        .notification-badge {{
            position: absolute;
            top: 0;
            right: 0;
            background: #ef4444;
            color: white;
            font-size: 11px;
            font-weight: bold;
            padding: 2px 6px;
            border-radius: 10px;
            min-width: 18px;
            text-align: center;
        }}
        </style>
        <div class="notification-bell">
            🔔{badge_html}
        </div>
    """, unsafe_allow_html=True)
    
    return unread


def render_notification_toast(notification: Notification):
    """Render a toast notification"""
    type_styles = {
        NotificationType.INFO: ("ℹ️", "#3b82f6", "rgba(59, 130, 246, 0.1)"),
        NotificationType.SUCCESS: ("✅", "#10b981", "rgba(16, 185, 129, 0.1)"),
        NotificationType.WARNING: ("⚠️", "#f59e0b", "rgba(245, 158, 11, 0.1)"),
        NotificationType.ERROR: ("❌", "#ef4444", "rgba(239, 68, 68, 0.1)"),
        NotificationType.TRANSACTION: ("💸", "#8b5cf6", "rgba(139, 92, 246, 0.1)"),
        NotificationType.GOVERNANCE: ("🗳️", "#06b6d4", "rgba(6, 182, 212, 0.1)"),
        NotificationType.NETWORK: ("🌐", "#6366f1", "rgba(99, 102, 241, 0.1)"),
        NotificationType.REWARD: ("🎁", "#22c55e", "rgba(34, 197, 94, 0.1)"),
        NotificationType.SECURITY: ("🛡️", "#f97316", "rgba(249, 115, 22, 0.1)"),
        NotificationType.MESSAGE: ("💬", "#ec4899", "rgba(236, 72, 153, 0.1)"),
    }
    
    icon, border_color, bg_color = type_styles.get(
        notification.notification_type, 
        ("📢", "#667eea", "rgba(102, 126, 234, 0.1)")
    )
    
    st.markdown(f"""
        <div class="notification-toast" style="
            background: {bg_color};
            border-left: 4px solid {border_color};
            padding: 12px 16px;
            border-radius: 8px;
            margin: 8px 0;
            animation: slideIn 0.3s ease;
        ">
            <div style="display: flex; align-items: flex-start; gap: 12px;">
                <span style="font-size: 20px;">{icon}</span>
                <div style="flex: 1;">
                    <div style="font-weight: 600; color: #e2e8f0; font-size: 14px;">{notification.title}</div>
                    <div style="color: #94a3b8; font-size: 13px; margin-top: 4px;">{notification.message}</div>
                    <div style="color: #64748b; font-size: 11px; margin-top: 6px;">{notification._time_ago()}</div>
                </div>
            </div>
        </div>
        <style>
        @keyframes slideIn {{
            from {{ transform: translateX(100%); opacity: 0; }}
            to {{ transform: translateX(0); opacity: 1; }}
        }}
        </style>
    """, unsafe_allow_html=True)


def render_notification_panel():
    """Render the full notification panel"""
    center = NotificationCenter()
    
    st.markdown("""
        <style>
        .notification-panel {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            border-radius: 12px;
            padding: 16px;
            max-height: 400px;
            overflow-y: auto;
        }
        .notification-item {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            padding: 12px;
            margin: 8px 0;
            border-left: 3px solid #667eea;
            transition: all 0.2s ease;
        }
        .notification-item:hover {
            background: rgba(255, 255, 255, 0.08);
            transform: translateX(4px);
        }
        .notification-item.unread {
            background: rgba(102, 126, 234, 0.1);
            border-left-color: #00d4ff;
        }
        .notification-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown("### 🔔 Notifications")
    with col2:
        if st.button("Mark All Read", key="mark_all_read"):
            center.mark_all_read()
            st.rerun()
    with col3:
        if st.button("Clear All", key="clear_all_notif"):
            center.clear_all()
            st.rerun()
    
    notifications = center.get_notifications(limit=20)
    
    if not notifications:
        st.info("No notifications yet. You'll see alerts for transactions, rewards, governance, and network events here.")
        return
    
    for notif in notifications:
        render_notification_toast(notif)
        
        col1, col2 = st.columns([3, 1])
        with col2:
            if not notif.read:
                if st.button("✓", key=f"read_{notif.id}", help="Mark as read"):
                    center.mark_read(notif.id)
                    st.rerun()


def render_notification_settings():
    """Render notification settings"""
    center = NotificationCenter()
    center._init_session_state()
    
    st.markdown("### ⚙️ Notification Settings")
    
    settings = st.session_state.notification_settings
    
    st.checkbox("Transaction Alerts", value=settings['transaction_alerts'], key="set_tx_alerts")
    st.checkbox("Governance Alerts", value=settings['governance_alerts'], key="set_gov_alerts")
    st.checkbox("Network Alerts", value=settings['network_alerts'], key="set_net_alerts")
    st.checkbox("Reward Alerts", value=settings['reward_alerts'], key="set_reward_alerts")
    st.checkbox("Security Alerts", value=settings['security_alerts'], key="set_sec_alerts")
    st.checkbox("Message Alerts", value=settings['message_alerts'], key="set_msg_alerts")
    
    if st.button("Save Settings", type="primary"):
        st.session_state.notification_settings = {
            'transaction_alerts': st.session_state.set_tx_alerts,
            'governance_alerts': st.session_state.set_gov_alerts,
            'network_alerts': st.session_state.set_net_alerts,
            'reward_alerts': st.session_state.set_reward_alerts,
            'security_alerts': st.session_state.set_sec_alerts,
            'message_alerts': st.session_state.set_msg_alerts
        }
        st.success("Settings saved!")


def get_notification_center() -> NotificationCenter:
    """Get or create the notification center singleton"""
    if 'notification_center' not in st.session_state:
        st.session_state.notification_center = NotificationCenter()
    return st.session_state.notification_center
