import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import { 
  Cpu, 
  Zap, 
  Activity, 
  Clock, 
  TrendingUp, 
  Shield, 
  AlertTriangle,
  CheckCircle,
  XCircle
} from 'lucide-react';
import { useWebSocket } from '@/hooks/useWebSocket';

interface QuantumState {
  amplitude: number;
  phase: number;
  probability: number;
  superposition: boolean;
}

interface QuantumCircuit {
  id: string;
  name: string;
  qubits: number;
  depth: number;
  fidelity: number;
  executionTime: number;
}

interface QuantumResult {
  settlementId: string;
  quantumState: QuantumState[];
  probabilityDistribution: Record<string, number>;
  executionTime: number;
  quantumAdvantage: number;
  confidence: number;
  success: boolean;
}

export const QuantumTradingInterface: React.FC = () => {
  const [selectedCircuit, setSelectedCircuit] = useState<string>('settlement');
  const [mineralData, setMineralData] = useState({
    participants: Array(4).fill({ balance: 1000 }),
    priceFactor: 0.7,
    constraints: { maxSlippage: 0.05, minLiquidity: 1000 }
  });
  const [quantumResult, setQuantumResult] = useState<QuantumResult | null>(null);
  const [isExecuting, setIsExecuting] = useState(false);
  const [executionProgress, setExecutionProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [quantumState, setQuantumState] = useState<QuantumState[]>([]);
  
  const { lastMessage, sendMessage } = useWebSocket('wss://api.dedan.ai/ws/quantum-updates');

  const availableCircuits: QuantumCircuit[] = [
    { id: 'settlement', name: 'Trade Settlement', qubits: 4, depth: 8, fidelity: 0.95, executionTime: 0.5 },
    { id: 'optimization', name: 'Price Optimization', qubits: 6, depth: 12, fidelity: 0.92, executionTime: 0.8 },
    { id: 'prediction', name: 'Market Prediction', qubits: 8, depth: 16, fidelity: 0.88, executionTime: 1.2 },
    { id: 'arbitrage', name: 'Arbitrage Detection', qubits: 5, depth: 10, fidelity: 0.90, executionTime: 0.7 }
  ];

  const executeQuantumCircuit = async () => {
    try {
      setIsExecuting(true);
      setError(null);
      setExecutionProgress(0);

      // Simulate quantum execution progress
      const progressInterval = setInterval(() => {
        setExecutionProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return prev;
          }
          return prev + 10;
        });
      }, 100);

      const response = await fetch('/api/v1/quantum/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          circuitType: selectedCircuit,
          mineralData,
          optimizationLevel: 'high'
        })
      });

      clearInterval(progressInterval);
      setExecutionProgress(100);

      if (response.ok) {
        const result: QuantumResult = await response.json();
        setQuantumResult(result);
        setQuantumState(result.quantumState);
      } else {
        throw new Error('Quantum execution failed');
      }
    } catch (err) {
      setError('Failed to execute quantum circuit');
      console.error('Quantum execution error:', err);
    } finally {
      setIsExecuting(false);
      setTimeout(() => setExecutionProgress(0), 1000);
    }
  };

  const visualizeQuantumState = () => {
    if (!quantumState.length) return null;

    return (
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {quantumState.map((state, index) => (
          <div key={index} className="text-center">
            <div className="relative w-16 h-16 mx-auto mb-2">
              <div 
                className="absolute inset-0 rounded-full border-2 border-blue-500"
                style={{
                  background: `radial-gradient(circle, rgba(59, 130, 246, ${state.probability}) 0%, transparent 70%)`,
                  transform: `rotate(${state.phase * 180}deg)`
                }}
              />
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-xs font-bold">|{index}⟩</span>
              </div>
            </div>
            <div className="text-xs">
              <p>Amp: {state.amplitude.toFixed(3)}</p>
              <p>Phase: {state.phase.toFixed(2)}</p>
              <p>Prob: {(state.probability * 100).toFixed(1)}%</p>
            </div>
          </div>
        ))}
      </div>
    );
  };

  const selectedCircuitData = availableCircuits.find(c => c.id === selectedCircuit);

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold flex items-center">
          <Cpu className="mr-3 h-8 w-8 text-blue-600" />
          Quantum Trading Interface
        </h1>
        <Badge variant={quantumResult?.success ? "default" : "secondary"}>
          {quantumResult?.success ? "Quantum Enhanced" : "Classical Mode"}
        </Badge>
      </div>

      {/* Circuit Selection */}
      <Card>
        <CardHeader>
          <CardTitle>Quantum Circuit Selection</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {availableCircuits.map(circuit => (
              <div
                key={circuit.id}
                className={`p-4 border rounded-lg cursor-pointer transition-all ${
                  selectedCircuit === circuit.id 
                    ? 'border-blue-500 bg-blue-50' 
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => setSelectedCircuit(circuit.id)}
              >
                <h3 className="font-semibold mb-2">{circuit.name}</h3>
                <div className="space-y-1 text-sm">
                  <div className="flex justify-between">
                    <span>Qubits:</span>
                    <span>{circuit.qubits}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Depth:</span>
                    <span>{circuit.depth}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Fidelity:</span>
                    <span>{(circuit.fidelity * 100).toFixed(1)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Time:</span>
                    <span>{circuit.executionTime}ms</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Configuration */}
      <Card>
        <CardHeader>
          <CardTitle>Quantum Parameters</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <div>
                <Label>Price Factor</Label>
                <Slider
                  value={[mineralData.priceFactor]}
                  onValueChange={([value]) => 
                    setMineralData(prev => ({ ...prev, priceFactor: value }))
                  }
                  max={1}
                  min={0}
                  step={0.1}
                  className="mt-2"
                />
                <div className="flex justify-between text-xs text-muted-foreground mt-1">
                  <span>0.0</span>
                  <span>{mineralData.priceFactor.toFixed(1)}</span>
                  <span>1.0</span>
                </div>
              </div>
              
              <div>
                <Label>Max Slippage</Label>
                <Slider
                  value={[mineralData.constraints.maxSlippage]}
                  onValueChange={([value]) => 
                    setMineralData(prev => ({
                      ...prev,
                      constraints: { ...prev.constraints, maxSlippage: value }
                    }))
                  }
                  max={0.1}
                  min={0.01}
                  step={0.01}
                  className="mt-2"
                />
                <div className="flex justify-between text-xs text-muted-foreground mt-1">
                  <span>1%</span>
                  <span>{(mineralData.constraints.maxSlippage * 100).toFixed(0)}%</span>
                  <span>10%</span>
                </div>
              </div>
            </div>
            
            <div className="space-y-4">
              <div>
                <Label>Min Liquidity</Label>
                <Input
                  type="number"
                  value={mineralData.constraints.minLiquidity}
                  onChange={(e) => 
                    setMineralData(prev => ({
                      ...prev,
                      constraints: { ...prev.constraints, minLiquidity: Number(e.target.value) }
                    }))
                  }
                  className="mt-2"
                />
              </div>
              
              <div>
                <Label>Participants</Label>
                <Select 
                  value={mineralData.participants.length.toString()}
                  onValueChange={(value) => {
                    const count = parseInt(value);
                    setMineralData(prev => ({
                      ...prev,
                      participants: Array(count).fill({ balance: 1000 })
                    }));
                  }}
                >
                  <SelectTrigger className="mt-2">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="2">2 Participants</SelectItem>
                    <SelectItem value="4">4 Participants</SelectItem>
                    <SelectItem value="6">6 Participants</SelectItem>
                    <SelectItem value="8">8 Participants</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Execution */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Zap className="mr-2 h-5 w-5" />
            Quantum Execution
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <Button
              onClick={executeQuantumCircuit}
              disabled={isExecuting}
              className="w-full"
              size="lg"
            >
              {isExecuting ? (
                <>
                  <Activity className="mr-2 h-4 w-4 animate-spin" />
                  Executing Quantum Circuit...
                </>
              ) : (
                <>
                  <Cpu className="mr-2 h-4 w-4" />
                  Execute Quantum Settlement
                </>
              )}
            </Button>
            
            {isExecuting && (
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Execution Progress</span>
                  <span>{executionProgress}%</span>
                </div>
                <Progress value={executionProgress} className="h-2" />
                <p className="text-xs text-muted-foreground">
                  Initializing quantum state... {executionProgress < 50 ? 'Entangling qubits...' : 'Measuring results...'}
                </p>
              </div>
            )}
            
            {error && (
              <Alert variant="destructive">
                <AlertTriangle className="h-4 w-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Results */}
      {quantumResult && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              {quantumResult.success ? (
                <CheckCircle className="mr-2 h-5 w-5 text-green-600" />
              ) : (
                <XCircle className="mr-2 h-5 w-5 text-red-600" />
              )}
              Quantum Results
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="overview" className="space-y-4">
              <TabsList className="grid w-full grid-cols-4">
                <TabsTrigger value="overview">Overview</TabsTrigger>
                <TabsTrigger value="quantum-state">Quantum State</TabsTrigger>
                <TabsTrigger value="probabilities">Probabilities</TabsTrigger>
                <TabsTrigger value="metrics">Metrics</TabsTrigger>
              </TabsList>
              
              <TabsContent value="overview" className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="text-center p-4 border rounded">
                    <Shield className="h-8 w-8 mx-auto mb-2 text-blue-600" />
                    <p className="font-semibold">Confidence</p>
                    <p className="text-2xl font-bold">
                      {(quantumResult.confidence * 100).toFixed(1)}%
                    </p>
                  </div>
                  
                  <div className="text-center p-4 border rounded">
                    <TrendingUp className="h-8 w-8 mx-auto mb-2 text-green-600" />
                    <p className="font-semibold">Quantum Advantage</p>
                    <p className="text-2xl font-bold text-green-600">
                      +{quantumResult.quantumAdvantage.toFixed(1)}%
                    </p>
                  </div>
                  
                  <div className="text-center p-4 border rounded">
                    <Clock className="h-8 w-8 mx-auto mb-2 text-purple-600" />
                    <p className="font-semibold">Execution Time</p>
                    <p className="text-2xl font-bold">
                      {quantumResult.executionTime.toFixed(2)}ms
                    </p>
                  </div>
                </div>
              </TabsContent>
              
              <TabsContent value="quantum-state">
                {visualizeQuantumState()}
              </TabsContent>
              
              <TabsContent value="probabilities">
                <div className="space-y-2">
                  {Object.entries(quantumResult.probabilityDistribution).map(([state, probability]) => (
                    <div key={state} className="flex items-center justify-between p-3 border rounded">
                      <span className="font-mono">{state}</span>
                      <div className="flex items-center space-x-2">
                        <div className="w-32">
                          <Progress value={probability * 100} className="h-2" />
                        </div>
                        <span className="text-sm w-12 text-right">
                          {(probability * 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </TabsContent>
              
              <TabsContent value="metrics" className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <h4 className="font-semibold">Circuit Performance</h4>
                    <div className="space-y-1 text-sm">
                      <div className="flex justify-between">
                        <span>Settlement ID:</span>
                        <span className="font-mono">{quantumResult.settlementId}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Qubits Used:</span>
                        <span>{selectedCircuitData?.qubits}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Circuit Depth:</span>
                        <span>{selectedCircuitData?.depth}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Expected Fidelity:</span>
                        <span>{(selectedCircuitData?.fidelity * 100).toFixed(1)}%</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <h4 className="font-semibold">Quantum Metrics</h4>
                    <div className="space-y-1 text-sm">
                      <div className="flex justify-between">
                        <span>Superposition States:</span>
                        <span>{quantumResult.quantumState.length}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Measurement Outcomes:</span>
                        <span>{Object.keys(quantumResult.probabilityDistribution).length}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Entanglement Level:</span>
                        <span>High</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Coherence Time:</span>
                        <span>0.5ms</span>
                      </div>
                    </div>
                  </div>
                </div>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default QuantumTradingInterface;
