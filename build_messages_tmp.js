const phone = $('Extract Message').item.json.phone;
const text = $('Extract Message').item.json.text;
const name = $('Extract Message').item.json.name || phone;
const hist = $('Get History').item.json?.history || [];
const session = $('Get Session').item.json || {};
const currentStep = session.current_step || 'new';
let chosenLanguage = session.chosen_language || '';

// === STEP 1: Detect language if not yet stored ===
function detectLang(str) {
  if (!str) return null;
  const s = str.toLowerCase();
  if (/bahasa|melayu|\bbm\b|bahsa/i.test(s)) return 'Bahasa Malaysia';
  if (/\benglish\b|\ben\b|inggeris/i.test(s)) return 'English';
  if (/中文|华语|chinese/i.test(s)) return '中文';
  if (/[一-鿿]/.test(str)) return '中文';
  if (/\b(saya|anda|boleh|dengan|untuk|yang|tidak|ada|ini|itu|mana|nama|kerja|tempat|tahun|sekarang|awak|kita|mereka|akan|sudah|belum|ingin|mahu|perlu)\b/i.test(s)) return 'Bahasa Malaysia';
  const ar = (str.match(/[a-zA-Z]/g)||[]).length / Math.max(str.length,1);
  if (ar>0.5 && /\b(the|is|are|was|have|has|can|want|need|my|your|yes|no|ok|please|thank|hi|hello|resume|job|work|name|year|skill|experience)\b/i.test(s)) return 'English';
  return null;
}

if (!chosenLanguage) {
  const userMsgs = hist.filter(h=>h.role==='user').map(h=>h.content);
  for (const m of userMsgs) { const l=detectLang(m); if(l) chosenLanguage=l; }
  const cur = detectLang(text);
  if (cur) chosenLanguage = cur;
  if (!chosenLanguage) {
    const asstMsgs = hist.filter(h=>h.role==='assistant').map(h=>h.content);
    for (let i=asstMsgs.length-1;i>=0;i--) { const l=detectLang(asstMsgs[i]); if(l){chosenLanguage=l;break;} }
  }
  if (chosenLanguage) {
    try {
      await this.helpers.httpRequest({ method:'POST', url:`http://127.0.0.1:5051/session/${phone}/step`, headers:{'Content-Type':'application/json'}, body:JSON.stringify({chosen_language:chosenLanguage}), returnFullResponse:false });
    } catch(e){}
  }
}

// === STEP 2: Load language-specific micro prompt ===
const langFile = {'Bahasa Malaysia':'ava_bm.txt','English':'ava_en.txt','中文':'ava_cn.txt'}[chosenLanguage] || 'ava_en.txt';
const sopPath = `E:/LK%20Agent/resume-ai/prompts/${langFile}`;
let sop = '';
try {
  const r = await this.helpers.httpRequest({ method:'GET', url:`http://127.0.0.1:5051/sop?path=${sopPath}`, returnFullResponse:false });
  sop = r.sop?.sop_content || '';
} catch(e) {
  sop = 'You are Ava, resume consultant. Reply ONLY with JSON: {"reply":"...","action":"NONE","data":{}}';
}

// === STEP 3: Inject step-specific micro instruction ===
const stepInstructions = {
  'new':              'Send the PDPA consent notice to the user NOW using the PDPA text in your instructions. Set action to "PDPA_SENT".',
  'pdpa_pending':     'User replied to PDPA. If they agree (Agree/setuju/ok/yes/同意), show the service menu (1-5 with prices) and ask them to choose a service. Set action to "SERVICE_SELECTED".',
  'service_select':   'User is choosing a service (1-5). Their number IS their service choice. Acknowledge their choice, then set action to "SEND_LAYOUT_IMG" to show layout samples.',
  'template_layout':  'User is choosing layout A or B. Their reply IS their layout choice. Set action to "SEND_COLOUR_IMG" to show colour samples. If user asks about samples, tell them the image you will show IS the sample.',
  'template_colour':  'User is choosing colour (1-5) AND style (I, II, or III). They may send both at once or one at a time. Their NUMBER = colour choice (not service). Once you have BOTH colour and style confirmed, set action to "TEMPLATE" with data {"layout":"<layout>","colour":"<colour>","style":"<style>"}. If user only gives colour, ask for style and keep action "NONE".',
  'data_collection':  'Collect resume info step by step. Required fields: (1) full name, (2) TARGET JOB TITLE — the position they are applying for, NOT their education or current role — ask explicitly if not given, (3) years of experience, (4) education, (5) work history, (6) key skills. NEVER invent or assume any data. ONLY use what the user explicitly typed. Once ALL 6 fields are collected, show a clean ORDER SUMMARY and ask: "Is everything correct? Reply YES to confirm and proceed with payment." Do NOT say you will create the resume now — resume is only created AFTER payment. Do NOT tell user to reply "ORDER". When user replies yes/ok/confirm/correct/betul/对, set action to "ORDER". Do NOT include ticket_no in data.',
  'order_pending':    'Order is placed. If user says paid / dah bayar / 已付 / sends screenshot, set action to "PAYMENT_RECEIVED". Do NOT create a new order.',
  'feedback_rating':  'User is giving star rating 1-5. Their NUMBER = their star rating. Never treat it as service or template selection. Acknowledge warmly, ask for comment, set action to "RATING_RECEIVED".',
  'feedback_comment': 'User is giving feedback comment. Find the star rating number they gave in history. Set action to "FEEDBACK" with data = {"rating":<that number>,"comment":"<their reply>"}.',
  'done':             'Conversation complete. Warm farewell only. Keep action "NONE". Do not restart any flow.',
};

const messages = [{ role:'system', content: sop }];
if (stepInstructions[currentStep]) {
  messages.push({ role:'system', content:`CURRENT TASK: ${stepInstructions[currentStep]}` });
}

// Data reminder for collection steps
if (['data_collection','order_pending'].includes(currentStep) && hist.length > 2) {
  const provided = hist.filter(h=>h.role==='user').map(h=>h.content).join('\n');
  messages.push({ role:'system', content:`ALREADY PROVIDED — do NOT re-ask:\n${provided.substring(0,1500)}` });
}

// Inject template choices for data_collection (selected by user before AI, stored in session)
if (currentStep === 'data_collection') {
  const tl = session.template_layout || '?';
  const tc = session.template_colour || '?';
  const ts = session.template_style || '?';
  if (tl !== '?' || tc !== '?' || ts !== '?') {
    messages.push({ role:'system', content:`TEMPLATE ALREADY CHOSEN (do NOT ask again): Layout=${tl}, Colour=${tc}, Style=${ts}. Include these in ORDER data.` });
  }
}

// Inactivity check
if (hist.length > 0) {
  const diffH = (Date.now() - new Date(hist[hist.length-1].timestamp).getTime()) / 3600000;
  if (diffH > 1) messages.push({ role:'system', content:`Session inactive ${Math.floor(diffH)}h. Ask if user wants to continue.` });
}

const recentHist = currentStep === 'data_collection' ? hist.slice(-10) : hist.slice(-6);
for (const h of recentHist) messages.push({ role:h.role, content:h.content });
messages.push({ role:'user', content:text });
return [{ json:{ phone, text, name, messages, currentStep } }];
