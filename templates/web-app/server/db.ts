import { drizzle } from 'drizzle-orm/node-postgres';
import pkg from 'pg';
const { Pool } = pkg;

const connectionString = process.env.DATABASE_URL || 'postgresql://dummy:dummy@localhost:5432/dummy';

const pool = new Pool({
  connectionString,
  // Don't actually try to connect for demo purposes
  max: 0,
});

export const db = drizzle(pool);
