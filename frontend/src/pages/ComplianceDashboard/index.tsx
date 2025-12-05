import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import {
  Shield,
  Info,
  CheckCircle2,
  AlertTriangle,
  Lock,
  FileText,
  Clock,
  ChevronRight,
  ExternalLink,
  ShieldCheck,
  Eye,
  Key,
} from 'lucide-react';
import { Link } from 'react-router-dom';

// Sample compliance metrics for preview
const COMPLIANCE_METRICS = [
  { label: 'PII Scan Rate', value: '100%', status: 'success', icon: Eye },
  { label: 'DLP Coverage', value: '98.5%', status: 'success', icon: ShieldCheck },
  { label: 'Audit Events (24h)', value: '1,247', status: 'info', icon: Clock },
  { label: 'Pending Reviews', value: '3', status: 'warning', icon: AlertTriangle },
];

const RECENT_EVENTS = [
  { type: 'success', message: 'Memory export verified', time: '2 min ago', icon: CheckCircle2 },
  { type: 'success', message: 'PII redaction completed', time: '5 min ago', icon: Shield },
  { type: 'warning', message: 'New memory region flagged for review', time: '12 min ago', icon: AlertTriangle },
  { type: 'success', message: 'DLP manifest sealed', time: '15 min ago', icon: Lock },
  { type: 'success', message: 'Cryptographic verification passed', time: '22 min ago', icon: Key },
];

const QUICK_LINKS = [
  {
    title: 'View Audit Logs',
    description: 'Browse full audit trail with filtering',
    href: '/agent',
    available: true,
  },
  {
    title: 'Export Compliance Report',
    description: 'Generate PDF/JSON compliance documentation',
    href: '/',
    available: true,
  },
  {
    title: 'Configure PII Rules',
    description: 'Customize detection patterns and thresholds',
    href: '/playground',
    available: true,
  },
];

export default function ComplianceDashboard() {
  return (
    <div className="h-full overflow-auto p-8">
      <div className="mb-8">
        <h1 className="text-4xl font-display font-bold text-gradient">Compliance Dashboard</h1>
        <p className="mt-2 text-gray-400">Audit trails, PII detection, and cryptographic verification</p>
      </div>

      {/* Quick Metrics Grid */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4 mb-8">
        {COMPLIANCE_METRICS.map((metric) => {
          const Icon = metric.icon;
          const statusColors = {
            success: 'text-success bg-success/20',
            warning: 'text-warning bg-warning/20',
            info: 'text-primary-400 bg-primary-500/20',
          };
          return (
            <Card key={metric.label} className="glass-morphism">
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-xs text-gray-500 uppercase tracking-wider">{metric.label}</p>
                    <p className="text-2xl font-bold text-gray-200 mt-1">{metric.value}</p>
                  </div>
                  <div className={`h-10 w-10 rounded-lg flex items-center justify-center ${statusColors[metric.status as keyof typeof statusColors]}`}>
                    <Icon className="h-5 w-5" aria-hidden="true" />
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Main Dashboard Card - Coming Soon */}
        <Card className="glass-morphism lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Shield className="h-5 w-5 text-success" aria-hidden="true" />
              <span>Compliance & Audit Center</span>
              <span className="ml-2 text-xs bg-success/20 text-success px-2 py-0.5 rounded-full">Coming Soon</span>
            </CardTitle>
            <CardDescription>Interactive audit timeline with full traceability</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex h-48 items-center justify-center border border-dashed border-white/20 rounded-lg bg-gradient-to-br from-success/5 to-primary-500/5">
              <div className="text-center">
                <Shield className="mx-auto h-12 w-12 text-success/50 animate-pulse" aria-hidden="true" />
                <p className="mt-4 text-gray-400 font-medium">
                  Full Compliance Dashboard
                </p>
                <p className="mt-2 text-sm text-gray-500">
                  Audit Timeline • PII Detection • Cryptographic Verification • DLP Tracking
                </p>
                <div className="mt-4 flex items-center justify-center space-x-2 text-xs text-gray-500">
                  <span className="flex items-center space-x-1">
                    <div className="h-2 w-2 rounded-full bg-success animate-pulse" />
                    <span>Backend Ready</span>
                  </span>
                  <span>•</span>
                  <span className="flex items-center space-x-1">
                    <div className="h-2 w-2 rounded-full bg-yellow-500" />
                    <span>Frontend In Progress</span>
                  </span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Recent Events Preview */}
        <Card className="glass-morphism">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2 text-base">
              <Clock className="h-4 w-4 text-primary-500" aria-hidden="true" />
              <span>Recent Compliance Events</span>
            </CardTitle>
            <CardDescription>Latest audit trail activity</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {RECENT_EVENTS.map((event, idx) => {
                const Icon = event.icon;
                const typeColors = {
                  success: 'text-success',
                  warning: 'text-warning',
                  error: 'text-red-400',
                };
                return (
                  <div key={idx} className="flex items-start space-x-3 pb-3 border-b border-white/5 last:border-0 last:pb-0">
                    <Icon className={`h-4 w-4 mt-0.5 ${typeColors[event.type as keyof typeof typeColors]}`} aria-hidden="true" />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-gray-300 truncate">{event.message}</p>
                      <p className="text-xs text-gray-500">{event.time}</p>
                    </div>
                  </div>
                );
              })}
            </div>
            <Button variant="ghost" size="sm" className="w-full mt-4 text-gray-400 hover:text-white">
              View All Events
              <ChevronRight className="h-4 w-4 ml-2" aria-hidden="true" />
            </Button>
          </CardContent>
        </Card>

        {/* Quick Links */}
        <Card className="glass-morphism">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2 text-base">
              <FileText className="h-4 w-4 text-accent-500" aria-hidden="true" />
              <span>Quick Actions</span>
            </CardTitle>
            <CardDescription>Common compliance operations</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {QUICK_LINKS.map((link) => (
                <Link
                  key={link.title}
                  to={link.href}
                  className="flex items-center justify-between p-3 rounded-lg border border-white/10 bg-white/5 hover:bg-white/10 hover:border-success/30 transition-all group"
                >
                  <div>
                    <p className="text-sm font-medium text-gray-200 group-hover:text-white">
                      {link.title}
                    </p>
                    <p className="text-xs text-gray-500">{link.description}</p>
                  </div>
                  <ChevronRight className="h-4 w-4 text-gray-500 group-hover:text-success transition-colors" aria-hidden="true" />
                </Link>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* API Documentation Link */}
      <div className="mt-6 p-4 rounded-lg border border-white/10 bg-white/5">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Info className="h-5 w-5 text-gray-400" aria-hidden="true" />
            <div>
              <p className="text-sm text-gray-300">Need to integrate with the Compliance API?</p>
              <p className="text-xs text-gray-500">GUMAS ethics validation and DLP tracking endpoints available</p>
            </div>
          </div>
          <Link to="/playground">
            <Button variant="outline" size="sm">
              <ExternalLink className="h-4 w-4 mr-2" aria-hidden="true" />
              Try Playground
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
}
