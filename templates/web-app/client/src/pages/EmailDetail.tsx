import { Layout } from "@/components/Layout";
import { TrustGauge } from "@/components/TrustGauge";
import { useEmail } from "@/hooks/use-emails";
import { useRoute } from "wouter";
import { format } from "date-fns";
import { AlertTriangle, CheckCircle2, ArrowLeft, Shield, BarChart3, Lock, Eye, Zap } from "lucide-react";
import { Link } from "wouter";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

export default function EmailDetail() {
  const [, params] = useRoute("/email/:id");
  const id = parseInt(params?.id || "0");
  const { data: email, isLoading } = useEmail(id);

  if (isLoading) {
    return (
      <Layout>
        <div className="flex h-[80vh] items-center justify-center">
          <div className="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full"></div>
        </div>
      </Layout>
    );
  }

  if (!email) {
    return (
      <Layout>
        <div className="text-center py-20">
          <h2 className="text-2xl font-bold">Email not found</h2>
          <Link href="/inbox" className="text-primary hover:underline mt-4 inline-block">Return to Inbox</Link>
        </div>
      </Layout>
    );
  }

  const analysis = email.analysis;
  
  // Data for bar chart
  const metricsData = [
    { name: 'Confidence', value: analysis?.confidence || 0, color: '#0ea5e9' }, // sky-500
    { name: 'Fidelity', value: analysis?.fidelity || 0, color: '#8b5cf6' },   // violet-500
    { name: 'Stability', value: analysis?.stability || 0, color: '#ec4899' }, // pink-500
  ];

  return (
    <Layout>
      <div className="max-w-6xl mx-auto space-y-6">
        <Link href="/inbox" className="inline-flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors mb-4">
          <ArrowLeft className="w-4 h-4" /> Back to Inbox
        </Link>

        {/* Top Header Card */}
        <div className="bg-card border border-border rounded-2xl p-6 shadow-lg">
          <div className="flex flex-col md:flex-row justify-between md:items-start gap-6">
            <div className="space-y-2 flex-grow">
              <div className="flex items-center gap-3 mb-1">
                {analysis?.verdict === 'phishing' ? (
                  <span className="bg-destructive/10 text-destructive border border-destructive/20 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider flex items-center gap-1.5">
                    <AlertTriangle className="w-3.5 h-3.5" /> Phishing Detected
                  </span>
                ) : (
                  <span className="bg-emerald-500/10 text-emerald-500 border border-emerald-500/20 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider flex items-center gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5" /> Verified Safe
                  </span>
                )}
                {analysis?.attackType && (
                  <span className="bg-secondary text-secondary-foreground border border-border px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider">
                    Type: {analysis.attackType}
                  </span>
                )}
              </div>
              <h1 className="text-2xl md:text-3xl font-display font-bold text-foreground leading-tight">
                {email.subject}
              </h1>
              <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-6 text-sm text-muted-foreground pt-2">
                <span className="font-mono bg-black/20 px-2 py-1 rounded border border-white/5">From: {email.sender}</span>
                <span>{email.receivedAt && format(new Date(email.receivedAt), 'MMMM d, yyyy • HH:mm:ss')}</span>
              </div>
            </div>
            
            <div className="flex-shrink-0">
               <div className="bg-background/50 rounded-xl border border-border p-4 flex flex-col items-center min-w-[140px]">
                 <span className="text-xs text-muted-foreground uppercase tracking-widest font-semibold mb-2">Verdict ID</span>
                 <span className="font-mono text-lg font-bold text-primary">#{analysis?.id.toString().padStart(6, '0')}</span>
               </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column: Analysis Metrics */}
          <div className="space-y-6">
            {/* Trust Score Gauge */}
            <div className="bg-card border border-border rounded-2xl p-6 flex flex-col items-center shadow-lg relative overflow-hidden group">
              <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-primary/50 to-transparent opacity-50 group-hover:opacity-100 transition-opacity" />
              <h3 className="text-lg font-display font-semibold mb-4 flex items-center gap-2">
                <Shield className="w-5 h-5 text-primary" /> Trust Analysis
              </h3>
              <TrustGauge score={analysis?.trustScore || 0} size={240} />
            </div>

            {/* Metrics Breakdown */}
            <div className="bg-card border border-border rounded-2xl p-6 shadow-lg">
              <h3 className="text-lg font-display font-semibold mb-6 flex items-center gap-2">
                <BarChart3 className="w-5 h-5 text-primary" /> Model Metrics
              </h3>
              <div className="h-[200px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={metricsData} layout="vertical" margin={{ left: 20, right: 20 }}>
                    <XAxis type="number" domain={[0, 100]} hide />
                    <YAxis dataKey="name" type="category" width={80} tick={{ fill: '#94a3b8', fontSize: 12 }} />
                    <Tooltip 
                      cursor={{fill: 'rgba(255,255,255,0.05)'}}
                      contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', borderRadius: '8px' }}
                    />
                    <Bar dataKey="value" radius={[0, 4, 4, 0]} barSize={20}>
                      {metricsData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
              
              <div className="grid grid-cols-3 gap-2 mt-4 pt-4 border-t border-border">
                {metricsData.map((m) => (
                  <div key={m.name} className="text-center">
                    <div className="text-[10px] uppercase tracking-wider text-muted-foreground">{m.name}</div>
                    <div className="text-lg font-bold" style={{ color: m.color }}>{m.value}%</div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Right Column: Content & Explanation */}
          <div className="lg:col-span-2 space-y-6">
            
            {/* AI Explanation */}
            <div className="bg-gradient-to-br from-card to-card/90 border border-border rounded-2xl p-6 shadow-lg relative overflow-hidden">
              <div className="absolute top-0 right-0 p-4 opacity-10">
                <Zap className="w-24 h-24 text-primary" />
              </div>
              
              <h3 className="text-lg font-display font-semibold mb-4 flex items-center gap-2 relative z-10">
                <Eye className="w-5 h-5 text-primary" /> XAI Explanation
              </h3>
              
              <div className="bg-background/60 backdrop-blur-sm rounded-xl p-6 border border-white/5 relative z-10">
                <p className="text-lg leading-relaxed text-foreground/90">
                  {analysis?.explanation}
                </p>
                
                {analysis?.attackType && (
                  <div className="mt-4 pt-4 border-t border-white/10">
                    <h4 className="text-sm font-semibold text-primary mb-1 uppercase tracking-wide">Defense Insight</h4>
                    <p className="text-sm text-muted-foreground">
                      This email exhibits characteristics of a <span className="text-foreground font-medium">{analysis.attackType}</span> attack. 
                      The system detected this with {analysis.confidence}% confidence.
                    </p>
                  </div>
                )}
              </div>
            </div>

            {/* Email Content */}
            <div className="bg-card border border-border rounded-2xl p-6 shadow-lg">
              <h3 className="text-lg font-display font-semibold mb-4 flex items-center gap-2">
                <Lock className="w-5 h-5 text-primary" /> Raw Content Analysis
              </h3>
              <div className="bg-black/30 rounded-xl p-6 font-mono text-sm leading-relaxed border border-white/5 whitespace-pre-wrap text-muted-foreground">
                {email.content}
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
