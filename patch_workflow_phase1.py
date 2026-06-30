import json, sys
sys.stdout.reconfigure(encoding='utf-8')

wf_path = '${PROJECT_ROOT}/resume-ai/n8n-exports/resume-ai-workflow.json'
with open(wf_path, 'r', encoding='utf-8') as f:
    wf = json.load(f)

# 1. Update Build Messages with latest code
with open('${PROJECT_ROOT}/resume-ai/build_messages_tmp.js', 'r', encoding='utf-8') as f:
    bm_code = f.read()

for n in wf['nodes']:
    if n['name'] == 'Build Messages':
        n['parameters']['jsCode'] = bm_code
        print('Updated Build Messages')
        break

# 2. Step Router Switch node
step_router = {
    "parameters": {
        "rules": {
            "values": [
                {
                    "conditions": {
                        "options": {},
                        "conditions": [{"leftValue": "={{ $('Get Session').item.json.current_step }}", "rightValue": "template_layout", "operator": {"type": "string", "operation": "equals"}}],
                        "combinator": "and"
                    },
                    "renameOutput": True,
                    "outputKey": "Layout"
                },
                {
                    "conditions": {
                        "options": {},
                        "conditions": [{"leftValue": "={{ $('Get Session').item.json.current_step }}", "rightValue": "template_colour", "operator": {"type": "string", "operation": "equals"}}],
                        "combinator": "and"
                    },
                    "renameOutput": True,
                    "outputKey": "Colour"
                },
                {
                    "conditions": {
                        "options": {},
                        "conditions": [{"leftValue": "={{ $('Get Session').item.json.current_step }}", "rightValue": "feedback_rating", "operator": {"type": "string", "operation": "equals"}}],
                        "combinator": "and"
                    },
                    "renameOutput": True,
                    "outputKey": "Rating"
                }
            ]
        },
        "options": {"fallbackOutput": "extra"}
    },
    "id": "node-steprouter",
    "name": "Step Router",
    "type": "n8n-nodes-base.switch",
    "typeVersion": 3.2,
    "position": [1500, 300]
}

