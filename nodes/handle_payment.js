// Step: payment_pending
// Task: Detect payment proof (image or keywords). Notify Telegram, advance to feedback.
const phone   = $('Extract Message').item.json.phone;
const text    = ($('Extract Message').item.json.text || '').trim();
const msgType = $('Extract Message').item.json.type || 'text';
const lang    = $('Get Session').item.json?.chosen_language || 'EN';
const name    = $('Extract Message').item.json.name || phone;

const FLASK    = 'http://127.0.0.1:5051';
const BAILEYS  = 'http://127.0.0.1:3001';
const TG_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN';
const TELEGRAM_ADMIN_CHAT_ID = YOUR_TELEGRAM_ADMIN_CHAT_ID;

async function send(msg)   { await this.helpers.httpRequest({ method:'POST', url:`${BAILEYS}/send`,         headers:{'Content-Type':'application/json'}, body:JSON.stringify({phone, text:msg}), returnFullResponse:false }); }
async function saveMsg(role, content) { await this.helpers.httpRequest({ method:'POST', url:`${FLASK}/conversations`, headers:{'Content-Type':'application/json'}, body:JSON.stringify({phone_number:phone, role, content}), returnFullResponse:false }); }
async function setStep(step) { await this.helpers.httpRequest({ method:'POST', url:`${FLASK}/session/${phone}/step`, headers:{'Content-Type':'application/json'}, body:JSON.stringify({current_step:step}), returnFullResponse:false }); }

// Detect payment proof: image attachment OR payment keywords
const isImage    = msgType === 'image' || msgType === 'document';
const hasKeyword = /paid|bayar|dah bayar|已付|transfer|slip|receipt|payment/i.test(text);
const isPaid     = isImage || hasKeyword;

await saveMsg('user', text || '[payment proof]');

if (isPaid) {
  // Notify Telegram
  const tgMsg = `💰 Payment Received!\n\nFrom: ${phone}\nName: ${name}\n\nPlease verify payment and deliver resume.`;
  try {
    await this.helpers.httpRequest({ method:'POST', url:`https://api.telegram.org/bot${TG_TOKEN}/sendMessage`, headers:{'Content-Type':'application/json'}, body:JSON.stringify({chat_id:TG_CHAT, text:tgMsg}), returnFullResponse:false });
  } catch(e) { console.log('TG notify failed:', e.message); }

  await setStep('feedback');

  const THANKS = {
    BM: 'Terima kasih! 🙏 Pembayaran anda sedang disahkan. Resume anda akan siap dalam 24 jam.\n\nSambil menunggu, boleh beri kami penilaian?\n\n⭐ Beri markah 1-5 untuk perkhidmatan kami.',
    EN: 'Thank you! 🙏 Your payment is being verified. Your resume will be ready within 24 hours.\n\nWhile waiting, could you rate our service?\n\n⭐ Give us a rating from 1 to 5.',
    CN: '謝謝！🙏 您的付款正在核實中。您的履歷將在 24 小時內完成。\n\n趁此機會，能給我們評分嗎？\n\n⭐ 請給我們 1 到 5 分的評價。'
  };
  await saveMsg('assistant', THANKS[lang]);
  await send(THANKS[lang]);
} else {
  const REMIND = {
    BM: 'Sila hantar bukti pembayaran (screenshot) setelah melakukan pembayaran. 😊',
    EN: 'Please send your payment screenshot after completing the transfer. 😊',
    CN: '請在完成匯款後，發送付款截圖。😊'
  };
  await saveMsg('assistant', REMIND[lang]);
  await send(REMIND[lang]);
}

return [{ json: { ok: true } }];
