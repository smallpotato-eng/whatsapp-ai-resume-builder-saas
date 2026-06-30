// Step: new
// Task: Show language menu. If user picks 1/2/3, save language, send PDPA, advance to pdpa.
const phone = $('Extract Message').item.json.phone;
const text  = ($('Extract Message').item.json.text || '').trim();

const FLASK   = 'http://127.0.0.1:5051';
const BAILEYS = 'http://127.0.0.1:3001';

async function send(msg)   { await this.helpers.httpRequest({ method:'POST', url:`${BAILEYS}/send`,         headers:{'Content-Type':'application/json'}, body:JSON.stringify({phone, text:msg}), returnFullResponse:false }); }
async function saveMsg(role, content) { await this.helpers.httpRequest({ method:'POST', url:`${FLASK}/conversations`, headers:{'Content-Type':'application/json'}, body:JSON.stringify({phone_number:phone, role, content}), returnFullResponse:false }); }
async function setStep(step, extra={}) { await this.helpers.httpRequest({ method:'POST', url:`${FLASK}/session/${phone}/step`, headers:{'Content-Type':'application/json'}, body:JSON.stringify({current_step:step, ...extra}), returnFullResponse:false }); }

const LANG_MENU = 'Hi! I\'m Ava 👋 Saya Ava!\n\nPlease choose your language / Sila pilih bahasa anda:\n\n1️⃣ Bahasa Malaysia\n2️⃣ English\n3️⃣ 中文';

const PDPA = {
  BM: 'Sebelum kita mulakan, sila ambil perhatian 📋\n\nAva Resume Studio mengumpul maklumat peribadi anda (nama, pendidikan, pengalaman kerja, kemahiran) semata-mata untuk tujuan penghasilan résumé. Maklumat anda tidak akan dikongsi dengan pihak ketiga.\n\n• Anda bertanggungjawab atas ketepatan maklumat yang diberikan.\n• Perkhidmatan kami tidak menjamin peluang pekerjaan.\n• Bayaran balik tidak tersedia setelah résumé dihantar.\n\nBalas "Setuju" untuk meneruskan. 😊',
  EN: 'Before we begin, please note 📋\n\nAva Resume Studio collects your personal information (name, education, work history, skills) solely for the purpose of creating your resume. Your data will not be shared with third parties.\n\n• You are responsible for the accuracy of information provided.\n• Our service does not guarantee employment outcomes.\n• Refunds are not available once the resume has been delivered.\n\nReply "Agree" to proceed. 😊',
  CN: '開始之前，請注意 📋\n\nAva Resume Studio 收集您的個人資料（姓名、學歷、工作經歷、技能），僅用於製作履歷。您的資料不會與第三方共享。\n\n• 您對所提供資料的準確性負責。\n• 本服務不保證求職結果。\n• 履歷交付後不提供退款。\n\n回覆「同意」即表示您接受以上條款。😊'
};

const langMap = { '1':'BM', '2':'EN', '3':'CN' };
const choice = langMap[text];

if (choice) {
  await setStep('pdpa', { chosen_language: choice });
  await saveMsg('user', text);
  await saveMsg('assistant', PDPA[choice]);
  await send(PDPA[choice]);
} else {
  await send(LANG_MENU);
}

return [{ json: { ok: true } }];
