import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Progress } from '@/components/ui/progress'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  ShoppingCart, 
  Mail, 
  TrendingUp, 
  Users, 
  DollarSign, 
  Eye, 
  MousePointer, 
  RefreshCw,
  CheckCircle,
  XCircle,
  Clock,
  Send,
  BarChart3,
  AlertCircle,
  Loader2,
  Edit
} from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts'
import AICKLogo from './assets/AICKLogo.png'
import './App.css'

// API Configuration
const API_BASE_URL = 'http://localhost:8000/api'

// API Helper Functions
const apiCall = async (endpoint, options = {}) => {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    })
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`)
    }
    
    return await response.json()
  } catch (error) {
    console.error('API call failed:', error)
    throw error
  }
}

// Mock data for demonstration (fallback)
const mockStats = {
  totalAbandonedCarts: 156,
  recoveryAttempts: 124,
  successfulRecoveries: 23,
  recoveryRate: 18.5,
  totalRevenueRecovered: 3247.50,
  emailOpenRate: 26.8,
  emailClickRate: 9.2
}

const mockChartData = [
  { date: '2024-01-10', abandoned: 12, recovered: 2 },
  { date: '2024-01-11', abandoned: 15, recovered: 3 },
  { date: '2024-01-12', abandoned: 8, recovered: 1 },
  { date: '2024-01-13', abandoned: 18, recovered: 4 },
  { date: '2024-01-14', abandoned: 22, recovered: 5 },
  { date: '2024-01-15', abandoned: 25, recovered: 6 },
  { date: '2024-01-16', abandoned: 19, recovered: 2 }
]

const pieData = [
  { name: 'Recovered', value: 23, color: '#587834' },
  { name: 'Pending', value: 45, color: '#f08b55' },
  { name: 'Failed', value: 88, color: '#ef4444' }
]

function App() {
  // State Management
  const [selectedCart, setSelectedCart] = useState(null)
  const [isGeneratingMessage, setIsGeneratingMessage] = useState(false)
  const [generatedMessage, setGeneratedMessage] = useState(null)
  const [isStartingRecovery, setIsStartingRecovery] = useState(false)
  const [isSendingEmail, setIsSendingEmail] = useState(false)
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [mockData, setMockData] = useState(null)
  const [stats, setStats] = useState(mockStats)
  const [alerts, setAlerts] = useState([])
  const [testEmail, setTestEmail] = useState('')
  const [editingMessage, setEditingMessage] = useState(false)
  const [editedSubject, setEditedSubject] = useState('')
  const [editedContent, setEditedContent] = useState('')

  // Load mock data on component mount
  useEffect(() => {
    loadMockData()
  }, [])

  const addAlert = (message, type = 'info') => {
    const alert = { id: Date.now(), message, type }
    setAlerts(prev => [...prev, alert])
    setTimeout(() => {
      setAlerts(prev => prev.filter(a => a.id !== alert.id))
    }, 5000)
  }

  const loadMockData = async () => {
    try {
      const response = await apiCall('/agent/mock-data')
      if (response.success) {
        setMockData(response.data)
        addAlert('Mock data loaded successfully', 'success')
      }
    } catch (error) {
      addAlert('Failed to load mock data: ' + error.message, 'error')
    }
  }

  const handleStartRecovery = async () => {
    setIsStartingRecovery(true)
    try {
      const response = await apiCall('/agent/start-recovery', {
        method: 'POST',
        body: JSON.stringify({
          use_mock: true,
          config: { test_mode: true }
        })
      })
      
      if (response.success) {
        addAlert('Recovery workflow started successfully!', 'success')
      } else {
        addAlert('Failed to start recovery workflow', 'error')
      }
    } catch (error) {
      addAlert('Error starting recovery: ' + error.message, 'error')
    } finally {
      setIsStartingRecovery(false)
    }
  }

  const handleRefreshData = async () => {
    setIsRefreshing(true)
    try {
      // Simulate API calls to refresh data
      await Promise.all([
        loadMockData(),
        // Add other data refresh calls here
      ])
      addAlert('Data refreshed successfully', 'success')
    } catch (error) {
      addAlert('Failed to refresh data: ' + error.message, 'error')
    } finally {
      setIsRefreshing(false)
    }
  }

  const handleGenerateMessage = async (cart) => {
    setIsGeneratingMessage(true)
    setSelectedCart(cart)
    
    try {
      const cartData = mockData?.cart || cart
      const customerData = mockData?.customer || {
        first_name: cart?.customerName?.split(' ')[0] || 'Valued Customer',
        email: cart?.customerEmail || 'customer@example.com'
      }

        const response = await apiCall('/agent/generate-message', {
          method: 'POST',
          body: JSON.stringify({
            cart: cartData,
            customer: customerData,
            use_mock: true // Always use mock in frontend demo
          })
        })

      if (response.success) {
        setGeneratedMessage({
          subject: response.email_subject,
          content: response.recovery_message,
          html: response.email_html_content
        })
        setEditedSubject(response.email_subject)
        setEditedContent(response.recovery_message)
        addAlert('Message generated successfully!', 'success')
      } else {
        addAlert('Failed to generate message: ' + (response.error_message || 'Unknown error'), 'error')
      }
    } catch (error) {
      addAlert('Error generating message: ' + error.message, 'error')
    } finally {
      setIsGeneratingMessage(false)
    }
  }

  const handleSendTestEmail = async () => {
    if (!testEmail) {
      addAlert('Please enter an email address', 'error')
      return
    }

    setIsSendingEmail(true)
    try {
      const response = await apiCall('/agent/test-email', {
        method: 'POST',
        body: JSON.stringify({ email: testEmail })
      })

      if (response.success) {
        addAlert(`Test email sent successfully to ${testEmail}!`, 'success')
        setTestEmail('')
      } else {
        addAlert('Failed to send test email: ' + response.message, 'error')
      }
    } catch (error) {
      addAlert('Error sending test email: ' + error.message, 'error')
    } finally {
      setIsSendingEmail(false)
    }
  }

  const handleSendRecoveryEmail = async () => {
    if (!selectedCart || !generatedMessage) {
      addAlert('No message to send', 'error')
      return
    }

    setIsSendingEmail(true)
    try {
      // Use the edited message content
      const messageToSend = editingMessage ? {
        subject: editedSubject,
        content: editedContent
      } : generatedMessage

      // For demo purposes, we'll use the test email endpoint
      // In a real implementation, this would be a separate recovery email endpoint
      const response = await apiCall('/agent/test-email', {
        method: 'POST',
        body: JSON.stringify({ 
          email: selectedCart.customerEmail || 'demo@example.com'
        })
      })

      if (response.success) {
        addAlert(`Recovery email sent to ${selectedCart.customerName}!`, 'success')
        // Update cart status to show email was sent
        if (mockData?.cart) {
          setMockData(prev => ({
            ...prev,
            cart: { ...prev.cart, email_sent: true }
          }))
        }
      } else {
        addAlert('Failed to send recovery email: ' + response.message, 'error')
      }
    } catch (error) {
      addAlert('Error sending recovery email: ' + error.message, 'error')
    } finally {
      setIsSendingEmail(false)
    }
  }

  const handleEditMessage = () => {
    setEditingMessage(true)
  }

  const handleSaveEdit = () => {
    setGeneratedMessage({
      ...generatedMessage,
      subject: editedSubject,
      content: editedContent
    })
    setEditingMessage(false)
    addAlert('Message updated successfully', 'success')
  }

  const handleCancelEdit = () => {
    setEditedSubject(generatedMessage?.subject || '')
    setEditedContent(generatedMessage?.content || '')
    setEditingMessage(false)
  }

  const getStatusBadge = (status) => {
    const statusConfig = {
      recovered: { label: 'Recovered', className: 'aick-status-success' },
      pending: { label: 'Pending', className: 'aick-status-pending' },
      failed: { label: 'Failed', className: 'aick-status-failed' }
    }
    
    const config = statusConfig[status] || statusConfig.pending
    return <Badge className={config.className}>{config.label}</Badge>
  }

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount)
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  // Create cart display data from mock data or fallback
  const displayCarts = mockData ? [{
    cartId: mockData.cart.id,
    customerName: `${mockData.customer.first_name} ${mockData.customer.last_name}`,
    customerEmail: mockData.customer.email,
    totalValue: parseFloat(mockData.cart.total_price),
    currency: mockData.cart.currency,
    abandonedAt: mockData.cart.updated_at,
    recoveryStatus: 'pending',
    emailSent: mockData.cart.email_sent || false,
    emailOpened: false,
    emailClicked: false,
    returnedToCart: false,
    checkoutCompleted: false,
    items: mockData.cart.line_items.map(item => ({
      name: item.title,
      price: parseFloat(item.price),
      quantity: item.quantity,
      image: item.image || `https://via.placeholder.com/60x60/f08b55/ffffff?text=${item.title.charAt(0)}`
    }))
  }] : []

  return (
    <div className="min-h-screen bg-background">
      {/* Alerts */}
      {alerts.length > 0 && (
        <div className="fixed top-4 right-4 z-50 space-y-2">
          {alerts.map(alert => (
            <Alert key={alert.id} className={`w-80 ${
              alert.type === 'success' ? 'border-green-500 bg-green-50' :
              alert.type === 'error' ? 'border-red-500 bg-red-50' :
              'border-blue-500 bg-blue-50'
            }`}>
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{alert.message}</AlertDescription>
            </Alert>
          ))}
        </div>
      )}

      {/* Header */}
      <header className="border-b bg-card">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="aick-logo-container">
              <img src={AICKLogo} alt="AICK Studio" className="aick-logo" />
              <div>
                <div className="aick-brand-text">AICK STUDIO</div>
                <div className="aick-tagline">Cart Recovery Agent</div>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <Button 
                variant="outline" 
                size="sm"
                onClick={handleRefreshData}
                disabled={isRefreshing}
              >
                <RefreshCw className={`h-4 w-4 mr-2 ${isRefreshing ? 'animate-spin' : ''}`} />
                Refresh Data
              </Button>
              <Button 
                className="aick-gradient"
                onClick={handleStartRecovery}
                disabled={isStartingRecovery}
              >
                {isStartingRecovery ? (
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                ) : (
                  <Send className="h-4 w-4 mr-2" />
                )}
                Start Recovery
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-6 py-8">
        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="aick-card-hover">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Abandoned Carts</CardTitle>
              <ShoppingCart className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.totalAbandonedCarts}</div>
              <p className="text-xs text-muted-foreground">+12% from last week</p>
            </CardContent>
          </Card>

          <Card className="aick-card-hover">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Recovery Rate</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.recoveryRate}%</div>
              <p className="text-xs text-muted-foreground">+2.1% from last week</p>
            </CardContent>
          </Card>

          <Card className="aick-card-hover">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Revenue Recovered</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{formatCurrency(stats.totalRevenueRecovered)}</div>
              <p className="text-xs text-muted-foreground">+15.3% from last week</p>
            </CardContent>
          </Card>

          <Card className="aick-card-hover">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Email Open Rate</CardTitle>
              <Mail className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.emailOpenRate}%</div>
              <p className="text-xs text-muted-foreground">+1.2% from last week</p>
            </CardContent>
          </Card>
        </div>

        {/* Main Content */}
        <Tabs defaultValue="dashboard" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
            <TabsTrigger value="carts">Cart Viewer</TabsTrigger>
            <TabsTrigger value="messages">Message Generator</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
          </TabsList>

          <TabsContent value="dashboard" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Recovery Trend Chart */}
              <Card>
                <CardHeader>
                  <CardTitle>Recovery Trend</CardTitle>
                  <CardDescription>Daily abandoned carts vs recovered carts</CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={mockChartData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} />
                      <YAxis />
                      <Tooltip />
                      <Line type="monotone" dataKey="abandoned" stroke="#f08b55" strokeWidth={2} />
                      <Line type="monotone" dataKey="recovered" stroke="#587834" strokeWidth={2} />
                    </LineChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              {/* Recovery Status Distribution */}
              <Card>
                <CardHeader>
                  <CardTitle>Recovery Status</CardTitle>
                  <CardDescription>Distribution of cart recovery outcomes</CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={pieData}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={100}
                        paddingAngle={5}
                        dataKey="value"
                      >
                        {pieData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                  <div className="flex justify-center gap-4 mt-4">
                    {pieData.map((entry, index) => (
                      <div key={index} className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full" style={{ backgroundColor: entry.color }}></div>
                        <span className="text-sm">{entry.name}: {entry.value}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Test Email Section */}
            <Card>
              <CardHeader>
                <CardTitle>Test Email Integration</CardTitle>
                <CardDescription>Send a test email to verify your SendGrid configuration</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex gap-4">
                  <Input
                    placeholder="Enter email address"
                    value={testEmail}
                    onChange={(e) => setTestEmail(e.target.value)}
                    className="flex-1"
                  />
                  <Button 
                    onClick={handleSendTestEmail}
                    disabled={isSendingEmail || !testEmail}
                  >
                    {isSendingEmail ? (
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    ) : (
                      <Send className="h-4 w-4 mr-2" />
                    )}
                    Send Test Email
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="carts" className="space-y-6">
            <div className="grid gap-6">
              {displayCarts.length > 0 ? displayCarts.map((cart) => (
                <Card key={cart.cartId} className="aick-card-hover">
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div>
                        <CardTitle className="text-lg">{cart.customerName}</CardTitle>
                        <CardDescription>{cart.customerEmail}</CardDescription>
                      </div>
                      <div className="text-right">
                        <div className="text-2xl font-bold">{formatCurrency(cart.totalValue)}</div>
                        {getStatusBadge(cart.recoveryStatus)}
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {/* Cart Items */}
                      <div className="space-y-2">
                        <h4 className="font-medium text-sm text-muted-foreground">Cart Items</h4>
                        <div className="flex gap-4 flex-wrap">
                          {cart.items.map((item, index) => (
                            <div key={index} className="flex items-center gap-3 p-2 bg-muted rounded-lg">
                              <img src={item.image} alt={item.name} className="w-12 h-12 rounded" />
                              <div>
                                <div className="font-medium text-sm">{item.name}</div>
                                <div className="text-xs text-muted-foreground">
                                  Qty: {item.quantity} × {formatCurrency(item.price)}
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Status Indicators */}
                      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                        <div className="flex items-center gap-2">
                          {cart.emailSent ? <CheckCircle className="h-4 w-4 text-green-500" /> : <XCircle className="h-4 w-4 text-red-500" />}
                          <span className="text-sm">Email Sent</span>
                        </div>
                        <div className="flex items-center gap-2">
                          {cart.emailOpened ? <Eye className="h-4 w-4 text-green-500" /> : <XCircle className="h-4 w-4 text-red-500" />}
                          <span className="text-sm">Opened</span>
                        </div>
                        <div className="flex items-center gap-2">
                          {cart.emailClicked ? <MousePointer className="h-4 w-4 text-green-500" /> : <XCircle className="h-4 w-4 text-red-500" />}
                          <span className="text-sm">Clicked</span>
                        </div>
                        <div className="flex items-center gap-2">
                          {cart.returnedToCart ? <RefreshCw className="h-4 w-4 text-green-500" /> : <XCircle className="h-4 w-4 text-red-500" />}
                          <span className="text-sm">Returned</span>
                        </div>
                        <div className="flex items-center gap-2">
                          {cart.checkoutCompleted ? <CheckCircle className="h-4 w-4 text-green-500" /> : <Clock className="h-4 w-4 text-yellow-500" />}
                          <span className="text-sm">Completed</span>
                        </div>
                      </div>

                      <div className="flex items-center justify-between pt-4 border-t">
                        <div className="text-sm text-muted-foreground">
                          Abandoned: {formatDate(cart.abandonedAt)}
                        </div>
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => handleGenerateMessage(cart)}
                          disabled={isGeneratingMessage}
                        >
                          {isGeneratingMessage ? (
                            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                          ) : (
                            <Mail className="h-4 w-4 mr-2" />
                          )}
                          Generate Message
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )) : (
                <Card>
                  <CardContent className="text-center py-8">
                    <ShoppingCart className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p className="text-muted-foreground">No abandoned carts found. Click "Refresh Data" to load cart data.</p>
                  </CardContent>
                </Card>
              )}
            </div>
          </TabsContent>

          <TabsContent value="messages" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Message Generator */}
              <Card>
                <CardHeader>
                  <CardTitle>AI Message Generator</CardTitle>
                  <CardDescription>Generate personalized recovery emails using GPT-4</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {selectedCart ? (
                    <div className="space-y-4">
                      <div className="p-4 bg-muted rounded-lg">
                        <h4 className="font-medium">{selectedCart.customerName}</h4>
                        <p className="text-sm text-muted-foreground">{selectedCart.customerEmail}</p>
                        <p className="text-sm">Cart Value: {formatCurrency(selectedCart.totalValue)}</p>
                      </div>
                      
                      {isGeneratingMessage ? (
                        <div className="space-y-3">
                          <div className="flex items-center gap-2">
                            <Loader2 className="h-4 w-4 animate-spin" />
                            <span className="text-sm">Generating personalized message...</span>
                          </div>
                          <Progress value={66} />
                        </div>
                      ) : generatedMessage ? (
                        <div className="space-y-4">
                          {editingMessage ? (
                            <>
                              <div>
                                <label className="text-sm font-medium">Subject Line</label>
                                <Input
                                  value={editedSubject}
                                  onChange={(e) => setEditedSubject(e.target.value)}
                                  className="mt-1"
                                />
                              </div>
                              <div>
                                <label className="text-sm font-medium">Message Content</label>
                                <Textarea
                                  value={editedContent}
                                  onChange={(e) => setEditedContent(e.target.value)}
                                  className="mt-1 min-h-[200px]"
                                />
                              </div>
                              <div className="flex gap-2">
                                <Button onClick={handleSaveEdit} className="aick-gradient">
                                  Save Changes
                                </Button>
                                <Button variant="outline" onClick={handleCancelEdit}>
                                  Cancel
                                </Button>
                              </div>
                            </>
                          ) : (
                            <>
                              <div>
                                <label className="text-sm font-medium">Subject Line</label>
                                <div className="p-3 bg-muted rounded mt-1">
                                  {generatedMessage.subject}
                                </div>
                              </div>
                              <div>
                                <label className="text-sm font-medium">Message Content</label>
                                <div className="p-3 bg-muted rounded mt-1 whitespace-pre-line">
                                  {generatedMessage.content}
                                </div>
                              </div>
                              <div className="flex gap-2">
                                <Button 
                                  className="aick-gradient"
                                  onClick={handleSendRecoveryEmail}
                                  disabled={isSendingEmail}
                                >
                                  {isSendingEmail ? (
                                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                                  ) : (
                                    <Send className="h-4 w-4 mr-2" />
                                  )}
                                  Send Email
                                </Button>
                                <Button variant="outline" onClick={handleEditMessage}>
                                  <Edit className="h-4 w-4 mr-2" />
                                  Edit Message
                                </Button>
                              </div>
                            </>
                          )}
                        </div>
                      ) : null}
                    </div>
                  ) : (
                    <div className="text-center py-8 text-muted-foreground">
                      <Mail className="h-12 w-12 mx-auto mb-4 opacity-50" />
                      <p>Select a cart from the Cart Viewer to generate a recovery message</p>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Email Status Tracker */}
              <Card>
                <CardHeader>
                  <CardTitle>Email Status Tracker</CardTitle>
                  <CardDescription>Monitor email engagement metrics</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-6">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-green-500">{stats.emailOpenRate}%</div>
                        <div className="text-sm text-muted-foreground">Open Rate</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-blue-500">{stats.emailClickRate}%</div>
                        <div className="text-sm text-muted-foreground">Click Rate</div>
                      </div>
                    </div>
                    
                    <div className="space-y-3">
                      <div className="flex justify-between text-sm">
                        <span>Emails Sent</span>
                        <span>{stats.recoveryAttempts}</span>
                      </div>
                      <Progress value={100} />
                      
                      <div className="flex justify-between text-sm">
                        <span>Emails Opened</span>
                        <span>{Math.round(stats.recoveryAttempts * stats.emailOpenRate / 100)}</span>
                      </div>
                      <Progress value={stats.emailOpenRate} />
                      
                      <div className="flex justify-between text-sm">
                        <span>Emails Clicked</span>
                        <span>{Math.round(stats.recoveryAttempts * stats.emailClickRate / 100)}</span>
                      </div>
                      <Progress value={stats.emailClickRate} />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="analytics" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Recovery Performance */}
              <Card>
                <CardHeader>
                  <CardTitle>Recovery Performance</CardTitle>
                  <CardDescription>Weekly recovery statistics</CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={mockChartData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="recovered" fill="#587834" />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              {/* Return Monitor Status */}
              <Card>
                <CardHeader>
                  <CardTitle>Return Monitor Status</CardTitle>
                  <CardDescription>Real-time monitoring of customer return activity</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between p-4 bg-green-50 rounded-lg border border-green-200">
                      <div className="flex items-center gap-3">
                        <CheckCircle className="h-5 w-5 text-green-500" />
                        <div>
                          <div className="font-medium">Recovered Carts</div>
                          <div className="text-sm text-muted-foreground">Successfully completed purchases</div>
                        </div>
                      </div>
                      <div className="text-2xl font-bold text-green-600">{stats.successfulRecoveries}</div>
                    </div>

                    <div className="flex items-center justify-between p-4 bg-orange-50 rounded-lg border border-orange-200">
                      <div className="flex items-center gap-3">
                        <Clock className="h-5 w-5 text-orange-500" />
                        <div>
                          <div className="font-medium">Pending Recovery</div>
                          <div className="text-sm text-muted-foreground">Emails sent, awaiting response</div>
                        </div>
                      </div>
                      <div className="text-2xl font-bold text-orange-600">45</div>
                    </div>

                    <div className="flex items-center justify-between p-4 bg-red-50 rounded-lg border border-red-200">
                      <div className="flex items-center gap-3">
                        <XCircle className="h-5 w-5 text-red-500" />
                        <div>
                          <div className="font-medium">Failed Recovery</div>
                          <div className="text-sm text-muted-foreground">No response or unsubscribed</div>
                        </div>
                      </div>
                      <div className="text-2xl font-bold text-red-600">88</div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}

export default App