# 3. Handle Layout Choice
handle_layout_code = (
    "const phone = $('Extract Message').item.json.phone;\n"
    "const text  = $('Extract Message').item.json.text || '';\n"
    "const lang  = $('Get Session').item.json?.chosen_language || 'English';\n"
    "\n"
    "const match = text.trim().toUpperCase().match(/\\b([AB])\\b/);\n"
    "\n"
    "if (match) {\n"
    "  const layout = match[1];\n"
    "  await this.helpers.httpRequest({ method:'POST', url:`http://127.0.0.1:5051/session/${phone}/step`,\n"
    "    headers:{'Content-Type':'application/json'},\n"
    "    body: JSON.stringify({ current_step:'template_colour', template_layout:layout }), returnFullResponse:false });\n"
    "\n"
    "  let reply = lang==='Bahasa Malaysia'\n"
    "    ? `Layout ${layout} dipilih! \\u2705\\n\\nSekarang pilih warna (1-5) dan gaya (I / II / III).\\nContoh: \"2 II\"`\n"
    "    : lang==='\\u4e2d\\u6587'\n"
    "    ? `\\u5df2\\u9078\\u7248\\u9762 ${layout} \\u2705\\n\\n\\u8acb\\u9078\\u984f\\u8272\\uff081-5\\uff09\\u548c\\u98a8\\u683c\\uff08I / II / III\\uff09\\u3002\\n\\u4f8b\\u5982\\uff1a\\u300c2 II\\u300d`\n"
    "    : `Layout ${layout} selected! \\u2705\\n\\nNow choose colour (1-5) and style (I / II / III).\\nExample: \"2 II\"`;\n"
    "\n"
    "  await this.helpers.httpRequest({ method:'POST', url:'http://127.0.0.1:5051/conversations',\n"
    "    headers:{'Content-Type':'application/json'}, body:JSON.stringify({phone_number:phone,role:'user',content:text}), returnFullResponse:false });\n"
    "  await this.helpers.httpRequest({ method:'POST', url:'http://127.0.0.1:5051/conversations',\n"
    "    headers:{'Content-Type':'application/json'}, body:JSON.stringify({phone_number:phone,role:'assistant',content:reply}), returnFullResponse:false });\n"
    "  await this.helpers.httpRequest({ method:'POST', url:'http://127.0.0.1:3001/send',\n"
    "    headers:{'Content-Type':'application/json'}, body:JSON.stringify({phone,text:reply}), returnFullResponse:false });\n"
    "  await this.helpers.httpRequest({ method:'POST', url:'http://127.0.0.1:3001/send-image',\n"
    "    headers:{'Content-Type':'application/json'}, body:JSON.stringify({phone,imagePath:'${PROJECT_ROOT}/resume-ai/templates/colour_swatch.png'}), returnFullResponse:false });\n"
    "\n"
    "  return [{ json:{ ok:true } }];\n"
    "} else {\n"
    "  let reply = lang==='Bahasa Malaysia' ? 'Sila taip A (dua kolum) atau B (satu kolum) \\ud83d\\ude0a'\n"
    "    : lang==='\\u4e2d\\u6587' ? '\\u8acb\\u8f38\\u5165 A\\uff08\\u96d9\\u6b04\\uff09\\u6216 B\\uff08\\u55ae\\u6b04\\uff09 \\ud83d\\ude0a'\n"
    "    : 'Please type A (two-column) or B (single-column) \\ud83d\\ude0a';\n"
    "  await this.helpers.httpRequest({ method:'POST', url:'http://127.0.0.1:5051/conversations',\n"
    "    headers:{'Content-Type':'application/json'}, body:JSON.stringify({phone_number:phone,role:'user',content:text}), returnFullResponse:false });\n"
    "  await this.helpers.httpRequest({ method:'POST', url:'http://127.0.0.1:5051/conversations',\n"
    "    headers:{'Content-Type':'application/json'}, body:JSON.stringify({phone_number:phone,role:'assistant',content:reply}), returnFullResponse:false });\n"
    "  await this.helpers.httpRequest({ method:'POST', url:'http://127.0.0.1:3001/send',\n"
    "    headers:{'Content-Type':'application/json'}, body:JSON.stringify({phone,text:reply}), returnFullResponse:false });\n"
    "  return [{ json:{ ok:false } }];\n"
    "}\n"
)

handle_layout = {
    "parameters": {"jsCode": handle_layout_code},
    "id": "node-handlelayout",
    "name": "Handle Layout Choice",
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [1700, 80]
}

