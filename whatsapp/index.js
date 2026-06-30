const { default: makeWASocket, DisconnectReason, useMultiFileAuthState, fetchLatestBaileysVersion } = require('@whiskeysockets/baileys')
const { Boom } = require('@hapi/boom')
const express = require('express')
const axios = require('axios')
const path = require('path')
const fs = require('fs')
const qrcode = require('qrcode-terminal')
const QRCode = require('qrcode')

const app = express()
app.use(express.json({ limit: '50mb' }))

const N8N_WEBHOOK = 'http://127.0.0.1:5678/webhook/whatsapp'
const SESSION_DIR = path.join(__dirname, 'sessions')
const UPLOADS_DIR = path.join(__dirname, '..', 'uploads')
const PORT = 3001

let sock = null
let isConnected = false

if (!fs.existsSync(UPLOADS_DIR)) fs.mkdirSync(UPLOADS_DIR, { recursive: true })

async function connectToWhatsApp() {
    const { state, saveCreds } = await useMultiFileAuthState(SESSION_DIR)
    const { version } = await fetchLatestBaileysVersion()
    sock = makeWASocket({ version, auth: state, browser: ['Resume-AI', 'Chrome', '1.0'], syncFullHistory: false })
    sock.ev.on('creds.update', saveCreds)

    sock.ev.on('connection.update', ({ connection, lastDisconnect, qr }) => {
        if (qr) {
            console.log('\n📱 Scan QR:\n')
            qrcode.generate(qr, { small: false })
            const qrPath = path.join(__dirname, 'qr.png')
            QRCode.toFile(qrPath, qr, { width: 400 }, (err) => {
                if (!err) {
                    console.log(`\n[QR saved] ${qrPath}`)
                    console.log('[Opening in browser for easy scanning...]')
                    require('child_process').exec(`start "" "${qrPath}"`)
                }
            })
        }
        if (connection === 'close') {
            isConnected = false
            const code = new Boom(lastDisconnect?.error)?.output?.statusCode
            if (code !== DisconnectReason.loggedOut) { console.log('🔄 Reconnecting...'); connectToWhatsApp() }
            else console.log('❌ Logged out. Delete sessions/ and restart.')
        } else if (connection === 'open') { isConnected = true; console.log('✅ WhatsApp connected!') }
    })

    sock.ev.on('messages.upsert', async ({ messages, type }) => {
        if (type !== 'notify') return
        for (const msg of messages) {
            if (msg.key.fromMe || !msg.message) continue
            const jid = msg.key.remoteJid
            if (jid.endsWith('@g.us')) continue
            const phone = jid.replace('@s.whatsapp.net', '')
            const name = msg.pushName || phone

            const docMsg = msg.message?.documentMessage
                || msg.message?.documentWithCaptionMessage?.message?.documentMessage
            if (docMsg) {
                const filename = docMsg.fileName || `doc_${Date.now()}`
                const filepath = path.join(UPLOADS_DIR, `${phone}_${Date.now()}_${filename}`)
                try {
                    const buffer = await sock.downloadMediaMessage(msg, 'buffer')
                    fs.writeFileSync(filepath, buffer)
                    console.log(`📎 [${phone}] saved: ${filepath}`)
                    await axios.post(N8N_WEBHOOK, { phone, name, text: '[ATTACHMENT]', filename, filepath }, { timeout: 30000 })
                } catch (err) { console.error(`❌ Doc error: ${err.message}`) }
                continue
            }

            const text = msg.message?.conversation || msg.message?.extendedTextMessage?.text || ''
            if (!text.trim()) continue
            console.log(`📩 [${phone}] ${name}: ${text}`)
            try { await axios.post(N8N_WEBHOOK, { phone, text, name }, { timeout: 30000 }) }
            catch (err) { console.error(`❌ n8n error: ${err.message}`) }
        }
    })
}

app.post('/send', async (req, res) => {
    const { phone, text } = req.body
    if (!isConnected) return res.status(500).json({ ok: false, error: 'Not connected' })
    if (!phone || !text) return res.status(400).json({ ok: false, error: 'Missing phone or text' })
    try {
        const jid = phone.includes('@') ? phone : `${phone}@s.whatsapp.net`
        await sock.sendMessage(jid, { text: String(text) })
        res.json({ ok: true })
    } catch (err) { res.status(500).json({ ok: false, error: err.message }) }
})

app.post('/send-image', async (req, res) => {
    const { phone, imagePath, caption } = req.body
    if (!isConnected) return res.status(500).json({ ok: false, error: 'Not connected' })
    if (!phone || !imagePath) return res.status(400).json({ ok: false, error: 'Missing phone or imagePath' })
    res.json({ ok: true })
    try {
        const buffer = fs.readFileSync(imagePath)
        const jid = phone.includes('@') ? phone : `${phone}@s.whatsapp.net`
        await sock.sendMessage(jid, { image: buffer, caption: caption || '' })
        console.log(`🖼️ Image sent to ${jid}`)
    } catch (err) { console.error(`❌ Image send error: ${err.message}`) }
})

app.get('/health', (req, res) => res.json({ ok: true, connected: isConnected }))

app.listen(PORT, () => console.log(`✅ Baileys on http://127.0.0.1:${PORT}`))
connectToWhatsApp()
