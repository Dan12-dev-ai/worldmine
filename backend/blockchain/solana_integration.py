"""
Solana Integration for DEDAN 2.0
High-performance Solana blockchain integration
"""

import asyncio
import base58
from solana.keypair import Keypair
from solana.publickey import PublicKey
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed
from solana.rpc.types import TxOpts
from solana.transaction import Transaction, TransactionInstruction
from anchorpy import Program, Provider, Wallet, Context
from typing import Dict, List, Optional, Any, Tuple
import logging
import time
import json
from datetime import datetime
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SolanaTransactionMetrics:
    """Solana transaction metrics"""
    signature: str
    slot: int
    block_time: int
    compute_units_consumed: int
    fee_lamports: int
    confirmation_time_ms: float
    success: bool
    error_message: Optional[str] = None

class SolanaIntegration:
    """High-performance Solana integration"""
    
    def __init__(self, rpc_url: str = "https://api.mainnet-beta.solana.com"):
        self.rpc_url = rpc_url
        self.client = None
        self.wallet = None
        self.program = None
        self.transaction_history = []
        self.connection_pool = []
        self.max_connections = 10
        
    async def initialize(self, private_key: str = None):
        """Initialize Solana connection"""
        try:
            # Create connection pool
            for i in range(self.max_connections):
                client = AsyncClient(self.rpc_url)
                self.connection_pool.append(client)
            
            self.client = self.connection_pool[0]
            
            # Initialize wallet if private key provided
            if private_key:
                self.wallet = Wallet(Keypair.from_secret_key(base58.b58decode(private_key)))
            
            logger.info(f"Initialized Solana connection to {self.rpc_url}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Solana: {e}")
            raise
    
    async def execute_transaction(
        self, 
        instructions: List[TransactionInstruction],
        signers: List = None,
        max_retries: int = 3
    ) -> Tuple[str, SolanaTransactionMetrics]:
        """Execute transaction with high performance"""
        start_time = time.time()
        
        for attempt in range(max_retries):
            try:
                # Get connection from pool
                client = self._get_connection()
                
                # Create transaction
                transaction = Transaction()
                for instruction in instructions:
                    transaction.add(instruction)
                
                # Set recent blockhash
                recent_blockhash = await client.get_latest_blockhash(Confirmed)
                transaction.recent_blockhash = recent_blockhash.value.blockhash
                
                # Sign transaction
                if self.wallet:
                    transaction.sign(self.wallet.keypair)
                if signers:
                    for signer in signers:
                        transaction.sign(signer)
                
                # Send transaction
                signature = await client.send_transaction(
                    transaction,
                    opts=TxOpts(
                        skip_preflight=False,
                        preflight_commitment=Confirmed,
                        max_retries=max_retries
                    )
                )
                
                # Wait for confirmation
                confirmation = await self._wait_for_confirmation(signature, timeout_ms=5000)
                
                execution_time = (time.time() - start_time) * 1000
                
                # Get transaction details
                tx_details = await client.get_transaction(
                    signature,
                    encoding="json",
                    commitment=Confirmed
                )
                
                metrics = SolanaTransactionMetrics(
                    signature=signature,
                    slot=tx_details.value.slot,
                    block_time=tx_details.value.block_time,
                    compute_units_consumed=tx_details.value.meta.compute_units_consumed,
                    fee_lamports=tx_details.value.meta.fee,
                    confirmation_time_ms=execution_time,
                    success=True
                )
                
                self.transaction_history.append(metrics)
                logger.info(f"Transaction {signature} confirmed in {execution_time:.2f}ms")
                
                return signature, metrics
                
            except Exception as e:
                logger.warning(f"Transaction attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    execution_time = (time.time() - start_time) * 1000
                    metrics = SolanaTransactionMetrics(
                        signature="",
                        slot=0,
                        block_time=0,
                        compute_units_consumed=0,
                        fee_lamports=0,
                        confirmation_time_ms=execution_time,
                        success=False,
                        error_message=str(e)
                    )
                    self.transaction_history.append(metrics)
                    raise e
                
                await asyncio.sleep(0.1 * (attempt + 1))  # Exponential backoff
    
    async def _wait_for_confirmation(self, signature: str, timeout_ms: float) -> Dict[str, Any]:
        """Wait for transaction confirmation"""
        timeout_seconds = timeout_ms / 1000
        start_time = time.time()
        
        while time.time() - start_time < timeout_seconds:
            try:
                result = await self.client.get_signature_statuses(
                    [signature],
                    commitment=Confirmed
                )
                
                if result.value[0]:
                    if result.value[0].confirmation_status == 'confirmed':
                        return result.value[0]
                    elif result.value[0].err:
                        raise Exception(f"Transaction failed: {result.value[0].err}")
                
                await asyncio.sleep(0.01)  # Check every 10ms
                
            except Exception as e:
                if "not found" not in str(e).lower():
                    raise e
        
        raise TimeoutError(f"Transaction {signature} not confirmed within {timeout_ms}ms")
    
    def _get_connection(self) -> AsyncClient:
        """Get connection from pool"""
        # Simple round-robin for now
        return self.connection_pool[len(self.transaction_history) % len(self.connection_pool)]
    
    async def get_account_balance(self, public_key: str) -> Tuple[float, int]:
        """Get account balance in SOL and lamports"""
        try:
            pubkey = PublicKey(public_key)
            balance = await self.client.get_balance(pubkey, commitment=Confirmed)
            
            lamports = balance.value
            sol_balance = lamports / 1_000_000_000  # Convert to SOL
            
            return sol_balance, lamports
            
        except Exception as e:
            logger.error(f"Error getting balance for {public_key}: {e}")
            return 0.0, 0
    
    async def get_program_accounts(self, program_id: str) -> List[Dict[str, Any]]:
        """Get all accounts for a program"""
        try:
            accounts = await self.client.get_program_accounts(
                PublicKey(program_id),
                commitment=Confirmed
            )
            
            return [
                {
                    'pubkey': str(account.pubkey),
                    'account': account.account,
                    'lamports': account.account.lamports,
                    'owner': str(account.account.owner)
                }
                for account in accounts.value
            ]
            
        except Exception as e:
            logger.error(f"Error getting program accounts: {e}")
            return []
    
    async def get_transaction_history(
        self, 
        address: str, 
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get transaction history for an address"""
        try:
            signatures = await self.client.get_signatures_for_address(
                PublicKey(address),
                limit=limit,
                commitment=Confirmed
            )
            
            transactions = []
            for sig_info in signatures.value:
                try:
                    tx = await self.client.get_transaction(
                        sig_info.signature,
                        encoding="json",
                        commitment=Confirmed
                    )
                    
                    transactions.append({
                        'signature': sig_info.signature,
                        'slot': tx.value.slot,
                        'block_time': tx.value.block_time,
                        'fee': tx.value.meta.fee,
                        'status': tx.value.meta.err is None,
                        'compute_units': tx.value.meta.compute_units_consumed
                    })
                    
                except Exception as e:
                    logger.warning(f"Error fetching transaction {sig_info.signature}: {e}")
                    continue
            
            return transactions
            
        except Exception as e:
            logger.error(f"Error getting transaction history: {e}")
            return []
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        if not self.transaction_history:
            return {"message": "No transactions executed yet"}
        
        successful_tx = [tx for tx in self.transaction_history if tx.success]
        failed_tx = [tx for tx in self.transaction_history if not tx.success]
        
        metrics = {
            'total_transactions': len(self.transaction_history),
            'successful_transactions': len(successful_tx),
            'failed_transactions': len(failed_tx),
            'success_rate': len(successful_tx) / len(self.transaction_history) * 100,
            'average_confirmation_time_ms': sum(tx.confirmation_time_ms for tx in successful_tx) / len(successful_tx) if successful_tx else 0,
            'min_confirmation_time_ms': min(tx.confirmation_time_ms for tx in successful_tx) if successful_tx else 0,
            'max_confirmation_time_ms': max(tx.confirmation_time_ms for tx in successful_tx) if successful_tx else 0,
            'average_compute_units': sum(tx.compute_units_consumed for tx in successful_tx) / len(successful_tx) if successful_tx else 0,
            'average_fee_lamports': sum(tx.fee_lamports for tx in successful_tx) / len(successful_tx) if successful_tx else 0,
            'total_fees_lamports': sum(tx.fee_lamports for tx in successful_tx),
            'transactions_under_100ms': len([tx for tx in successful_tx if tx.confirmation_time_ms < 100]),
            'transactions_under_500ms': len([tx for tx in successful_tx if tx.confirmation_time_ms < 500]),
            'transactions_under_1000ms': len([tx for tx in successful_tx if tx.confirmation_time_ms < 1000])
        }
        
        return metrics

# Usage example
async def main():
    """Main execution function"""
    solana = SolanaIntegration()
    await solana.initialize()
    
    # Get account balance
    balance, lamports = await solana.get_account_balance("11111111111111111111111111111112")
    print(f"System program balance: {balance} SOL ({lamports} lamports)")
    
    # Get performance metrics
    metrics = solana.get_performance_metrics()
    print(f"Performance metrics: {json.dumps(metrics, indent=2)}")

if __name__ == "__main__":
    asyncio.run(main())
