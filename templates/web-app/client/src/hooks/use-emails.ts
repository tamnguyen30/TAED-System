import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api, buildUrl, type InsertEmail } from "@shared/routes";
import { useToast } from "@/hooks/use-toast";

// === TYPES ===
// Importing types directly from schema/routes is preferred, 
// but we define helper types for components where needed if they don't exist in exports

// === HOOKS ===

// GET /api/emails
export function useEmails() {
  return useQuery({
    queryKey: [api.emails.list.path],
    queryFn: async () => {
      const res = await fetch(api.emails.list.path);
      if (!res.ok) throw new Error("Failed to fetch emails");
      // Validate with Zod schema from routes
      return api.emails.list.responses[200].parse(await res.json());
    },
  });
}

// GET /api/emails/:id
export function useEmail(id: number) {
  return useQuery({
    queryKey: [api.emails.get.path, id],
    queryFn: async () => {
      const url = buildUrl(api.emails.get.path, { id });
      const res = await fetch(url);
      if (res.status === 404) return null;
      if (!res.ok) throw new Error("Failed to fetch email details");
      return api.emails.get.responses[200].parse(await res.json());
    },
    enabled: !!id,
  });
}

// POST /api/analyze (Create Email + Analyze)
export function useAnalyzeEmail() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: async (data: InsertEmail) => {
      // Validate input before sending (client-side validation)
      const validated = api.emails.analyze.input.parse(data);
      
      const res = await fetch(api.emails.analyze.path, {
        method: api.emails.analyze.method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(validated),
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.message || "Analysis failed");
      }

      return api.emails.analyze.responses[201].parse(await res.json());
    },
    onSuccess: (data) => {
      toast({
        title: "Analysis Complete",
        description: `Email analyzed with verdict: ${data.analysis?.verdict}`,
        variant: data.analysis?.verdict === "phishing" ? "destructive" : "default",
      });
      // Invalidate both list and stats to update dashboard
      queryClient.invalidateQueries({ queryKey: [api.emails.list.path] });
      queryClient.invalidateQueries({ queryKey: [api.stats.get.path] });
    },
    onError: (error) => {
      toast({
        title: "Analysis Failed",
        description: error instanceof Error ? error.message : "Unknown error occurred",
        variant: "destructive",
      });
    },
  });
}

// GET /api/stats
export function useStats() {
  return useQuery({
    queryKey: [api.stats.get.path],
    queryFn: async () => {
      const res = await fetch(api.stats.get.path);
      if (!res.ok) throw new Error("Failed to fetch stats");
      return api.stats.get.responses[200].parse(await res.json());
    },
    // Refresh stats every 30 seconds
    refetchInterval: 30000, 
  });
}
