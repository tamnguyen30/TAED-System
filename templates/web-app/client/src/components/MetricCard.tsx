import { cn } from "@/lib/utils";
import { LucideIcon } from "lucide-react";

interface MetricCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  trend?: string;
  color?: "default" | "primary" | "destructive" | "warning";
  className?: string;
}

export function MetricCard({ title, value, icon: Icon, trend, color = "default", className }: MetricCardProps) {
  const colorStyles = {
    default: "text-foreground bg-card border-border",
    primary: "text-primary bg-primary/5 border-primary/20",
    destructive: "text-destructive bg-destructive/5 border-destructive/20",
    warning: "text-yellow-500 bg-yellow-500/5 border-yellow-500/20",
  };

  const iconStyles = {
    default: "text-muted-foreground",
    primary: "text-primary",
    destructive: "text-destructive",
    warning: "text-yellow-500",
  };

  return (
    <div className={cn(
      "relative overflow-hidden rounded-2xl p-6 border transition-all duration-300 hover:shadow-lg",
      colorStyles[color],
      className
    )}>
      <div className="flex justify-between items-start">
        <div>
          <p className="text-sm font-medium text-muted-foreground uppercase tracking-wider mb-1">{title}</p>
          <h3 className="text-3xl font-display font-bold">{value}</h3>
          {trend && (
            <p className="text-xs mt-2 text-muted-foreground">
              {trend}
            </p>
          )}
        </div>
        <div className={cn("p-3 rounded-xl bg-background/50 backdrop-blur-sm border border-white/5", iconStyles[color])}>
          <Icon className="w-6 h-6" />
        </div>
      </div>
      
      {/* Background Decor */}
      <div className="absolute -bottom-4 -right-4 w-24 h-24 bg-gradient-to-br from-white/5 to-transparent rounded-full blur-2xl" />
    </div>
  );
}
