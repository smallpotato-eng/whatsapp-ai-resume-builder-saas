// Step: pdpa
// Task: Wait for agree. If agreed, show service menu, advance to service_select.
const phone = $('Extract Message').item.json.phone;
const text  = ($('Extract Message').item.json.text || '').trim();
const lang  = $('Get Session').item.json?.chosen_language || 'EN';

const FLASK   = 'http://127.0.0.1:5051';
const BAILEYS = 'http://127.0.0.1:3001';

async function send(msg)   { await this.helpers.httpRequest({ method:'POST', url:`${BAILEYS}/send`,         headers:{'Content-Type':'application/json'}, body:JSON.stringify({phone, text:msg}), returnFullResponse:false }); }
async function saveMsg(role, content) { await this.helpers.httpRequest({ method:'POST', url:`${FLASK}/conversations`, headers:{'Content-Type':'application/json'}, body:JSON.stringify({phone_number:phone, role, content}), returnFullResponse:false }); }
async function setStep(step) { await this.helpers.httpRequest({ method:'POST', url:`${FLASK}/session/${phone}/step`, headers:{'Content-Type':'application/json'}, body:JSON.stringify({current_step:step}), returnFullResponse:false }); }

const isAgreed = /^(agree|setuju|同意|ok|yes|ya|是|對|好)$/i.test(text);

const SERVICE_MENU = {
  BM: 'Terima kasih! 😊\n\nSila pilih perkhidmatan:\n\n1️⃣ Tulis Resume dari Awal — RM7\n2️⃣ Perbaiki Resume Sedia Ada — RM5\n3️⃣ Pengoptimuman ATS — RM5\n4️⃣ Surat Lamaran — RM3\n5️⃣ Pakej Penuh (Resume + Surat Lamaran) — RM10\n\nBalas nombor pilihan anda.',
  EN: 'Thank you! 😊\n\nPlease choose a service:\n\n1️⃣ Write Resume from Scratch — RM7\n2️⃣ Improve Existing Resume — RM5\n3️⃣ ATS Optimisation — RM5\n4️⃣ Cover Letter — RM3\n5️⃣ Full Package (Resume + Cover Letter) — RM10\n\nReply with the number of your choice.',
  CN: '感謝您的同意！😊\n\n請選擇服務：\n\n1️⃣ 從頭撰寫履歷 — RM7\n2️⃣ 改善現有履歷 — RM5\n3️⃣ ATS 優化 — RM5\n4️⃣ 求職信 — RM3\n5️⃣ 全套（履歷 + 求職信）— RM10\n\n請回覆號碼。'
};

const REMINDER = {
  BM: 'Sila balas "Setuju" untuk meneruskan. 😊',
  EN: 'Please reply "Agree" to proceed. 😊',
  CN: '請回覆「同意」以繼續。😊'
};

await saveMsg('user', text);

if (isAgreed) {
  await setStep('service_select');
  await saveMsg('assistant', SERVICE_MENU[lang]);
  await send(SERVICE_MENU[lang]);
} else {
  await saveMsg('assistant', REMINDER[lang]);
  await send(REMINDER[lang]);
}

return [{ json: { ok: true } }];
