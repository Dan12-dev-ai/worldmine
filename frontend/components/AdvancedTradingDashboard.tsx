import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { LineChart, Line, AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { TrendingUp, TrendingDown, Activity, DollarSign, Package, Clock, AlertTriangle } from 'lucide-react';
import { useWebSocket } from '@/hooks/useWebSocket';
import { useRealTimeData } from '@/hooks/useRealTimeData';
import { useLocalStorage } from '@/hooks/useLocalStorage';

interface MarketData {
  timestamp: string;
  price: number;
  volume: number;
  change: number;
  changePercent: number;
}

interface Order {
  id: string;
  type: 'buy' | 'sell';
  mineral: string;
  quantity: number;
  price: number;
  status: 'pending' | 'filled' | 'cancelled';
  createdAt: string;
}

interface Portfolio {
  totalValue: number;
  dailyChange: number;
  dailyChangePercent: number;
  minerals: Array<{
    symbol: string;
    name: string;
    quantity: number;
    value: number;
    change: number;
    changePercent: number;
  }>;
}

export const AdvancedTradingDashboard: React.FC = () => {
  const [selectedMineral, setSelectedMineral] = useState<string>('gold');
  const [marketData, setMarketData] = useState<MarketData[]>([]);
  const [orders, setOrders] = useState<Order[]>([]);
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // WebSocket for real-time updates
  const { lastMessage, sendMessage } = useWebSocket('wss://api.dedan.ai/ws/market-updates');
  
  // Real-time data hook
  const { data: realTimeData, isConnected } = useRealTimeData();
  
  // Local storage for preferences
  const [preferences, setPreferences] = useLocalStorage('trading-preferences', {
    theme: 'dark',
    autoRefresh: true,
    refreshInterval: 5000,
    showAdvancedCharts: true
  });

  // Fetch initial data
  useEffect(() => {
    fetchInitialData();
  }, [selectedMineral]);

  // Handle WebSocket messages
  useEffect(() => {
    if (lastMessage) {
      const data = JSON.parse(lastMessage.data);
      handleRealTimeUpdate(data);
    }
  }, [lastMessage]);

  const fetchInitialData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [marketResponse, ordersResponse, portfolioResponse] = await Promise.all([
        fetch(`/api/v1/market/data/${selectedMineral}`).then(r => r.json()),
        fetch('/api/v1/orders').then(r => r.json()),
        fetch('/api/v1/portfolio').then(r => r.json())
      ]);
      
      setMarketData(marketResponse.data);
      setOrders(ordersResponse.data);
      setPortfolio(portfolioResponse.data);
    } catch (err) {
      setError('Failed to fetch trading data');
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRealTimeUpdate = useCallback((data: any) => {
    if (data.type === 'market_update' && data.mineral === selectedMineral) {
      setMarketData(prev => {
        const newData = [...prev, {
          timestamp: data.timestamp,
          price: data.price,
          volume: data.volume,
          change: data.change,
          changePercent: data.changePercent
        }];
        return newData.slice(-100); // Keep last 100 points
      });
    }
    
    if (data.type === 'order_update') {
      setOrders(prev => {
        const index = prev.findIndex(o => o.id === data.order.id);
        if (index >= 0) {
          const newOrders = [...prev];
          newOrders[index] = data.order;
          return newOrders;
        }
        return [...prev, data.order];
      });
    }
    
    if (data.type === 'portfolio_update') {
      setPortfolio(data.portfolio);
    }
  }, [selectedMineral]);

  const placeOrder = async (orderData: Partial<Order>) => {
    try {
      const response = await fetch('/api/v1/orders', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(orderData)
      });
      
      if (response.ok) {
        const newOrder = await response.json();
        setOrders(prev => [...prev, newOrder]);
      } else {
        throw new Error('Failed to place order');
      }
    } catch (err) {
      setError('Failed to place order');
      console.error('Error placing order:', err);
    }
  };

  const cancelOrder = async (orderId: string) => {
    try {
      const response = await fetch(`/api/v1/orders/${orderId}`, {
        method: 'DELETE'
      });
      
      if (response.ok) {
        setOrders(prev => prev.map(o => 
          o.id === orderId ? { ...o, status: 'cancelled' } : o
        ));
      }
    } catch (err) {
      setError('Failed to cancel order');
      console.error('Error cancelling order:', err);
    }
  };

  // Memoized calculations
  const marketStats = useMemo(() => {
    if (marketData.length === 0) return null;
    
    const latest = marketData[marketData.length - 1];
    const previous = marketData[marketData.length - 2] || latest;
    
    return {
      currentPrice: latest.price,
      change: latest.change,
      changePercent: latest.changePercent,
      volume: latest.volume,
      high: Math.max(...marketData.map(d => d.price)),
      low: Math.min(...marketData.map(d => d.price)),
      average: marketData.reduce((sum, d) => sum + d.price, 0) / marketData.length
    };
  }, [marketData]);

  const activeOrders = useMemo(() => 
    orders.filter(o => o.status === 'pending'), [orders]
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <Alert className="mb-6">
        <AlertTriangle className="h-4 w-4" />
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Advanced Trading Dashboard</h1>
        <div className="flex items-center space-x-2">
          <Badge variant={isConnected ? "default" : "secondary"}>
            {isConnected ? "Connected" : "Disconnected"}
          </Badge>
          <Button variant="outline" size="sm">
            <Activity className="h-4 w-4 mr-2" />
            Real-time
          </Button>
        </div>
      </div>

      {/* Market Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Current Price</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ${marketStats?.currentPrice.toFixed(2)}
            </div>
            <p className={`text-xs ${
              marketStats?.changePercent >= 0 ? 'text-green-600' : 'text-red-600'
            }`}>
              {marketStats?.changePercent >= 0 ? '+' : ''}{marketStats?.changePercent.toFixed(2)}%
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">24h Volume</CardTitle>
            <Package className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {marketStats?.volume.toLocaleString()}
            </div>
            <p className="text-xs text-muted-foreground">
              Units traded
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">24h High</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ${marketStats?.high.toFixed(2)}
            </div>
            <p className="text-xs text-muted-foreground">
              Highest price
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">24h Low</CardTitle>
            <TrendingDown className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ${marketStats?.low.toFixed(2)}
            </div>
            <p className="text-xs text-muted-foreground">
              Lowest price
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Main Content */}
      <Tabs defaultValue="chart" className="space-y-4">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="chart">Price Chart</TabsTrigger>
          <TabsTrigger value="orders">Orders</TabsTrigger>
          <TabsTrigger value="portfolio">Portfolio</TabsTrigger>
          <TabsTrigger value="advanced">Advanced</TabsTrigger>
        </TabsList>

        <TabsContent value="chart" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Price Chart - {selectedMineral.toUpperCase()}</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
                <AreaChart data={marketData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="timestamp" 
                    tickFormatter={(value) => new Date(value).toLocaleTimeString()}
                  />
                  <YAxis domain={['dataMin - 5', 'dataMax + 5']} />
                  <Tooltip 
                    labelFormatter={(value) => new Date(value).toLocaleString()}
                    formatter={(value: any) => [`$${value.toFixed(2)}`, 'Price']}
                  />
                  <Area 
                    type="monotone" 
                    dataKey="price" 
                    stroke="#8884d8" 
                    fill="#8884d8" 
                    fillOpacity={0.3}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="orders" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Active Orders</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {activeOrders.map(order => (
                  <div key={order.id} className="flex items-center justify-between p-4 border rounded">
                    <div className="flex items-center space-x-4">
                      <Badge variant={order.type === 'buy' ? 'default' : 'secondary'}>
                        {order.type.toUpperCase()}
                      </Badge>
                      <div>
                        <p className="font-medium">{order.mineral.toUpperCase()}</p>
                        <p className="text-sm text-muted-foreground">
                          {order.quantity} units @ ${order.price.toFixed(2)}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge variant="outline">{order.status}</Badge>
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => cancelOrder(order.id)}
                      >
                        Cancel
                      </Button>
                    </div>
                  </div>
                ))}
                {activeOrders.length === 0 && (
                  <p className="text-center text-muted-foreground py-8">
                    No active orders
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="portfolio" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Portfolio Overview</CardTitle>
            </CardHeader>
            <CardContent>
              {portfolio && (
                <div className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="text-center">
                      <p className="text-sm text-muted-foreground">Total Value</p>
                      <p className="text-2xl font-bold">
                        ${portfolio.totalValue.toFixed(2)}
                      </p>
                    </div>
                    <div className="text-center">
                      <p className="text-sm text-muted-foreground">Daily Change</p>
                      <p className={`text-2xl font-bold ${
                        portfolio.dailyChange >= 0 ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {portfolio.dailyChange >= 0 ? '+' : ''}${portfolio.dailyChange.toFixed(2)}
                      </p>
                    </div>
                    <div className="text-center">
                      <p className="text-sm text-muted-foreground">Daily %</p>
                      <p className={`text-2xl font-bold ${
                        portfolio.dailyChangePercent >= 0 ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {portfolio.dailyChangePercent >= 0 ? '+' : ''}{portfolio.dailyChangePercent.toFixed(2)}%
                      </p>
                    </div>
                  </div>
                  
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold">Holdings</h3>
                    {portfolio.minerals.map(mineral => (
                      <div key={mineral.symbol} className="flex items-center justify-between p-4 border rounded">
                        <div>
                          <p className="font-medium">{mineral.name}</p>
                          <p className="text-sm text-muted-foreground">
                            {mineral.quantity} units
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="font-medium">${mineral.value.toFixed(2)}</p>
                          <p className={`text-sm ${
                            mineral.changePercent >= 0 ? 'text-green-600' : 'text-red-600'
                          }`}>
                            {mineral.changePercent >= 0 ? '+' : ''}{mineral.changePercent.toFixed(2)}%
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="advanced" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Advanced Analytics</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-lg font-semibold mb-4">Volume Analysis</h3>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={marketData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="timestamp" />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="volume" fill="#82ca9d" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
                
                <div>
                  <h3 className="text-lg font-semibold mb-4">Price Volatility</h3>
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between mb-2">
                        <span>Volatility Index</span>
                        <span>15.2%</span>
                      </div>
                      <Progress value={15.2} className="h-2" />
                    </div>
                    <div>
                      <div className="flex justify-between mb-2">
                        <span>Risk Level</span>
                        <span>Medium</span>
                      </div>
                      <Progress value={50} className="h-2" />
                    </div>
                    <div>
                      <div className="flex justify-between mb-2">
                        <span>Liquidity Score</span>
                        <span>78.5</span>
                      </div>
                      <Progress value={78.5} className="h-2" />
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AdvancedTradingDashboard;
