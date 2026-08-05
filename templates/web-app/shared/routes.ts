import { z } from 'zod';
import { insertEmailSchema, insertAnalysisResultSchema, emails, analysisResults } from './schema';

export const errorSchemas = {
  validation: z.object({
    message: z.string(),
    field: z.string().optional(),
  }),
  notFound: z.object({
    message: z.string(),
  }),
  internal: z.object({
    message: z.string(),
  }),
};

export const api = {
  emails: {
    list: {
      method: 'GET' as const,
      path: '/api/emails',
      responses: {
        200: z.array(z.custom<typeof emails.$inferSelect & { analysis: typeof analysisResults.$inferSelect | null }>()),
      },
    },
    get: {
      method: 'GET' as const,
      path: '/api/emails/:id',
      responses: {
        200: z.custom<typeof emails.$inferSelect & { analysis: typeof analysisResults.$inferSelect | null }>(),
        404: errorSchemas.notFound,
      },
    },
    analyze: { // Simulate receiving/injecting an email
      method: 'POST' as const,
      path: '/api/analyze',
      input: insertEmailSchema,
      responses: {
        201: z.custom<typeof emails.$inferSelect & { analysis: typeof analysisResults.$inferSelect | null }>(),
        400: errorSchemas.validation,
      },
    },
  },
  stats: {
    get: {
      method: 'GET' as const,
      path: '/api/stats',
      responses: {
        200: z.object({
          totalScanned: z.number(),
          threatsBlocked: z.number(),
          avgTrustScore: z.number(),
        }),
      },
    },
  },
};

export function buildUrl(path: string, params?: Record<string, string | number>): string {
  let url = path;
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (url.includes(`:${key}`)) {
        url = url.replace(`:${key}`, String(value));
      }
    });
  }
  return url;
}
