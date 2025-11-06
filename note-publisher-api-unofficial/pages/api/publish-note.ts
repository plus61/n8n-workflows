import type { NextApiRequest, NextApiResponse } from 'next';

type SuccessResponse = {
  success: true;
  url: string;
  articleId: string;
  title: string;
  publishedAt: string;
};

type ErrorResponse = {
  success: false;
  error: string;
  details?: string;
};

type Response = SuccessResponse | ErrorResponse;

// Rate limiting
const rateLimitMap = new Map<string, number[]>();

function checkRateLimit(apiKey: string): boolean {
  const now = Date.now();
  const requests = rateLimitMap.get(apiKey) || [];
  const recentRequests = requests.filter(time => now - time < 60000);

  if (recentRequests.length >= 10) {
    return false;
  }

  recentRequests.push(now);
  rateLimitMap.set(apiKey, recentRequests);
  return true;
}

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<Response>
) {
  // Method check
  if (req.method !== 'POST') {
    return res.status(405).json({
      success: false,
      error: 'Method not allowed. Use POST.'
    });
  }

  // API Key authentication
  const apiKey = req.headers['x-api-key'] as string;
  const expectedKey = process.env.API_SECRET_KEY;

  if (!expectedKey) {
    return res.status(500).json({
      success: false,
      error: 'Server configuration error',
      details: 'API_SECRET_KEY not configured'
    });
  }

  if (!apiKey || apiKey !== expectedKey) {
    return res.status(401).json({
      success: false,
      error: 'Unauthorized. Invalid API key.',
      details: `Received: ${apiKey?.substring(0, 10)}..., Expected: ${expectedKey?.substring(0, 10)}...`
    });
  }

  // Rate limit check
  if (!checkRateLimit(apiKey)) {
    return res.status(429).json({
      success: false,
      error: 'Rate limit exceeded',
      details: 'Maximum 10 requests per minute'
    });
  }

  // Validation
  const { title, body, categories } = req.body;

  if (!title || typeof title !== 'string') {
    return res.status(400).json({
      success: false,
      error: 'Validation error',
      details: 'title is required and must be a string'
    });
  }

  if (!body || typeof body !== 'string') {
    return res.status(400).json({
      success: false,
      error: 'Validation error',
      details: 'body is required and must be a string'
    });
  }

  if (categories && !Array.isArray(categories)) {
    return res.status(400).json({
      success: false,
      error: 'Validation error',
      details: 'categories must be an array'
    });
  }

  // note credentials
  const noteSessionCookie = process.env.NOTE_SESSION_COOKIE;

  if (!noteSessionCookie) {
    return res.status(500).json({
      success: false,
      error: 'Server configuration error',
      details: 'NOTE_SESSION_COOKIE not configured. Please login to note.com and extract your session cookie.'
    });
  }

  try {
    // Prepare hashtags
    const hashtags = (categories || []).slice(0, 5).map((tag: string) => {
      return tag.startsWith('#') ? tag : `#${tag}`;
    });

    // Call note unofficial API
    const apiResponse = await fetch('https://note.com/api/v2/notes', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Cookie': `_note_session_v5=${noteSessionCookie}`,
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'application/json',
        'Origin': 'https://note.com',
        'Referer': 'https://note.com/'
      },
      body: JSON.stringify({
        name: title,
        body: body,
        status: 'published', // 自動公開 - AI生成記事は直接公開
        publish_at: null,
        hashtag_notes: hashtags.map((tag: string) => ({ name: tag }))
      })
    });

    if (!apiResponse.ok) {
      const errorText = await apiResponse.text();

      // 認証エラー（セッションクッキー期限切れ）の特別処理
      if (apiResponse.status === 401 || apiResponse.status === 403) {
        return res.status(401).json({
          success: false,
          error: 'note authentication failed',
          details: `Session cookie may be expired. Status: ${apiResponse.status}, Response: ${errorText.substring(0, 200)}`
        });
      }

      return res.status(500).json({
        success: false,
        error: 'note API request failed',
        details: `Status: ${apiResponse.status}, Response: ${errorText.substring(0, 500)}`
      });
    }

    const data = await apiResponse.json();

    // Extract article info
    // note API response structure may vary - adjust based on actual response
    const articleId = data.data?.key || data.key || 'unknown';
    const articleUrl = `https://note.com/${data.data?.user?.urlname || '61beef'}/n/${articleId}`;

    return res.status(200).json({
      success: true,
      url: articleUrl,
      articleId: articleId,
      title: title,
      publishedAt: new Date().toISOString()
    });

  } catch (error: any) {
    console.error('Error publishing to note:', error);
    return res.status(500).json({
      success: false,
      error: 'Internal server error',
      details: error.message || 'Unknown error occurred'
    });
  }
}

export const config = {
  maxDuration: 30, // Shorter timeout since no browser automation
};
