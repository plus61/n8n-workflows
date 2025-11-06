import type { NextApiRequest, NextApiResponse } from 'next';

type HealthResponse = {
  status: 'healthy' | 'unhealthy';
  timestamp: string;
  checks: {
    apiKeyConfigured: boolean;
    noteSessionConfigured: boolean;
    noteSessionValid?: boolean;
  };
  message?: string;
};

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<HealthResponse>
) {
  const apiKey = process.env.API_SECRET_KEY;
  const noteSession = process.env.NOTE_SESSION_COOKIE;

  const checks = {
    apiKeyConfigured: !!apiKey,
    noteSessionConfigured: !!noteSession,
  };

  // note セッションクッキーの有効性を簡易チェック
  // note.com のユーザー情報取得APIを叩いて確認
  let noteSessionValid = false;
  if (noteSession) {
    try {
      const testResponse = await fetch('https://note.com/api/v2/creators/current', {
        method: 'GET',
        headers: {
          'Cookie': `_note_session_v5=${noteSession}`,
          'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        },
        signal: AbortSignal.timeout(5000), // 5秒タイムアウト
      });

      noteSessionValid = testResponse.ok;
    } catch (error) {
      noteSessionValid = false;
    }
  }

  const allHealthy = checks.apiKeyConfigured && checks.noteSessionConfigured && noteSessionValid;

  return res.status(allHealthy ? 200 : 503).json({
    status: allHealthy ? 'healthy' : 'unhealthy',
    timestamp: new Date().toISOString(),
    checks: {
      ...checks,
      noteSessionValid,
    },
    message: allHealthy
      ? 'All systems operational'
      : 'Configuration issues detected. Check environment variables and session cookie validity.',
  });
}

export const config = {
  maxDuration: 10,
};
