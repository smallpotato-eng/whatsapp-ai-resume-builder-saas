// Step: collecting
// AI task: extract resume data, merge with existing. When complete, create order.
const phone   = $('Extract Message').item.json.phone;
const text    = ($('Extract Message').item.json.text || '').trim();
const lang    = $('Get Session').item.json?.chosen_language || 'EN';
const session = $('Get Session').item.json || {};
const existing = session.collected_data || {};

const FLASK   = 'http://127.0.0.1:5051';
const BAILEYS = 'http://127.0.0.1:3001';
const GEMINI_KEY = 'YOUR_GEMINI_API_KEY';
const GROQ_KEY   = 'YOUR_GROQ_API_KEY';

async function send(msg)   { await this.helpers.httpRequest({ method:'POST', url:`${BAILEYS}/send`,         headers:{'Content-Type':'application/json'}, body:JSON.stringify({phone, text:msg}), returnFullResponse:false }); }
async function saveMsg(role, content) { await this.helpers.httpRequest({ method:'POST', url:`${FLASK}/conversations`, headers:{'Content-Type':'application/json'}, body:JSON.stringify({phone_number:phone, role, content}), returnFullResponse:false }); }
async function setStep(step) { await this.helpers.httpRequest({ method:'POST', url:`${FLASK}/session/${phone}/step`, headers:{'Content-Type':'application/json'}, body:JSON.stringify({current_step:step}), returnFullResponse:false }); }
async function saveData(data) { return await this.helpers.httpRequest({ method:'POST', url:`${FLASK}/session/${phone}/data`, headers:{'Content-Type':'application/json'}, body:JSON.stringify(data), returnFullResponse:false }); }

const langName = { BM:'Bahasa Malaysia', EN:'English', CN:'Traditional Chinese' }[lang];

const systemPrompt = `You are Ava, a resume assistant collecting information to build a resume.
Reply language: ${langName}.
Previously collected data: ${JSON.stringify(existing)}

Extract any NEW resume information from the user's message and merge with existing data.
Required fields: name, target_job, experience_years, education, work_history, skills.
If any required field is still missing after merging, gently ask for it.
If ALL fields are present, show a confirmation summary and ask user to confirm.
The user confirms with: yes/ok/confirm/betul/setuju/是/好/對.

Output ONLY valid JSON:
{
  "reply": "your response in ${langName}",
  "extracted_data": { "name":"...", "target_job":"...", "experience_years":"...", "education":"...", "work_history":"...", "skills":"..." },
  "is_all_complete": false,
  "user_confirmed": false
}
Set is_all_complete=true only when ALL 6 fields are present.
Set user_confirmed=true only when user explicitly confirmed a summary.`;

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
  } catch(e2) { raw = '{"reply":"Please provide your information.","extracted_data":{},"is_all_complete":false,"user_confirmed":false}'; }
}

let parsed = { reply:'Please provide your information.', extracted_data:{}, is_all_complete:false, user_confirmed:false };
try { parsed = JSON.parse(raw.match(/\{[\s\S]*\}/)?.[0] || raw); } catch(e) {}

const reply         = parsed.reply || 'Please provide your information.';
const extractedData = parsed.extracted_data || {};
const isComplete    = parsed.is_all_complete === true;
const confirmed     = parsed.user_confirmed === true;

// Always save extracted data
if (Object.keys(extractedData).length > 0) {
  await saveData(extractedData);
}

await saveMsg('user', text);
await saveMsg('assistant', reply);
await send(reply);

// Only create order when complete AND confirmed
if (isComplete && confirmed) {
  const merged = { ...existing, ...extractedData };
  const orderResp = await this.helpers.httpRequest({ method:'POST', url:`${FLASK}/orders`, headers:{'Content-Type':'application/json'},
    body: JSON.stringify({
      phone_number: phone,
      customer_name: merged.name || '',
      service: merged.service || 'Resume',
      amount: merged.amount || 7,
      details: { target_job: merged.target_job, layout: merged.layout, colour: merged.colour, style: merged.style }
    }), returnFullResponse:false });

  const ticket = orderResp.ticket_no || '';
  await setStep('payment_pending');

  const TICKET_MSG = {
    BM: `Pesanan anda telah diterima! 🎉\n\nNombor Pesanan: *${ticket}*\n\nSila buat pembayaran:\n🏦 Example Bank\n💳 Akaun: 0000000000\n👤 Nama: Example Account Name\n💰 Jumlah: RM${merged.amount || 7}\n\nGunakan nombor pesanan sebagai rujukan. Hantar screenshot selepas bayar. 😊`,
    EN: `Your order has been received! 🎉\n\nOrder Number: *${ticket}*\n\nPlease make payment:\n🏦 Example Bank\n💳 Account: 0000000000\n👤 Name: Example Account Name\n💰 Amount: RM${merged.amount || 7}\n\nUse the order number as reference. Send screenshot after payment. 😊`,
    CN: `您的訂單已收到！🎉\n\n訂單號碼：*${ticket}*\n\n請完成付款：\n🏦 Example Bank\n💳 帳號：0000000000\n👤 姓名：Example Account Name\n💰 金額：RM${merged.amount || 7}\n\n請以訂單號碼作為付款備注。付款後發送截圖。😊`
  };
  await saveMsg('assistant', TICKET_MSG[lang]);
  await send(TICKET_MSG[lang]);
}

return [{ json: { ok: true } }];
