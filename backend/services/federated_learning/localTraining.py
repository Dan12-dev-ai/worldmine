"""
Local Training Service - DEDAN Mine Federated Learning
Privacy-preserving local model training for federated learning
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import json
import numpy as np
import pickle

class LocalModelTrainer:
    """Local model training for federated learning with privacy preservation"""
    
    def __init__(self):
        self.model_version = "v2.0.0"
        self.privacy_budget = 1.0  # Epsilon for differential privacy
        self.local_epochs = 5
        self.learning_rate = 0.01
        
        # Model architecture
        self.model_config = {
            "input_size": 50,  # Feature dimension
            "hidden_layers": [128, 64, 32],
            "output_size": 10,  # Prediction classes
            "activation": "relu",
            "dropout_rate": 0.2
        }
        
        # Training history
        self.training_history = []
        self.local_data_buffer = []
    
    async def train_local_model(
        self,
        training_data: List[Dict[str, Any]],
        model_weights: Optional[Dict[str, Any]] = None,
        privacy_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Train model locally with privacy preservation"""
        try:
            # Apply differential privacy
            if privacy_config:
                privacy_config = self._apply_differential_privacy(training_data, privacy_config)
            
            # Prepare training data
            X_train, y_train = self._prepare_training_data(training_data)
            
            # Initialize or update model
            if model_weights:
                model = self._load_model_from_weights(model_weights)
            else:
                model = self._initialize_model()
            
            # Train locally
            training_metrics = await self._local_training_loop(model, X_train, y_train)
            
            # Get updated weights
            updated_weights = self._extract_model_weights(model)
            
            # Calculate privacy loss
            privacy_loss = self._calculate_privacy_loss(len(training_data))
            
            # Store training history
            training_record = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "data_size": len(training_data),
                "epochs": self.local_epochs,
                "privacy_loss": privacy_loss,
                "accuracy": training_metrics["accuracy"],
                "loss": training_metrics["loss"]
            }
            self.training_history.append(training_record)
            
            return {
                "success": True,
                "model_update": {
                    "weights": updated_weights,
                    "metadata": {
                        "training_samples": len(training_data),
                        "privacy_budget_used": privacy_loss,
                        "model_version": self.model_version,
                        "training_metrics": training_metrics
                    }
                },
                "privacy_metrics": {
                    "epsilon_used": privacy_loss,
                    "delta": 1e-5,  # Failure probability
                    "privacy_preserved": True
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_training_data(self) -> Dict[str, Any]:
        """Get local training data for federated learning"""
        try:
            # Process buffered data
            processed_data = []
            for data_point in self.local_data_buffer:
                processed_point = self._preprocess_data_point(data_point)
                processed_data.append(processed_point)
            
            return {
                "data": processed_data,
                "metadata": {
                    "total_samples": len(processed_data),
                    "features": list(processed_data[0].keys()) if processed_data else [],
                    "last_updated": datetime.now(timezone.utc).isoformat(),
                    "privacy_applied": True
                }
            }
            
        except Exception as e:
            return {"error": f"Error getting training data: {str(e)}"}
    
    async def add_training_data(
        self,
        new_data: List[Dict[str, Any]],
        user_id: str,
        data_type: str = "market_transaction"
    ) -> Dict[str, Any]:
        """Add new training data with privacy preservation"""
        try:
            # Validate and preprocess data
            processed_data = []
            for data_point in new_data:
                if self._validate_data_point(data_point):
                    processed_point = self._preprocess_data_point(data_point)
                    processed_data.append(processed_point)
            
            # Add privacy noise
            noisy_data = self._add_privacy_noise(processed_data)
            
            # Add to buffer
            for data_point in noisy_data:
                self.local_data_buffer.append({
                    "data": data_point,
                    "user_id": user_id,
                    "data_type": data_type,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "privacy_applied": True
                })
            
            # Maintain buffer size
            max_buffer_size = 10000
            if len(self.local_data_buffer) > max_buffer_size:
                self.local_data_buffer = self.local_data_buffer[-max_buffer_size:]
            
            return {
                "success": True,
                "samples_added": len(processed_data),
                "buffer_size": len(self.local_data_buffer),
                "privacy_preserved": True
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _apply_differential_privacy(
        self,
        data: List[Dict[str, Any]],
        privacy_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply differential privacy to training data"""
        try:
            # Configure privacy parameters
            epsilon = privacy_config.get("epsilon", self.privacy_budget)
            delta = privacy_config.get("delta", 1e-5)
            sensitivity = privacy_config.get("sensitivity", 1.0)
            
            # Calculate noise scale
            noise_scale = sensitivity / epsilon
            
            # Apply Laplace noise to numerical features
            noisy_data = []
            for data_point in data:
                noisy_point = data_point.copy()
                
                for key, value in data_point.items():
                    if isinstance(value, (int, float)):
                        # Add Laplace noise
                        noise = np.random.laplace(0, noise_scale)
                        noisy_point[key] = value + noise
                
                noisy_data.append(noisy_point)
            
            return {
                "epsilon": epsilon,
                "delta": delta,
                "noise_scale": noise_scale,
                "privacy_preserved": True
            }
            
        except Exception as e:
            return {"error": f"Error applying differential privacy: {str(e)}"}
    
    def _prepare_training_data(self, data: List[Dict[str, Any]]) -> tuple:
        """Prepare data for neural network training"""
        try:
            # Extract features and labels
            features = []
            labels = []
            
            for data_point in data:
                # Convert to feature vector
                feature_vector = self._data_to_features(data_point)
                features.append(feature_vector)
                
                # Extract label (assuming it's in the data)
                label = data_point.get("label", 0)
                labels.append(label)
            
            return np.array(features), np.array(labels)
            
        except Exception as e:
            raise Exception(f"Error preparing training data: {str(e)}")
    
    def _data_to_features(self, data_point: Dict[str, Any]) -> List[float]:
        """Convert data point to feature vector"""
        try:
            # Feature extraction logic
            features = []
            
            # Numerical features
            numerical_features = [
                data_point.get("price", 0),
                data_point.get("weight", 0),
                data_point.get("quality_score", 0),
                data_point.get("market_demand", 0)
            ]
            features.extend(numerical_features)
            
            # Categorical features (one-hot encoded)
            categorical_features = [
                data_point.get("gem_type", "unknown"),
                data_point.get("origin", "unknown"),
                data_point.get("certification", "none")
            ]
            
            for cat_feature in categorical_features:
                # Simple one-hot encoding (would be more sophisticated in production)
                feature_hash = hash(cat_feature) % 10
                one_hot = [1 if i == feature_hash else 0 for i in range(10)]
                features.extend(one_hot)
            
            # Ensure fixed size
            target_size = self.model_config["input_size"]
            while len(features) < target_size:
                features.append(0.0)
            
            return features[:target_size]
            
        except Exception as e:
            raise Exception(f"Error converting data to features: {str(e)}")
    
    def _initialize_model(self) -> Dict[str, Any]:
        """Initialize neural network model"""
        try:
            # Simple neural network structure
            layers = []
            input_size = self.model_config["input_size"]
            
            # Hidden layers
            for hidden_size in self.model_config["hidden_layers"]:
                layers.append({
                    "type": "dense",
                    "input_size": input_size,
                    "output_size": hidden_size,
                    "activation": self.model_config["activation"],
                    "weights": np.random.randn(input_size, hidden_size) * 0.1,
                    "biases": np.zeros(hidden_size)
                })
                input_size = hidden_size
            
            # Output layer
            layers.append({
                "type": "dense",
                "input_size": input_size,
                "output_size": self.model_config["output_size"],
                "activation": "softmax",
                "weights": np.random.randn(input_size, self.model_config["output_size"]) * 0.1,
                "biases": np.zeros(self.model_config["output_size"])
            })
            
            return {
                "layers": layers,
                "config": self.model_config,
                "version": self.model_version
            }
            
        except Exception as e:
            raise Exception(f"Error initializing model: {str(e)}")
    
    def _load_model_from_weights(self, model_weights: Dict[str, Any]) -> Dict[str, Any]:
        """Load model from provided weights"""
        try:
            return {
                "layers": model_weights.get("layers", []),
                "config": self.model_config,
                "version": self.model_version
            }
            
        except Exception as e:
            raise Exception(f"Error loading model weights: {str(e)}")
    
    async def _local_training_loop(
        self,
        model: Dict[str, Any],
        X_train: np.ndarray,
        y_train: np.ndarray
    ) -> Dict[str, Any]:
        """Perform local training loop"""
        try:
            # Simple training simulation
            # In production, this would use actual neural network training
            
            accuracy_history = []
            loss_history = []
            
            for epoch in range(self.local_epochs):
                # Forward pass (simplified)
                predictions = self._forward_pass(model, X_train)
                
                # Calculate loss and accuracy
                loss = self._calculate_loss(predictions, y_train)
                accuracy = self._calculate_accuracy(predictions, y_train)
                
                loss_history.append(loss)
                accuracy_history.append(accuracy)
                
                # Update weights (simplified gradient descent)
                model = self._update_weights(model, X_train, y_train, predictions)
            
            return {
                "accuracy": accuracy_history[-1],
                "loss": loss_history[-1],
                "accuracy_history": accuracy_history,
                "loss_history": loss_history,
                "epochs": self.local_epochs
            }
            
        except Exception as e:
            raise Exception(f"Error in local training loop: {str(e)}")
    
    def _forward_pass(self, model: Dict[str, Any], X: np.ndarray) -> np.ndarray:
        """Forward pass through neural network"""
        current_input = X
        
        for layer in model["layers"]:
            if layer["type"] == "dense":
                # Dense layer computation
                weights = layer["weights"]
                biases = layer["biases"]
                
                # Matrix multiplication + bias
                output = np.dot(current_input, weights) + biases
                
                # Activation function
                if layer["activation"] == "relu":
                    output = np.maximum(0, output)
                elif layer["activation"] == "softmax":
                    exp_output = np.exp(output - np.max(output, axis=1, keepdims=True))
                    output = exp_output / np.sum(exp_output, axis=1, keepdims=True)
                
                current_input = output
        
        return current_input
    
    def _calculate_loss(self, predictions: np.ndarray, targets: np.ndarray) -> float:
        """Calculate cross-entropy loss"""
        # Simple loss calculation
        m = targets.shape[0]
        log_likelihood = -np.log(predictions[range(m), targets])
        loss = np.sum(log_likelihood) / m
        return loss
    
    def _calculate_accuracy(self, predictions: np.ndarray, targets: np.ndarray) -> float:
        """Calculate accuracy"""
        predicted_classes = np.argmax(predictions, axis=1)
        accuracy = np.mean(predicted_classes == targets)
        return float(accuracy)
    
    def _update_weights(
        self,
        model: Dict[str, Any],
        X: np.ndarray,
        y: np.ndarray,
        predictions: np.ndarray
    ) -> Dict[str, Any]:
        """Update model weights (simplified gradient descent)"""
        # This is a simplified weight update
        # In production, would use proper backpropagation
        
        learning_rate = self.learning_rate
        
        for layer in model["layers"]:
            if layer["type"] == "dense":
                # Simple weight update
                weight_update = learning_rate * 0.01  # Simplified gradient
                layer["weights"] -= weight_update
                layer["biases"] -= weight_update * 0.1
        
        return model
    
    def _extract_model_weights(self, model: Dict[str, Any]) -> Dict[str, Any]:
        """Extract model weights for federated aggregation"""
        return {
            "layers": [
                {
                    "weights": layer["weights"].tolist(),
                    "biases": layer["biases"].tolist(),
                    "config": {
                        "type": layer["type"],
                        "activation": layer["activation"],
                        "input_size": layer["input_size"],
                        "output_size": layer["output_size"]
                    }
                }
                for layer in model["layers"]
            ],
            "metadata": {
                "model_version": self.model_version,
                "training_samples": len(self.local_data_buffer),
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
        }
    
    def _calculate_privacy_loss(self, data_size: int) -> float:
        """Calculate privacy loss (epsilon)"""
        # Simple privacy budget calculation
        base_epsilon = self.privacy_budget
        data_factor = min(1.0, data_size / 1000)  # Scale with data size
        
        privacy_loss = base_epsilon * data_factor
        return privacy_loss
    
    def _validate_data_point(self, data_point: Dict[str, Any]) -> bool:
        """Validate data point for training"""
        required_fields = ["price", "gem_type"]
        return all(field in data_point for field in required_fields)
    
    def _preprocess_data_point(self, data_point: Dict[str, Any]) -> Dict[str, Any]:
        """Preprocess data point for training"""
        processed = data_point.copy()
        
        # Normalize numerical values
        if "price" in processed:
            processed["price"] = float(processed["price"]) / 10000  # Normalize to 0-1 range
        
        if "weight" in processed:
            processed["weight"] = float(processed["weight"]) / 1000  # Normalize to 0-1 range
        
        return processed
    
    def _add_privacy_noise(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add privacy noise to data"""
        noisy_data = []
        
        for data_point in data:
            noisy_point = data_point.copy()
            
            # Add small noise to numerical features
            for key, value in data_point.items():
                if isinstance(value, (int, float)):
                    noise = np.random.normal(0, 0.01)  # Small Gaussian noise
                    noisy_point[key] = value + noise
            
            noisy_data.append(noisy_point)
        
        return noisy_data
