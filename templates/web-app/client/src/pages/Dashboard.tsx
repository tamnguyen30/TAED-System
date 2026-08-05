import { Layout } from "@/components/Layout";
import { MetricCard } from "@/components/MetricCard";
import { TrustGauge } from "@/components/TrustGauge";
import { useStats, useEmails } from "@/hooks/use-emails";
import { ShieldAlert, ShieldCheck, Activity, Search, AlertTriangle, CheckCircle2 } from "lucide-react";
import { Link } from "wouter";
import { format } from "date-fns";

export default function Dashboard() {
  const { data: stats, isLoading: statsLoading } = useStats();
  const { data: recentEmails, isLoading: emailsLoading } = useEmails();

  // Slice to get only 5 most recent
  const recentActivity = recentEmails?.slice(0, 5) || [];

  if (statsLoading || emailsLoading) {
    return (
      <Layout>
        <div className="flex h-[80vh] items-center justify-center">
          <div className="flex flex-col items-center gap-4">
            <div className="w-16 h-16 border-4 border-primary/30 border-t-primary rounded-full animate-spin" />
            <p className="text-muted-foreground animate-pulse">Initializing Defense Systems...</p>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
          <div>
            <h2 className="text-3xl font-display font-bold text-foreground">System Overview</h2>
            <p className="text-muted-foreground">Real-time threat monitoring and trust analysis.</p>
          </div>
          <div className="flex items-center gap-2 text-sm text-primary bg-primary/10 px-3 py-1.5 rounded-full border border-primary/20 animate-pulse">
            <Activity className="w-4 h-4" />
            <span className="font-semibold">SYSTEM ACTIVE</span>
          </div>
        </div>

        {/* Top Stats Row */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <MetricCard
            title="Total Scanned"
            value={stats?.totalScanned || 0}
            icon={Search}
            trend="+12% from last week"
            color="default"
          />
          <MetricCard
            title="Threats Blocked"
            value={stats?.threatsBlocked || 0}
            icon={ShieldAlert}
            trend="Active mitigation engaged"
            color="destructive"
          />
          <MetricCard
            title="Avg Trust Score"
            value={`${stats?.avgTrustScore || 0}%`}
            icon={ShieldCheck}
            trend="System integrity stable"
            color="primary"
          />
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Recent Activity Column (2/3 width) */}
          <div className="lg:col-span-2 space-y-6">
            <div className="flex items-center justify-between">
              <h3 className="text-xl font-display font-semibold">Recent Analysis</h3>
              <Link href="/inbox" className="text-sm text-primary hover:text-primary/80 hover:underline">
                View All
              </Link>
            </div>

            <div className="bg-card border border-border rounded-2xl overflow-hidden shadow-sm">
              {recentActivity.length === 0 ? (
                <div className="p-12 text-center text-muted-foreground">
                  <ShieldCheck className="w-12 h-12 mx-auto mb-4 opacity-20" />
                  <p>No activity recorded yet.</p>
                </div>
              ) : (
                <div className="divide-y divide-border/50">
                  {recentActivity.map((email) => (
                    <Link key={email.id} href={`/email/${email.id}`} className="block hover:bg-white/5 transition-colors">
                      <div className="p-4 flex items-center gap-4">
                        <div className={`
                          flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center border
                          ${email.analysis?.verdict === 'phishing' 
                            ? 'bg-destructive/10 border-destructive/20 text-destructive' 
                            : 'bg-emerald-500/10 border-emerald-500/20 text-emerald-500'}
                        `}>
                          {email.analysis?.verdict === 'phishing' ? <AlertTriangle className="w-5 h-5" /> : <CheckCircle2 className="w-5 h-5" />}
                        </div>
                        
                        <div className="flex-grow min-w-0">
                          <h4 className="font-medium truncate">{email.subject}</h4>
                          <p className="text-sm text-muted-foreground truncate">{email.sender}</p>
                        </div>

                        <div className="text-right hidden sm:block">
                          <div className={`text-sm font-bold ${
                             email.analysis?.trustScore && email.analysis.trustScore < 50 ? 'text-destructive' : 'text-emerald-500'
                          }`}>
                            {email.analysis?.trustScore}% Trust
                          </div>
                          <div className="text-xs text-muted-foreground">
                            {email.receivedAt && format(new Date(email.receivedAt), 'MMM d, HH:mm')}
                          </div>
                        </div>
                      </div>
                    </Link>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* System Health Column (1/3 width) */}
          <div className="space-y-6">
            <h3 className="text-xl font-display font-semibold">System Integrity</h3>
            <div className="bg-card border border-border rounded-2xl p-6 flex flex-col items-center justify-center min-h-[300px] shadow-lg shadow-black/20">
              <TrustGauge score={stats?.avgTrustScore || 0} size={220} />
              <div className="mt-6 text-center space-y-2">
                <p className="text-sm text-muted-foreground">
                  Overall system trust level based on aggregate analysis of all processed emails.
                </p>
                <div className="flex justify-center gap-4 pt-4">
                  <div className="flex items-center gap-2 text-xs">
                    <span className="w-2 h-2 rounded-full bg-[hsl(var(--trust-high))]"></span> Safe
                  </div>
                  <div className="flex items-center gap-2 text-xs">
                    <span className="w-2 h-2 rounded-full bg-[hsl(var(--trust-med))]"></span> Warning
                  </div>
                  <div className="flex items-center gap-2 text-xs">
                    <span className="w-2 h-2 rounded-full bg-[hsl(var(--trust-low))]"></span> Critical
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
