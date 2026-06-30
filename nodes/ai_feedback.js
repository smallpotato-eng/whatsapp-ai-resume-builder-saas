// Step: feedback
// AI task: collect rating (1-5) and comment. Save, send farewell, set done.
const phone   = $('Extract Message').item.json.phone;
const text    = ($('Extract Message').item.json.text || '').trim();
const lang    = $('Get Session').item.json?.chosen_language || 'EN';
const session = $('Get Session').item.json || {};

const FLASK   = 'http://127.0.0.1:5051';
const BAILEYS = 'http://127.0.0.1:3001';
const GEMINI_KEY = 'YOUR_GEMINI_API_KEY';
const GROQ_KEY   = 'YOUR_GROQ_API_KEY';

async function send(msg)   { await this.helpers.httpRequest({ method:'POST', url:`${BAILEYS}/send`,         headers:{'Content-Type':'application/json'}, body:JSON.stringify({phone, text:msg}), returnFullResponse:false }); }
async function saveMsg(role, content) { await this.helpers.httpRequest({ method:'POST', url:`${FLASK}/conversations`, headers:{'Content-Type':'application/json'}, body:JSON.stringify({phone_number:phone, role, content}), returnFullResponse:false }); }
async function setStep(step) { await this.helpers.httpRequest({ method:'POST', url:`${FLASK}/session/${phone}/step`, headers:{'Content-Type':'application/json'}, body:JSON.stringify({current_step:step}), returnFullResponse:false }); }

const langName = { BM:'Bahasa Malaysia', EN:'English', CN:'Traditional Chinese' }[lang];
const existingData = session.collected_data || {};

const systemPrompt = `You are Ava. The customer just received their resume. Collect feedback.
Reply language: ${langName}.
Previously collected: rating=${existingData._feedback_rating || 'none'}, comment=${existingData._feedback_comment || 'none'}.
Step 1: If no rating yet, extract a star rating (1-5) from the message.
Step 2: If rating exists but no comment, ask for a short comment.
Step 3: If both exist, thank them warmly and say goodbye.
Output ONLY valid JSON:
{"reply":"your response","rating":null or 1-5,"comment":null or "string","is_done":false}
Set is_done=true only when BOTH rating and comment are present.`;

const messages = [
  { role:'system', content: systemPrompt },
  { role:'user',   content: text }
];

let raw = '';
try {
  const r = await this.helpers.httpRequest({ method:'POST', url:'https://generativelanguage.googleapis.com/v1beta/openai/chat/completions', headers:{Authorization:`Bearer ${GEMINI_KEY}`,'Content-Type':'application/json'}, body:JSON.stringify({model:'gemini-2.0-flash',temperature:0.2,response_format:{type:'json_object'},messages}), returnFullResponse:false });
  raw = r.choices?.[0]?.message?.content || '';
} catch(e) {
  try {
    const r = await this.helpers.httpRequest({ method:'POST', url:'https://api.groq.com/openai/v1/chat/completions', headers:{Authorization:`Bearer ${GROQ_KEY}`,'Content-Type':'application/json'}, body:JSON.stringify({model:'llama-3.3-70b-versatile',temperature:0.2,response_format:{type:'json_object'},messages}), returnFullResponse:false });
    raw = r.choices?.[0]?.message?.content || '';
  } catch(e2) { raw = '{"reply":"Thank you for your feedback!","rating":null,"comment":null,"is_done":false}'; }
}

let parsed = { reply:'Thank you!', rating:null, comment:null, is_done:false };
try { parsed = JSON.parse(raw.match(/\{[\s\S]*\}/)?.[0] || raw); } catch(e) {}

const reply  = parsed.reply || 'Thank you!';
const isDone = parsed.is_done === true;

await saveMsg('user', text);
await saveMsg('assistant', reply);
await send(reply);

// Save partial feedback data
const feedbackUpdate = {};
if (parsed.rating)  feedbackUpdate._feedback_rating  = parsed.rating;
if (parsed.comment) feedbackUpdate._feedback_comment = parsed.comment;
if (Object.keys(feedbackUpdate).length > 0) {
  await this.helpers.httpRequest({ method:'POST', url:`${FLASK}/session/${phone}/data`, headers:{'Content-Type':'application/json'}, body:JSON.stringify(feedbackUpdate), returnFullResponse:false });
}

if (isDone) {
  const rating  = parsed.rating  || existingData._feedback_rating  || 0;
  const comment = parsed.comment || existingData._feedback_comment || '';

  // Get latest order for ticket_no
  let ticketNo = '';
  try {
    const orders = await this.helpers.httpRequest({ method:'GET', url:`${FLASK}/orders/${phone}`, returnFullResponse:false });
    if (Array.isArray(orders) && orders.length > 0) ticketNo = orders[0].ticket_no || '';
  } catch(e) {}

  // Save feedback to DB
  await this.helpers.httpRequest({ method:'POST', url:`${FLASK}/feedback`, headers:{'Content-Type':'application/json'},
    body: JSON.stringify({ phone_number:phone, ticket_no:ticketNo, rating, comment }), returnFullResponse:false });

  await setStep('done');
}

return [{ json: { ok: true } }];
