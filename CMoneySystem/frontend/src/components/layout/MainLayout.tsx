import { Outlet, Link, useLocation } from 'react-router-dom';
import { Home, TrendingUp, BarChart3, Sliders, History } from 'lucide-react';
import { cn } from '@/utils/helpers';

const navigation = [
  { name: '首页', href: '/', icon: Home },
  { name: '综合分析', href: '/analysis', icon: BarChart3 },
  { name: '股价预测', href: '/prediction', icon: TrendingUp },
  { name: '因子配置', href: '/factors', icon: Sliders },
  { name: '历史记录', href: '/history', icon: History },
];

export default function MainLayout() {
  const location = useLocation();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-primary">
                CMoney 股价预测系统
              </h1>
            </div>
            <nav className="hidden md:flex space-x-8">
              {navigation.map((item) => {
                const Icon = item.icon;
                const isActive =
                  location.pathname === item.href ||
                  (item.href !== '/' && location.pathname.startsWith(item.href));

                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={cn(
                      'inline-flex items-center px-1 pt-1 text-sm font-medium border-b-2 transition-colors',
                      isActive
                        ? 'border-primary text-primary'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    )}
                  >
                    <Icon className="w-4 h-4 mr-2" />
                    {item.name}
                  </Link>
                );
              })}
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <p className="text-center text-sm text-gray-500">
            © 2025 CMoney. 仅供学习和研究使用.
          </p>
        </div>
      </footer>
    </div>
  );
}
