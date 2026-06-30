"""
Build resume-ai-workflow.json from scratch (Micro-LLM + State Machine architecture).
Run: python build_workflow_v2.py
"""
import json, os, sys
sys.stdout.reconfigure(encoding='utf-8')

NODES_DIR = '${PROJECT_ROOT}/resume-ai/nodes'
OUT_PATH  = '${PROJECT_ROOT}/resume-ai/n8n-exports/resume-ai-workflow.json'

def read_js(filename):
    with open(f'{NODES_DIR}/{filename}', 'r', encoding='utf-8') as f:
        return f.read()

# ─── Node definitions ───────────────────────────────────────────────────────

nodes = [

# ── Entry ──────────────────────────────────────────────────────────────────
{
  "id":"node-webhook","name":"Webhook","type":"n8n-nodes-base.webhook","typeVersion":2,
  "position":[0,300],
  "parameters":{"path":"whatsapp","httpMethod":"POST","responseMode":"responseNode","options":{}}
},
{
  "id":"node-extract","name":"Extract Message","type":"n8n-nodes-base.code","typeVersion":2,
  "position":[200,300],
  "parameters":{"jsCode":"""
const body = $input.first().json?.body || $input.first().json;
const msg  = body?.data?.message || body?.message || body || {};
const phone = (msg?.key?.remoteJid || body?.phone || '').replace('@s.whatsapp.net','');
const text  = msg?.message?.conversation || msg?.message?.extendedTextMessage?.text || msg?.text || body?.text || '';
const type  = msg?.message?.imageMessage ? 'image' : msg?.message?.documentMessage ? 'document' : 'text';
const name  = msg?.pushName || body?.name || phone;
return [{ json:{ phone, text, type, name } }];
"""}
},
{
  "id":"node-isreset","name":"Is Reset","type":"n8n-nodes-base.if","typeVersion":2.2,
  "position":[400,300],
  "parameters":{"conditions":{"options":{},"conditions":[{"leftValue":"={{ $json.text }}","rightValue":"/start","operator":{"type":"string","operation":"startsWith"}}],"combinator":"and"}}
},
{
  "id":"node-deletesession","name":"Delete Session","type":"n8n-nodes-base.httpRequest","typeVersion":4.2,
  "position":[600,120],
  "parameters":{"method":"DELETE","url":"=http://127.0.0.1:5051/session/{{ $('Extract Message').item.json.phone }}","options":{}}
},
{
  "id":"node-sendlangmenu","name":"Send Lang Menu","type":"n8n-nodes-base.httpRequest","typeVersion":4.2,
  "position":[800,120],
  "parameters":{"method":"POST","url":"http://127.0.0.1:3001/send","sendBody":True,"contentType":"raw","rawContentType":"application/json",
    "body":"={{ JSON.stringify({ phone: $('Extract Message').item.json.phone, text: 'Hi! I\\'m Ava 👋\\n\\nPlease choose your language:\\n\\n1️⃣ Bahasa Malaysia\\n2️⃣ English\\n3️⃣ 中文' }) }}","options":{}}
},

# ── Session ─────────────────────────────────────────────────────────────────
{
  "id":"node-getsession","name":"Get Session","type":"n8n-nodes-base.httpRequest","typeVersion":4.2,
  "position":[600,300],
  "parameters":{"method":"GET","url":"=http://127.0.0.1:5051/session/{{ $('Extract Message').item.json.phone }}","options":{"response":{"response":{"responseFormat":"json","fullResponse":False}}},"onError":"continueErrorOutput"}
},
{
  "id":"node-isnewuser","name":"Is New User","type":"n8n-nodes-base.if","typeVersion":2.2,
  "position":[800,300],
  "parameters":{"conditions":{"options":{},"conditions":[{"leftValue":"={{ Object.keys($json).length }}","rightValue":0,"operator":{"type":"number","operation":"equals"}}],"combinator":"and"}}
},
{
  "id":"node-createsession","name":"Create Session","type":"n8n-nodes-base.httpRequest","typeVersion":4.2,
  "position":[1000,480],
  "parameters":{"method":"POST","url":"http://127.0.0.1:5051/session","sendBody":True,"contentType":"raw","rawContentType":"application/json",
    "body":"={{ JSON.stringify({ phone_number: $('Extract Message').item.json.phone }) }}","options":{}}
},

# ── Master Switch ─────────────────────────────────────────────────────────
{
  "id":"node-masterswitch","name":"Master Switch","type":"n8n-nodes-base.switch","typeVersion":3.2,
  "position":[1000,300],
  "parameters":{
    "rules":{"values":[
      {"conditions":{"options":{},"conditions":[{"leftValue":"={{ $('Get Session').item.json?.current_step || 'new' }}","rightValue":"new",             "operator":{"type":"string","operation":"equals"}}],"combinator":"and"},"renameOutput":True,"outputKey":"new"},
      {"conditions":{"options":{},"conditions":[{"leftValue":"={{ $('Get Session').item.json?.current_step || 'new' }}","rightValue":"pdpa",            "operator":{"type":"string","operation":"equals"}}],"combinator":"and"},"renameOutput":True,"outputKey":"pdpa"},
      {"conditions":{"options":{},"conditions":[{"leftValue":"={{ $('Get Session').item.json?.current_step || 'new' }}","rightValue":"service_select",  "operator":{"type":"string","operation":"equals"}}],"combinator":"and"},"renameOutput":True,"outputKey":"service"},
      {"conditions":{"options":{},"conditions":[{"leftValue":"={{ $('Get Session').item.json?.current_step || 'new' }}","rightValue":"template_select", "operator":{"type":"string","operation":"equals"}}],"combinator":"and"},"renameOutput":True,"outputKey":"template"},
      {"conditions":{"options":{},"conditions":[{"leftValue":"={{ $('Get Session').item.json?.current_step || 'new' }}","rightValue":"collecting",      "operator":{"type":"string","operation":"equals"}}],"combinator":"and"},"renameOutput":True,"outputKey":"collecting"},
      {"conditions":{"options":{},"conditions":[{"leftValue":"={{ $('Get Session').item.json?.current_step || 'new' }}","rightValue":"payment_pending", "operator":{"type":"string","operation":"equals"}}],"combinator":"and"},"renameOutput":True,"outputKey":"payment"},
      {"conditions":{"options":{},"conditions":[{"leftValue":"={{ $('Get Session').item.json?.current_step || 'new' }}","rightValue":"feedback",        "operator":{"type":"string","operation":"equals"}}],"combinator":"and"},"renameOutput":True,"outputKey":"feedback"},
    ]},
    "options":{"fallbackOutput":"none"}
  }
},

# ── Branch nodes ─────────────────────────────────────────────────────────
{
  "id":"node-handlenew",      "name":"Handle New",      "type":"n8n-nodes-base.code","typeVersion":2,
  "position":[1280,60],   "parameters":{"jsCode": read_js('handle_new.js')}
},
{
  "id":"node-handlepdpa",     "name":"Handle PDPA",     "type":"n8n-nodes-base.code","typeVersion":2,
  "position":[1280,160],  "parameters":{"jsCode": read_js('handle_pdpa.js')}
},
{
  "id":"node-handleservice",  "name":"Handle Service",  "type":"n8n-nodes-base.code","typeVersion":2,
  "position":[1280,260],  "parameters":{"jsCode": read_js('handle_service.js')}
},
{
  "id":"node-handletemplate", "name":"Handle Template", "type":"n8n-nodes-base.code","typeVersion":2,
  "position":[1280,360],  "parameters":{"jsCode": read_js('handle_template.js')}
},
{
  "id":"node-aicollecting",   "name":"AI Collecting",   "type":"n8n-nodes-base.code","typeVersion":2,
  "position":[1280,460],  "parameters":{"jsCode": read_js('ai_collecting.js')}
},
{
  "id":"node-handlepayment",  "name":"Handle Payment",  "type":"n8n-nodes-base.code","typeVersion":2,
  "position":[1280,560],  "parameters":{"jsCode": read_js('handle_payment.js')}
},
{
  "id":"node-aifeedback",     "name":"AI Feedback",     "type":"n8n-nodes-base.code","typeVersion":2,
  "position":[1280,660],  "parameters":{"jsCode": read_js('ai_feedback.js')}
},

# ── Respond to webhook ────────────────────────────────────────────────────
{
  "id":"node-respondok","name":"Respond OK","type":"n8n-nodes-base.respondToWebhook","typeVersion":1.1,
  "position":[200,500],
  "parameters":{"respondWith":"json","responseBody":"={\"ok\":true}","options":{}}
},

]

