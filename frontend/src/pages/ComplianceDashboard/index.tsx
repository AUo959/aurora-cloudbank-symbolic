import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Shield, Info } from 'lucide-react';

export default function ComplianceDashboard() {
  return (
    <div className="h-full p-8">
      <div className="mb-8">
        <h1 className="text-4xl font-display font-bold text-gradient">Compliance Dashboard</h1>
        <p className="mt-2 text-gray-400">Audit trails, PII detection, and cryptographic verification</p>
      </div>

      <Card className="glass-morphism">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Shield className="h-5 w-5 text-success" />
            <span>Compliance & Audit</span>
          </CardTitle>
          <CardDescription>Full audit trail explorer coming soon</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex h-96 items-center justify-center border border-dashed border-white/20 rounded-lg">
            <div className="text-center">
              <Info className="mx-auto h-12 w-12 text-gray-500" />
              <p className="mt-4 text-gray-400">
                Compliance Dashboard
              </p>
              <p className="mt-2 text-sm text-gray-500">
                Audit timeline • PII detection • Cryptographic verification • DLP tracking
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
