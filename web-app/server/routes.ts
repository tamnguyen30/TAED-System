import type { Express } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage";
import { api } from "@shared/routes";
import { z } from "zod";
import { execSync } from "child_process";
import { fileURLToPath } from "url";
import { dirname } from "path";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

export async function registerRoutes(
  httpServer: Server,
  app: Express
): Promise<Server> {
  
  await storage.seed();

  app.get(api.emails.list.path, async (req, res) => {
    const emails = await storage.getEmails();
    res.json(emails);
  });

  app.get(api.emails.get.path, async (req, res) => {
    const email = await storage.getEmail(Number(req.params.id));
    if (!email) {
      return res.status(404).json({ message: 'Email not found' });
    }
    res.json(email);
  });

  app.post(api.emails.analyze.path, async (req, res) => {
    try {
      const input = api.emails.analyze.input.parse(req.body);
      const email = await storage.createEmail(input);

      const pythonResult = execSync(
        `python3 taed_robust_final.py "${input.content.replace(/"/g, '\\"')}"`,
        { encoding: 'utf-8', cwd: __dirname + '/..' }
      );
      
      const aiResult = JSON.parse(pythonResult);
      
      const analysis = await storage.createAnalysis({
        emailId: email.id,
        trustScore: aiResult.trustScore,
        confidence: aiResult.confidence,
        fidelity: aiResult.fidelity,
        stability: aiResult.stability,
        verdict: aiResult.verdict,
        explanation: aiResult.explanation + (aiResult.modelVotes ? '\n\nModel Votes:\n' + aiResult.modelVotes.join('\n') : ''),
        attackType: aiResult.attackType,
      });
      
      res.status(201).json({ ...email, analysis });
    } catch (err) {
      console.error(err);
      res.status(500).json({ message: "Analysis Error" });
    }
  });

  app.get(api.stats.get.path, async (req, res) => {
    const stats = await storage.getStats();
    res.json(stats);
  });

  return httpServer;
}
