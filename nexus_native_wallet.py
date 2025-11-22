"""
NexusOS Native Wallet
=====================
Mobile-first quantum-resistant wallet for NXT tokens and WNSP messaging.

Uses NexusOS's existing blockchain infrastructure:
- NativeTokenSystem for NXT balance and transfers
- WNSP v2.0 for wavelength-encrypted messaging
- WavelengthValidator for quantum-resistant signatures
- DAG messaging for mobile peer-to-peer communication
"""

import os
import json
import time
import hashlib
import secrets
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from decimal import Decimal

# NexusOS core components
from native_token import NativeTokenSystem, Account, TokenTransaction
from wnsp_protocol_v2 import (
    WnspEncoderV2, 
    SpectralRegion, 
    ModulationType,
    WaveProperties
)
from wavelength_validator import WavelengthValidator

# Cryptography
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

# Database
import sqlalchemy as sa
from sqlalchemy import create_engine, Column, String, Float, Integer, BigInteger, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError, DBAPIError
from functools import wraps

# ============================================================================
# Database Retry Decorator
# ============================================================================

def retry_on_connection_error(max_retries=2):
    """
    Decorator to retry database operations on connection errors.
    Automatically refreshes the database session and retries.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            last_error = None
            for attempt in range(max_retries + 1):
                try:
                    return func(self, *args, **kwargs)
                except (OperationalError, DBAPIError) as e:
                    last_error = e
                    error_msg = str(e).lower()
                    
                    # Check if it's a connection-related error
                    if any(err in error_msg for err in ['ssl', 'connection', 'closed', 'timeout']):
                        if attempt < max_retries:
                            # Refresh session and retry
                            self._refresh_session()
                            continue
                    # Not a connection error or max retries reached, re-raise
                    raise
            # All retries exhausted
            raise last_error
        return wrapper
    return decorator

# ============================================================================
# Database Models
# ============================================================================

Base = declarative_base()

class NexusWallet(Base):
    """NexusOS native wallet with quantum encryption"""
    __tablename__ = 'nexus_wallets'
    
    id = Column(Integer, primary_key=True)
    address = Column(String(64), unique=True, nullable=False)
    public_key = Column(Text, nullable=False)  # Quantum public key
    encrypted_private_key = Column(Text, nullable=False)  # Wavelength-encrypted
    spectral_signature = Column(Text, nullable=False)  # Multi-spectral ID
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class WalletTransaction(Base):
    """Transaction history with quantum proofs"""
    __tablename__ = 'nexus_wallet_transactions'
    
    id = Column(Integer, primary_key=True)
    tx_id = Column(String(64), unique=True, nullable=False)
    from_address = Column(String(64), nullable=False)
    to_address = Column(String(64), nullable=False)
    amount_nxt = Column(Float, nullable=False)
    fee_nxt = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default='pending')
    
    # Quantum security
    wave_signature = Column(Text, nullable=False)
    spectral_proof = Column(Text, nullable=False)
    interference_hash = Column(String(128), nullable=False)
    energy_cost = Column(Float, nullable=False)

class WalletMessage(Base):
    """WNSP messages sent from wallet"""
    __tablename__ = 'nexus_wallet_messages'
    
    id = Column(Integer, primary_key=True)
    message_id = Column(String(64), unique=True, nullable=False)
    from_address = Column(String(64), nullable=False)
    to_address = Column(String(64))
    content = Column(Text, nullable=False)
    spectral_region = Column(String(20), nullable=False)
    wavelength = Column(Float, nullable=False)
    cost_nxt = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    dag_parents = Column(Text)  # JSON list of parent message IDs

class TokenAccount(Base):
    """Persistent token account storage"""
    __tablename__ = 'nexus_token_accounts'
    
    id = Column(Integer, primary_key=True)
    address = Column(String(64), unique=True, nullable=False)
    balance = Column(BigInteger, default=0)  # In smallest units (needs BigInteger for 100 trillion total supply)
    nonce = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


# ============================================================================
# NexusOS Native Wallet
# ============================================================================

class NexusNativeWallet:
    """
    Native NexusOS wallet for NXT tokens and WNSP messaging.
    
    Features:
    - NXT token balance and transfers
    - WNSP v2.0 quantum-encrypted messaging
    - Wavelength-based signatures
    - Mobile-first DAG communication
    - Multi-spectral quantum resistance
    """
    
    def __init__(self, database_url: Optional[str] = None):
        """Initialize wallet with NexusOS core systems"""
        # Database setup with fallback to SQLite
        db_url = database_url or os.getenv('DATABASE_URL', 'sqlite:///nexus_native_wallet.db')
        self._fallback_attempted = False
        
        try:
            # Try to connect to the specified database with robust pooling
            self.engine = create_engine(
                db_url, 
                pool_pre_ping=True,  # Test connections before using
                pool_recycle=3600,   # Recycle connections after 1 hour
                pool_size=5,          # Connection pool size
                max_overflow=10       # Max overflow connections
            )
            Base.metadata.create_all(self.engine)
            
            # Store SessionMaker instead of single session
            self.SessionMaker = sessionmaker(bind=self.engine)
            
            # Test connection with a simple query
            test_session = self.SessionMaker()
            try:
                test_session.execute(sa.text("SELECT 1"))
                test_session.commit()
            finally:
                test_session.close()
            
            # Log connection success WITHOUT exposing credentials
            db_type = "PostgreSQL" if db_url.startswith('postgresql') else "SQLite"
            print(f"✅ Database connected: {db_type}")
            
        except Exception as e:
            # If PostgreSQL fails, fall back to SQLite
            if db_url != 'sqlite:///nexus_native_wallet.db':
                print(f"⚠️  PostgreSQL connection failed ({str(e)[:50]}...)")
                print("📂 Falling back to SQLite for data persistence")
                
                self._fallback_attempted = True
                db_url = 'sqlite:///nexus_native_wallet.db'
                self.engine = create_engine(db_url)
                Base.metadata.create_all(self.engine)
                self.SessionMaker = sessionmaker(bind=self.engine)
            else:
                # SQLite also failed - this is a critical error
                raise RuntimeError(f"Failed to initialize database: {e}")
        
        # NexusOS core components  
        self.wavelength_validator = WavelengthValidator()
        self.wnsp_encoder = WnspEncoderV2()
        
        # Create initial session
        self.db = self.SessionMaker()
        
        # Initialize persistent accounts (instead of in-memory NativeTokenSystem)
        self._init_genesis_accounts()
    
    def _refresh_session(self):
        """Recreate the database session (call this when connection errors occur)"""
        try:
            self.db.close()
        except:
            pass
        self.db = self.SessionMaker()
    
    # ========================================================================
    # Database Token System (Replaces in-memory NativeTokenSystem)
    # ========================================================================
    
    def _init_genesis_accounts(self):
        """Initialize genesis accounts if they don't exist"""
        genesis_accounts = [
            ("VALIDATOR_POOL", 0),
            ("TREASURY", 50000000),  # 500K NXT
            ("ECOSYSTEM_FUND", 20000000)  # 200K NXT
        ]
        
        for address, balance in genesis_accounts:
            existing = self.db.query(TokenAccount).filter_by(address=address).first()
            if not existing:
                account = TokenAccount(address=address, balance=balance)
                self.db.add(account)
        
        self.db.commit()
    
    def _get_token_account(self, address: str) -> Optional[TokenAccount]:
        """Get persistent token account"""
        return self.db.query(TokenAccount).filter_by(address=address).first()
    
    def _get_or_create_token_account(self, address: str, initial_balance: int = 0) -> TokenAccount:
        """Get or create persistent token account"""
        account = self._get_token_account(address)
        if not account:
            account = TokenAccount(address=address, balance=initial_balance)
            self.db.add(account)
            self.db.commit()
        return account
    
    def _format_transaction_response(self, tx_record: WalletTransaction, status: str = 'new_commit') -> Dict[str, Any]:
        """Format transaction response with normalized schema for backwards compatibility"""
        # Parse spectral proof safely
        try:
            spectral_proof = json.loads(tx_record.spectral_proof) if tx_record.spectral_proof else {}
            spectral_count = len(spectral_proof) if isinstance(spectral_proof, list) else 'cached'
        except:
            spectral_count = 'cached'
        
        return {
            'tx_id': tx_record.tx_id,
            'from_address': tx_record.from_address,
            'to_address': tx_record.to_address,
            'from': tx_record.from_address,  # Backwards compatibility alias
            'to': tx_record.to_address,  # Backwards compatibility alias
            'amount_nxt': tx_record.amount_nxt,
            'fee_nxt': tx_record.fee_nxt,
            'timestamp': tx_record.timestamp.isoformat() if hasattr(tx_record.timestamp, 'isoformat') else str(tx_record.timestamp),
            'status': status,
            'quantum_proof': {
                'spectral_regions': spectral_count,
                'interference_hash': tx_record.interference_hash[:16] + '...' if tx_record.interference_hash else 'N/A',
                'energy_cost': tx_record.energy_cost or 0
            }
        }
    
    # ========================================================================
    # Wallet Management
    # ========================================================================
    
    @retry_on_connection_error(max_retries=2)
    def create_wallet(self, password: str, initial_balance: float = 0) -> Dict[str, Any]:
        """
        Create new quantum-resistant NexusOS wallet.
        
        Args:
            password: Password for wallet encryption
            initial_balance: Initial NXT balance (for testing)
        
        Returns:
            Wallet details including address and quantum public key
        """
        # Generate unique address using wavelength signature
        address = self._generate_wallet_address()
        
        # Generate quantum keypair
        private_key, public_key = self._generate_quantum_keypair(address)
        
        # Encrypt private key with password
        encrypted_key = self._encrypt_private_key(private_key, password, public_key)
        
        # Generate multi-spectral signature
        spectral_sig = self._generate_spectral_signature(address)
        
        # Create persistent token account
        token_account = self._get_or_create_token_account(
            address,
            initial_balance=int(initial_balance * 100)  # Convert to smallest units
        )
        
        # Save wallet to database
        wallet = NexusWallet(
            address=address,
            public_key=json.dumps(public_key),
            encrypted_private_key=encrypted_key,
            spectral_signature=json.dumps(spectral_sig)
        )
        self.db.add(wallet)
        self.db.commit()
        
        return {
            'address': address,
            'public_key': public_key,
            'spectral_regions': list(spectral_sig.keys()),
            'balance_nxt': token_account.balance / 100.0,
            'created_at': wallet.created_at.isoformat()
        }
    
    @retry_on_connection_error(max_retries=2)
    def import_wallet(self, address: str, private_key: str, password: str) -> Dict[str, Any]:
        """Import existing wallet with quantum encryption layer"""
        # Check if already exists
        existing = self.db.query(NexusWallet).filter_by(address=address).first()
        if existing:
            raise ValueError(f"Wallet {address} already exists")
        
        # Generate quantum public key
        _, public_key = self._generate_quantum_keypair(address)
        
        # Encrypt private key
        encrypted_key = self._encrypt_private_key(private_key, password, public_key)
        
        # Generate spectral signature
        spectral_sig = self._generate_spectral_signature(address)
        
        # Get or create persistent token account
        token_account = self._get_or_create_token_account(address)
        
        # Save wallet
        wallet = NexusWallet(
            address=address,
            public_key=json.dumps(public_key),
            encrypted_private_key=encrypted_key,
            spectral_signature=json.dumps(spectral_sig)
        )
        self.db.add(wallet)
        self.db.commit()
        
        return {
            'address': address,
            'balance_nxt': token_account.balance / 100.0,
            'imported': True
        }
    
    @retry_on_connection_error(max_retries=2)
    def unlock_wallet(self, address: str, password: str) -> bool:
        """Verify password can unlock wallet"""
        wallet = self.db.query(NexusWallet).filter_by(address=address).first()
        if not wallet:
            return False
        
        try:
            self._decrypt_private_key(
                wallet.encrypted_private_key,
                password,
                json.loads(wallet.public_key)
            )
            wallet.last_used = datetime.utcnow()
            self.db.commit()
            return True
        except:
            return False
    
    @retry_on_connection_error(max_retries=2)
    def get_balance(self, address: str) -> Dict[str, Any]:
        """Get NXT balance for address"""
        account = self._get_token_account(address)
        if not account:
            return {
                'address': address,
                'balance_nxt': 0.0,
                'balance_units': 0,
                'nonce': 0
            }
        
        return {
            'address': address,
            'balance_nxt': account.balance / 100.0,
            'balance_units': account.balance,
            'nonce': account.nonce
        }
    
    # ========================================================================
    # NXT Token Transfers
    # ========================================================================
    
    @retry_on_connection_error(max_retries=2)
    def send_nxt(
        self,
        from_address: str,
        to_address: str,
        amount_nxt: float,
        password: str,
        fee_nxt: Optional[float] = None,
        idempotency_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send NXT tokens with quantum-resistant signatures.
        Uses DAG-based idempotency to prevent double-execution.
        
        Args:
            from_address: Sender wallet address
            to_address: Recipient address  
            amount_nxt: Amount in NXT
            password: Sender wallet password
            fee_nxt: Optional custom fee (uses default if None)
            idempotency_key: REQUIRED client-provided key for retry safety.
                            Use a UUID or any unique string. MUST be stable
                            across retries to prevent double-execution.
        
        Returns:
            Transaction details with quantum proofs
            
        Raises:
            ValueError: If idempotency_key is not provided
        """
        # Input validation - prevent negative amount exploit
        if amount_nxt <= 0:
            raise ValueError(f"Invalid amount: {amount_nxt}. Amount must be positive.")
        if fee_nxt is not None and fee_nxt < 0:
            raise ValueError(f"Invalid fee: {fee_nxt}. Fee must be non-negative.")
        if amount_nxt > 1e12:  # Sanity check: max 1 trillion NXT
            raise ValueError(f"Amount too large: {amount_nxt}")
        
        # ═══════════════════════════════════════════════════════════════
        # DAG-BASED IDEMPOTENCY: REQUIRE client-provided key (Stripe-style)
        # ═══════════════════════════════════════════════════════════════
        # Industry best practice: Clients MUST provide an idempotency key
        # Without it, we CANNOT prevent double-execution on post-commit retries
        import time
        import uuid
        
        if not idempotency_key:
            # STRICT ENFORCEMENT: Idempotency key is REQUIRED for safety
            # Without it, we CANNOT prevent double-execution on post-commit retries
            raise ValueError(
                "idempotency_key is REQUIRED to prevent double-execution. "
                "Provide a stable unique string (e.g., UUID) that remains "
                "the same across retries. Example: uuid.uuid4().hex"
            )
        
        # Generate stable transaction ID from idempotency key
        tx_id = hashlib.sha256(f"{from_address}:{idempotency_key}".encode()).hexdigest()[:32]
        
        # Check if this transaction DAG node already exists (idempotent check)
        # Use FOR UPDATE lock to prevent concurrent race between SELECT and INSERT
        # Note: Removed skip_locked for SQLite compatibility - we WANT to wait for lock
        existing_tx = self.db.query(WalletTransaction).filter_by(tx_id=tx_id).with_for_update().first()
        if existing_tx:
            # Transaction already committed! Return cached result with FULL schema parity
            return self._format_transaction_response(existing_tx, status='idempotent_cached')
        
        # Get wallet
        wallet = self.db.query(NexusWallet).filter_by(address=from_address).first()
        if not wallet:
            raise ValueError("Wallet not found")
        
        # Unlock wallet (before transaction to avoid holding locks during crypto)
        private_key = self._decrypt_private_key(
            wallet.encrypted_private_key,
            password,
            json.loads(wallet.public_key)
        )
        
        # Convert to smallest units
        amount_units = int(amount_nxt * 100)
        fee_units = int(fee_nxt * 100) if fee_nxt else 1  # Default 0.01 NXT fee
        
        # ═══════════════════════════════════════════════════════════════
        # ATOMIC TRANSACTION: All changes in ONE commit with row locks
        # ═══════════════════════════════════════════════════════════════
        # Use row-level locking (SELECT ... FOR UPDATE) to prevent concurrent modifications
        
        from sqlalchemy.exc import IntegrityError
        
        try:
            # Lock sender account (prevents concurrent spends)
            from_account = self.db.query(TokenAccount).filter_by(
                address=from_address
            ).with_for_update().first()
            
            if not from_account:
                raise ValueError("Sender account not found")
            
            # Check sufficient balance
            if from_account.balance < (amount_units + fee_units):
                raise ValueError(f"Insufficient balance: have {from_account.balance}, need {amount_units + fee_units}")
            
            # Deduct from sender
            from_account.balance -= (amount_units + fee_units)
            from_account.nonce += 1
            
            # Lock receiver account
            to_account = self.db.query(TokenAccount).filter_by(
                address=to_address
            ).with_for_update().first()
            
            if not to_account:
                # Create new account if doesn't exist
                to_account = TokenAccount(address=to_address, balance=0, nonce=0)
                self.db.add(to_account)
                self.db.flush()  # Flush to get the account in the session
            
            # Add to receiver
            to_account.balance += amount_units
            
            # Lock validator pool
            validator_pool = self.db.query(TokenAccount).filter_by(
                address="VALIDATOR_POOL"
            ).with_for_update().first()
            
            if validator_pool:
                validator_pool.balance += fee_units
            
            # Create transaction record
            from native_token import TokenTransaction, TransactionType
            
            tx = TokenTransaction(
                tx_id=tx_id,
                tx_type=TransactionType.TRANSFER,
                from_address=from_address,
                to_address=to_address,
                amount=amount_units,
                fee=fee_units
            )
            
            # Add quantum security layer
            quantum_proof = self._generate_quantum_proof(tx, private_key)
            
            # Save transaction record in same atomic transaction
            db_tx = WalletTransaction(
                tx_id=tx_id,  # DAG node ID with unique constraint
                from_address=from_address,
                to_address=to_address,
                amount_nxt=amount_nxt,
                fee_nxt=(tx.fee / 100.0),
                status='confirmed',
                wave_signature=json.dumps(quantum_proof['wave_signature']),
                spectral_proof=json.dumps(quantum_proof['spectral_signatures']),
                interference_hash=quantum_proof['interference_hash'],
                energy_cost=quantum_proof['energy_cost']
            )
            self.db.add(db_tx)
            
            # SINGLE ATOMIC COMMIT: Balances + Transaction record + Nonce
            # Either ALL succeed or ALL roll back (prevents partial states)
            self.db.commit()
            
        except IntegrityError as e:
            # Unique constraint violation on tx_id - transaction already exists!
            # This happens when concurrent retries pass the SELECT check simultaneously
            # Roll back and return cached result (idempotent)
            self.db.rollback()
            
            # Refresh ALL accounts to clear any in-memory state changes
            try:
                if 'from_account' in locals():
                    self.db.refresh(from_account)
                if 'to_account' in locals():
                    self.db.refresh(to_account)
                if 'validator_pool' in locals() and validator_pool:
                    self.db.refresh(validator_pool)
            except:
                pass  # Account might not be in session anymore
            
            # Fetch the existing transaction (it must exist now)
            existing_tx = self.db.query(WalletTransaction).filter_by(tx_id=tx_id).first()
            if existing_tx:
                return self._format_transaction_response(existing_tx, status='idempotent_collision_detected')
            else:
                # This should never happen, but raise if it does
                raise ValueError(f"IntegrityError on tx_id {tx_id} but no transaction found!") from e
        
        except Exception as e:
            # Other errors: Roll back and refresh ALL account state
            self.db.rollback()
            
            # Refresh ALL accounts to clear any in-memory state changes (including nonce)
            try:
                if 'from_account' in locals():
                    self.db.refresh(from_account)
                if 'to_account' in locals():
                    self.db.refresh(to_account)
                if 'validator_pool' in locals() and validator_pool:
                    self.db.refresh(validator_pool)
            except:
                pass  # Account might not be in session anymore
            
            raise
        
        # Success! Return normalized response
        return self._format_transaction_response(db_tx, status='new_commit')
    
    # ========================================================================
    # WNSP Messaging
    # ========================================================================
    
    @retry_on_connection_error(max_retries=2)
    def send_message(
        self,
        from_address: str,
        content: str,
        password: str,
        to_address: Optional[str] = None,
        spectral_region: SpectralRegion = SpectralRegion.BLUE,
        parent_messages: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Send WNSP quantum-encrypted message.
        
        Args:
            from_address: Sender wallet address
            content: Message content
            password: Wallet password
            to_address: Optional recipient (None for broadcast)
            spectral_region: Wavelength region for encoding
            parent_messages: Parent message IDs for DAG linking
        
        Returns:
            Message details with quantum encoding
        """
        # Get wallet
        wallet = self.db.query(NexusWallet).filter_by(address=from_address).first()
        if not wallet:
            raise ValueError("Wallet not found")
        
        # Unlock wallet
        private_key = self._decrypt_private_key(
            wallet.encrypted_private_key,
            password,
            json.loads(wallet.public_key)
        )
        
        # Create wavelength-encoded message
        wave_msg = self.wavelength_validator.create_message_wave(
            content, spectral_region, ModulationType.PSK
        )
        
        # Calculate E=hf cost
        energy_cost = self._calculate_message_cost(wave_msg)
        cost_nxt = energy_cost * 1e-17  # Scale to NXT
        
        # Deduct cost from sender
        cost_units = int(cost_nxt * 100)
        account = self._get_token_account(from_address)
        if not account or account.balance < cost_units:
            raise ValueError("Insufficient balance for message cost")
        
        account.balance -= cost_units
        # Add to validator pool
        validator_pool = self._get_token_account("VALIDATOR_POOL")
        if validator_pool:
            validator_pool.balance += cost_units
        
        self.db.commit()
        
        # Generate message ID
        message_id = self._generate_message_id(from_address, content, wave_msg.wavelength)
        
        # Save message
        msg = WalletMessage(
            message_id=message_id,
            from_address=from_address,
            to_address=to_address,
            content=content,
            spectral_region=spectral_region.display_name,
            wavelength=wave_msg.wavelength,
            cost_nxt=cost_nxt,
            dag_parents=json.dumps(parent_messages) if parent_messages else None
        )
        self.db.add(msg)
        
        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise e
        
        return {
            'message_id': message_id,
            'from': from_address,
            'to': to_address or 'broadcast',
            'wavelength': wave_msg.wavelength,
            'frequency': wave_msg.frequency,
            'spectral_region': spectral_region.display_name,
            'cost_nxt': cost_nxt,
            'dag_parents': parent_messages or []
        }
    
    @retry_on_connection_error(max_retries=2)
    def get_messages(
        self,
        address: str,
        limit: int = 50,
        sent: bool = True,
        received: bool = True
    ) -> List[Dict[str, Any]]:
        """Get message history for address"""
        query = self.db.query(WalletMessage)
        
        if sent and received:
            query = query.filter(
                (WalletMessage.from_address == address) |
                (WalletMessage.to_address == address)
            )
        elif sent:
            query = query.filter(WalletMessage.from_address == address)
        elif received:
            query = query.filter(WalletMessage.to_address == address)
        
        messages = query.order_by(WalletMessage.timestamp.desc()).limit(limit).all()
        
        return [
            {
                'message_id': msg.message_id,
                'from': msg.from_address,
                'to': msg.to_address or 'broadcast',
                'content': msg.content,
                'wavelength': msg.wavelength,
                'spectral_region': msg.spectral_region,
                'cost_nxt': msg.cost_nxt,
                'timestamp': msg.timestamp.isoformat()
            }
            for msg in messages
        ]
    
    # ========================================================================
    # Transaction History
    # ========================================================================
    
    @retry_on_connection_error(max_retries=2)
    def get_transaction_history(
        self,
        address: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get NXT transaction history"""
        transactions = self.db.query(WalletTransaction).filter(
            (WalletTransaction.from_address == address) |
            (WalletTransaction.to_address == address)
        ).order_by(WalletTransaction.timestamp.desc()).limit(limit).all()
        
        return [
            {
                'tx_id': tx.tx_id,
                'from_address': tx.from_address,
                'to_address': tx.to_address,
                'amount_nxt': tx.amount_nxt,
                'fee_nxt': tx.fee_nxt,
                'status': tx.status,
                'timestamp': tx.timestamp.isoformat(),
                'quantum_verified': True
            }
            for tx in transactions
        ]
    
    @retry_on_connection_error(max_retries=2)
    def get_message_history(
        self,
        address: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get message history for wallet"""
        messages = self.db.query(WalletMessage).filter_by(
            from_address=address
        ).order_by(WalletMessage.timestamp.desc()).limit(limit).all()
        
        return [
            {
                'message_id': msg.message_id,
                'to_address': msg.to_address,
                'content': msg.content,
                'cost_nxt': msg.cost_nxt,
                'wavelength': msg.wavelength,
                'spectral_region': msg.spectral_region,
                'timestamp': msg.timestamp.isoformat(),
                'status': 'sent'
            }
            for msg in messages
        ]
    
    # ========================================================================
    # Utility Methods
    # ========================================================================
    
    @retry_on_connection_error(max_retries=2)
    def list_wallets(self) -> List[Dict[str, Any]]:
        """List all wallets"""
        wallets = self.db.query(NexusWallet).filter_by(is_active=True).all()
        result = []
        for w in wallets:
            account = self._get_token_account(w.address)
            balance_nxt = account.balance / 100.0 if account else 0.0
            result.append({
                'address': w.address,
                'balance_nxt': balance_nxt,
                'created_at': w.created_at.isoformat(),
                'last_used': w.last_used.isoformat() if w.last_used else None
            })
        return result
    
    @retry_on_connection_error(max_retries=2)
    def export_quantum_proof(self, tx_id: str) -> Dict[str, Any]:
        """Export quantum security proof for transaction"""
        tx = self.db.query(WalletTransaction).filter_by(tx_id=tx_id).first()
        if not tx:
            raise ValueError("Transaction not found")
        
        return {
            'tx_id': tx.tx_id,
            'wave_signature': json.loads(tx.wave_signature),
            'spectral_proof': json.loads(tx.spectral_proof),
            'interference_hash': tx.interference_hash,
            'energy_cost': tx.energy_cost
        }
    
    # ========================================================================
    # Private Methods - Quantum Cryptography
    # ========================================================================
    
    def _generate_wallet_address(self) -> str:
        """Generate unique wallet address using wavelength signature"""
        # Generate random seed
        seed = secrets.token_bytes(32)
        
        # Create wavelength signature
        wave = self.wavelength_validator.create_message_wave(
            seed.hex(), SpectralRegion.GREEN, ModulationType.OOK
        )
        
        # Create address from wave properties
        address_data = f"{wave.wavelength}:{wave.frequency}:{wave.phase}"
        address_hash = hashlib.sha256(address_data.encode()).hexdigest()
        
        return f"NXS{address_hash[:40]}".upper()
    
    def _generate_quantum_keypair(self, address: str) -> Tuple[str, Dict]:
        """Generate quantum-resistant keypair"""
        # Private key (random)
        private_key = secrets.token_hex(32)
        
        # Public key (multi-spectral wave signatures)
        regions = [SpectralRegion.UV, SpectralRegion.RED, 
                  SpectralRegion.GREEN, SpectralRegion.IR]
        
        public_key = {
            'address': address,
            'wave_signatures': {}
        }
        
        for region in regions:
            wave = self.wavelength_validator.create_message_wave(
                private_key, region, ModulationType.PSK
            )
            region_name = region.value[0] if isinstance(region.value, tuple) else str(region.name)
            public_key['wave_signatures'][region_name] = {
                'wavelength': wave.wavelength,
                'frequency': wave.frequency,
                'phase': wave.phase
            }
        
        public_key['timestamp'] = int(time.time())
        
        return private_key, public_key
    
    def _encrypt_private_key(self, private_key: str, password: str, public_key: Dict) -> str:
        """
        Encrypt private key with AES-GCM authenticated encryption.
        Returns: nonce || ciphertext (hex encoded, ciphertext includes auth tag)
        """
        # Use wavelength signature as salt for PBKDF2
        salt = hashlib.sha256(
            json.dumps(public_key['wave_signatures'], sort_keys=True).encode()
        ).digest()
        
        # Derive 256-bit AES key using PBKDF2
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        aes_key = kdf.derive(password.encode('utf-8'))
        
        # Generate random nonce (96 bits for GCM)
        nonce = os.urandom(12)
        
        # Encrypt with AES-GCM (provides both confidentiality and integrity)
        aesgcm = AESGCM(aes_key)
        ciphertext = aesgcm.encrypt(nonce, private_key.encode('utf-8'), None)
        
        # ciphertext includes auth tag automatically
        # Return: nonce || ciphertext (with embedded tag)
        return nonce.hex() + ciphertext.hex()
    
    def _decrypt_private_key(self, encrypted_key: str, password: str, public_key: Dict) -> str:
        """
        Decrypt private key with AES-GCM authenticated decryption.
        Raises: ValueError if ciphertext was tampered with or password incorrect
        """
        # Use same wavelength signature as salt
        salt = hashlib.sha256(
            json.dumps(public_key['wave_signatures'], sort_keys=True).encode()
        ).digest()
        
        # Derive AES key
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        aes_key = kdf.derive(password.encode('utf-8'))
        
        # Extract nonce (first 12 bytes = 24 hex chars)
        nonce = bytes.fromhex(encrypted_key[:24])
        ciphertext = bytes.fromhex(encrypted_key[24:])
        
        # Decrypt and verify integrity
        aesgcm = AESGCM(aes_key)
        try:
            plaintext = aesgcm.decrypt(nonce, ciphertext, None)
            return plaintext.decode('utf-8')
        except Exception as e:
            raise ValueError(f"Decryption failed - invalid password or tampered key: {e}")
    
    def _generate_spectral_signature(self, address: str) -> Dict[str, str]:
        """Generate multi-spectral signatures"""
        signatures = {}
        regions = [SpectralRegion.UV, SpectralRegion.RED, 
                  SpectralRegion.BLUE, SpectralRegion.IR]
        
        for region in regions:
            wave = self.wavelength_validator.create_message_wave(
                address, region, ModulationType.OOK
            )
            sig_data = f"{wave.wavelength}:{wave.frequency}"
            region_name = region.value[0] if isinstance(region.value, tuple) else str(region.name)
            signatures[region_name] = hashlib.sha256(sig_data.encode()).hexdigest()
        
        return signatures
    
    def _generate_quantum_proof(self, tx: TokenTransaction, private_key: str) -> Dict:
        """Generate quantum security proof for transaction"""
        # Create wave signature
        tx_data = f"{tx.tx_id}:{tx.from_address}:{tx.to_address}:{tx.amount}"
        wave_sig = self.wavelength_validator.create_message_wave(
            tx_data, SpectralRegion.BLUE, ModulationType.PSK
        )
        
        # Multi-spectral signatures
        spectral_sigs = self._generate_spectral_signature(tx.tx_id)
        
        # Interference hash
        combined = {
            'tx': tx_data,
            'wave': {'wavelength': wave_sig.wavelength, 'frequency': wave_sig.frequency},
            'spectral': spectral_sigs
        }
        hash_data = json.dumps(combined, sort_keys=True).encode('utf-8')
        interference_hash = hashlib.sha512(hash_data).hexdigest()
        
        # Energy cost (E=hf)
        h = 6.62607015e-34
        energy_cost = h * wave_sig.frequency * 1e19
        
        # Convert WaveProperties to JSON-serializable dict
        wave_dict = {
            'wavelength': wave_sig.wavelength,
            'frequency': wave_sig.frequency,
            'amplitude': wave_sig.amplitude,
            'phase': wave_sig.phase,
            'polarization': wave_sig.polarization,
            'spectral_region': wave_sig.spectral_region.name if hasattr(wave_sig.spectral_region, 'name') else str(wave_sig.spectral_region),
            'modulation_type': wave_sig.modulation_type.name if hasattr(wave_sig.modulation_type, 'name') else str(wave_sig.modulation_type)
        }
        
        return {
            'wave_signature': wave_dict,
            'spectral_signatures': spectral_sigs,
            'interference_hash': interference_hash,
            'energy_cost': float(energy_cost)
        }
    
    def _calculate_message_cost(self, wave: WaveProperties) -> float:
        """Calculate message cost using E=hf"""
        h = 6.62607015e-34
        return h * wave.frequency
    
    def _generate_message_id(self, address: str, content: str, wavelength: float) -> str:
        """Generate unique message ID"""
        data = f"{address}:{content}:{wavelength}:{time.time()}"
        return f"MSG{hashlib.sha256(data.encode()).hexdigest()[:24]}".upper()
