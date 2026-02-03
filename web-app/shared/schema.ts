import { pgTable, text, serial, integer, boolean, timestamp } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";
import { sql } from "drizzle-orm";

// === TABLE DEFINITIONS ===
export const emails = pgTable("emails", {
  id: serial("id").primaryKey(),
  subject: text("subject").notNull(),
  sender: text("sender").notNull(),
  content: text("content").notNull(),
  receivedAt: timestamp("received_at").defaultNow(),
  isSimulated: boolean("is_simulated").default(false),
});

export const analysisResults = pgTable("analysis_results", {
  id: serial("id").primaryKey(),
  emailId: integer("email_id").notNull().references(() => emails.id),
  trustScore: integer("trust_score").notNull(), // 0-100
  confidence: integer("confidence").notNull(), // 0-100
  fidelity: integer("fidelity").notNull(), // 0-100
  stability: integer("stability").notNull(), // 0-100
  verdict: text("verdict").notNull(), // 'PHISHING' | 'SAFE'
  explanation: text("explanation").notNull(),
  attackType: text("attack_type"),
  createdAt: timestamp("created_at").defaultNow(),
});

// === BASE SCHEMAS ===
export const insertEmailSchema = createInsertSchema(emails).omit({ id: true, receivedAt: true });
export const insertAnalysisResultSchema = createInsertSchema(analysisResults).omit({ id: true, createdAt: true });

// === EXPLICIT API CONTRACT TYPES ===
export type Email = typeof emails.$inferSelect;
export type InsertEmail = z.infer<typeof insertEmailSchema>;

export type AnalysisResult = typeof analysisResults.$inferSelect;
export type InsertAnalysisResult = z.infer<typeof insertAnalysisResultSchema>;

export type CreateEmailRequest = InsertEmail;
export type EmailResponse = Email & { analysis?: AnalysisResult | null };

export interface DashboardStats {
  totalScanned: number;
  threatsBlocked: number;
  avgTrustScore: number;
}