# 4. Handle Colour Choice
handle_colour_code = (
    "const phone   = $('Extract Message').item.json.phone;\n"
    "const text    = $('Extract Message').item.json.text || '';\n"
    "const lang    = $('Get Session').item.json?.chosen_language || 'English';\n"
    "const layout  = $('Get Session').item.json?.template_layout || 'A';\n"
    "\n"
    "const colourMatch = text.match(/[1-5]/);\n"
    "const styleMatch  = text.toUpperCase().match(/\\b(III|II|I)\\b/);\n"
    "const colour = colourMatch ? colourMatch[0] : null;\n"
    "const style  = styleMatch  ? styleMatch[1]  : null;\n"
    "\n"
    "const colourNames = {'1':'Navy Blue','2':'Charcoal','3':'Teal','4':'Crimson','5':'Warm Beige'};\n"
    "const styleNames  = {'I':'Classic','II':'Modern','III':'Minimal'};\n"
    "\n"
    "async function saveAndSend(userText, aiReply) {\n"
    "  await this.helpers.httpRequest({ method:'POST', url:'http://127.0.0.1:5051/conversations',\n"
    "    headers:{'Content-Type':'application/json'}, body:JSON.stringify({phone_number:phone,role:'user',content:userText}), returnFullResponse:false });\n"
    "  await this.helpers.httpRequest({ method:'POST', url:'http://127.0.0.1:5051/conversations',\n"
    "    headers:{'Content-Type':'application/json'}, body:JSON.stringify({phone_number:phone,role:'assistant',content:aiReply}), returnFullResponse:false });\n"
    "  await this.helpers.httpRequest({ method:'POST', url:'http://127.0.0.1:3001/send',\n"
    "    headers:{'Content-Type':'application/json'}, body:JSON.stringify({phone,text:aiReply}), returnFullResponse:false });\n"
    "}\n"
    "\n"
    "if (colour && style) {\n"
    "  await this.helpers.httpRequest({ method:'POST', url:`http://127.0.0.1:5051/session/${phone}/step`,\n"
    "    headers:{'Content-Type':'application/json'},\n"
    "    body:JSON.stringify({current_step:'data_collection',template_colour:colour,template_style:style}), returnFullResponse:false });\n"
    "\n"
    "  let confirm = lang==='Bahasa Malaysia'\n"
    "    ? `Layout ${layout} | ${colourNames[colour]} | ${styleNames[style]} \\u2705\\n\\nMenjana preview...`\n"
    "    : lang==='\\u4e2d\\u6587'\n"
    "    ? `\\u7248\\u9762 ${layout} | ${colourNames[colour]} | ${styleNames[style]} \\u2705\\n\\n\\u751f\\u6210\\u9810\\u89bd\\u4e2d\\u22ef`\n"
    "    : `Layout ${layout} | ${colourNames[colour]} | ${styleNames[style]} \\u2705\\n\\nGenerating preview...`;\n"
    "  await saveAndSend.call(this, text, confirm);\n"
    "\n"
    "  try {\n"
    "    const prev = await this.helpers.httpRequest({ method:'POST', url:'http://127.0.0.1:5051/generate-preview',\n"
    "      headers:{'Content-Type':'application/json'}, body:JSON.stringify({phone,layout,colour,style}), returnFullResponse:false });\n"
    "    if (prev.ok && prev.imagePath) {\n"
    "      const cap = lang==='Bahasa Malaysia' ? 'Preview resume anda! \\ud83d\\ude0a'\n"
    "        : lang==='\\u4e2d\\u6587' ? '\\u60a8\\u7684\\u5c65\\u6b77\\u9810\\u89bd\\uff01\\ud83d\\ude0a'\n"
    "        : 'Your resume preview! \\ud83d\\ude0a';\n"
    "      await this.helpers.httpRequest({ method:'POST', url:'http://127.0.0.1:3001/send-image',\n"
    "        headers:{'Content-Type':'application/json'}, body:JSON.stringify({phone,imagePath:prev.imagePath,caption:cap}), returnFullResponse:false });\n"
    "    }\n"
    "  } catch(e) { console.log('Preview failed:', e.message); }\n"
    "\n"
    "  let ask = lang==='Bahasa Malaysia'\n"
    "    ? '\\u270f\\ufe0f Sekarang saya perlukan maklumat anda:\\n\\n1\\ufe0f\\u20e3 Nama penuh\\n2\\ufe0f\\u20e3 Jawatan sasaran (cth: Software Engineer)\\n3\\ufe0f\\u20e3 Tahun pengalaman\\n4\\ufe0f\\u20e3 Pendidikan (universiti, program, CGPA)\\n5\\ufe0f\\u20e3 Pengalaman kerja (syarikat, jawatan, tempoh)\\n6\\ufe0f\\u20e3 Kemahiran utama'\n"
    "    : lang==='\\u4e2d\\u6587'\n"
    "    ? '\\u270f\\ufe0f \\u8acb\\u63d0\\u4f9b\\u4ee5\\u4e0b\\u8cc7\\u6599\\uff1a\\n\\n1\\ufe0f\\u20e3 \\u5168\\u540d\\n2\\ufe0f\\u20e3 \\u76ee\\u6a19\\u8077\\u4f4d\\uff08\\u4f8b\\uff1a\\u8edf\\u9ad4\\u5de5\\u7a0b\\u5e2b\\uff09\\n3\\ufe0f\\u20e3 \\u5de5\\u4f5c\\u5e74\\u8cc7\\n4\\ufe0f\\u20e3 \\u5b78\\u6b77\\uff08\\u5927\\u5b78\\u3001\\u79d1\\u7cfb\\u3001GPA\\uff09\\n5\\ufe0f\\u20e3 \\u5de5\\u4f5c\\u7d93\\u6b77\\uff08\\u516c\\u53f8\\u3001\\u8077\\u4f4d\\u3001\\u4efb\\u671f\\uff09\\n6\\ufe0f\\u20e3 \\u4e3b\\u8981\\u6280\\u80fd'\n"
    "    : '\\u270f\\ufe0f Please provide your details:\\n\\n1\\ufe0f\\u20e3 Full name\\n2\\ufe0f\\u20e3 Target job title (e.g. Software Engineer)\\n3\\ufe0f\\u20e3 Years of experience\\n4\\ufe0f\\u20e3 Education (university, programme, CGPA)\\n5\\ufe0f\\u20e3 Work experience (company, role, duration)\\n6\\ufe0f\\u20e3 Key skills';\n"
    "  await this.helpers.httpRequest({ method:'POST', url:'http://127.0.0.1:5051/conversations',\n"
    "    headers:{'Content-Type':'application/json'}, body:JSON.stringify({phone_number:phone,role:'assistant',content:ask}), returnFullResponse:false });\n"
    "  await this.helpers.httpRequest({ method:'POST', url:'http://127.0.0.1:3001/send',\n"
    "    headers:{'Content-Type':'application/json'}, body:JSON.stringify({phone,text:ask}), returnFullResponse:false });\n"
    "  return [{ json:{ ok:true } }];\n"
    "\n"
    "} else if (colour && !style) {\n"
    "  let reply = lang==='Bahasa Malaysia'\n"
    "    ? `Warna ${colour} dipilih! Pilih gaya: I (Classic), II (Modern), atau III (Minimal)`\n"
    "    : lang==='\\u4e2d\\u6587'\n"
    "    ? `\\u984f\\u8272 ${colour} \\u5df2\\u9078\\uff01\\u8acb\\u9078\\u98a8\\u683c\\uff1aI\\uff08\\u7d93\\u5178\\uff09\\u3001II\\uff08\\u73fe\\u4ee3\\uff09\\u6216 III\\uff08\\u7c21\\u7d04\\uff09`\n"
    "    : `Colour ${colour} selected! Choose style: I (Classic), II (Modern), or III (Minimal)`;\n"
    "  await saveAndSend.call(this, text, reply);\n"
    "  return [{ json:{ ok:false } }];\n"
    "\n"
    "} else {\n"
    "  let reply = lang==='Bahasa Malaysia' ? 'Sila pilih warna (1-5) dan gaya (I/II/III). Contoh: \"2 II\"'\n"
    "    : lang==='\\u4e2d\\u6587' ? '\\u8acb\\u9078\\u984f\\u8272\\uff081-5\\uff09\\u548c\\u98a8\\u683c\\uff08I/II/III\\uff09\\u3002\\u4f8b\\u5982\\uff1a\\u300c2 II\\u300d'\n"
    "    : 'Please choose colour (1-5) and style (I/II/III). Example: \"2 II\"';\n"
    "  await saveAndSend.call(this, text, reply);\n"
    "  return [{ json:{ ok:false } }];\n"
    "}\n"
)

