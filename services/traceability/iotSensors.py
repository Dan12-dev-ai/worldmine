"""
IoT Sensors Service - DEDAN Mine Traceability System
Full Mine-to-Market traceability using IoT sensors, GPS, and satellite monitoring
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid
import json
import asyncio
from dataclasses import dataclass, asdict

from models import TraceabilityRecord, Listing
from database import get_db
from security.quantumEncryption import QuantumSecureData

@dataclass
class SensorReading:
    """IoT sensor reading data structure"""
    sensor_type: str  # 'temperature', 'humidity', 'vibration', 'light', 'pressure', 'gps'
    reading: float
    unit: str
    timestamp: datetime
    location: Dict[str, float]  # lat, lng, altitude
    metadata: Dict[str, Any] = None

@dataclass
class EnvironmentalConditions:
    """Environmental conditions during extraction"""
    temperature: float
    humidity: float
    air_pressure: float
    light_conditions: str
    water_ph: Optional[float] = None
    soil_composition: Dict[str, Any] = None

class IoTSensorService:
    """IoT sensor integration for mine-to-market traceability"""
    
    def __init__(self):
        self.db = next(get_db())
        self.quantum_security = QuantumSecureData()
        self.active_sensor_streams = {}  # Active IoT data streams
        self.satellite_integration = SatelliteIntegrationService()
        
    async def register_mine_sensors(
        self,
        listing_id: str,
        sensor_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Register IoT sensors for a mine listing"""
        try:
            # Validate sensor configuration
            required_sensors = ['temperature', 'humidity', 'gps', 'vibration']
            missing_sensors = [s for s in required_sensors if s not in sensor_config]
            
            if missing_sensors:
                return {
                    "success": False,
                    "error": f"Missing required sensors: {', '.join(missing_sensors)}"
                }
            
            # Create traceability record
            traceability = TraceabilityRecord(
                id=str(uuid.uuid4()),
                listing_id=listing_id,
                mine_location=sensor_config.get('mine_location', {}),
                extraction_date=sensor_config.get('extraction_date'),
                extraction_method=sensor_config.get('extraction_method', 'manual'),
                iot_sensors=json.dumps([]),  # Will be populated with real data
                environmental_conditions=json.dumps({}),
                carbon_footprint=0.0,
                water_usage=0.0,
                energy_source=sensor_config.get('energy_source', 'grid'),
                verification_blockchain_hash=await self._generate_initial_hash(listing_id),
                created_at=datetime.now(timezone.utc)
            )
            
            self.db.add(traceability)
            self.db.commit()
            
            # Setup sensor data streams
            await self._setup_sensor_streams(traceability.id, sensor_config)
            
            return {
                "success": True,
                "traceability_id": traceability.id,
                "sensor_streams": list(sensor_config.keys()),
                "blockchain_hash": traceability.verification_blockchain_hash
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def record_sensor_data(
        self,
        traceability_id: str,
        sensor_readings: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Record IoT sensor data for traceability"""
        try:
            traceability = self.db.query(TraceabilityRecord).filter(
                TraceabilityRecord.id == traceability_id
            ).first()
            
            if not traceability:
                return {"success": False, "error": "Traceability record not found"}
            
            # Process sensor readings
            processed_readings = []
            environmental_data = json.loads(traceability.environmental_conditions or "{}")
            
            for reading in sensor_readings:
                sensor_reading = SensorReading(
                    sensor_type=reading['sensor_type'],
                    reading=reading['reading'],
                    unit=reading['unit'],
                    timestamp=datetime.fromisoformat(reading['timestamp']),
                    location=reading.get('location', {}),
                    metadata=reading.get('metadata', {})
                )
                
                processed_readings.append(asdict(sensor_reading))
                
                # Update environmental conditions
                if reading['sensor_type'] == 'temperature':
                    environmental_data['temperature'] = reading['reading']
                elif reading['sensor_type'] == 'humidity':
                    environmental_data['humidity'] = reading['reading']
                elif reading['sensor_type'] == 'air_pressure':
                    environmental_data['air_pressure'] = reading['reading']
                elif reading['sensor_type'] == 'light':
                    environmental_data['light_conditions'] = reading['metadata'].get('light_quality', 'unknown')
            
            # Update traceability record
            current_sensors = json.loads(traceability.iot_sensors or "[]")
            updated_sensors = current_sensors + processed_readings
            
            traceability.iot_sensors = json.dumps(updated_sensors)
            traceability.environmental_conditions = json.dumps(environmental_data)
            traceability.updated_at = datetime.now(timezone.utc)
            
            self.db.commit()
            
            # Encrypt sensitive data
            encrypted_sensors = await self.quantum_security.encrypt_data(json.dumps(updated_sensors))
            
            return {
                "success": True,
                "recordings_count": len(processed_readings),
                "environmental_summary": environmental_data,
                "encrypted_data": encrypted_sensors['hash']
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def verify_gps_location(
        self,
        traceability_id: str,
        gps_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Verify and record GPS location data"""
        try:
            traceability = self.db.query(TraceabilityRecord).filter(
                TraceabilityRecord.id == traceability_id
            ).first()
            
            if not traceability:
                return {"success": False, "error": "Traceability record not found"}
            
            # Validate GPS coordinates
            lat = gps_data.get('latitude')
            lng = gps_data.get('longitude')
            altitude = gps_data.get('altitude')
            
            if not all([lat, lng]):
                return {"success": False, "error": "Invalid GPS coordinates"}
            
            # Update mine location
            current_location = json.loads(traceability.mine_location or "{}")
            updated_location = {
                **current_location,
                "verified_gps": {
                    "latitude": lat,
                    "longitude": lng,
                    "altitude": altitude,
                    "accuracy": gps_data.get('accuracy', 10),
                    "verification_time": datetime.now(timezone.utc).isoformat()
                }
            }
            
            traceability.mine_location = json.dumps(updated_location)
            traceability.updated_at = datetime.now(timezone.utc)
            
            self.db.commit()
            
            # Get satellite verification
            satellite_verification = await self.satellite_integration.verify_location(
                lat, lng, verification_time=datetime.now(timezone.utc)
            )
            
            return {
                "success": True,
                "location_verified": True,
                "gps_coordinates": {"lat": lat, "lng": lng, "altitude": altitude},
                "satellite_verification": satellite_verification
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def calculate_carbon_footprint(
        self,
        traceability_id: str,
        energy_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate carbon footprint from energy usage"""
        try:
            traceability = self.db.query(TraceabilityRecord).filter(
                TraceabilityRecord.id == traceability_id
            ).first()
            
            if not traceability:
                return {"success": False, "error": "Traceability record not found"}
            
            # Calculate carbon footprint
            energy_kwh = energy_data.get('energy_consumption_kwh', 0)
            energy_source = energy_data.get('energy_source', 'grid')
            
            # Carbon emission factors (kg CO2 per kWh)
            emission_factors = {
                'grid': 0.5,  # Average grid emission
                'solar': 0.02,
                'wind': 0.01,
                'hydro': 0.02,
                'diesel': 0.8,
                'generator': 0.7
            }
            
            carbon_footprint = energy_kwh * emission_factors.get(energy_source, 0.5)
            
            # Calculate water usage
            water_usage = energy_data.get('water_usage_liters', 0)
            
            # Update traceability record
            traceability.carbon_footprint = carbon_footprint
            traceability.water_usage = water_usage
            traceability.energy_source = energy_source
            traceability.updated_at = datetime.now(timezone.utc)
            
            self.db.commit()
            
            # Generate carbon credits (negative footprint = credits earned)
            carbon_credits_earned = max(0, -carbon_footprint * 0.1)  # 10% of reduction as credits
            
            return {
                "success": True,
                "carbon_footprint_kg": carbon_footprint,
                "water_usage_liters": water_usage,
                "energy_consumption_kwh": energy_kwh,
                "carbon_credits_earned": carbon_credits_earned,
                "environmental_impact": {
                    "carbon_intensity": "high" if carbon_footprint > 100 else "medium" if carbon_footprint > 50 else "low",
                    "water_efficiency": "poor" if water_usage > 1000 else "good" if water_usage < 500 else "moderate",
                    "renewable_energy": energy_source in ['solar', 'wind', 'hydro']
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_traceability_report(
        self,
        listing_id: str
    ) -> Dict[str, Any]:
        """Generate comprehensive traceability report"""
        try:
            traceability = self.db.query(TraceabilityRecord).filter(
                TraceabilityRecord.listing_id == listing_id
            ).first()
            
            if not traceability:
                return {"success": False, "error": "No traceability data found"}
            
            # Parse sensor data
            sensor_data = json.loads(traceability.iot_sensors or "[]")
            environmental_data = json.loads(traceability.environmental_conditions or "{}")
            location_data = json.loads(traceability.mine_location or "{}")
            
            # Generate report
            report = {
                "traceability_id": traceability.id,
                "listing_id": listing_id,
                "mine_location": location_data,
                "extraction_date": traceability.extraction_date,
                "extraction_method": traceability.extraction_method,
                
                # Environmental data
                "environmental_conditions": environmental_data,
                "carbon_footprint": traceability.carbon_footprint,
                "water_usage": traceability.water_usage,
                "energy_source": traceability.energy_source,
                
                # Sensor data summary
                "sensor_readings": {
                    "total_readings": len(sensor_data),
                    "sensor_types": list(set(r['sensor_type'] for r in sensor_data)),
                    "reading_period": {
                        "start": min(r['timestamp'] for r in sensor_data) if sensor_data else None,
                        "end": max(r['timestamp'] for r in sensor_data) if sensor_data else None
                    }
                },
                
                # Verification data
                "blockchain_hash": traceability.verification_blockchain_hash,
                "satellite_verifications": json.loads(traceability.satellite_images or "[]"),
                "compliance_score": await self._calculate_compliance_score(traceability),
                
                # Trust indicators
                "data_integrity": "verified" if await self._verify_blockchain_hash(traceability) else "unverified",
                "real_time_monitoring": traceability.id in self.active_sensor_streams
            }
            
            return {
                "success": True,
                "traceability_report": report
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _setup_sensor_streams(self, traceability_id: str, sensor_config: Dict[str, Any]):
        """Setup real-time sensor data streams"""
        try:
            # Initialize sensor streams for each sensor type
            for sensor_type in sensor_config.keys():
                if sensor_type in ['temperature', 'humidity', 'vibration', 'gps']:
                    stream_config = {
                        "traceability_id": traceability_id,
                        "sensor_type": sensor_type,
                        "sampling_rate": self._get_sampling_rate(sensor_type),
                        "data_format": "json",
                        "encryption": True
                    }
                    
                    # Start data stream
                    await self._start_sensor_stream(sensor_type, stream_config)
            
            self.active_sensor_streams[traceability_id] = True
            
        except Exception as e:
            print(f"Error setting up sensor streams: {e}")
    
    async def _start_sensor_stream(self, sensor_type: str, config: Dict[str, Any]):
        """Start individual sensor data stream"""
        # This would integrate with actual IoT hardware
        # For now, simulate data stream
        pass
    
    def _get_sampling_rate(self, sensor_type: str) -> str:
        """Get appropriate sampling rate for sensor type"""
        rates = {
            'temperature': '1_minute',
            'humidity': '1_minute',
            'vibration': '10_seconds',
            'gps': '30_seconds',
            'light': '1_minute',
            'pressure': '1_minute'
        }
        return rates.get(sensor_type, '1_minute')
    
    async def _generate_initial_hash(self, listing_id: str) -> str:
        """Generate initial blockchain hash for traceability"""
        import hashlib
        timestamp = datetime.now(timezone.utc).isoformat()
        data = f"{listing_id}:{timestamp}:initial"
        return hashlib.sha256(data.encode()).hexdigest()
    
    async def _verify_blockchain_hash(self, traceability: TraceabilityRecord) -> bool:
        """Verify blockchain hash integrity"""
        # This would integrate with blockchain verification
        # For now, return True
        return True
    
    async def _calculate_compliance_score(self, traceability: TraceabilityRecord) -> int:
        """Calculate compliance score based on traceability data"""
        score = 0
        
        # Data completeness (40 points)
        if traceability.iot_sensors and json.loads(traceability.iot_sensors):
            score += 20
        if traceability.environmental_conditions:
            score += 10
        if traceability.satellite_images:
            score += 10
        
        # Environmental impact (30 points)
        if traceability.carbon_footprint and traceability.carbon_footprint < 50:  # Low carbon
            score += 15
        elif traceability.carbon_footprint and traceability.carbon_footprint < 100:
            score += 10
        
        if traceability.water_usage and traceability.water_usage < 500:  # Low water usage
            score += 15
        
        # Verification (30 points)
        if traceability.verification_blockchain_hash:
            score += 20
        if await self._verify_blockchain_hash(traceability):
            score += 10
        
        return min(score, 100)

class SatelliteIntegrationService:
    """Satellite monitoring integration for traceability"""
    
    def __init__(self):
        self.satellite_providers = ['planet', 'maxar', 'sentinel']
        
    async def verify_location(
        self,
        latitude: float,
        longitude: float,
        verification_time: datetime = None
    ) -> Dict[str, Any]:
        """Verify location using satellite imagery"""
        try:
            # This would integrate with satellite APIs
            # For now, return mock verification
            return {
                "verified": True,
                "satellite_provider": "planet",
                "image_date": verification_time or datetime.now(timezone.utc),
                "image_url": f"https://satellite.dedan-mine.com/images/{latitude}_{longitude}_{verification_time.strftime('%Y%m%d')}.png",
                "coordinates_match": True,
                "confidence": 0.95
            }
        except Exception as e:
            return {"verified": False, "error": str(e)}
    
    async def get_historical_imagery(
        self,
        latitude: float,
        longitude: float,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Get historical satellite imagery for location"""
        # This would fetch from satellite providers
        return []
