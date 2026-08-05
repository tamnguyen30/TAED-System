import { useState } from "react";
import { useForm } from "react-hook-form";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useLocation } from "wouter";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { AlertCircle, Send, AlertTriangle, CheckCircle } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

type SimulateForm = {
  subject: string;
  sender: string;
  content: string;
};

export default function Simulate() {
  const [, setLocation] = useLocation();
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const { register, handleSubmit, formState: { errors }, setValue } = useForm<SimulateForm>();

  const analyzeMutation = useMutation({
    mutationFn: async (data: SimulateForm) => {
      const response = await fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...data,
          isSimulated: true,
        }),
      });

      if (!response.ok) {
        throw new Error("Analysis failed");
      }

      return response.json();
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["/api/emails"] });
      setIsAnalyzing(false);
      
      if (data && data.id) {
        toast({
          title: "Analysis Complete",
          description: `Verdict: ${data.analysis?.verdict} | Trust Score: ${data.analysis?.trustScore}%`,
        });
        setTimeout(() => {
          setLocation(`/email/${data.id}`);
        }, 200);
      }
    },
    onError: () => {
      toast({
        title: "Analysis Failed",
        description: "Could not analyze email. Please try again.",
        variant: "destructive",
      });
      setIsAnalyzing(false);
    },
  });

  const onSubmit = async (data: SimulateForm) => {
    setIsAnalyzing(true);
    analyzeMutation.mutate(data);
  };

  const populatePhishingExample = () => {
    setValue("subject", "Urgent: Account Suspended - Verify Immediately");
    setValue("sender", "security@paypa1-verify.com");
    setValue("content", `Dear Valued Customer,

Your PayPal account has been temporarily suspended due to unusual activity. Please verify immediately:

http://paypa1-secure.com/verify

Failure to confirm within 24 hours will result in permanent account closure.

Best regards,
PayPal Security Team`);
  };

  const populateSafeExample = () => {
    setValue("subject", "Your Amazon Order Has Shipped");
    setValue("sender", "shipment-tracking@amazon.com");
    setValue("content", `Hello,

Your recent order has shipped and will arrive by Friday, January 31st.

Track your package: amazon.com/orders

Thank you for shopping with Amazon!`);
  };

  return (
    <div className="container max-w-4xl py-12">
      <div className="space-y-8">
        <div className="space-y-2">
          <h1 className="text-4xl font-display font-bold">Email Analysis</h1>
          <p className="text-lg text-muted-foreground">
            Submit an email for TAED analysis to detect phishing attempts.
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Test Email Content</CardTitle>
            <CardDescription>
              Enter email details or use example data.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex gap-2 mb-6">
              <Button 
                type="button" 
                variant="outline" 
                onClick={populatePhishingExample}
              >
                <AlertTriangle className="w-4 h-4 mr-2" />
                Load Phishing Example
              </Button>
              <Button 
                type="button" 
                variant="outline" 
                onClick={populateSafeExample}
              >
                <CheckCircle className="w-4 h-4 mr-2" />
                Load Safe Example
              </Button>
            </div>

            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="subject">Subject Line</Label>
                <Input
                  id="subject"
                  {...register("subject", { required: "Subject is required" })}
                />
                {errors.subject && (
                  <p className="text-sm text-destructive">{errors.subject.message}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="sender">Sender Address</Label>
                <Input
                  id="sender"
                  type="email"
                  {...register("sender", { required: "Sender is required" })}
                />
                {errors.sender && (
                  <p className="text-sm text-destructive">{errors.sender.message}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="content">Email Content</Label>
                <Textarea
                  id="content"
                  className="min-h-[200px]"
                  {...register("content", { required: "Content is required" })}
                />
                {errors.content && (
                  <p className="text-sm text-destructive">{errors.content.message}</p>
                )}
              </div>

              <Button 
                type="submit" 
                size="lg" 
                className="w-full"
                disabled={isAnalyzing}
              >
                {isAnalyzing ? "Analyzing..." : "Analyze Email"}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
