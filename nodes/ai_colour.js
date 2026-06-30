// Step: template_colour — pure regex, no AI, no loops
const phone    = $('Extract Message').item.json.phone;
const text     = ($('Extract Message').item.json.text || '').trim();
const lang     = $('Get Session').item.json?.chosen_language || 'EN';
const session  = $('Get Session').item.json || {};
const existing = session.collected_data || {};

const FLASK   = 'http://127.0.0.1:5051';
const BAILEYS = 'http://127.0.0.1:3001';

async function send(msg) { await this.helpers.httpRequest({ method:'POST', url:`${BAILEYS}/send`, headers:{'Content-Type':'application/json'}, body:JSON.stringify({phone, text:msg}), returnFullResponse:false }); }
async function sendImg(imagePath, caption) { await this.helpers.httpRequest({ method:'POST', url:`${BAILEYS}/send-image`, headers:{'Content-Type':'application/json'}, body:JSON.stringify({phone, imagePath, caption}), returnFullResponse:false }); }
async function saveMsg(role, content) { await this.helpers.httpRequest({ method:'POST', url:`${FLASK}/conversations`, headers:{'Content-Type':'application/json'}, body:JSON.stringify({phone_number:phone, role, content}), returnFullResponse:false }); }
async function setStep(step) { await this.helpers.httpRequest({ method:'POST', url:`${FLASK}/session/${phone}/step`, headers:{'Content-Type':'application/json'}, body:JSON.stringify({current_step:step}), returnFullResponse:false }); }
async function saveData(data) { await this.helpers.httpRequest({ method:'POST', url:`${FLASK}/session/${phone}/data`, headers:{'Content-Type':'application/json'}, body:JSON.stringify(data), returnFullResponse:false }); }

// Detect from current message
const colourMatch = text.match(/\b([1-5])\b/);
const styleMatch  = text.match(/\b(III|II|I)\b/i);

// Merge new detections with previously saved partial choices
const colour = colourMatch ? colourMatch[1] : (existing.colour || null);
const style  = styleMatch  ? styleMatch[1].toUpperCase() : (existing.style || null);

await saveMsg('user', text);

if (colour && style) {
  // Both chosen — advance
  await saveData({ colour, style });
  await setStep('collecting');

  const layout = existing.layout || 'A';
  try {
    const prev = await this.helpers.httpRequest({ method:'POST', url:`${FLASK}/generate-preview`, headers:{'Content-Type':'application/json'}, body:JSON.stringify({phone, layout, colour, style}), returnFullResponse:false });
    if (prev.ok && prev.imagePath) {
      const cap = { BM:'Preview resume anda! 😊', EN:'Your resume preview! 😊', CN:'您的履歷預覽！😊' }[lang];
      await sendImg(prev.imagePath, cap);
    }
  } catch(e) {}

  const ASK = {
    BM: '✏️ Saya suka pilihan anda!\n\nSekarang sila berikan maklumat berikut:\n\n1️⃣ Nama penuh\n2️⃣ *Jawatan sasaran* (cth: Software Engineer, Pengurus)\n3️⃣ Tahun pengalaman kerja\n4️⃣ Pendidikan (universiti, program, CGPA)\n5️⃣ Pengalaman kerja (syarikat, jawatan, tempoh)\n6️⃣ Kemahiran utama\n\nBoleh hantar semua sekali atau satu per satu.',
    EN: '✏️ Love your choices!\n\nPlease provide the following:\n\n1️⃣ Full name\n2️⃣ *Target job title* (e.g. Software Engineer, Manager)\n3️⃣ Years of experience\n4️⃣ Education (university, programme, CGPA)\n5️⃣ Work experience (company, role, duration)\n6️⃣ Key skills\n\nYou can send all at once or one by one.',
    CN: '✏️ 很好的選擇！\n\n請提供以下資料：\n\n1️⃣ 全名\n2️⃣ *目標職位*（例：軟體工程師、經理）\n3️⃣ 工作年資\n4️⃣ 學歷（大學、科系、GPA）\n5️⃣ 工作經歷（公司、職位、任期）\n6️⃣ 主要技能\n\n可一次發送或逐項提供。'
  };
  await saveMsg('assistant', ASK[lang]);
  await send(ASK[lang]);

} else if (colour && !style) {
  // Save partial colour
  await saveData({ colour });
  const ASK = {
    BM: `Warna *${colour}* dipilih ✅\n\nSila pilih gaya resume anda:\n\n*I* — Klasik\n*II* — Moden\n*III* — Kontemporari`,
    EN: `Colour *${colour}* selected ✅\n\nNow choose your resume style:\n\n*I* — Classic\n*II* — Modern\n*III* — Contemporary`,
    CN: `已選顏色 *${colour}* ✅\n\n請選擇履歷樣式：\n\n*I* — 經典\n*II* — 現代\n*III* — 當代`
  };
  await saveMsg('assistant', ASK[lang]);
  await send(ASK[lang]);

} else if (!colour && style) {
  // Save partial style
  await saveData({ style });
  const ASK = {
    BM: `Gaya *${style}* dipilih ✅\n\nSila pilih nombor warna (1-5) untuk resume anda.`,
    EN: `Style *${style}* selected ✅\n\nPlease choose a colour number (1-5) for your resume.`,
    CN: `已選樣式 *${style}* ✅\n\n請選擇顏色編號（1-5）。`
  };
  await saveMsg('assistant', ASK[lang]);
  await send(ASK[lang]);

} else {
  // Neither — re-ask
  const ASK = {
    BM: 'Sila hantar nombor warna (1-5) dan gaya resume (I, II, atau III).\n\nContoh: *3 II*',
    EN: 'Please send your colour number (1-5) and resume style (I, II, or III).\n\nExample: *3 II*',
    CN: '請發送顏色編號（1-5）和樣式（I、II 或 III）。\n\n例如：*3 II*'
  };
  await saveMsg('assistant', ASK[lang]);
  await send(ASK[lang]);
}

return [{ json: { ok: true } }];
