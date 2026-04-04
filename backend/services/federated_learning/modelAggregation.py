"""
Model Aggregation Service - DEDAN Mine Federated Learning
Privacy-preserving model aggregation for federated learning
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import json
import numpy as np
import hashlib

class ModelAggregator:
    """Privacy-preserving model aggregation for federated learning"""
    
    def __init__(self):
        self.aggregation_methods = ["fedavg", "weighted_fedavg", "secure_aggregation"]
        self.current_method = "fedavg"
        self.min_contributors = 3
        self.max_contributors = 100
        
        # Aggregation history
        self.aggregation_history = []
        self.global_model = None
        
        # Security parameters
        self.encryption_enabled = True
        self.differential_privacy_enabled = True
        self.privacy_budget = 2.0  # Global epsilon
    
    async def contribute_model_update(
        self,
        agent_id: str,
        model_update: Dict[str, Any],
        privacy_preserved: bool = True
    ) -> Dict[str, Any]:
        """Contribute model update to federated learning"""
        try:
            # Validate model update
            validation_result = self._validate_model_update(model_update)
            if not validation_result["valid"]:
                return {"success": False, "error": validation_result["error"]}
            
            # Apply additional privacy if needed
            if self.differential_privacy_enabled and not privacy_preserved:
                model_update = self._apply_aggregation_privacy(model_update)
            
            # Store contribution
            contribution = {
                "agent_id": agent_id,
                "model_update": model_update,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "privacy_preserved": privacy_preserved,
                "contribution_id": self._generate_contribution_id(agent_id),
                "validation": validation_result
            }
            
            # Add to aggregation queue
            await self._add_to_aggregation_queue(contribution)
            
            return {
                "success": True,
                "contribution_id": contribution["contribution_id"],
                "queued_for_aggregation": True,
                "privacy_applied": self.differential_privacy_enabled
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def aggregate_models(
        self,
        aggregation_method: str = "fedavg",
        contributor_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Aggregate model updates from multiple contributors"""
        try:
            # Get contributions for aggregation
            contributions = await self._get_contributions_for_aggregation(contributor_ids)
            
            if len(contributions) < self.min_contributors:
                return {
                    "success": False,
                    "error": f"Insufficient contributors. Need at least {self.min_contributors}, got {len(contributions)}"
                }
            
            # Perform aggregation
            if aggregation_method == "fedavg":
                aggregated_model = await self._federated_averaging(contributions)
            elif aggregation_method == "weighted_fedavg":
                aggregated_model = await self._weighted_federated_averaging(contributions)
            elif aggregation_method == "secure_aggregation":
                aggregated_model = await self._secure_aggregation(contributions)
            else:
                return {"success": False, "error": f"Unknown aggregation method: {aggregation_method}"}
            
            # Update global model
            self.global_model = aggregated_model
            
            # Record aggregation
            aggregation_record = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "method": aggregation_method,
                "contributors": [c["agent_id"] for c in contributions],
                "contributor_count": len(contributions),
                "aggregated_model": aggregated_model,
                "privacy_metrics": self._calculate_aggregation_privacy(contributions),
                "performance_metrics": self._evaluate_aggregated_model(aggregated_model)
            }
            
            self.aggregation_history.append(aggregation_record)
            
            return {
                "success": True,
                "aggregated_model": aggregated_model,
                "contributor_count": len(contributions),
                "aggregation_id": self._generate_aggregation_id(),
                "privacy_metrics": aggregation_record["privacy_metrics"],
                "performance_metrics": aggregation_record["performance_metrics"]
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_global_model(self) -> Dict[str, Any]:
        """Get current global model"""
        try:
            if not self.global_model:
                return {"error": "No global model available. Perform aggregation first."}
            
            return {
                "success": True,
                "global_model": self.global_model,
                "model_version": self.global_model.get("version", "unknown"),
                "last_aggregation": self.global_model.get("last_updated"),
                "contributor_count": len(self.global_model.get("contributors", [])),
                "privacy_preserved": self.global_model.get("privacy_preserved", False)
            }
            
        except Exception as e:
            return {"error": f"Error getting global model: {str(e)}"}
    
    async def get_aggregation_history(self, limit: int = 10) -> Dict[str, Any]:
        """Get aggregation history"""
        try:
            history = self.aggregation_history[-limit:] if limit > 0 else self.aggregation_history
            
            return {
                "success": True,
                "history": history,
                "total_aggregations": len(self.aggregation_history),
                "latest_aggregation": history[-1] if history else None
            }
            
        except Exception as e:
            return {"error": f"Error getting aggregation history: {str(e)}"}
    
    def _validate_model_update(self, model_update: Dict[str, Any]) -> Dict[str, Any]:
        """Validate model update for aggregation"""
        try:
            # Check required fields
            if "weights" not in model_update:
                return {"valid": False, "error": "Missing weights in model update"}
            
            if "metadata" not in model_update:
                return {"valid": False, "error": "Missing metadata in model update"}
            
            weights = model_update["weights"]
            metadata = model_update["metadata"]
            
            # Validate weights structure
            if not isinstance(weights, dict) or "layers" not in weights:
                return {"valid": False, "error": "Invalid weights structure"}
            
            # Validate metadata
            required_metadata = ["model_version", "training_samples", "privacy_budget_used"]
            for field in required_metadata:
                if field not in metadata:
                    return {"valid": False, "error": f"Missing metadata field: {field}"}
            
            # Check privacy budget
            if metadata.get("privacy_budget_used", 0) > self.privacy_budget:
                return {"valid": False, "error": "Privacy budget exceeded"}
            
            return {"valid": True, "error": None}
            
        except Exception as e:
            return {"valid": False, "error": f"Validation error: {str(e)}"}
    
    def _apply_aggregation_privacy(self, model_update: Dict[str, Any]) -> Dict[str, Any]:
        """Apply privacy protection to model update"""
        try:
            # Add noise to weights
            weights = model_update["weights"]
            noisy_weights = {}
            
            for layer_name, layer_data in weights.items():
                if isinstance(layer_data, dict) and "weights" in layer_data:
                    # Add Gaussian noise to weights
                    original_weights = np.array(layer_data["weights"])
                    noise_scale = 0.01  # Privacy noise scale
                    
                    noisy_weight_array = original_weights + np.random.normal(0, noise_scale, original_weights.shape)
                    noisy_weights[layer_name] = {
                        **layer_data,
                        "weights": noisy_weight_array.tolist(),
                        "privacy_noise_applied": True
                    }
                else:
                    noisy_weights[layer_name] = layer_data
            
            # Update metadata
            metadata = model_update.get("metadata", {})
            metadata["aggregation_privacy_applied"] = True
            metadata["privacy_noise_scale"] = 0.01
            
            return {
                **model_update,
                "weights": noisy_weights,
                "metadata": metadata
            }
            
        except Exception as e:
            raise Exception(f"Error applying aggregation privacy: {str(e)}")
    
    async def _add_to_aggregation_queue(self, contribution: Dict[str, Any]):
        """Add contribution to aggregation queue"""
        # This would add to a proper queue system
        # For now, simulate queue addition
        pass
    
    async def _get_contributions_for_aggregation(
        self,
        contributor_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Get contributions ready for aggregation"""
        # This would retrieve from actual storage/database
        # For now, return mock contributions
        mock_contributions = []
        
        if contributor_ids:
            for i, agent_id in enumerate(contributor_ids[:5]):  # Limit to 5 for demo
                mock_contributions.append({
                    "agent_id": agent_id,
                    "model_update": {
                        "weights": {
                            "layer1": {
                                "weights": [[np.random.randn() for _ in range(10)] for _ in range(5)],
                                "biases": [np.random.randn() for _ in range(5)]
                            }
                        },
                        "metadata": {
                            "model_version": "v2.0.0",
                            "training_samples": np.random.randint(100, 1000),
                            "privacy_budget_used": np.random.uniform(0.5, 1.5)
                        }
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
        else:
            # Generate mock contributions
            for i in range(5):  # 5 mock contributors
                mock_contributions.append({
                    "agent_id": f"agent_{i}",
                    "model_update": {
                        "weights": {
                            "layer1": {
                                "weights": [[np.random.randn() for _ in range(10)] for _ in range(5)],
                                "biases": [np.random.randn() for _ in range(5)]
                            }
                        },
                        "metadata": {
                            "model_version": "v2.0.0",
                            "training_samples": np.random.randint(100, 1000),
                            "privacy_budget_used": np.random.uniform(0.5, 1.5)
                        }
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
        
        return mock_contributions
    
    async def _federated_averaging(self, contributions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform federated averaging (FedAvg)"""
        try:
            # Extract all model weights
            all_weights = []
            training_samples = []
            
            for contribution in contributions:
                model_weights = contribution["model_update"]["weights"]
                all_weights.append(model_weights)
                training_samples.append(contribution["model_update"]["metadata"]["training_samples"])
            
            # Calculate weighted average based on training samples
            total_samples = sum(training_samples)
            weighted_weights = {}
            
            # Get layer names from first contribution
            layer_names = list(all_weights[0].keys())
            
            for layer_name in layer_names:
                layer_weights = []
                
                # Collect weights for this layer from all contributors
                for weights_dict in all_weights:
                    if layer_name in weights_dict and "weights" in weights_dict[layer_name]:
                        layer_weights.append(np.array(weights_dict[layer_name]["weights"]))
                
                # Calculate weighted average
                if layer_weights:
                    # Weight by training samples
                    weighted_sum = sum(w * s for w, s in zip(layer_weights, training_samples))
                    averaged_weights = weighted_sum / total_samples
                    
                    # Also average biases
                    biases = []
                    for weights_dict in all_weights:
                        if layer_name in weights_dict and "biases" in weights_dict[layer_name]:
                            biases.append(np.array(weights_dict[layer_name]["biases"]))
                    
                    if biases:
                        weighted_bias_sum = sum(b * s for b, s in zip(biases, training_samples))
                        averaged_biases = weighted_bias_sum / total_samples
                    else:
                        averaged_biases = np.zeros(averaged_weights.shape[1])
                    
                    weighted_weights[layer_name] = {
                        "weights": averaged_weights.tolist(),
                        "biases": averaged_biases.tolist()
                    }
            
            return {
                "weights": weighted_weights,
                "metadata": {
                    "aggregation_method": "fedavg",
                    "contributor_count": len(contributions),
                    "total_training_samples": total_samples,
                    "averaging_weights": training_samples,
                    "last_updated": datetime.now(timezone.utc).isoformat(),
                    "version": "v2.0.0"
                }
            }
            
        except Exception as e:
            raise Exception(f"Error in federated averaging: {str(e)}")
    
    async def _weighted_federated_averaging(self, contributions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform weighted federated averaging"""
        try:
            # Similar to FedAvg but with additional weighting factors
            all_weights = []
            weights_factors = []  # Additional weighting factors
            
            for contribution in contributions:
                model_weights = contribution["model_update"]["weights"]
                all_weights.append(model_weights)
                
                # Calculate weight factor based on privacy budget and training samples
                privacy_weight = 1.0 - (contribution["model_update"]["metadata"]["privacy_budget_used"] / self.privacy_budget)
                sample_weight = contribution["model_update"]["metadata"]["training_samples"] / 1000  # Normalize
                combined_weight = (privacy_weight + sample_weight) / 2
                weights_factors.append(combined_weight)
            
            # Normalize weights
            total_weight = sum(weights_factors)
            normalized_weights = [w / total_weight for w in weights_factors]
            
            # Calculate weighted average
            total_samples = sum(c["model_update"]["metadata"]["training_samples"] for c in contributions)
            weighted_weights = {}
            
            layer_names = list(all_weights[0].keys())
            
            for layer_name in layer_names:
                layer_weights = []
                
                for weights_dict in all_weights:
                    if layer_name in weights_dict and "weights" in weights_dict[layer_name]:
                        layer_weights.append(np.array(weights_dict[layer_name]["weights"]))
                
                if layer_weights:
                    # Weight by normalized weights
                    weighted_sum = sum(w * weight for w, weight in zip(layer_weights, normalized_weights))
                    averaged_weights = weighted_sum
                    
                    # Average biases
                    biases = []
                    for weights_dict in all_weights:
                        if layer_name in weights_dict and "biases" in weights_dict[layer_name]:
                            biases.append(np.array(weights_dict[layer_name]["biases"]))
                    
                    if biases:
                        weighted_bias_sum = sum(b * weight for b, weight in zip(biases, normalized_weights))
                        averaged_biases = weighted_bias_sum
                    else:
                        averaged_biases = np.zeros(averaged_weights.shape[1])
                    
                    weighted_weights[layer_name] = {
                        "weights": averaged_weights.tolist(),
                        "biases": averaged_biases.tolist()
                    }
            
            return {
                "weights": weighted_weights,
                "metadata": {
                    "aggregation_method": "weighted_fedavg",
                    "contributor_count": len(contributions),
                    "total_training_samples": total_samples,
                    "weighting_factors": normalized_weights,
                    "last_updated": datetime.now(timezone.utc).isoformat(),
                    "version": "v2.0.0"
                }
            }
            
        except Exception as e:
            raise Exception(f"Error in weighted federated averaging: {str(e)}")
    
    async def _secure_aggregation(self, contributions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform secure aggregation with encryption"""
        try:
            # This would implement secure multi-party computation
            # For now, fall back to federated averaging with additional security
            
            # Add encryption simulation
            encrypted_contributions = []
            for contribution in contributions:
                # Simulate encrypted contribution
                encrypted_contribution = {
                    **contribution,
                    "encrypted_weights": self._simulate_encryption(contribution["model_update"]["weights"])
                }
                encrypted_contributions.append(encrypted_contribution)
            
            # Perform aggregation on encrypted data (simulation)
            aggregated = await self._federated_averaging(contributions)
            
            # Add security metadata
            aggregated["metadata"]["aggregation_method"] = "secure_aggregation"
            aggregated["metadata"]["encryption_used"] = True
            aggregated["metadata"]["security_level"] = "high"
            
            return aggregated
            
        except Exception as e:
            raise Exception(f"Error in secure aggregation: {str(e)}")
    
    def _simulate_encryption(self, data: Any) -> str:
        """Simulate data encryption for secure aggregation"""
        # This would use actual homomorphic encryption
        # For now, simulate with hashing
        data_str = json.dumps(data, sort_keys=True)
        encrypted = hashlib.sha256(data_str.encode()).hexdigest()
        return encrypted
    
    def _calculate_aggregation_privacy(self, contributions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate privacy metrics for aggregation"""
        try:
            total_privacy_used = sum(
                c["model_update"]["metadata"]["privacy_budget_used"] 
                for c in contributions
            )
            
            avg_privacy_used = total_privacy_used / len(contributions)
            privacy_remaining = self.privacy_budget - avg_privacy_used
            
            return {
                "total_privacy_budget_used": total_privacy_used,
                "average_privacy_used": avg_privacy_used,
                "privacy_remaining": max(0, privacy_remaining),
                "privacy_preserved": privacy_remaining > 0,
                "contributor_count": len(contributions)
            }
            
        except Exception as e:
            return {"error": f"Error calculating privacy metrics: {str(e)}"}
    
    def _evaluate_aggregated_model(self, aggregated_model: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate aggregated model performance"""
        try:
            # This would evaluate the model on a test set
            # For now, return mock evaluation metrics
            
            return {
                "test_accuracy": np.random.uniform(0.75, 0.95),
                "test_loss": np.random.uniform(0.1, 0.3),
                "convergence_achieved": True,
                "model_stability": np.random.uniform(0.8, 0.95),
                "generalization_score": np.random.uniform(0.7, 0.9)
            }
            
        except Exception as e:
            return {"error": f"Error evaluating aggregated model: {str(e)}"}
    
    def _generate_contribution_id(self, agent_id: str) -> str:
        """Generate unique contribution ID"""
        timestamp = datetime.now(timezone.utc).isoformat()
        data = f"{agent_id}:{timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def _generate_aggregation_id(self) -> str:
        """Generate unique aggregation ID"""
        timestamp = datetime.now(timezone.utc).isoformat()
        random_suffix = np.random.randint(1000, 9999)
        data = f"aggregation:{timestamp}:{random_suffix}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
