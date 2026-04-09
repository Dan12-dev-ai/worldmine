"""
Satellite Controlled Transactions - DEDAN Mine Unified Architecture
Mandatory coordinate-lock + Sentinel API provenance with unified state management
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import json
import asyncio
import math
from dataclasses import dataclass

from core import unified_state_manager, FeaturePriority

@dataclass
class SatelliteCoordinates:
    """Satellite-verified coordinates"""
    latitude: float
    longitude: float
    altitude: float
    accuracy: float
    timestamp: datetime
    satellite_id: str
    provenance_hash: str

class SatelliteTransactionController:
    """Satellite Controlled Transactions with unified state integration"""
    
    def __init__(self):
        self.coordinate_tolerance = 0.001  # ~100 meters tolerance
        self.max_altitude_variance = 1000  # meters
        self.required_accuracy = 50  # meters
        self.sentinel_api_timeout = 30  # seconds
        
        # Sentinel API endpoints (mock)
        self.sentinel_endpoints = {
            "verify_coordinates": "https://api.sentinel-earth.com/v1/verify",
            "get_provenance": "https://api.sentinel-earth.com/v1/provenance",
            "satellite_pass": "https://api.sentinel-earth.com/v1/pass"
        }
    
    async def verify_transaction_coordinates(
        self,
        session_id: str,
        transaction_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Verify transaction coordinates with satellite data"""
        try:
            # Get unified session
            session = await unified_state_manager.get_session(session_id)
            if not session:
                return {"success": False, "error": "Session not found"}
            
            # Extract coordinates from transaction
            coordinates = transaction_data.get("coordinates")
            if not coordinates:
                return {"success": False, "error": "No coordinates provided"}
            
            # Validate coordinate format
            validation_result = await self._validate_coordinates(coordinates)
            if not validation_result["valid"]:
                return {"success": False, "error": validation_result["error"]}
            
            # Verify with Sentinel API
            sentinel_verification = await self._verify_with_sentinel_api(coordinates)
            
            if not sentinel_verification["verified"]:
                return {
                    "success": False,
                    "error": "Satellite verification failed",
                    "sentinel_error": sentinel_verification.get("error")
                }
            
            # Check coordinate consistency with session
            consistency_check = await self._check_coordinate_consistency(session, coordinates)
            
            # Execute satellite verification feature through unified state
            result = await unified_state_manager.execute_feature_request(
                feature_name="satellite_controlled_transactions",
                user_id=session.user_id,
                session_id=session_id,
                request_data={
                    "coordinates": coordinates,
                    "sentinel_verification": sentinel_verification,
                    "consistency_check": consistency_check,
                    "transaction_data": transaction_data
                }
            )
            
            if result["success"]:
                return {
                    "success": True,
                    "coordinates_verified": True,
                    "space_verified": True,
                    "sentinel_provenance": result["result"]["sentinel_provenance"],
                    "verification_details": {
                        "satellite_id": sentinel_verification["satellite_id"],
                        "accuracy": sentinel_verification["accuracy"],
                        "timestamp": sentinel_verification["timestamp"],
                        "provenance_hash": sentinel_verification["provenance_hash"],
                        "coordinate_consistency": consistency_check["consistent"]
                    },
                    "transaction_approved": consistency_check["consistent"] and sentinel_verification["verified"]
                }
            else:
                return result
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _validate_coordinates(self, coordinates: Dict[str, Any]) -> Dict[str, Any]:
        """Validate coordinate format and values"""
        try:
            lat = coordinates.get("latitude")
            lng = coordinates.get("longitude")
            alt = coordinates.get("altitude", 0)
            
            # Check required fields
            if lat is None or lng is None:
                return {"valid": False, "error": "Latitude and longitude are required"}
            
            # Check coordinate ranges
            if not (-90 <= lat <= 90):
                return {"valid": False, "error": f"Latitude {lat} out of range (-90 to 90)"}
            
            if not (-180 <= lng <= 180):
                return {"valid": False, "error": f"Longitude {lng} out of range (-180 to 180)"}
            
            # Check altitude (optional but should be reasonable)
            if alt < -500 or alt > 50000:  # -500m to 50km
                return {"valid": False, "error": f"Altitude {alt} out of reasonable range"}
            
            return {"valid": True}
            
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    async def _verify_with_sentinel_api(self, coordinates: Dict[str, Any]) -> Dict[str, Any]:
        """Verify coordinates with Sentinel API (mock implementation)"""
        try:
            # In production, this would call actual Sentinel API
            # For now, simulate verification with realistic data
            
            lat = coordinates["latitude"]
            lng = coordinates["longitude"]
            alt = coordinates.get("altitude", 0)
            
            # Simulate API call delay
            await asyncio.sleep(0.1)
            
            # Generate mock verification data
            satellite_id = f"SENTINEL-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Calculate mock accuracy based on location
            base_accuracy = 10.0  # 10 meters base accuracy
            urban_factor = 1.5 if self._is_urban_area(lat, lng) else 1.0
            accuracy = base_accuracy * urban_factor
            
            # Generate provenance hash
            provenance_data = f"{lat},{lng},{alt},{datetime.now(timezone.utc).isoformat()}"
            provenance_hash = self._generate_provenance_hash(provenance_data)
            
            # Simulate verification success (95% success rate)
            import random
            verified = random.random() < 0.95
            
            if verified:
                return {
                    "verified": True,
                    "satellite_id": satellite_id,
                    "accuracy": accuracy,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "provenance_hash": provenance_hash,
                    "confidence": 0.95,
                    "satellite_pass_time": (datetime.now(timezone.utc) - timedelta(minutes=15)).isoformat()
                }
            else:
                return {
                    "verified": False,
                    "error": "No recent satellite pass over location",
                    "satellite_id": satellite_id,
                    "next_pass": (datetime.now(timezone.utc) + timedelta(hours=2)).isoformat()
                }
                
        except Exception as e:
            return {"verified": False, "error": str(e)}
    
    async def _check_coordinate_consistency(
        self,
        session: UnifiedUserSession,
        coordinates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check coordinate consistency with session history"""
        try:
            current_lat = coordinates["latitude"]
            current_lng = coordinates["longitude"]
            current_alt = coordinates.get("altitude", 0)
            
            # Get historical coordinates from session
            historical_coords = session.behavior_patterns.get("coordinates", [])
            
            if len(historical_coords) == 0:
                # First transaction for this user
                return {
                    "consistent": True,
                    "first_transaction": True,
                    "message": "First transaction - coordinates established"
                }
            
            # Check against most recent coordinates
            recent_coords = historical_coords[-1]
            
            # Calculate distance
            distance = self._calculate_distance(
                current_lat, current_lng,
                recent_coords["latitude"], recent_coords["longitude"]
            )
            
            # Check altitude difference
            alt_diff = abs(current_alt - recent_coords.get("altitude", 0))
            
            # Determine consistency
            consistent = distance <= self.coordinate_tolerance and alt_diff <= self.max_altitude_variance
            
            if consistent:
                message = f"Coordinates consistent with previous location (distance: {distance:.6f}°)"
            else:
                message = f"Coordinates inconsistent (distance: {distance:.6f}°, altitude diff: {alt_diff}m)"
            
            return {
                "consistent": consistent,
                "distance": distance,
                "altitude_difference": alt_diff,
                "previous_coordinates": recent_coords,
                "message": message
            }
            
        except Exception as e:
            return {"consistent": False, "error": str(e)}
    
    def _calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate distance between two coordinates (simplified)"""
        # Using simplified Euclidean distance for demonstration
        # In production, use Haversine formula for accurate distances
        return math.sqrt((lat2 - lat1) ** 2 + (lng2 - lng1) ** 2)
    
    def _is_urban_area(self, lat: float, lng: float) -> bool:
        """Check if coordinates are in urban area (mock implementation)"""
        # Mock urban area detection based on coordinate ranges
        # In production, use actual geographic data
        urban_areas = [
            # Addis Ababa area
            {"lat_min": 8.8, "lat_max": 9.2, "lng_min": 38.6, "lng_max": 39.0},
            # Nairobi area
            {"lat_min": -1.3, "lat_max": -1.1, "lng_min": 36.7, "lng_max": 37.0},
            # Dar es Salaam area
            {"lat_min": -6.9, "lat_max": -6.7, "lng_min": 39.1, "lng_max": 39.3}
        ]
        
        for area in urban_areas:
            if (area["lat_min"] <= lat <= area["lat_max"] and 
                area["lng_min"] <= lng <= area["lng_max"]):
                return True
        
        return False
    
    def _generate_provenance_hash(self, data: str) -> str:
        """Generate provenance hash for coordinates"""
        import hashlib
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    async def get_transaction_provenance(
        self,
        session_id: str,
        transaction_id: str
    ) -> Dict[str, Any]:
        """Get provenance data for a transaction"""
        try:
            session = await unified_state_manager.get_session(session_id)
            if not session:
                return {"success": False, "error": "Session not found"}
            
            # Get provenance from session
            provenance = session.sentinel_provenance
            
            if not provenance:
                return {"success": False, "error": "No provenance data available"}
            
            # Get additional provenance details from Sentinel API
            additional_details = await self._get_provenance_details(provenance)
            
            return {
                "success": True,
                "provenance_hash": provenance,
                "verification_details": additional_details,
                "space_verified": session.space_verified,
                "location_verified": session.location_verified
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _get_provenance_details(self, provenance_hash: str) -> Dict[str, Any]:
        """Get detailed provenance information from Sentinel API"""
        try:
            # Mock implementation - would call actual Sentinel API
            await asyncio.sleep(0.1)
            
            return {
                "satellite_id": f"SENTINEL-{provenance_hash}",
                "capture_time": datetime.now(timezone.utc).isoformat(),
                "image_resolution": "10m",
                "cloud_cover": "5%",
                "processing_level": "L1C",
                "data_source": "Sentinel-2",
                "verification_confidence": 0.98
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    async def update_session_coordinates(
        self,
        session_id: str,
        coordinates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update session with new coordinates"""
        try:
            session = await unified_state_manager.get_session(session_id)
            if not session:
                return {"success": False, "error": "Session not found"}
            
            # Add timestamp to coordinates
            coordinates_with_time = {
                **coordinates,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            # Update session behavior patterns
            coord_history = session.behavior_patterns.get("coordinates", [])
            coord_history.append(coordinates_with_time)
            
            # Keep only recent coordinates
            session.behavior_patterns["coordinates"] = coord_history[-10:]  # Keep last 10
            
            # Update session state
            await unified_state_manager.update_session(session_id, {
                "behavior_patterns": session.behavior_patterns
            })
            
            return {
                "success": True,
                "coordinates_updated": True,
                "total_coordinates": len(coord_history)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_space_verification_status(
        self,
        session_id: str
    ) -> Dict[str, Any]:
        """Get current space verification status for session"""
        try:
            session = await unified_state_manager.get_session(session_id)
            if not session:
                return {"success": False, "error": "Session not found"}
            
            return {
                "success": True,
                "space_verified": session.space_verified,
                "location_verified": session.location_verified,
                "satellite_coordinates": session.satellite_coordinates,
                "sentinel_provenance": session.sentinel_provenance,
                "last_verification": session.updated_at.isoformat()
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

# Singleton instance
satellite_transaction_controller = SatelliteTransactionController()
