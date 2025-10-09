import { useState } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell
} from 'recharts'
import { 
  Users, 
  TrendingUp, 
  DollarSign, 
  Activity,
  Bell,
  Search,
  Menu,
  Settings,
  LogOut
} from 'lucide-react'
import './App.css'

const projectsData = [
  { name: 'يناير', projects: 12 },
  { name: 'فبراير', projects: 19 },
  { name: 'مارس', projects: 15 },
  { name: 'أبريل', projects: 25 },
  { name: 'مايو', projects: 22 },
  { name: 'يونيو', projects: 30 }
]

const revenueData = [
  { name: 'الاستشارات', value: 35, color: '#8B7355' },
  { name: 'التسويق الرقمي', value: 30, color: '#D4C4A8' },
  { name: 'التصميم الإبداعي', value: 20, color: '#A0956B' },
  { name: 'التطوير التقني', value: 15, color: '#F5F0E8' }
]

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      {/* Sidebar */}
      <div className={`fixed inset-y-0 left-0 z-50 w-64 bg-white dark:bg-gray-800 shadow-lg transform ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0`}>
        <div className="flex items-center justify-center h-16 bg-gradient-to-r from-amber-600 to-amber-700">
          <h1 className="text-xl font-bold text-white">لوحة تحكم آيديا</h1>
        </div>
        <nav className="mt-8">
          <div className="px-4 space-y-2">
            <a href="#" className="flex items-center px-4 py-2 text-gray-700 dark:text-gray-200 bg-amber-100 dark:bg-amber-900 rounded-lg">
              <Activity className="w-5 h-5 ml-3" />
              لوحة القيادة
            </a>
            <a href="#" className="flex items-center px-4 py-2 text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg">
              <Users className="w-5 h-5 ml-3" />
              العملاء
            </a>
            <a href="#" className="flex items-center px-4 py-2 text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg">
              <TrendingUp className="w-5 h-5 ml-3" />
              المشاريع
            </a>
            <a href="#" className="flex items-center px-4 py-2 text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg">
              <DollarSign className="w-5 h-5 ml-3" />
              التقارير المالية
            </a>
            <a href="#" className="flex items-center px-4 py-2 text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg">
              <Settings className="w-5 h-5 ml-3" />
              الإعدادات
            </a>
          </div>
        </nav>
      </div>

      {/* Main Content */}
      <div className="lg:mr-64">
        {/* Header */}
        <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between px-6 py-4">
            <div className="flex items-center">
              <Button
                variant="ghost"
                size="sm"
                className="lg:hidden ml-2"
                onClick={() => setSidebarOpen(!sidebarOpen)}
              >
                <Menu className="w-6 h-6" />
              </Button>
              <h2 className="text-xl font-semibold text-gray-800 dark:text-white">مرحباً بك في لوحة تحكم آيديا</h2>
            </div>
            <div className="flex items-center space-x-4">
              <Button variant="ghost" size="sm">
                <Bell className="w-5 h-5" />
              </Button>
              <Button variant="ghost" size="sm">
                <Search className="w-5 h-5" />
              </Button>
              <Button variant="ghost" size="sm">
                <LogOut className="w-5 h-5" />
              </Button>
            </div>
          </div>
        </header>

        {/* Dashboard Content */}
        <main className="p-6">
          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <Card className="bg-gradient-to-r from-blue-500 to-blue-600 text-white">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">إجمالي العملاء</CardTitle>
                <Users className="h-4 w-4" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">245</div>
                <p className="text-xs opacity-80">+12% من الشهر الماضي</p>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-r from-green-500 to-green-600 text-white">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">المشاريع النشطة</CardTitle>
                <Activity className="h-4 w-4" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">32</div>
                <p className="text-xs opacity-80">+8% من الشهر الماضي</p>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-r from-amber-500 to-amber-600 text-white">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">الإيرادات الشهرية</CardTitle>
                <DollarSign className="h-4 w-4" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">$45,231</div>
                <p className="text-xs opacity-80">+20% من الشهر الماضي</p>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-r from-purple-500 to-purple-600 text-white">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">معدل الرضا</CardTitle>
                <TrendingUp className="h-4 w-4" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">98.5%</div>
                <p className="text-xs opacity-80">+2% من الشهر الماضي</p>
              </CardContent>
            </Card>
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            <Card>
              <CardHeader>
                <CardTitle>المشاريع الشهرية</CardTitle>
                <CardDescription>عدد المشاريع المكتملة خلال الأشهر الستة الماضية</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={projectsData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="projects" fill="#8B7355" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>توزيع الإيرادات</CardTitle>
                <CardDescription>توزيع الإيرادات حسب نوع الخدمة</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={revenueData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {revenueData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
                <div className="mt-4 space-y-2">
                  {revenueData.map((item, index) => (
                    <div key={index} className="flex items-center justify-between">
                      <div className="flex items-center">
                        <div className="w-3 h-3 rounded-full ml-2" style={{ backgroundColor: item.color }}></div>
                        <span className="text-sm">{item.name}</span>
                      </div>
                      <span className="text-sm font-medium">{item.value}%</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Recent Projects */}
          <Card>
            <CardHeader>
              <CardTitle>المشاريع الحديثة</CardTitle>
              <CardDescription>آخر المشاريع التي تم العمل عليها</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {[
                  { name: 'تطوير موقع شركة التقنية المتقدمة', client: 'شركة التقنية المتقدمة', status: 'قيد التنفيذ', progress: 75 },
                  { name: 'حملة تسويقية لمتجر الأزياء', client: 'متجر الأناقة', status: 'مكتمل', progress: 100 },
                  { name: 'تصميم هوية بصرية لمطعم', client: 'مطعم الذواقة', status: 'قيد المراجعة', progress: 90 },
                  { name: 'تطبيق جوال للتوصيل', client: 'شركة التوصيل السريع', status: 'قيد التنفيذ', progress: 45 }
                ].map((project, index) => (
                  <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex-1">
                      <h4 className="font-medium">{project.name}</h4>
                      <p className="text-sm text-gray-600 dark:text-gray-400">{project.client}</p>
                      <div className="mt-2">
                        <Progress value={project.progress} className="w-full" />
                      </div>
                    </div>
                    <div className="mr-4">
                      <Badge variant={project.status === 'مكتمل' ? 'default' : project.status === 'قيد التنفيذ' ? 'secondary' : 'outline'}>
                        {project.status}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </main>
      </div>
    </div>
  )
}

export default App

