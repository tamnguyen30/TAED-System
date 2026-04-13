import { db } from "./db";
import { emails, analysisResults, type InsertEmail, type Email, type AnalysisResult, type InsertAnalysisResult } from "@shared/schema";

export interface IStorage {
  getEmails(): Promise<(Email & { analysis: AnalysisResult | null })[]>;
  getEmail(id: number): Promise<(Email & { analysis: AnalysisResult | null }) | undefined>;
  createEmail(email: InsertEmail): Promise<Email>;
  createAnalysis(analysis: InsertAnalysisResult): Promise<AnalysisResult>;
  getStats(): Promise<{ totalScanned: number; threatsBlocked: number; avgTrustScore: number }>;
  seed(): Promise<void>;
}

let mockEmails: any[] = [];
let mockId = 1;

export class DatabaseStorage implements IStorage {
  async getEmails() {
    return mockEmails;
  }

  async getEmail(id: number) {
    return mockEmails.find(e => e.id === id);
  }

  async createEmail(email: InsertEmail) {
    const newEmail = { ...email, id: mockId++, receivedAt: new Date() };
    mockEmails.push({ ...newEmail, analysis: null });
    return newEmail;
  }

  async createAnalysis(analysis: InsertAnalysisResult) {
    const email = mockEmails.find(e => e.id === analysis.emailId);
    const newAnalysis = { ...analysis, id: mockId++, createdAt: new Date() };
    if (email) email.analysis = newAnalysis;
    return newAnalysis;
  }

  async getStats() {
    return {
      totalScanned: mockEmails.length,
      threatsBlocked: mockEmails.filter(e => e.analysis?.verdict === 'PHISHING').length,
      avgTrustScore: mockEmails.length > 0 
        ? Math.round(mockEmails.reduce((sum, e) => sum + (e.analysis?.trustScore || 0), 0) / mockEmails.length)
        : 0,
    };
  }

  async seed() {
    console.log("Demo mode - no database seed needed");
  }
}

export const storage = new DatabaseStorage();
