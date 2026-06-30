const messages = $json.messages;
const phone = $('Extract Message').item.json.phone;
const GEMINI_KEY = 'YOUR_GEMINI_API_KEY';
const GEMINI_MODEL = 'gemini-2.0-flash';
const GROQ_KEY = 'YOUR_GROQ_API_KEY';
const GROQ_MODEL = 'llama-3.3-70b-versatile';
const OLLAMA_MODEL = 'llama3.1:8b';

let raw = '', provider = '';

// Layer 1: Gemini 2.0 Flash (with JSON response format)
try {
  const resp = await this.helpers.httpRequest({
    method: 'POST',
    url: 'https://generativelanguage.googleapis.com/v1beta/openai/chat/completions',
    headers: { 'Authorization': `Bearer ${GEMINI_KEY}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({
      model: GEMINI_MODEL,
      temperature: 0.3,
      response_format: { type: 'json_object' },
      messages
    }),
    returnFullResponse: false
  });
  raw = resp.choices?.[0]?.message?.content || '';
  provider = 'gemini';
  if (!raw) throw new Error('Empty');
} catch(e1) {
  console.log('[FB1] Gemini:', e1.message);
  // Layer 2: Groq 70b
  try {
    const resp = await this.helpers.httpRequest({
      method: 'POST',
      url: 'https://api.groq.com/openai/v1/chat/completions',
      headers: { 'Authorization': `Bearer ${GROQ_KEY}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: GROQ_MODEL,
        temperature: 0.3,
        response_format: { type: 'json_object' },
        messages
      }),
      returnFullResponse: false
    });
    raw = resp.choices?.[0]?.message?.content || '';
    provider = 'groq';
    if (!raw) throw new Error('Empty');
  } catch(e2) {
    console.log('[FB2] Groq:', e2.message);
    // Layer 3: Local Ollama (no JSON mode support, parse manually)
    try {
      const resp = await this.helpers.httpRequest({
        method: 'POST',
        url: 'http://127.0.0.1:11434/api/chat',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model: OLLAMA_MODEL, stream: false, messages }),
        returnFullResponse: false
      });
      raw = resp.message?.content || '';
      provider = 'ollama';
    } catch(e3) {
      raw = '{"reply":"Sorry, AI service is temporarily unavailable. Please try again.","action":"NONE","data":{}}';
      provider = 'error';
    }
  }
}

// === Parse structured JSON response ===
let tag = 'FAQ', tagData = null, reply = raw;
try {
  const jsonMatch = raw.match(/\{[\s\S]*\}/);
  if (jsonMatch) {
    const parsed = JSON.parse(jsonMatch[0]);
    reply = parsed.reply || raw;
    // Guard: reject template placeholders leaking from system prompt
    if (!reply || reply.trim().startsWith('<') || reply.includes('<mesej') || reply.includes('<English') || reply.includes('<繁體')) {
      console.log('[GUARD] AI leaked template placeholder, discarding reply');
      reply = '...'; // will be retried or fallback; log for debugging
      throw new Error('template_leak');
    }
    const action = (parsed.action || 'NONE').trim().toUpperCase();
    tag = (action === 'NONE' || action === '') ? 'FAQ' : action;
    tagData = (parsed.data && Object.keys(parsed.data).length > 0) ? parsed.data : null;
  }
} catch(e) {
  console.log('[PARSE] JSON parse failed, using raw:', e.message);
  reply = raw;
  tag = 'FAQ';
}

// === Update session step ===
const stepMap = {
  'PDPA_SENT':        'pdpa_pending',
  'SERVICE_SELECTED': 'service_select',
  'SEND_LAYOUT_IMG':  'template_layout',
  'SEND_COLOUR_IMG':  'template_colour',
  'TEMPLATE':         'data_collection',
  'ORDER':            'order_pending',
  'PAYMENT_RECEIVED': 'feedback_rating',
  'RATING_RECEIVED':  'feedback_comment',
  'FEEDBACK':         'done',
};
const newStep = stepMap[tag];
if (newStep) {
  try {
    await this.helpers.httpRequest({ method:'POST', url:`http://127.0.0.1:5051/session/${phone}/step`, headers:{'Content-Type':'application/json'}, body:JSON.stringify({current_step:newStep}), returnFullResponse:false });
  } catch(e) { console.log('[STEP] failed:', e.message); }
}

console.log(`[AI] provider=${provider} action=${tag} step->${newStep||'—'}`);
return [{ json:{ phone, tag, tagData, reply, provider } }];
