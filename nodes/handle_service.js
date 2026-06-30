// Step: service_select
// Task: User picks 1-5. Store service, advance to template_layout, send layout image.
const phone = $('Extract Message').item.json.phone;
const text  = ($('Extract Message').item.json.text || '').trim();
const lang  = $('Get Session').item.json?.chosen_language || 'EN';

const FLASK   = 'http://127.0.0.1:5051';
const BAILEYS = 'http://127.0.0.1:3001';

async function send(msg)   { await this.helpers.httpRequest({ method:'POST', url:`${BAILEYS}/send`,         headers:{'Content-Type':'application/json'}, body:JSON.stringify({phone, text:msg}), returnFullResponse:false }); }
async function sendImg(imagePath) { await this.helpers.httpRequest({ method:'POST', url:`${BAILEYS}/send-image`, headers:{'Content-Type':'application/json'}, body:JSON.stringify({phone, imagePath}), returnFullResponse:false }); }
async function saveMsg(role, content) { await this.helpers.httpRequest({ method:'POST', url:`${FLASK}/conversations`, headers:{'Content-Type':'application/json'}, body:JSON.stringify({phone_number:phone, role, content}), returnFullResponse:false }); }
async function setStep(step) { await this.helpers.httpRequest({ method:'POST', url:`${FLASK}/session/${phone}/step`, headers:{'Content-Type':'application/json'}, body:JSON.stringify({current_step:step}), returnFullResponse:false }); }
async function saveData(data) { await this.helpers.httpRequest({ method:'POST', url:`${FLASK}/session/${phone}/data`, headers:{'Content-Type':'application/json'}, body:JSON.stringify(data), returnFullResponse:false }); }

const SERVICES = {
  '1': { name_BM:'Tulis Resume dari Awal',      name_EN:'Write Resume from Scratch', name_CN:'從頭撰寫履歷', amount:7  },
  '2': { name_BM:'Perbaiki Resume Sedia Ada',    name_EN:'Improve Existing Resume',   name_CN:'改善現有履歷', amount:5  },
  '3': { name_BM:'Pengoptimuman ATS',             name_EN:'ATS Optimisation',          name_CN:'ATS 優化',    amount:5  },
  '4': { name_BM:'Surat Lamaran',                 name_EN:'Cover Letter',              name_CN:'求職信',       amount:3  },
  '5': { name_BM:'Pakej Penuh',                   name_EN:'Full Package',              name_CN:'全套',         amount:10 },
};

const LAYOUT_ASK = {
  BM: 'Pilihan hebat! 🎨\n\nSekarang sila pilih susun atur resume anda:\n\n*A* = Dua kolum (moden, padat)\n*B* = Satu kolum (klasik, mudah dibaca)\n\nBalas A atau B.',
  EN: 'Great choice! 🎨\n\nNow please choose your resume layout:\n\n*A* = Two-column (modern, compact)\n*B* = Single-column (classic, easy to read)\n\nReply A or B.',
  CN: '很好！🎨\n\n請選擇履歷版面：\n\n*A* = 雙欄（現代、緊湊）\n*B* = 單欄（經典、易讀）\n\n回覆 A 或 B。'
};

const RETRY = {
  BM: 'Sila pilih nombor 1 hingga 5 untuk memilih perkhidmatan. 😊',
  EN: 'Please reply with a number from 1 to 5 to choose a service. 😊',
  CN: '請回覆 1 至 5 的數字選擇服務。😊'
};

const choice = text.match(/^[1-5]$/)?.[0];
await saveMsg('user', text);

if (choice) {
  const svc = SERVICES[choice];
  const svcName = svc[`name_${lang}`];
  await saveData({ service: svcName, amount: svc.amount });
  await setStep('template_layout');
  await saveMsg('assistant', LAYOUT_ASK[lang]);
  await send(LAYOUT_ASK[lang]);
  await sendImg('${PROJECT_ROOT}/resume-ai/templates/layout_preview.png');
} else {
  await saveMsg('assistant', RETRY[lang]);
  await send(RETRY[lang]);
}

return [{ json: { ok: true } }];
