import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Label } from '@/components/ui/label.jsx'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { TrendingUp, DollarSign, BarChart3, Activity } from 'lucide-react'
import './App.css'

const API_BASE_URL = 'http://localhost:5001/api'

function App() {
  const [strategies, setStrategies] = useState([])
  const [selectedStrategy, setSelectedStrategy] = useState('')
  const [initialCapital, setInitialCapital] = useState(100000)
  const [backtestResult, setBacktestResult] = useState(null)
  const [comparisonResults, setComparisonResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [stockData, setStockData] = useState([])

  useEffect(() => {
    fetchStrategies()
    fetchStockData()
  }, [])

  const fetchStrategies = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/strategies`)
      const data = await response.json()
      setStrategies(data.strategies)
      if (data.strategies.length > 0) {
        setSelectedStrategy(data.strategies[0])
      }
    } catch (error) {
      console.error('Error fetching strategies:', error)
    }
  }

  const fetchStockData = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/stock-data`)
      const data = await response.json()
      setStockData(data.data.slice(-30)) // Last 30 days for chart
    } catch (error) {
      console.error('Error fetching stock data:', error)
    }
  }

  const runBacktest = async () => {
    if (!selectedStrategy) return
    
    setLoading(true)
    try {
      const response = await fetch(`${API_BASE_URL}/backtest`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          strategy: selectedStrategy,
          initial_capital: initialCapital
        })
      })
      const data = await response.json()
      setBacktestResult(data)
    } catch (error) {
      console.error('Error running backtest:', error)
    } finally {
      setLoading(false)
    }
  }

  const compareStrategies = async () => {
    setLoading(true)
    try {
      const response = await fetch(`${API_BASE_URL}/compare-strategies`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          strategies: strategies,
          initial_capital: initialCapital
        })
      })
      const data = await response.json()
      setComparisonResults(data)
    } catch (error) {
      console.error('Error comparing strategies:', error)
    } finally {
      setLoading(false)
    }
  }

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(value)
  }

  const formatPercentage = (value) => {
    return `${(value * 100).toFixed(2)}%`
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
      <div className="max-w-7xl mx-auto">
        <header className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">NVIDIA Trading Bot</h1>
          <p className="text-lg text-gray-600">Advanced algorithmic trading strategies for NVIDIA stock</p>
        </header>

        {/* Controls */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5" />
              Trading Configuration
            </CardTitle>
            <CardDescription>
              Configure your trading strategy and initial capital
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              <div>
                <Label htmlFor="strategy">Trading Strategy</Label>
                <Select value={selectedStrategy} onValueChange={setSelectedStrategy}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select a strategy" />
                  </SelectTrigger>
                  <SelectContent>
                    {strategies.map((strategy) => (
                      <SelectItem key={strategy} value={strategy}>
                        {strategy}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="capital">Initial Capital</Label>
                <Input
                  id="capital"
                  type="number"
                  value={initialCapital}
                  onChange={(e) => setInitialCapital(Number(e.target.value))}
                  placeholder="100000"
                />
              </div>
              <div className="flex items-end gap-2">
                <Button onClick={runBacktest} disabled={loading || !selectedStrategy} className="flex-1">
                  {loading ? 'Running...' : 'Run Backtest'}
                </Button>
                <Button onClick={compareStrategies} disabled={loading} variant="outline">
                  Compare All
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Stock Price Chart */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              NVIDIA Stock Price (Last 30 Days)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={stockData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="date" 
                  tickFormatter={(value) => new Date(value).toLocaleDateString()}
                />
                <YAxis />
                <Tooltip 
                  labelFormatter={(value) => new Date(value).toLocaleDateString()}
                  formatter={(value) => [formatCurrency(value), 'Price']}
                />
                <Line type="monotone" dataKey="close" stroke="#2563eb" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Backtest Results */}
        {backtestResult && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="h-5 w-5" />
                  {backtestResult.strategy} Strategy Results
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div className="text-center p-4 bg-green-50 rounded-lg">
                    <DollarSign className="h-8 w-8 text-green-600 mx-auto mb-2" />
                    <p className="text-sm text-gray-600">Final Value</p>
                    <p className="text-2xl font-bold text-green-600">
                      {formatCurrency(backtestResult.final_value)}
                    </p>
                  </div>
                  <div className="text-center p-4 bg-blue-50 rounded-lg">
                    <TrendingUp className="h-8 w-8 text-blue-600 mx-auto mb-2" />
                    <p className="text-sm text-gray-600">Total Return</p>
                    <p className="text-2xl font-bold text-blue-600">
                      {formatPercentage(backtestResult.metrics['Total Return'])}
                    </p>
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>Annualized Return:</span>
                    <span className="font-semibold">{formatPercentage(backtestResult.metrics['Annualized Return'])}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Max Drawdown:</span>
                    <span className="font-semibold text-red-600">{formatPercentage(backtestResult.metrics['Max Drawdown'])}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Sharpe Ratio:</span>
                    <span className="font-semibold">{backtestResult.metrics['Sharpe Ratio'].toFixed(4)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Total Trades:</span>
                    <span className="font-semibold">{backtestResult.trade_history.length}</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Portfolio Performance</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={backtestResult.portfolio_history}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="date" 
                      tickFormatter={(value) => new Date(value).toLocaleDateString()}
                    />
                    <YAxis />
                    <Tooltip 
                      labelFormatter={(value) => new Date(value).toLocaleDateString()}
                      formatter={(value) => [formatCurrency(value), 'Portfolio Value']}
                    />
                    <Line type="monotone" dataKey="value" stroke="#10b981" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Strategy Comparison */}
        {comparisonResults && (
          <Card>
            <CardHeader>
              <CardTitle>Strategy Comparison</CardTitle>
              <CardDescription>
                Performance comparison of all trading strategies
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                {Object.entries(comparisonResults).map(([strategy, data]) => (
                  <div key={strategy} className="p-4 border rounded-lg">
                    <h3 className="font-semibold mb-2">{strategy}</h3>
                    <div className="space-y-1 text-sm">
                      <div className="flex justify-between">
                        <span>Final Value:</span>
                        <span className="font-medium">{formatCurrency(data.final_value)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Return:</span>
                        <span className="font-medium">{formatPercentage(data.metrics['Total Return'])}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Sharpe:</span>
                        <span className="font-medium">{data.metrics['Sharpe Ratio'].toFixed(2)}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              
              <ResponsiveContainer width="100%" height={400}>
                <LineChart>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="date" 
                    tickFormatter={(value) => new Date(value).toLocaleDateString()}
                  />
                  <YAxis />
                  <Tooltip 
                    labelFormatter={(value) => new Date(value).toLocaleDateString()}
                    formatter={(value) => [formatCurrency(value), 'Portfolio Value']}
                  />
                  <Legend />
                  {Object.entries(comparisonResults).map(([strategy, data], index) => {
                    const colors = ['#2563eb', '#10b981', '#f59e0b', '#ef4444']
                    return (
                      <Line 
                        key={strategy}
                        type="monotone" 
                        dataKey="value" 
                        data={data.portfolio_history}
                        stroke={colors[index % colors.length]} 
                        strokeWidth={2}
                        name={strategy}
                      />
                    )
                  })}
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}

export default App

