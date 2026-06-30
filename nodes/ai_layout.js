// Step: template_layout — pure regex, no AI
const phone = $('Extract Message').item.json.phone;
const text  = ($('Extract Message').item.json.text || '').trim();
const lang  = $('Get Session').item.json?.chosen_language || 'EN';

const FLASK   = 'http://127.0.0.1:5051';
const BAILEYS = 'http://127.0.0.1:3001';

async function send(msg) { await this.helpers.httpRequest({ method:'POST', url:`${BAILEYS}/send`, headers:{'Content-Type':'application/json'}, body:JSON.stringify({phone, text:msg}), returnFullResponse:false }); }
async function sendImg(imagePath) { await this.helpers.httpRequest({ method:'POST', url:`${BAILEYS}/send-image`, headers:{'Content-Type':'application/json'}, body:JSON.stringify({phone, imagePath}), returnFullResponse:false }); }
async function saveMsg(role, content) { await this.helpers.httpRequest({ method:'POST', url:`${FLASK}/conversations`, headers:{'Content-Type':'application/json'}, body:JSON.stringify({phone_number:phone, role, content}), returnFullResponse:false }); }
async function setStep(step) { await this.helpers.httpRequest({ method:'POST', url:`${FLASK}/session/${phone}/step`, headers:{'Content-Type':'application/json'}, body:JSON.stringify({current_step:step}), returnFullResponse:false }); }
async function saveData(data) { await this.helpers.httpRequest({ method:'POST', url:`${FLASK}/session/${phone}/data`, headers:{'Content-Type':'application/json'}, body:JSON.stringify(data), returnFullResponse:false }); }

// Detect A or B
const match = text.match(/\b(A|B)\b/i);
const choice = match ? match[1].toUpperCase() : null;

await saveMsg('user', text);

if (choice === 'A' || choice === 'B') {
  await saveData({ layout: choice });
  await setStep('template_colour');

  const CONFIRM = {
    BM: `Layout *${choice}* dipilih ✅\n\n🎨 Sekarang pilih warna dan gaya.\n\nWarna:\n1=Navy Blue | 2=Charcoal | 3=Teal | 4=Crimson | 5=Warm Beige\n\nGaya:\nI=Klasik | II=Moden | III=Minimal\n\nContoh: *2 II*`,
    EN: `Layout *${choice}* selected ✅\n\n🎨 Now choose your colour and style.\n\nColour:\n1=Navy Blue | 2=Charcoal | 3=Teal | 4=Crimson | 5=Warm Beige\n\nStyle:\nI=Classic | II=Modern | III=Minimal\n\nExample: *2 II*`,
    CN: `已選版型 *${choice}* ✅\n\n🎨 請選擇顏色和風格。\n\n顏色：\n1=深藍 | 2=炭灰 | 3=青綠 | 4=深紅 | 5=暖米\n\n風格：\nI=經典 | II=現代 | III=簡約\n\n例如：*2 II*`
  };
  await saveMsg('assistant', CONFIRM[lang]);
  await send(CONFIRM[lang]);
  try { await sendImg('${PROJECT_ROOT}/resume-ai/templates/colour_swatch.png'); } catch(e) {}

} else {
  const ASK = {
    BM: 'Sila taip *A* atau *B* untuk memilih layout resume anda.',
    EN: 'Please type *A* or *B* to choose your resume layout.',
    CN: '請輸入 *A* 或 *B* 選擇履歷版型。'
  };
  await saveMsg('assistant', ASK[lang]);
  await send(ASK[lang]);
}

return [{ json: { ok: true } }];
