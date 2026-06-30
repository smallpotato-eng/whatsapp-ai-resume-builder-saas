// Step: template_select
// Show 6 template previews OR detect choice 1-6
const phone    = $('Extract Message').item.json.phone;
const text     = ($('Extract Message').item.json.text || '').trim();
const lang     = $('Get Session').item.json?.chosen_language || 'EN';
const session  = $('Get Session').item.json || {};
const existing = session.collected_data || {};

const FLASK   = 'http://127.0.0.1:5051';
const BAILEYS = 'http://127.0.0.1:3001';
const TPL_DIR = '${PROJECT_ROOT}/resume-ai/templates';

async function send(msg) { await this.helpers.httpRequest({ method:'POST', url:`${BAILEYS}/send`, headers:{'Content-Type':'application/json'}, body:JSON.stringify({phone, text:msg}), returnFullResponse:false }); }
async function sendImg(imagePath, caption) {
  try { await this.helpers.httpRequest({ method:'POST', url:`${BAILEYS}/send-image`, headers:{'Content-Type':'application/json'}, body:JSON.stringify({phone, imagePath, caption}), returnFullResponse:false }); }
  catch(e) { console.log('sendImg failed:', e.message); }
}
async function saveMsg(role, content) { await this.helpers.httpRequest({ method:'POST', url:`${FLASK}/conversations`, headers:{'Content-Type':'application/json'}, body:JSON.stringify({phone_number:phone, role, content}), returnFullResponse:false }); }
async function setStep(step) { await this.helpers.httpRequest({ method:'POST', url:`${FLASK}/session/${phone}/step`, headers:{'Content-Type':'application/json'}, body:JSON.stringify({current_step:step}), returnFullResponse:false }); }
async function saveData(data) { await this.helpers.httpRequest({ method:'POST', url:`${FLASK}/session/${phone}/data`, headers:{'Content-Type':'application/json'}, body:JSON.stringify(data), returnFullResponse:false }); }

const TEMPLATE_NAMES = {
  BM: ['Klasik','Moden','Minimal','Bold','Eksekutif','Fresh Grad'],
  EN: ['Classic','Modern','Minimal','Bold','Executive','Fresh Grad'],
  CN: ['經典','現代','簡約','大膽','高管','應屆生']
};

// Detect choice 1-6
const match = text.match(/\b([1-6])\b/);
const choice = match ? parseInt(match[1]) : null;

await saveMsg('user', text);

if (!existing._templates_shown) {
  // First time in this step — send all 6 previews
  const INTRO = {
    BM: '🎨 Pilih template resume anda!\n\nSila lihat 6 contoh di bawah dan balas dengan nombor pilihan anda (1-6):',
    EN: '🎨 Choose your resume template!\n\nHere are 6 designs — reply with your choice (1-6):',
    CN: '🎨 請選擇您的履歷模板！\n\n以下是 6 種設計——請回覆您的選擇（1-6）：'
  };
  await saveMsg('assistant', INTRO[lang]);
  await send(INTRO[lang]);

  // Send all 6 preview images
  const names = TEMPLATE_NAMES[lang];
  for (let i = 1; i <= 6; i++) {
    await sendImg(`${TPL_DIR}/preview_${i}.png`, `*${i}. ${names[i-1]}*`);
  }

  await saveData({ _templates_shown: true });

} else if (choice && choice >= 1 && choice <= 6) {
  // User made a choice
  const names = TEMPLATE_NAMES[lang];
  await saveData({ template_choice: choice });
  await setStep('collecting');

  const CONFIRM = {
    BM: `Template *${choice}. ${TEMPLATE_NAMES.BM[choice-1]}* dipilih ✅\n\n✏️ Sekarang sila berikan maklumat berikut:\n\n1️⃣ Nama penuh\n2️⃣ Nombor telefon & emel\n3️⃣ *Jawatan sasaran*\n4️⃣ Pengalaman kerja (syarikat, jawatan, tahun, tugas utama)\n5️⃣ Pendidikan (universiti, program, tahun, CGPA)\n6️⃣ Kemahiran utama\n\nBoleh hantar semua sekali atau satu per satu 😊`,
    EN: `Template *${choice}. ${TEMPLATE_NAMES.EN[choice-1]}* selected ✅\n\n✏️ Please provide the following information:\n\n1️⃣ Full name\n2️⃣ Phone number & email\n3️⃣ *Target job title*\n4️⃣ Work experience (company, role, year, key duties)\n5️⃣ Education (university, programme, year, CGPA)\n6️⃣ Key skills\n\nYou can send everything at once or one by one 😊`,
    CN: `已選模板 *${choice}. ${TEMPLATE_NAMES.CN[choice-1]}* ✅\n\n✏️ 請提供以下資料：\n\n1️⃣ 全名\n2️⃣ 電話號碼和電郵\n3️⃣ *目標職位*\n4️⃣ 工作經歷（公司、職位、年份、主要職責）\n5️⃣ 學歷（大學、科系、年份、GPA）\n6️⃣ 主要技能\n\n可一次發送或逐項提供 😊`
  };
  await saveMsg('assistant', CONFIRM[lang]);
  await send(CONFIRM[lang]);

} else {
  // Already shown but no valid choice yet
  const RE_ASK = {
    BM: 'Sila balas dengan nombor template pilihan anda (1-6) 😊',
    EN: 'Please reply with your template choice (1-6) 😊',
    CN: '請回覆您選擇的模板號碼（1-6）😊'
  };
  await saveMsg('assistant', RE_ASK[lang]);
  await send(RE_ASK[lang]);
}

return [{ json: { ok: true } }];
