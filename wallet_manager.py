#!/usr/bin/env python3
"""
Wallet Manager for WNSP P2P Hub
Simplified wallet system with PostgreSQL storage
"""

import psycopg2
import os
import hashlib
import secrets
from typing import Dict, Optional

UNITS_PER_NXT = 100_000_000  # 100 million units per NXT

class WalletManager:
    """Manages wallet authentication and NXT balances"""
    
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
        """Create wallets table if it doesn't exist"""
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS wallets (
                        id SERIAL PRIMARY KEY,
                        device_id VARCHAR(255) UNIQUE NOT NULL,
                        device_name VARCHAR(255) NOT NULL,
                        contact VARCHAR(255) NOT NULL,
                        balance_units BIGINT DEFAULT 0,
                        auth_token VARCHAR(255) UNIQUE NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.commit()
                print("✅ Wallets table initialized")
        except Exception as e:
            print(f"❌ Database initialization error: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def create_wallet(self, device_name: str, contact: str) -> Dict:
        """Create new wallet with initial balance"""
        conn = self._get_connection()
        try:
            # Generate unique device ID from contact
            device_id = hashlib.sha256(f"{contact}{secrets.token_hex(8)}".encode()).hexdigest()[:16]
            auth_token = secrets.token_urlsafe(32)
            
            # Initial balance: 1,000,000 units = 0.01 NXT
            initial_balance = 1_000_000
            
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO wallets (device_id, device_name, contact, balance_units, auth_token)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id, device_id, balance_units
                """, (device_id, device_name, contact, initial_balance, auth_token))
                
                result = cur.fetchone()
                conn.commit()
                
                if not result:
                    return {
                        'success': False,
                        'error': 'Failed to create wallet'
                    }
                
                return {
                    'success': True,
                    'wallet': {
                        'device_id': device_id,
                        'device_name': device_name,
                        'balance_units': initial_balance,
                        'balance_nxt': initial_balance / UNITS_PER_NXT,
                        'auth_token': auth_token
                    }
                }
        except psycopg2.IntegrityError:
            conn.rollback()
            return {
                'success': False,
                'error': 'Wallet already exists for this contact'
            }
        except Exception as e:
            conn.rollback()
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            conn.close()
    
    def login_wallet(self, contact: str) -> Dict:
        """Login to wallet using contact"""
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT device_id, device_name, balance_units, auth_token
                    FROM wallets
                    WHERE contact = %s
                """, (contact,))
                
                row = cur.fetchone()
                
                if not row:
                    return {
                        'success': False,
                        'error': 'Wallet not found. Please create a new wallet.'
                    }
                
                # Update last seen
                cur.execute("""
                    UPDATE wallets SET last_seen = CURRENT_TIMESTAMP
                    WHERE contact = %s
                """, (contact,))
                conn.commit()
                
                return {
                    'success': True,
                    'wallet': {
                        'device_id': row[0],
                        'device_name': row[1],
                        'balance_units': row[2],
                        'balance_nxt': row[2] / UNITS_PER_NXT,
                        'auth_token': row[3]
                    }
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            conn.close()
    
    def get_balance(self, device_id: str) -> Dict:
        """Get wallet balance"""
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT balance_units FROM wallets
                    WHERE device_id = %s
                """, (device_id,))
                
                row = cur.fetchone()
                
                if not row:
                    return {
                        'success': False,
                        'error': 'Wallet not found'
                    }
                
                return {
                    'success': True,
                    'balance_units': row[0],
                    'balance_nxt': row[0] / UNITS_PER_NXT
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            conn.close()
    
    def deduct_balance(self, device_id: str, amount_units: int) -> bool:
        """Deduct balance from wallet"""
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                # Check current balance
                cur.execute("""
                    SELECT balance_units FROM wallets
                    WHERE device_id = %s
                """, (device_id,))
                
                row = cur.fetchone()
                if not row or row[0] < amount_units:
                    return False
                
                # Deduct balance
                cur.execute("""
                    UPDATE wallets
                    SET balance_units = balance_units - %s
                    WHERE device_id = %s
                """, (amount_units, device_id))
                
                conn.commit()
                return True
        except Exception as e:
            print(f"❌ Deduct balance error: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()


# Global instance
wallet_manager = None

def get_wallet_manager():
    """Get or create wallet manager instance"""
    global wallet_manager
    if wallet_manager is None:
        try:
            wallet_manager = WalletManager()
        except Exception as e:
            print(f"❌ Failed to initialize wallet manager: {e}")
            return None
    return wallet_manager
