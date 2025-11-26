#!/usr/bin/env python3
"""
Friend Management System for WNSP P2P Hub
GPL v3.0 License
Manages friend relationships with PostgreSQL storage
"""

import psycopg2
import os
import json
from datetime import datetime
from typing import List, Dict, Optional

class FriendManager:
    """Manages friend relationships for WNSP users"""
    
    def __init__(self):
        """Initialize database connection"""
        self.db_url = os.environ.get('DATABASE_URL')
        if not self.db_url:
            raise ValueError("DATABASE_URL environment variable not set")
        
        self._init_database()
    
    def _get_connection(self):
        """Get database connection"""
        return psycopg2.connect(self.db_url)
    
    def _init_database(self):
        """Create friends table if it doesn't exist"""
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS friends (
                        id SERIAL PRIMARY KEY,
                        user_id VARCHAR(255) NOT NULL,
                        friend_name VARCHAR(255) NOT NULL,
                        friend_contact VARCHAR(255) NOT NULL,
                        device_id VARCHAR(255),
                        country VARCHAR(100),
                        state_region VARCHAR(100),
                        sim_number VARCHAR(50),
                        can_share_media BOOLEAN DEFAULT TRUE,
                        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(user_id, friend_contact)
                    )
                """)
                
                # Add columns if they don't exist (for existing tables)
                cur.execute("""
                    DO $$
                    BEGIN
                        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                      WHERE table_name='friends' AND column_name='country') THEN
                            ALTER TABLE friends ADD COLUMN country VARCHAR(100);
                        END IF;
                        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                      WHERE table_name='friends' AND column_name='state_region') THEN
                            ALTER TABLE friends ADD COLUMN state_region VARCHAR(100);
                        END IF;
                        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                      WHERE table_name='friends' AND column_name='sim_number') THEN
                            ALTER TABLE friends ADD COLUMN sim_number VARCHAR(50);
                        END IF;
                        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                      WHERE table_name='friends' AND column_name='can_share_media') THEN
                            ALTER TABLE friends ADD COLUMN can_share_media BOOLEAN DEFAULT TRUE;
                        END IF;
                    END $$;
                """)
                
                conn.commit()
                print("✅ Friends table initialized with country/state/SIM fields")
        except Exception as e:
            print(f"❌ Database initialization error: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def add_friend(self, user_id: str, friend_name: str, friend_contact: str, 
                   device_id: Optional[str] = None, country: Optional[str] = None,
                   state_region: Optional[str] = None, sim_number: Optional[str] = None,
                   can_share_media: bool = True) -> Dict:
        """Add a new friend with location and media sharing info"""
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO friends (user_id, friend_name, friend_contact, device_id, 
                                        country, state_region, sim_number, can_share_media)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id, added_at
                """, (user_id, friend_name, friend_contact, device_id, 
                      country, state_region, sim_number, can_share_media))
                
                result = cur.fetchone()
                conn.commit()
                
                if not result:
                    return {
                        'success': False,
                        'error': 'Failed to add friend'
                    }
                
                return {
                    'success': True,
                    'friend': {
                        'id': result[0],
                        'name': friend_name,
                        'contact': friend_contact,
                        'device_id': device_id,
                        'country': country,
                        'state_region': state_region,
                        'sim_number': sim_number,
                        'can_share_media': can_share_media,
                        'added_at': result[1].isoformat()
                    }
                }
        except psycopg2.IntegrityError:
            conn.rollback()
            return {
                'success': False,
                'error': 'Friend already exists'
            }
        except Exception as e:
            conn.rollback()
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            conn.close()
    
    def get_friends(self, user_id: str) -> List[Dict]:
        """Get all friends for a user with location and media sharing info"""
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, friend_name, friend_contact, device_id, 
                           country, state_region, sim_number, can_share_media, added_at
                    FROM friends
                    WHERE user_id = %s
                    ORDER BY added_at DESC
                """, (user_id,))
                
                friends = []
                for row in cur.fetchall():
                    friends.append({
                        'id': row[0],
                        'name': row[1],
                        'contact': row[2],
                        'device_id': row[3],
                        'country': row[4],
                        'state_region': row[5],
                        'sim_number': row[6],
                        'can_share_media': row[7] if row[7] is not None else True,
                        'added_at': row[8].isoformat() if row[8] else None
                    })
                
                return friends
        except Exception as e:
            print(f"❌ Get friends error: {e}")
            return []
        finally:
            conn.close()
    
    def remove_friend(self, user_id: str, friend_id: int) -> bool:
        """Remove a friend"""
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    DELETE FROM friends
                    WHERE id = %s AND user_id = %s
                """, (friend_id, user_id))
                
                deleted = cur.rowcount > 0
                conn.commit()
                return deleted
        except Exception as e:
            print(f"❌ Remove friend error: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def get_friend_by_contact(self, user_id: str, friend_contact: str) -> Optional[Dict]:
        """Get friend by contact"""
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, friend_name, friend_contact, device_id, added_at
                    FROM friends
                    WHERE user_id = %s AND friend_contact = %s
                """, (user_id, friend_contact))
                
                row = cur.fetchone()
                if row:
                    return {
                        'id': row[0],
                        'name': row[1],
                        'contact': row[2],
                        'device_id': row[3],
                        'added_at': row[4].isoformat() if row[4] else None
                    }
                return None
        except Exception as e:
            print(f"❌ Get friend by contact error: {e}")
            return None
        finally:
            conn.close()


# Global instance
friend_manager = None

def get_friend_manager():
    """Get or create friend manager instance"""
    global friend_manager
    if friend_manager is None:
        try:
            friend_manager = FriendManager()
        except Exception as e:
            print(f"❌ Failed to initialize friend manager: {e}")
            return None
    return friend_manager
