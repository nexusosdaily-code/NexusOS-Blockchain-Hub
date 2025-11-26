"""
NexusOS Achievement System
==========================

Physics-themed gamification with achievements and badges that reward
user engagement across the NexusOS ecosystem.

Achievement Categories:
- Genesis: First-time actions (first transaction, first vote, etc.)
- Wavelength: Physics-based milestones (spectral mastery)
- Community: Governance and social engagement
- Economic: Trading and staking achievements
- Explorer: Discovery and learning milestones
"""

import os
from datetime import datetime
from typing import Dict, List, Optional, Literal
from dataclasses import dataclass, field
from enum import Enum
import json
from sqlalchemy import create_engine, Column, String, Integer, Float, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

def get_database_url() -> Optional[str]:
    """Get database URL from environment"""
    url = os.environ.get("DATABASE_URL")
    if not url:
        url = os.getenv("DATABASE_URL")
    return url


class AchievementCategory(Enum):
    GENESIS = "genesis"
    WAVELENGTH = "wavelength"
    COMMUNITY = "community"
    ECONOMIC = "economic"
    EXPLORER = "explorer"


class AchievementRarity(Enum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


@dataclass
class AchievementDefinition:
    """Definition of an achievement"""
    id: str
    name: str
    description: str
    category: AchievementCategory
    rarity: AchievementRarity
    icon: str
    xp_reward: int
    requirement_type: str
    requirement_value: float
    secret: bool = False


class UserAchievement(Base):
    """Database model for user achievements"""
    __tablename__ = 'user_achievements'
    
    id = Column(Integer, primary_key=True)
    wallet_address = Column(String(66), nullable=False, index=True)
    achievement_id = Column(String(50), nullable=False)
    unlocked_at = Column(DateTime, default=datetime.utcnow)
    progress = Column(Float, default=0.0)
    is_unlocked = Column(Boolean, default=False)
    notified = Column(Boolean, default=False)


class UserStats(Base):
    """Database model for tracking user statistics"""
    __tablename__ = 'user_stats'
    
    id = Column(Integer, primary_key=True)
    wallet_address = Column(String(66), nullable=False, unique=True, index=True)
    total_xp = Column(Integer, default=0)
    level = Column(Integer, default=1)
    transactions_sent = Column(Integer, default=0)
    transactions_received = Column(Integer, default=0)
    total_volume = Column(Float, default=0.0)
    swaps_completed = Column(Integer, default=0)
    votes_cast = Column(Integer, default=0)
    proposals_created = Column(Integer, default=0)
    staking_days = Column(Integer, default=0)
    referrals = Column(Integer, default=0)
    login_streak = Column(Integer, default=0)
    last_login = Column(DateTime)
    achievements_unlocked = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


ACHIEVEMENT_DEFINITIONS: List[AchievementDefinition] = [
    AchievementDefinition(
        id="first_light",
        name="First Light",
        description="Send your first NXT transaction",
        category=AchievementCategory.GENESIS,
        rarity=AchievementRarity.COMMON,
        icon="✨",
        xp_reward=50,
        requirement_type="transactions_sent",
        requirement_value=1
    ),
    AchievementDefinition(
        id="photon_collector",
        name="Photon Collector",
        description="Receive your first NXT transfer",
        category=AchievementCategory.GENESIS,
        rarity=AchievementRarity.COMMON,
        icon="🌟",
        xp_reward=50,
        requirement_type="transactions_received",
        requirement_value=1
    ),
    AchievementDefinition(
        id="wave_rider",
        name="Wave Rider",
        description="Complete your first swap on the DEX",
        category=AchievementCategory.GENESIS,
        rarity=AchievementRarity.COMMON,
        icon="🌊",
        xp_reward=75,
        requirement_type="swaps_completed",
        requirement_value=1
    ),
    AchievementDefinition(
        id="civic_duty",
        name="Civic Duty",
        description="Cast your first governance vote",
        category=AchievementCategory.GENESIS,
        rarity=AchievementRarity.COMMON,
        icon="🗳️",
        xp_reward=100,
        requirement_type="votes_cast",
        requirement_value=1
    ),
    AchievementDefinition(
        id="infrared_initiate",
        name="Infrared Initiate",
        description="Trade 100 NXT total volume",
        category=AchievementCategory.WAVELENGTH,
        rarity=AchievementRarity.COMMON,
        icon="🔴",
        xp_reward=100,
        requirement_type="total_volume",
        requirement_value=100
    ),
    AchievementDefinition(
        id="visible_voyager",
        name="Visible Voyager",
        description="Trade 1,000 NXT total volume",
        category=AchievementCategory.WAVELENGTH,
        rarity=AchievementRarity.UNCOMMON,
        icon="🟢",
        xp_reward=250,
        requirement_type="total_volume",
        requirement_value=1000
    ),
    AchievementDefinition(
        id="ultraviolet_master",
        name="Ultraviolet Master",
        description="Trade 10,000 NXT total volume",
        category=AchievementCategory.WAVELENGTH,
        rarity=AchievementRarity.RARE,
        icon="🟣",
        xp_reward=500,
        requirement_type="total_volume",
        requirement_value=10000
    ),
    AchievementDefinition(
        id="xray_expert",
        name="X-Ray Expert",
        description="Trade 100,000 NXT total volume",
        category=AchievementCategory.WAVELENGTH,
        rarity=AchievementRarity.EPIC,
        icon="💠",
        xp_reward=1000,
        requirement_type="total_volume",
        requirement_value=100000
    ),
    AchievementDefinition(
        id="gamma_legend",
        name="Gamma Legend",
        description="Trade 1,000,000 NXT total volume",
        category=AchievementCategory.WAVELENGTH,
        rarity=AchievementRarity.LEGENDARY,
        icon="⚡",
        xp_reward=5000,
        requirement_type="total_volume",
        requirement_value=1000000
    ),
    AchievementDefinition(
        id="transaction_wave",
        name="Transaction Wave",
        description="Send 10 transactions",
        category=AchievementCategory.ECONOMIC,
        rarity=AchievementRarity.COMMON,
        icon="📤",
        xp_reward=100,
        requirement_type="transactions_sent",
        requirement_value=10
    ),
    AchievementDefinition(
        id="frequency_trader",
        name="Frequency Trader",
        description="Complete 25 swaps",
        category=AchievementCategory.ECONOMIC,
        rarity=AchievementRarity.UNCOMMON,
        icon="🔄",
        xp_reward=300,
        requirement_type="swaps_completed",
        requirement_value=25
    ),
    AchievementDefinition(
        id="harmonic_trader",
        name="Harmonic Trader",
        description="Complete 100 swaps",
        category=AchievementCategory.ECONOMIC,
        rarity=AchievementRarity.RARE,
        icon="🎵",
        xp_reward=750,
        requirement_type="swaps_completed",
        requirement_value=100
    ),
    AchievementDefinition(
        id="quantum_staker",
        name="Quantum Staker",
        description="Stake continuously for 7 days",
        category=AchievementCategory.ECONOMIC,
        rarity=AchievementRarity.UNCOMMON,
        icon="⚛️",
        xp_reward=400,
        requirement_type="staking_days",
        requirement_value=7
    ),
    AchievementDefinition(
        id="entangled_staker",
        name="Entangled Staker",
        description="Stake continuously for 30 days",
        category=AchievementCategory.ECONOMIC,
        rarity=AchievementRarity.RARE,
        icon="🔮",
        xp_reward=1000,
        requirement_type="staking_days",
        requirement_value=30
    ),
    AchievementDefinition(
        id="voice_of_the_network",
        name="Voice of the Network",
        description="Cast 10 governance votes",
        category=AchievementCategory.COMMUNITY,
        rarity=AchievementRarity.UNCOMMON,
        icon="📢",
        xp_reward=300,
        requirement_type="votes_cast",
        requirement_value=10
    ),
    AchievementDefinition(
        id="proposal_pioneer",
        name="Proposal Pioneer",
        description="Create your first governance proposal",
        category=AchievementCategory.COMMUNITY,
        rarity=AchievementRarity.RARE,
        icon="📜",
        xp_reward=500,
        requirement_type="proposals_created",
        requirement_value=1
    ),
    AchievementDefinition(
        id="civilization_architect",
        name="Civilization Architect",
        description="Create 5 governance proposals",
        category=AchievementCategory.COMMUNITY,
        rarity=AchievementRarity.EPIC,
        icon="🏛️",
        xp_reward=1500,
        requirement_type="proposals_created",
        requirement_value=5
    ),
    AchievementDefinition(
        id="network_ambassador",
        name="Network Ambassador",
        description="Refer 3 new users",
        category=AchievementCategory.COMMUNITY,
        rarity=AchievementRarity.RARE,
        icon="🤝",
        xp_reward=750,
        requirement_type="referrals",
        requirement_value=3
    ),
    AchievementDefinition(
        id="dedicated_citizen",
        name="Dedicated Citizen",
        description="Login 7 days in a row",
        category=AchievementCategory.EXPLORER,
        rarity=AchievementRarity.UNCOMMON,
        icon="📅",
        xp_reward=200,
        requirement_type="login_streak",
        requirement_value=7
    ),
    AchievementDefinition(
        id="steadfast_node",
        name="Steadfast Node",
        description="Login 30 days in a row",
        category=AchievementCategory.EXPLORER,
        rarity=AchievementRarity.RARE,
        icon="🏆",
        xp_reward=1000,
        requirement_type="login_streak",
        requirement_value=30
    ),
    AchievementDefinition(
        id="level_5",
        name="Rising Frequency",
        description="Reach level 5",
        category=AchievementCategory.EXPLORER,
        rarity=AchievementRarity.UNCOMMON,
        icon="📈",
        xp_reward=250,
        requirement_type="level",
        requirement_value=5
    ),
    AchievementDefinition(
        id="level_10",
        name="Wavelength Adept",
        description="Reach level 10",
        category=AchievementCategory.EXPLORER,
        rarity=AchievementRarity.RARE,
        icon="🌈",
        xp_reward=500,
        requirement_type="level",
        requirement_value=10
    ),
    AchievementDefinition(
        id="level_25",
        name="Spectral Master",
        description="Reach level 25",
        category=AchievementCategory.EXPLORER,
        rarity=AchievementRarity.EPIC,
        icon="👑",
        xp_reward=2500,
        requirement_type="level",
        requirement_value=25
    ),
    AchievementDefinition(
        id="genesis_citizen",
        name="Genesis Citizen",
        description="Be among the first 1000 users",
        category=AchievementCategory.GENESIS,
        rarity=AchievementRarity.LEGENDARY,
        icon="🌅",
        xp_reward=5000,
        requirement_type="special",
        requirement_value=1000,
        secret=True
    ),
]


class AchievementSystem:
    """Main achievement system controller"""
    
    XP_PER_LEVEL = 500
    
    def __init__(self):
        self.engine = None
        self.Session = None
        self.achievements = {a.id: a for a in ACHIEVEMENT_DEFINITIONS}
        self._init_database()
    
    def _init_database(self):
        """Initialize database connection"""
        db_url = get_database_url()
        if db_url:
            try:
                self.engine = create_engine(db_url)
                Base.metadata.create_all(self.engine)
                self.Session = sessionmaker(bind=self.engine)
                print("✅ Achievement system: Database connected")
            except Exception as e:
                print(f"❌ Achievement DB init error: {e}")
                self.engine = None
        else:
            print("⚠️ Achievement system: No DATABASE_URL found, using in-memory fallback")
    
    def _get_session(self):
        """Get database session"""
        if self.Session:
            return self.Session()
        return None
    
    def get_or_create_user_stats(self, wallet_address: str) -> Optional[UserStats]:
        """Get or create user stats record"""
        session = self._get_session()
        if not session:
            return None
        
        try:
            stats = session.query(UserStats).filter_by(wallet_address=wallet_address).first()
            if not stats:
                stats = UserStats(wallet_address=wallet_address)
                session.add(stats)
                session.commit()
            return stats
        except Exception as e:
            session.rollback()
            print(f"Error getting user stats: {e}")
            return None
        finally:
            session.close()
    
    def get_user_achievements(self, wallet_address: str) -> List[Dict]:
        """Get all achievements for a user with progress"""
        session = self._get_session()
        if not session:
            return self._get_default_achievements()
        
        try:
            user_achievements = session.query(UserAchievement).filter_by(
                wallet_address=wallet_address
            ).all()
            
            achievement_map = {ua.achievement_id: ua for ua in user_achievements}
            
            result = []
            for achievement in ACHIEVEMENT_DEFINITIONS:
                if achievement.secret and achievement.id not in achievement_map:
                    continue
                
                user_ach = achievement_map.get(achievement.id)
                result.append({
                    'id': achievement.id,
                    'name': achievement.name,
                    'description': achievement.description,
                    'category': achievement.category.value,
                    'rarity': achievement.rarity.value,
                    'icon': achievement.icon,
                    'xp_reward': achievement.xp_reward,
                    'progress': user_ach.progress if user_ach else 0.0,
                    'is_unlocked': user_ach.is_unlocked if user_ach else False,
                    'unlocked_at': user_ach.unlocked_at.isoformat() if user_ach and user_ach.is_unlocked else None,
                    'requirement_value': achievement.requirement_value
                })
            
            return result
        except Exception as e:
            print(f"Error getting achievements: {e}")
            return self._get_default_achievements()
        finally:
            session.close()
    
    def _get_default_achievements(self) -> List[Dict]:
        """Return default achievement list when database unavailable"""
        return [
            {
                'id': a.id,
                'name': a.name,
                'description': a.description,
                'category': a.category.value,
                'rarity': a.rarity.value,
                'icon': a.icon,
                'xp_reward': a.xp_reward,
                'progress': 0.0,
                'is_unlocked': False,
                'unlocked_at': None,
                'requirement_value': a.requirement_value
            }
            for a in ACHIEVEMENT_DEFINITIONS if not a.secret
        ]
    
    def check_and_unlock_achievements(self, wallet_address: str) -> List[Dict]:
        """Check all achievements and unlock any that are completed"""
        session = self._get_session()
        if not session:
            return []
        
        try:
            stats = session.query(UserStats).filter_by(wallet_address=wallet_address).first()
            if not stats:
                return []
            
            newly_unlocked = []
            
            for achievement in ACHIEVEMENT_DEFINITIONS:
                existing = session.query(UserAchievement).filter_by(
                    wallet_address=wallet_address,
                    achievement_id=achievement.id
                ).first()
                
                if existing and existing.is_unlocked:
                    continue
                
                current_value = self._get_stat_value(stats, achievement.requirement_type)
                progress = min(100.0, (current_value / achievement.requirement_value) * 100)
                
                if not existing:
                    existing = UserAchievement(
                        wallet_address=wallet_address,
                        achievement_id=achievement.id,
                        progress=progress
                    )
                    session.add(existing)
                else:
                    existing.progress = progress
                
                if current_value >= achievement.requirement_value:
                    existing.is_unlocked = True
                    existing.unlocked_at = datetime.utcnow()
                    existing.notified = False
                    
                    stats.total_xp += achievement.xp_reward
                    stats.achievements_unlocked += 1
                    stats.level = (stats.total_xp // self.XP_PER_LEVEL) + 1
                    
                    newly_unlocked.append({
                        'id': achievement.id,
                        'name': achievement.name,
                        'icon': achievement.icon,
                        'xp_reward': achievement.xp_reward,
                        'rarity': achievement.rarity.value
                    })
            
            session.commit()
            return newly_unlocked
        except Exception as e:
            session.rollback()
            print(f"Error checking achievements: {e}")
            return []
        finally:
            session.close()
    
    def _get_stat_value(self, stats: UserStats, stat_type: str) -> float:
        """Get the current value of a stat from UserStats"""
        stat_mapping = {
            'transactions_sent': stats.transactions_sent,
            'transactions_received': stats.transactions_received,
            'total_volume': stats.total_volume,
            'swaps_completed': stats.swaps_completed,
            'votes_cast': stats.votes_cast,
            'proposals_created': stats.proposals_created,
            'staking_days': stats.staking_days,
            'referrals': stats.referrals,
            'login_streak': stats.login_streak,
            'level': stats.level,
            'special': 0
        }
        return stat_mapping.get(stat_type, 0)
    
    def record_action(self, wallet_address: str, action_type: str, value: float = 1.0) -> List[Dict]:
        """Record a user action and check for new achievements"""
        session = self._get_session()
        if not session:
            return []
        
        try:
            stats = session.query(UserStats).filter_by(wallet_address=wallet_address).first()
            if not stats:
                stats = UserStats(wallet_address=wallet_address)
                session.add(stats)
            
            if action_type == 'transaction_sent':
                stats.transactions_sent += 1
                stats.total_volume += value
            elif action_type == 'transaction_received':
                stats.transactions_received += 1
            elif action_type == 'swap':
                stats.swaps_completed += 1
                stats.total_volume += value
            elif action_type == 'vote':
                stats.votes_cast += 1
            elif action_type == 'proposal':
                stats.proposals_created += 1
            elif action_type == 'stake_day':
                stats.staking_days += 1
            elif action_type == 'referral':
                stats.referrals += 1
            elif action_type == 'login':
                today = datetime.utcnow().date()
                if stats.last_login:
                    last_login_date = stats.last_login.date()
                    if (today - last_login_date).days == 1:
                        stats.login_streak += 1
                    elif (today - last_login_date).days > 1:
                        stats.login_streak = 1
                else:
                    stats.login_streak = 1
                stats.last_login = datetime.utcnow()
            
            stats.updated_at = datetime.utcnow()
            session.commit()
            session.close()
            
            return self.check_and_unlock_achievements(wallet_address)
        except Exception as e:
            session.rollback()
            print(f"Error recording action: {e}")
            return []
        finally:
            if session:
                session.close()
    
    def get_user_level_info(self, wallet_address: str) -> Dict:
        """Get user level and XP information"""
        session = self._get_session()
        if not session:
            return {'level': 1, 'xp': 0, 'xp_to_next': self.XP_PER_LEVEL, 'progress': 0.0}
        
        try:
            stats = session.query(UserStats).filter_by(wallet_address=wallet_address).first()
            if not stats:
                return {'level': 1, 'xp': 0, 'xp_to_next': self.XP_PER_LEVEL, 'progress': 0.0}
            
            xp_in_current_level = stats.total_xp % self.XP_PER_LEVEL
            progress = (xp_in_current_level / self.XP_PER_LEVEL) * 100
            
            return {
                'level': stats.level,
                'xp': stats.total_xp,
                'xp_in_level': xp_in_current_level,
                'xp_to_next': self.XP_PER_LEVEL - xp_in_current_level,
                'progress': progress,
                'achievements_unlocked': stats.achievements_unlocked
            }
        except Exception as e:
            print(f"Error getting level info: {e}")
            return {'level': 1, 'xp': 0, 'xp_to_next': self.XP_PER_LEVEL, 'progress': 0.0}
        finally:
            session.close()
    
    def get_unnotified_achievements(self, wallet_address: str) -> List[Dict]:
        """Get achievements that haven't been shown to the user yet"""
        session = self._get_session()
        if not session:
            return []
        
        try:
            unnotified = session.query(UserAchievement).filter_by(
                wallet_address=wallet_address,
                is_unlocked=True,
                notified=False
            ).all()
            
            result = []
            for ua in unnotified:
                if ua.achievement_id in self.achievements:
                    ach = self.achievements[ua.achievement_id]
                    result.append({
                        'id': ach.id,
                        'name': ach.name,
                        'description': ach.description,
                        'icon': ach.icon,
                        'xp_reward': ach.xp_reward,
                        'rarity': ach.rarity.value
                    })
                    ua.notified = True
            
            session.commit()
            return result
        except Exception as e:
            session.rollback()
            print(f"Error getting unnotified achievements: {e}")
            return []
        finally:
            session.close()
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """Get top users by XP"""
        session = self._get_session()
        if not session:
            return []
        
        try:
            top_users = session.query(UserStats).order_by(
                UserStats.total_xp.desc()
            ).limit(limit).all()
            
            return [
                {
                    'wallet_address': u.wallet_address[:8] + '...' + u.wallet_address[-4:],
                    'level': u.level,
                    'xp': u.total_xp,
                    'achievements': u.achievements_unlocked
                }
                for u in top_users
            ]
        except Exception as e:
            print(f"Error getting leaderboard: {e}")
            return []
        finally:
            session.close()


achievement_system = AchievementSystem()


def get_achievement_system() -> AchievementSystem:
    """Get the global achievement system instance"""
    return achievement_system
