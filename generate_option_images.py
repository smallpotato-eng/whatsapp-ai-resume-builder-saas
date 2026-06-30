from playwright.sync_api import sync_playwright

EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

LAYOUT_HTML = """<!DOCTYPE html><html><head><meta charset="UTF-8">
<style>
* {margin:0;padding:0;box-sizing:border-box}
body {font-family:'Arial',sans-serif;background:#f0f2f5;width:720px;padding:24px}
h2 {text-align:center;margin-bottom:20px;color:#222;font-size:1.15rem;font-weight:700}
.row {display:flex;gap:20px}
.card {flex:1;background:#fff;border-radius:12px;padding:16px;box-shadow:0 3px 12px rgba(0,0,0,.12)}
.label {font-size:1rem;font-weight:700;color:#1B3A6B;margin-bottom:4px}
.desc {font-size:0.75rem;color:#666;margin-bottom:14px}
/* Layout A preview */
.preview-a {border:1px solid #e0e0e0;border-radius:6px;overflow:hidden}
.a-header {background:#1B3A6B;padding:10px 12px}
.a-header .name {color:#fff;font-size:0.85rem;font-weight:700}
.a-header .title {color:#a8c4e8;font-size:0.65rem;margin-top:2px}
.a-body {padding:10px 12px}
.a-section {margin-bottom:8px}
.a-sec-title {font-size:0.6rem;font-weight:700;color:#1B3A6B;text-transform:uppercase;border-bottom:1.5px solid #1B3A6B;padding-bottom:2px;margin-bottom:4px}
.a-line {height:5px;background:#e8e8e8;border-radius:2px;margin:3px 0}
/* Layout B preview */
.preview-b {border:1px solid #e0e0e0;border-radius:6px;overflow:hidden;display:flex}
.b-side {width:38%;background:#1B3A6B;padding:10px 8px}
.b-side .name {color:#fff;font-size:0.75rem;font-weight:700}
.b-side .title {color:#a8c4e8;font-size:0.58rem;margin-top:2px;margin-bottom:8px}
.b-side .sl {height:4px;background:rgba(255,255,255,.25);border-radius:2px;margin:3px 0}
.b-main {flex:1;padding:10px 8px}
.b-section {margin-bottom:7px}
.b-sec-title {font-size:0.58rem;font-weight:700;color:#1B3A6B;text-transform:uppercase;border-bottom:1.5px solid #1B3A6B;padding-bottom:2px;margin-bottom:4px}
.b-line {height:4px;background:#e8e8e8;border-radius:2px;margin:3px 0}
.badge {display:inline-block;padding:3px 10px;border-radius:10px;font-size:0.68rem;margin-top:10px;font-weight:600}
.badge-a {background:#e8f4e8;color:#2d7a2d}
.badge-b {background:#e8f0fb;color:#1B3A6B}
footer {text-align:center;margin-top:18px;color:#999;font-size:0.78rem}
</style></head><body>
<h2>📐 Choose Your Resume Layout</h2>
<div class="row">
  <div class="card">
    <div class="label">A &nbsp;Single Column</div>
    <div class="desc">Traditional top-to-bottom layout</div>
    <div class="preview-a">
      <div class="a-header">
        <div class="name">Alex Johnson</div>
        <div class="title">Senior Marketing Manager · alex@email.com</div>
      </div>
      <div class="a-body">
        <div class="a-section">
          <div class="a-sec-title">Work Experience</div>
          <div class="a-line"></div><div class="a-line" style="width:85%"></div><div class="a-line" style="width:75%"></div>
        </div>
        <div class="a-section">
          <div class="a-sec-title">Education</div>
          <div class="a-line" style="width:70%"></div><div class="a-line" style="width:55%"></div>
        </div>
        <div class="a-section">
          <div class="a-sec-title">Skills</div>
          <div class="a-line" style="width:90%"></div>
        </div>
      </div>
    </div>
    <div><span class="badge badge-a">✅ Best for ATS &amp; large companies</span></div>
  </div>
  <div class="card">
    <div class="label">B &nbsp;Two-Column</div>
    <div class="desc">Sidebar for contact info, main area for experience</div>
    <div class="preview-b">
      <div class="b-side">
        <div class="name">Alex Johnson</div>
        <div class="title">Marketing Manager</div>
        <div style="font-size:0.55rem;color:#a8c4e8;margin-bottom:4px">Contact</div>
        <div class="sl"></div><div class="sl" style="width:80%"></div>
        <div style="font-size:0.55rem;color:#a8c4e8;margin:6px 0 2px">Skills</div>
        <div class="sl"></div><div class="sl" style="width:70%"></div><div class="sl" style="width:85%"></div>
      </div>
      <div class="b-main">
        <div class="b-section">
          <div class="b-sec-title">Work Experience</div>
          <div class="b-line"></div><div class="b-line" style="width:85%"></div><div class="b-line" style="width:70%"></div>
        </div>
        <div class="b-section">
          <div class="b-sec-title">Education</div>
          <div class="b-line" style="width:75%"></div><div class="b-line" style="width:60%"></div>
        </div>
      </div>
    </div>
    <div><span class="badge badge-b">✨ Great for design &amp; creative roles</span></div>
  </div>
</div>
<footer>Reply A or B</footer>
</body></html>"""

COLOUR_HTML = """<!DOCTYPE html><html><head><meta charset="UTF-8">
<style>
* {margin:0;padding:0;box-sizing:border-box}
body {font-family:Arial,sans-serif;background:#f4f4f4;width:680px;padding:28px}
h2 {text-align:center;margin-bottom:18px;color:#333;font-size:1.1rem}
.row {display:flex;gap:12px;justify-content:center}
.sw {width:118px;border-radius:10px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.12);background:#fff}
.sw .clr {height:68px}
.sw .info {padding:10px;text-align:center}
.sw .num {font-size:1.3rem;font-weight:700;color:#333}
.sw .name {font-size:0.68rem;color:#777;margin-top:2px}
footer {text-align:center;margin-top:16px;color:#aaa;font-size:0.75rem}
</style></head><body>
<h2>🎨 Choose Your Colour</h2>
<div class="row">
  <div class="sw"><div class="clr" style="background:#1B3A6B"></div><div class="info"><div class="num">1</div><div class="name">Navy Blue</div></div></div>
  <div class="sw"><div class="clr" style="background:#2D2D2D"></div><div class="info"><div class="num">2</div><div class="name">Charcoal</div></div></div>
  <div class="sw"><div class="clr" style="background:#2A9D8F"></div><div class="info"><div class="num">3</div><div class="name">Teal</div></div></div>
  <div class="sw"><div class="clr" style="background:#C1121F"></div><div class="info"><div class="num">4</div><div class="name">Crimson</div></div></div>
  <div class="sw"><div class="clr" style="background:#8B5E3C"></div><div class="info"><div class="num">5</div><div class="name">Warm Beige</div></div></div>
</div>
<footer>Reply 1, 2, 3, 4 or 5</footer>
</body></html>"""

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=EDGE_PATH, headless=True)
        page = browser.new_page(viewport={"width": 680, "height": 500})

        page.set_content(LAYOUT_HTML, wait_until="networkidle")
        page.screenshot(path=r"${PROJECT_ROOT}\resume-ai\templates\layout_preview.png", full_page=True)
        print("[OK] layout_preview.png")

        page.set_content(COLOUR_HTML, wait_until="networkidle")
        page.screenshot(path=r"${PROJECT_ROOT}\resume-ai\templates\colour_swatch.png", full_page=True)
        print("[OK] colour_swatch.png")

        browser.close()

if __name__ == "__main__":
    main()
