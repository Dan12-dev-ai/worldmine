import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { 
  LineChart, 
  Line, 
  AreaChart, 
  Area, 
  CandlestickChart,
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer,
  ReferenceLine
} from 'recharts';
import { 
  TrendingUp, 
  TrendingDown, 
  Activity, 
  Zap, 
  Pause, 
  Play,
  Maximize2,
  Minimize2
} from 'lucide-react';
import { useWebSocket } from '@/hooks/useWebSocket';
import { useThrottle } from '@/hooks/useThrottle';

interface MarketDataPoint {
  timestamp: number;
  price: number;
  volume: number;
  high: number;
  low: number;
  open: number;
  close: number;
}

interface ChartConfig {
  type: 'line' | 'area' | 'candlestick';
  timeframe: '1m' | '5m' | '15m' | '1h' | '4h' | '1d';
  showVolume: boolean;
  showMA: boolean;
  maPeriod: number;
}

export const RealTimeMarketChart: React.FC = () => {
  const [data, setData] = useState<MarketDataPoint[]>([]);
  const [config, setConfig] = useState<ChartConfig>({
    type: 'area',
    timeframe: '5m',
    showVolume: true,
    showMA: true,
    maPeriod: 20
  });
  const [isPlaying, setIsPlaying] = useState(true);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [selectedMineral, setSelectedMineral] = useState('gold');
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'disconnected' | 'connecting'>('connecting');
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
  
  const chartRef = useRef<HTMLDivElement>(null);
  const { lastMessage, sendMessage } = useWebSocket('wss://api.dedan.ai/ws/market-data');
  
  // Throttled data update to prevent performance issues
  const throttledUpdate = useThrottle((newData: MarketDataPoint) => {
    setData(prev => {
      const updated = [...prev, newData];
      return updated.slice(-500); // Keep last 500 points
    });
  }, 100);

  useEffect(() => {
    fetchInitialData();
  }, [selectedMineral, config.timeframe]);

  useEffect(() => {
    if (lastMessage) {
      const message = JSON.parse(lastMessage.data);
      handleRealTimeUpdate(message);
    }
  }, [lastMessage]);

  const fetchInitialData = async () => {
    try {
      const response = await fetch(
        `/api/v1/market/history/${selectedMineral}?timeframe=${config.timeframe}&limit=500`
      );
      const historyData = await response.json();
      setData(historyData.data || []);
      setConnectionStatus('connected');
    } catch (error) {
      console.error('Failed to fetch initial data:', error);
      setConnectionStatus('disconnected');
    }
  };

  const handleRealTimeUpdate = useCallback((message: any) => {
    if (message.mineral === selectedMineral && message.type === 'price_update') {
      const newPoint: MarketDataPoint = {
        timestamp: message.timestamp,
        price: message.price,
        volume: message.volume,
        high: message.high,
        low: message.low,
        open: message.open,
        close: message.close
      };
      
      throttledUpdate(newPoint);
      setLastUpdate(new Date());
    }
  }, [selectedMineral, throttledUpdate]);

  const calculateMA = useCallback((data: MarketDataPoint[], period: number) => {
    return data.map((point, index) => {
      if (index < period - 1) return null;
      const sum = data.slice(index - period + 1, index + 1).reduce((acc, p) => acc + p.price, 0);
      return sum / period;
    });
  }, []);

  const maData = calculateMA(data, config.maPeriod);
  
  const currentPrice = data.length > 0 ? data[data.length - 1].price : 0;
  const priceChange = data.length > 1 ? currentPrice - data[data.length - 2].price : 0;
  const priceChangePercent = data.length > 1 ? (priceChange / data[data.length - 2].price) * 100 : 0;

  const togglePlayback = () => {
    setIsPlaying(!isPlaying);
    sendMessage(JSON.stringify({
      type: 'toggle_stream',
      mineral: selectedMineral,
      enabled: !isPlaying
    }));
  };

  const toggleFullscreen = () => {
    if (!isFullscreen && chartRef.current) {
      chartRef.current.requestFullscreen?.();
    } else {
      document.exitFullscreen?.();
    }
    setIsFullscreen(!isFullscreen);
  };

  const renderChart = () => {
    switch (config.type) {
      case 'line':
        return (
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
            <XAxis 
              dataKey="timestamp" 
              type="number"
              scale="time"
              domain={['dataMin', 'dataMax']}
              tickFormatter={(value) => new Date(value).toLocaleTimeString()}
            />
            <YAxis 
              domain={['dataMin - 5', 'dataMax + 5']}
              tickFormatter={(value) => `$${value.toFixed(2)}`}
            />
            <Tooltip 
              labelFormatter={(value) => new Date(value).toLocaleString()}
              formatter={(value: any) => [`$${value.toFixed(2)}`, 'Price']}
            />
            <Legend />
            <Line 
              type="monotone" 
              dataKey="price" 
              stroke="#3b82f6" 
              strokeWidth={2}
              dot={false}
              name="Price"
            />
            {config.showMA && (
              <Line 
                type="monotone" 
                dataKey={(data: any, index: number) => maData[index]}
                stroke="#ef4444" 
                strokeWidth={1}
                strokeDasharray="5 5"
                dot={false}
                name={`MA${config.maPeriod}`}
              />
            )}
          </LineChart>
        );
      
      case 'area':
        return (
          <AreaChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
            <XAxis 
              dataKey="timestamp" 
              type="number"
              scale="time"
              domain={['dataMin', 'dataMax']}
              tickFormatter={(value) => new Date(value).toLocaleTimeString()}
            />
            <YAxis 
              domain={['dataMin - 5', 'dataMax + 5']}
              tickFormatter={(value) => `$${value.toFixed(2)}`}
            />
            <Tooltip 
              labelFormatter={(value) => new Date(value).toLocaleString()}
              formatter={(value: any) => [`$${value.toFixed(2)}`, 'Price']}
            />
            <Legend />
            <Area 
              type="monotone" 
              dataKey="price" 
              stroke="#3b82f6" 
              fill="#3b82f6"
              fillOpacity={0.3}
              strokeWidth={2}
              name="Price"
            />
            {config.showMA && (
              <Line 
                type="monotone" 
                dataKey={(data: any, index: number) => maData[index]}
                stroke="#ef4444" 
                strokeWidth={1}
                strokeDasharray="5 5"
                dot={false}
                name={`MA${config.maPeriod}`}
              />
            )}
          </AreaChart>
        );
      
      case 'candlestick':
        return (
          <CandlestickChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
            <XAxis 
              dataKey="timestamp" 
              type="number"
              scale="time"
              domain={['dataMin', 'dataMax']}
              tickFormatter={(value) => new Date(value).toLocaleTimeString()}
            />
            <YAxis 
              domain={['dataMin - 5', 'dataMax + 5']}
              tickFormatter={(value) => `$${value.toFixed(2)}`}
            />
            <Tooltip 
              labelFormatter={(value) => new Date(value).toLocaleString()}
              content={({ active, payload }: any) => {
                if (active && payload && payload[0]) {
                  const data = payload[0].payload;
                  return (
                    <div className="bg-white p-3 border rounded shadow-lg">
                      <p className="font-semibold">{new Date(data.timestamp).toLocaleString()}</p>
                      <p>Open: ${data.open.toFixed(2)}</p>
                      <p>High: ${data.high.toFixed(2)}</p>
                      <p>Low: ${data.low.toFixed(2)}</p>
                      <p>Close: ${data.close.toFixed(2)}</p>
                      <p>Volume: {data.volume.toLocaleString()}</p>
                    </div>
                  );
                }
                return null;
              }}
            />
            <Legend />
          </CandlestickChart>
        );
      
      default:
        return null;
    }
  };

  return (
    <div className={`space-y-4 ${isFullscreen ? 'fixed inset-0 z-50 bg-black' : ''}`} ref={chartRef}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <h2 className="text-2xl font-bold">Real-Time Market Chart</h2>
          <Badge variant={connectionStatus === 'connected' ? 'default' : 'secondary'}>
            {connectionStatus === 'connected' ? (
              <>
                <Activity className="h-3 w-3 mr-1" />
                Live
              </>
            ) : (
              <>
                <Pause className="h-3 w-3 mr-1" />
                {connectionStatus}
              </>
            )}
          </Badge>
        </div>
        
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={togglePlayback}
          >
            {isPlaying ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
          </Button>
          
          <Button
            variant="outline"
            size="sm"
            onClick={toggleFullscreen}
          >
            {isFullscreen ? <Minimize2 className="h-4 w-4" /> : <Maximize2 className="h-4 w-4" />}
          </Button>
        </div>
      </div>

      {/* Controls */}
      <div className="flex flex-wrap items-center gap-4">
        <Select value={selectedMineral} onValueChange={setSelectedMineral}>
          <SelectTrigger className="w-32">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="gold">Gold</SelectItem>
            <SelectItem value="silver">Silver</SelectItem>
            <SelectItem value="copper">Copper</SelectItem>
            <SelectItem value="iron">Iron</SelectItem>
            <SelectItem value="platinum">Platinum</SelectItem>
          </SelectContent>
        </Select>

        <Select value={config.type} onValueChange={(value) => setConfig(prev => ({ ...prev, type: value as any }))}>
          <SelectTrigger className="w-32">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="line">Line</SelectItem>
            <SelectItem value="area">Area</SelectItem>
            <SelectItem value="candlestick">Candlestick</SelectItem>
          </SelectContent>
        </Select>

        <Select value={config.timeframe} onValueChange={(value) => setConfig(prev => ({ ...prev, timeframe: value as any }))}>
          <SelectTrigger className="w-24">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="1m">1m</SelectItem>
            <SelectItem value="5m">5m</SelectItem>
            <SelectItem value="15m">15m</SelectItem>
            <SelectItem value="1h">1h</SelectItem>
            <SelectItem value="4h">4h</SelectItem>
            <SelectItem value="1d">1d</SelectItem>
          </SelectContent>
        </Select>

        <Button
          variant="outline"
          size="sm"
          onClick={() => setConfig(prev => ({ ...prev, showMA: !prev.showMA }))}
        >
          MA{config.showMA ? ' ON' : ' OFF'}
        </Button>

        <Button
          variant="outline"
          size="sm"
          onClick={() => setConfig(prev => ({ ...prev, showVolume: !prev.showVolume }))}
        >
          Vol{config.showVolume ? ' ON' : ' OFF'}
        </Button>
      </div>

      {/* Price Display */}
      <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
        <div>
          <p className="text-3xl font-bold">${currentPrice.toFixed(2)}</p>
          <div className="flex items-center space-x-2">
            {priceChange >= 0 ? (
              <TrendingUp className="h-4 w-4 text-green-600" />
            ) : (
              <TrendingDown className="h-4 w-4 text-red-600" />
            )}
            <span className={`font-semibold ${priceChange >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {priceChange >= 0 ? '+' : ''}{priceChange.toFixed(2)} ({priceChangePercent.toFixed(2)}%)
            </span>
          </div>
        </div>
        
        <div className="text-right text-sm text-gray-600">
          <p>Last Update: {lastUpdate.toLocaleTimeString()}</p>
          <p>Data Points: {data.length}</p>
        </div>
      </div>

      {/* Chart */}
      <Card>
        <CardContent className="p-0">
          <ResponsiveContainer width="100%" height={isFullscreen ? window.innerHeight - 200 : 400}>
            {renderChart()}
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Volume Chart */}
      {config.showVolume && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Volume</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={100}>
              <AreaChart data={data}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
                <XAxis 
                  dataKey="timestamp" 
                  type="number"
                  scale="time"
                  domain={['dataMin', 'dataMax']}
                  tickFormatter={(value) => new Date(value).toLocaleTimeString()}
                />
                <YAxis tickFormatter={(value) => value.toLocaleString()} />
                <Tooltip 
                  labelFormatter={(value) => new Date(value).toLocaleString()}
                  formatter={(value: any) => [value.toLocaleString(), 'Volume']}
                />
                <Area 
                  type="monotone" 
                  dataKey="volume" 
                  stroke="#10b981" 
                  fill="#10b981"
                  fillOpacity={0.3}
                />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default RealTimeMarketChart;