# ─── Connections ─────────────────────────────────────────────────────────────

connections = {
  "Webhook":         {"main": [[{"node":"Extract Message","type":"main","index":0}]]},
  "Extract Message": {"main": [[{"node":"Is Reset","type":"main","index":0}]]},
  "Is Reset":        {"main": [
    [{"node":"Delete Session",  "type":"main","index":0}],   # true = reset
    [{"node":"Get Session",     "type":"main","index":0}],   # false = normal
  ]},
  "Delete Session":  {"main": [[{"node":"Send Lang Menu","type":"main","index":0}]]},
  "Get Session":     {"main": [[{"node":"Is New User","type":"main","index":0}]]},
  "Is New User":     {"main": [
    [{"node":"Create Session","type":"main","index":0}],  # true = new
    [{"node":"Master Switch", "type":"main","index":0}],  # false = existing
  ]},
  "Create Session":  {"main": [[{"node":"Master Switch","type":"main","index":0}]]},
  "Master Switch":   {"main": [
    [{"node":"Handle New",      "type":"main","index":0}],  # 0 new
    [{"node":"Handle PDPA",     "type":"main","index":0}],  # 1 pdpa
    [{"node":"Handle Service",  "type":"main","index":0}],  # 2 service_select
    [{"node":"Handle Template", "type":"main","index":0}],  # 3 template_select
    [{"node":"AI Collecting",   "type":"main","index":0}],  # 4 collecting
    [{"node":"Handle Payment",  "type":"main","index":0}],  # 5 payment_pending
    [{"node":"AI Feedback",     "type":"main","index":0}],  # 6 feedback
  ]},
  # All branch handlers → Respond OK
  "Handle New":      {"main": [[{"node":"Respond OK","type":"main","index":0}]]},
  "Handle PDPA":     {"main": [[{"node":"Respond OK","type":"main","index":0}]]},
  "Handle Service":  {"main": [[{"node":"Respond OK","type":"main","index":0}]]},
  "Handle Template": {"main": [[{"node":"Respond OK","type":"main","index":0}]]},
  "AI Collecting":   {"main": [[{"node":"Respond OK","type":"main","index":0}]]},
  "Handle Payment":  {"main": [[{"node":"Respond OK","type":"main","index":0}]]},
  "AI Feedback":     {"main": [[{"node":"Respond OK","type":"main","index":0}]]},
  "Send Lang Menu":  {"main": [[{"node":"Respond OK","type":"main","index":0}]]},
}

# ─── Assemble workflow ────────────────────────────────────────────────────────

workflow = {
  "name": "Resume-AI v2",
  "nodes": nodes,
  "connections": connections,
  "active": False,
  "settings": {"executionOrder": "v1"},
  "versionId": "resume-ai-v2",
  "meta": {"instanceId": "resume-ai"},
  "id": "resume-ai-v2",
  "tags": []
}

os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
with open(OUT_PATH, 'w', encoding='utf-8') as f:
    json.dump(workflow, f, indent=2, ensure_ascii=False)

print(f'Workflow saved to {OUT_PATH}')
print(f'Nodes: {len(nodes)}')
print(f'Connections: {len(connections)} source nodes')
