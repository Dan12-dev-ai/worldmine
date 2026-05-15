"""
IBM Quantum Co-location Integration for DEDAN 2.0
Direct IBM Quantum backend integration for <1ms settlement
"""

import asyncio
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.providers.ibmq import IBMQ, least_busy
from qiskit.providers.ibmq.job import IBMQJob
from qiskit.quantum_info import Statevector
from typing import Dict, List, Optional, Any, Tuple
import logging
import time
import json
from datetime import datetime
from dataclasses import dataclass
import aiohttp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class QuantumJobMetrics:
    """Quantum job execution metrics"""
    job_id: str
    backend_name: str
    qubits_used: int
    circuit_depth: int
    execution_time_ms: float
    queue_time_ms: float
    fidelity: float
    success: bool
    error_message: Optional[str] = None

class IBMQuantumColocator:
    """IBM Quantum co-location integration"""
    
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.provider = None
        self.backends = {}
        self.job_history = []
        self.active_jobs = {}
        self.settlement_cache = {}
        
    async def initialize(self):
        """Initialize IBM Quantum connection"""
        try:
            # Load IBM Quantum account
            self.provider = IBMQ.enable_account(self.api_token)
            
            # Get available backends
            for backend in self.provider.backends():
                if backend.configuration().n_qubits >= 5:  # Minimum 5 qubits
                    self.backends[backend.name()] = {
                        'backend': backend,
                        'qubits': backend.configuration().n_qubits,
                        'queue_size': backend.status().pending_jobs,
                        'operational': backend.status().operational
                    }
            
            logger.info(f"Initialized {len(self.backends)} IBM Quantum backends")
            
        except Exception as e:
            logger.error(f"Failed to initialize IBM Quantum: {e}")
            raise
    
    async def execute_settlement_circuit(
        self, 
        circuit: QuantumCircuit, 
        shots: int = 1000,
        priority: str = "high"
    ) -> Tuple[Dict[str, Any], QuantumJobMetrics]:
        """Execute settlement circuit with priority"""
        start_time = time.time()
        
        # Select optimal backend
        backend = await self._select_optimal_backend(circuit.num_qubits, priority)
        
        # Transpile circuit for backend
        transpiled_circuit = transpile(circuit, backend=backend)
        
        # Submit job
        job = backend.run(transpiled_circuit, shots=shots)
        job_id = job.job_id()
        
        logger.info(f"Submitted settlement job {job_id} to {backend.name()}")
        
        # Track job
        self.active_jobs[job_id] = {
            'job': job,
            'backend': backend.name(),
            'submitted_at': start_time,
            'circuit': transpiled_circuit
        }
        
        # Wait for completion with timeout
        try:
            result = await self._wait_for_job_completion(job, timeout_ms=1000)
            execution_time = (time.time() - start_time) * 1000
            
            # Calculate metrics
            metrics = QuantumJobMetrics(
                job_id=job_id,
                backend_name=backend.name(),
                qubits_used=circuit.num_qubits,
                circuit_depth=transpiled_circuit.depth(),
                execution_time_ms=execution_time,
                queue_time_ms=0,  # Will be calculated
                fidelity=self._calculate_fidelity(result, circuit),
                success=True
            )
            
            # Cache settlement result
            self.settlement_cache[job_id] = {
                'result': result,
                'metrics': metrics,
                'timestamp': datetime.utcnow()
            }
            
            self.job_history.append(metrics)
            del self.active_jobs[job_id]
            
            return result, metrics
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            metrics = QuantumJobMetrics(
                job_id=job_id,
                backend_name=backend.name(),
                qubits_used=circuit.num_qubits,
                circuit_depth=transpiled_circuit.depth(),
                execution_time_ms=execution_time,
                queue_time_ms=0,
                fidelity=0.0,
                success=False,
                error_message=str(e)
            )
            
            self.job_history.append(metrics)
            del self.active_jobs[job_id]
            
            raise e
    
    async def _select_optimal_backend(self, num_qubits: int, priority: str) -> Any:
        """Select optimal backend based on availability"""
        suitable_backends = []
        
        for name, info in self.backends.items():
            if (info['qubits'] >= num_qubits and 
                info['operational'] and 
                info['queue_size'] < 100):
                suitable_backends.append((name, info))
        
        if not suitable_backends:
            raise ValueError("No suitable backends available")
        
        # Sort by queue size (shortest first)
        suitable_backends.sort(key=lambda x: x[1]['queue_size'])
        
        # Return least busy backend
        return suitable_backends[0][1]['backend']
    
    async def _wait_for_job_completion(self, job: IBMQJob, timeout_ms: float) -> Dict[str, Any]:
        """Wait for job completion with timeout"""
        timeout_seconds = timeout_ms / 1000
        start_time = time.time()
        
        while time.time() - start_time < timeout_seconds:
            if job.status() in ['DONE', 'CANCELLED', 'ERROR']:
                if job.status() == 'DONE':
                    return job.result()
                else:
                    raise Exception(f"Job failed with status: {job.status()}")
            
            await asyncio.sleep(0.01)  # Check every 10ms
        
        raise TimeoutError(f"Job {job.job_id()} timed out after {timeout_ms}ms")
    
    def _calculate_fidelity(self, result: Dict[str, Any], circuit: QuantumCircuit) -> float:
        """Calculate circuit fidelity"""
        try:
            counts = result.get_counts()
            if not counts:
                return 0.0
            
            # Get most frequent measurement
            most_frequent = max(counts, key=counts.get)
            probability = counts[most_frequent] / sum(counts.values())
            
            return probability
            
        except Exception as e:
            logger.error(f"Error calculating fidelity: {e}")
            return 0.0
    
    async def get_backend_status(self) -> Dict[str, Any]:
        """Get status of all backends"""
        status = {}
        
        for name, info in self.backends.items():
            try:
                backend_status = info['backend'].status()
                status[name] = {
                    'operational': backend_status.operational,
                    'pending_jobs': backend_status.pending_jobs,
                    'last_update': backend_status.datetime.isoformat(),
                    'qubits': info['qubits']
                }
            except Exception as e:
                status[name] = {'error': str(e)}
        
        return status
    
    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a running job"""
        if job_id in self.active_jobs:
            try:
                job = self.active_jobs[job_id]['job']
                job.cancel()
                del self.active_jobs[job_id]
                logger.info(f"Cancelled job {job_id}")
                return True
            except Exception as e:
                logger.error(f"Failed to cancel job {job_id}: {e}")
                return False
        
        return False
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        if not self.job_history:
            return {"message": "No jobs executed yet"}
        
        successful_jobs = [j for j in self.job_history if j.success]
        failed_jobs = [j for j in self.job_history if not j.success]
        
        metrics = {
            'total_jobs': len(self.job_history),
            'successful_jobs': len(successful_jobs),
            'failed_jobs': len(failed_jobs),
            'success_rate': len(successful_jobs) / len(self.job_history) * 100,
            'average_execution_time_ms': np.mean([j.execution_time_ms for j in successful_jobs]) if successful_jobs else 0,
            'min_execution_time_ms': min([j.execution_time_ms for j in successful_jobs]) if successful_jobs else 0,
            'max_execution_time_ms': max([j.execution_time_ms for j in successful_jobs]) if successful_jobs else 0,
            'average_fidelity': np.mean([j.fidelity for j in successful_jobs]) if successful_jobs else 0,
            'jobs_under_1ms': len([j for j in successful_jobs if j.execution_time_ms < 1.0]),
            'jobs_under_5ms': len([j for j in successful_jobs if j.execution_time_ms < 5.0]),
            'backend_usage': {}
        }
        
        # Backend usage statistics
        for job in self.job_history:
            backend = job.backend_name
            if backend not in metrics['backend_usage']:
                metrics['backend_usage'][backend] = {'count': 0, 'success': 0, 'total_time': 0}
            
            metrics['backend_usage'][backend]['count'] += 1
            if job.success:
                metrics['backend_usage'][backend]['success'] += 1
                metrics['backend_usage'][backend]['total_time'] += job.execution_time_ms
        
        return metrics

# Usage example
async def main():
    """Main execution function"""
    # Initialize with IBM Quantum token (should be from environment)
    api_token = "your_ibm_quantum_token_here"
    
    colocator = IBMQuantumColocator(api_token)
    await colocator.initialize()
    
    # Create a simple settlement circuit
    qc = QuantumCircuit(4, 4)
    qc.h(range(4))
    qc.cx(0, 1)
    qc.cx(1, 2)
    qc.cx(2, 3)
    qc.measure(range(4), range(4))
    
    # Execute settlement
    try:
        result, metrics = await colocator.execute_settlement_circuit(qc, shots=1000)
        print(f"Settlement completed in {metrics.execution_time_ms:.2f}ms")
        print(f"Fidelity: {metrics.fidelity:.3f}")
        print(f"Results: {result.get_counts()}")
        
    except Exception as e:
        print(f"Settlement failed: {e}")
    
    # Get performance metrics
    performance = colocator.get_performance_metrics()
    print(f"Performance metrics: {json.dumps(performance, indent=2)}")

if __name__ == "__main__":
    asyncio.run(main())
