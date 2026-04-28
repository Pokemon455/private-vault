const https = require('https');
exports.handler = async (event) => {
  const headers = { 'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json' };
  if (event.httpMethod === 'OPTIONS') return { statusCode: 200, headers, body: '' };
  if (event.httpMethod !== 'POST') return { statusCode: 405, headers, body: 'Method Not Allowed' };
  try {
    const { messages } = JSON.parse(event.body);
    const response = await fetch('https://integrate.api.nvidia.com/v1/chat/completions', {
      method: 'POST',
      headers: { 'Authorization': 'Bearer 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', 'Content-Type': 'application/json' },
      body: JSON.stringify({ model: 'openai/gpt-oss-20b', max_tokens: 500, messages })
    });
    const data = await response.json();
    return { statusCode: 200, headers, body: JSON.stringify({ reply: data.choices[0].message.content }) };
  } catch(e) {
    return { statusCode: 500, headers, body: JSON.stringify({ error: e.message }) };
  }
};