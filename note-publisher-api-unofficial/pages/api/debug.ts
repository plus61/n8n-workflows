import type { NextApiRequest, NextApiResponse } from 'next';

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  const apiKey = process.env.API_SECRET_KEY;
  const noteSession = process.env.NOTE_SESSION_COOKIE;

  return res.status(200).json({
    apiKeyExists: !!apiKey,
    apiKeyLength: apiKey?.length || 0,
    apiKeyFirst10: apiKey?.substring(0, 10) || 'N/A',
    noteSessionExists: !!noteSession,
    noteSessionLength: noteSession?.length || 0,
    noteSessionFirst10: noteSession?.substring(0, 10) || 'N/A',
  });
}
