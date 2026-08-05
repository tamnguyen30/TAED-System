import { Layout } from "@/components/Layout";
import { useEmails } from "@/hooks/use-emails";
import { Link } from "wouter";
import { format } from "date-fns";
import { Search, AlertTriangle, CheckCircle2, ShieldQuestion } from "lucide-react";
import { useState } from "react";
import { cn } from "@/lib/utils";

export default function Inbox() {
  const { data: emails, isLoading } = useEmails();
  const [searchTerm, setSearchTerm] = useState("");

  const filteredEmails = emails?.filter(email => 
    email.subject.toLowerCase().includes(searchTerm.toLowerCase()) || 
    email.sender.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h2 className="text-3xl font-display font-bold">Analysis Inbox</h2>
            <p className="text-muted-foreground">Review processed communications and verdicts.</p>
          </div>
          
          <div className="relative w-full md:w-96">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <input 
              type="text"
              placeholder="Search subjects or senders..."
              className="w-full pl-10 pr-4 py-2 rounded-xl bg-card border border-border focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/50 transition-all"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
        </div>

        {/* Email List */}
        <div className="bg-card border border-border rounded-2xl overflow-hidden shadow-sm">
          {isLoading ? (
             <div className="p-20 text-center">
               <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin mx-auto" />
             </div>
          ) : filteredEmails?.length === 0 ? (
            <div className="p-20 text-center text-muted-foreground">
              <Search className="w-12 h-12 mx-auto mb-4 opacity-20" />
              <p>No emails found matching your criteria.</p>
            </div>
          ) : (
            <div className="divide-y divide-border/50">
              <div className="grid grid-cols-12 gap-4 p-4 text-xs font-semibold text-muted-foreground uppercase tracking-wider bg-black/20">
                <div className="col-span-1 text-center">Verdict</div>
                <div className="col-span-6 md:col-span-5">Message Details</div>
                <div className="hidden md:block col-span-2 text-center">Trust Score</div>
                <div className="hidden md:block col-span-2 text-center">Attack Type</div>
                <div className="col-span-5 md:col-span-2 text-right">Time</div>
              </div>
              
              {filteredEmails?.map((email) => (
                <Link key={email.id} href={`/email/${email.id}`} className="grid grid-cols-12 gap-4 p-4 items-center hover:bg-white/5 transition-colors cursor-pointer group">
                  {/* Verdict Icon */}
                  <div className="col-span-1 flex justify-center">
                    {email.analysis?.verdict === 'phishing' ? (
                      <div className="w-8 h-8 rounded-full bg-destructive/10 flex items-center justify-center text-destructive ring-1 ring-destructive/30 group-hover:bg-destructive group-hover:text-destructive-foreground transition-colors">
                        <AlertTriangle className="w-4 h-4" />
                      </div>
                    ) : email.analysis?.verdict === 'benign' ? (
                      <div className="w-8 h-8 rounded-full bg-emerald-500/10 flex items-center justify-center text-emerald-500 ring-1 ring-emerald-500/30 group-hover:bg-emerald-500 group-hover:text-white transition-colors">
                        <CheckCircle2 className="w-4 h-4" />
                      </div>
                    ) : (
                      <div className="w-8 h-8 rounded-full bg-yellow-500/10 flex items-center justify-center text-yellow-500 ring-1 ring-yellow-500/30">
                        <ShieldQuestion className="w-4 h-4" />
                      </div>
                    )}
                  </div>

                  {/* Message Details */}
                  <div className="col-span-6 md:col-span-5 min-w-0">
                    <h4 className="font-semibold text-foreground truncate group-hover:text-primary transition-colors">{email.subject}</h4>
                    <p className="text-sm text-muted-foreground truncate">{email.sender}</p>
                  </div>

                  {/* Trust Score */}
                  <div className="hidden md:flex col-span-2 flex-col items-center justify-center">
                    <div className="w-full max-w-[80px] h-1.5 bg-secondary rounded-full overflow-hidden">
                      <div 
                        className={cn("h-full rounded-full", 
                          (email.analysis?.trustScore || 0) > 80 ? "bg-emerald-500" : 
                          (email.analysis?.trustScore || 0) > 50 ? "bg-yellow-500" : "bg-destructive"
                        )}
                        style={{ width: `${email.analysis?.trustScore || 0}%` }}
                      />
                    </div>
                    <span className="text-xs font-mono mt-1 text-muted-foreground">{email.analysis?.trustScore}%</span>
                  </div>

                  {/* Attack Type */}
                  <div className="hidden md:block col-span-2 text-center">
                    {email.analysis?.attackType ? (
                      <span className="px-2 py-1 rounded text-[10px] font-bold uppercase bg-background border border-border text-muted-foreground">
                        {email.analysis.attackType}
                      </span>
                    ) : (
                      <span className="text-muted-foreground text-xs">-</span>
                    )}
                  </div>

                  {/* Time */}
                  <div className="col-span-5 md:col-span-2 text-right text-sm text-muted-foreground font-mono">
                    {email.receivedAt && format(new Date(email.receivedAt), 'HH:mm')}
                    <div className="text-xs opacity-50">{email.receivedAt && format(new Date(email.receivedAt), 'MMM d')}</div>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}