handle_colour = {
    "parameters": {"jsCode": handle_colour_code},
    "id": "node-handlecolour",
    "name": "Handle Colour Choice",
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [1700, 220]
}

# 5. Handle Rating
handle_rating_code = (
    "const phone = $('Extract Message').item.json.phone;\n"
    "const text  = $('Extract Message').item.json.text || '';\n"
    "const lang  = $('Get Session').item.json?.chosen_language || 'English';\n"
    "\n"
    "const match  = text.trim().match(/(?<!\\d)([1-5])(?!\\d)/);\n"
    "const rating = match ? match[1] : null;\n"
    "\n"
    "if (rating) {\n"
    "  await this.helpers.httpRequest({ method:'POST', url:`http://127.0.0.1:5051/session/${phone}/step`,\n"
    "    headers:{'Content-Type':'application/json'}, body:JSON.stringify({current_step:'feedback_comment'}), returnFullResponse:false });\n"
    "\n"
    "  const stars = '\\u2b50'.repeat(parseInt(rating));\n"
    "  let reply = lang==='Bahasa Malaysia'\n"
    "    ? `${stars} Terima kasih atas ${rating} bintang!\\n\\nBoleh tinggalkan komen ringkas? \\ud83d\\ude0a`\n"
    "    : lang==='\\u4e2d\\u6587'\n"
    "    ? `${stars} \\u611f\\u8b1d\\u60a8\\u7d66 ${rating} \\u661f\\uff01\\n\\n\\u53ef\\u4ee5\\u7559\\u4e0b\\u7c21\\u77ed\\u8a55\\u8a9e\\u55ce\\uff1f\\ud83d\\ude0a`\n"
    "    : `${stars} Thank you for the ${rating}-star rating!\\n\\nCould you leave a short comment? \\ud83d\\ude0a`;\n"
    "\n"
    "  await this.helpers.httpRequest({ method:'POST', url:'http://127.0.0.1:5051/conversations',\n"
    "    headers:{'Content-Type':'application/json'}, body:JSON.stringify({phone_number:phone,role:'user',content:text}), returnFullResponse:false });\n"
    "  await this.helpers.httpRequest({ method:'POST', url:'http://127.0.0.1:5051/conversations',\n"
    "    headers:{'Content-Type':'application/json'}, body:JSON.stringify({phone_number:phone,role:'assistant',content:reply}), returnFullResponse:false });\n"
    "  await this.helpers.httpRequest({ method:'POST', url:'http://127.0.0.1:3001/send',\n"
    "    headers:{'Content-Type':'application/json'}, body:JSON.stringify({phone,text:reply}), returnFullResponse:false });\n"
    "  return [{ json:{ ok:true, rating:parseInt(rating) } }];\n"
    "\n"
    "} else {\n"
    "  let reply = lang==='Bahasa Malaysia' ? 'Sila berikan penilaian antara 1 hingga 5 \\u2b50'\n"
    "    : lang==='\\u4e2d\\u6587' ? '\\u8acb\\u7d66 1 \\u5230 5 \\u984f\\u661f\\u7684\\u8a55\\u5206 \\u2b50'\n"
    "    : 'Please rate us from 1 to 5 \\u2b50';\n"
    "  await this.helpers.httpRequest({ method:'POST', url:'http://127.0.0.1:5051/conversations',\n"
    "    headers:{'Content-Type':'application/json'}, body:JSON.stringify({phone_number:phone,role:'user',content:text}), returnFullResponse:false });\n"
    "  await this.helpers.httpRequest({ method:'POST', url:'http://127.0.0.1:5051/conversations',\n"
    "    headers:{'Content-Type':'application/json'}, body:JSON.stringify({phone_number:phone,role:'assistant',content:reply}), returnFullResponse:false });\n"
    "  await this.helpers.httpRequest({ method:'POST', url:'http://127.0.0.1:3001/send',\n"
    "    headers:{'Content-Type':'application/json'}, body:JSON.stringify({phone,text:reply}), returnFullResponse:false });\n"
    "  return [{ json:{ ok:false } }];\n"
    "}\n"
)

handle_rating = {
    "parameters": {"jsCode": handle_rating_code},
    "id": "node-handlerating",
    "name": "Handle Rating",
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [1700, 680]
}

# 6. Add new nodes
wf['nodes'].extend([step_router, handle_layout, handle_colour, handle_rating])

# 7. Update connections
conns = wf['connections']
conns['Get History'] = {"main": [[{"node": "Step Router", "type": "main", "index": 0}]]}
conns['Step Router'] = {"main": [
    [{"node": "Handle Layout Choice", "type": "main", "index": 0}],
    [{"node": "Handle Colour Choice", "type": "main", "index": 0}],
    [{"node": "Handle Rating",        "type": "main", "index": 0}],
    [{"node": "Build Messages",       "type": "main", "index": 0}],
]}

with open(wf_path, 'w', encoding='utf-8') as f:
    json.dump(wf, f, indent=2, ensure_ascii=False)

print('Phase 1 patch complete.')
print('New nodes: Step Router, Handle Layout Choice, Handle Colour Choice, Handle Rating')
print('Get History -> Step Router -> [Layout|Colour|Rating|Build Messages(fallback)]')
