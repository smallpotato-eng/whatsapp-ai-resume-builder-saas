from playwright.sync_api import sync_playwright

EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

HTML = """<!DOCTYPE html><html><head><meta charset="UTF-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Roboto:wght@400;700&display=swap');
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Inter',Arial,sans-serif;background:#f0f2f5;width:900px;padding:28px}

/* Header */
.header{text-align:center;margin-bottom:24px}
.header h1{font-size:1.5rem;font-weight:700;color:#1B3A6B}
.header p{font-size:0.85rem;color:#888;margin-top:4px}

/* Container */
.row{display:flex;gap:20px}
.panel{flex:1}
.panel-title{text-align:center;padding:10px 0;font-weight:700;font-size:0.95rem;border-radius:8px 8px 0 0;letter-spacing:0.5px}
.before-title{background:#e0e0e0;color:#666}
.after-title{background:#1B3A6B;color:#fff}

/* BEFORE */
.before-resume{background:#fff;border:1px solid #ddd;border-radius:0 0 8px 8px;padding:18px;font-family:monospace;font-size:0.72rem;color:#444;line-height:1.7;min-height:420px}
.before-resume .ugly-name{font-size:0.85rem;font-weight:bold;margin-bottom:8px}
.before-resume p{margin-bottom:6px}

/* AFTER */
.after-resume{background:#fff;border:2px solid #1B3A6B;border-radius:0 0 8px 8px;min-height:420px;overflow:hidden;box-shadow:0 4px 16px rgba(27,58,107,.15)}
.after-header{background:#1B3A6B;padding:16px 20px}
.after-name{color:#fff;font-size:1.1rem;font-weight:700;letter-spacing:0.3px}
.after-title-text{color:#a8c4e8;font-size:0.72rem;margin-top:3px}
.after-contact{display:flex;gap:16px;margin-top:8px}
.after-contact span{color:#c8d8f0;font-size:0.62rem}
.after-body{padding:14px 18px}
.after-section{margin-bottom:12px}
.after-sec-label{font-size:0.62rem;font-weight:700;color:#1B3A6B;text-transform:uppercase;letter-spacing:1px;border-bottom:1.5px solid #1B3A6B;padding-bottom:3px;margin-bottom:7px}
.job-row{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:2px}
.job-title{font-size:0.72rem;font-weight:700;color:#222}
.job-date{font-size:0.62rem;color:#888}
.job-company{font-size:0.65rem;color:#1B3A6B;margin-bottom:4px}
.job-bullets{padding-left:12px}
.job-bullets li{font-size:0.62rem;color:#444;margin-bottom:2px;line-height:1.5}
.skills-row{display:flex;flex-wrap:wrap;gap:5px}
.skill-tag{background:#e8f0fb;color:#1B3A6B;font-size:0.6rem;padding:3px 8px;border-radius:10px;font-weight:600}
.edu-row{display:flex;justify-content:space-between}
.edu-deg{font-size:0.68rem;font-weight:700;color:#222}
.edu-year{font-size:0.62rem;color:#888}
.edu-school{font-size:0.62rem;color:#555}

/* Arrow */
.arrow{display:flex;align-items:center;justify-content:center;width:44px;flex-shrink:0}
.arrow-inner{font-size:2rem;color:#1B3A6B;font-weight:700}

/* Badge */
.badge-row{display:flex;justify-content:center;gap:16px;margin-top:18px}
.badge{padding:7px 18px;border-radius:20px;font-size:0.75rem;font-weight:600}
.badge-before{background:#ffeaea;color:#c0392b}
.badge-after{background:#e8f4e8;color:#1a7a1a}

/* Watermark */
.watermark{text-align:center;margin-top:16px;color:#bbb;font-size:0.72rem}
.watermark span{color:#1B3A6B;font-weight:700}
</style></head><body>

<div class="header">
  <h1>✨ Resume Transformation</h1>
  <p>See the difference a professional resume makes</p>
</div>

<div class="row">

  <!-- BEFORE -->
  <div class="panel">
    <div class="panel-title before-title">❌ BEFORE</div>
    <div class="before-resume">
      <div class="ugly-name">AHMAD SYAHMI BIN RAZALI</div>
      <p>Phone: 012-3456789 | Email: syahmi123@gmail.com</p>
      <p>-----------------------------------------------</p>
      <p>OBJECTIVE: Looking for a job in marketing or related field. I am a hardworking person and fast learner. I can work in a team or alone.</p>
      <p>-----------------------------------------------</p>
      <p>EDUCATION</p>
      <p>Bachelor of Business Administration, UiTM Shah Alam, 2022</p>
      <p>-----------------------------------------------</p>
      <p>WORK EXPERIENCE</p>
      <p>Marketing Executive at ABC Sdn Bhd (2022-2024)</p>
      <p>- Handle social media</p>
      <p>- Do reports</p>
      <p>- Help with events</p>
      <p>- Other tasks given by supervisor</p>
      <p>-----------------------------------------------</p>
      <p>SKILLS</p>
      <p>Microsoft Office, Social Media, Communication, Teamwork</p>
      <p>-----------------------------------------------</p>
      <p>HOBBIES: Reading, Travelling, Cooking</p>
    </div>
  </div>

  <!-- Arrow -->
  <div class="arrow"><div class="arrow-inner">→</div></div>

  <!-- AFTER -->
  <div class="panel">
    <div class="panel-title after-title">✅ AFTER</div>
    <div class="after-resume">
      <div class="after-header">
        <div class="after-name">Ahmad Syahmi bin Razali</div>
        <div class="after-title-text">Digital Marketing Executive</div>
        <div class="after-contact">
          <span>📞 012-345 6789</span>
          <span>✉ syahmi@email.com</span>
          <span>📍 Shah Alam, Selangor</span>
        </div>
      </div>
      <div class="after-body">
        <div class="after-section">
          <div class="after-sec-label">Professional Summary</div>
          <div style="font-size:0.63rem;color:#444;line-height:1.6">Results-driven Digital Marketing Executive with 2+ years of experience driving brand growth through data-led social media strategies. Proven track record of increasing engagement by 40%.</div>
        </div>
        <div class="after-section">
          <div class="after-sec-label">Work Experience</div>
          <div class="job-row"><span class="job-title">Digital Marketing Executive</span><span class="job-date">Jan 2022 – Dec 2024</span></div>
          <div class="job-company">ABC Sdn Bhd · Shah Alam</div>
          <ul class="job-bullets">
            <li>Grew Instagram following by <strong>40%</strong> in 6 months via targeted content strategy</li>
            <li>Produced weekly performance reports, reducing reporting time by 30%</li>
            <li>Coordinated 8 brand events with 200+ attendees each</li>
          </ul>
        </div>
        <div class="after-section">
          <div class="after-sec-label">Education</div>
          <div class="edu-row"><span class="edu-deg">Bachelor of Business Administration (Hons)</span><span class="edu-year">2022</span></div>
          <div class="edu-school">Universiti Teknologi MARA (UiTM) Shah Alam</div>
        </div>
        <div class="after-section">
          <div class="after-sec-label">Skills</div>
          <div class="skills-row">
            <span class="skill-tag">Meta Ads Manager</span>
            <span class="skill-tag">Google Analytics</span>
            <span class="skill-tag">Canva</span>
            <span class="skill-tag">Content Strategy</span>
            <span class="skill-tag">Data Reporting</span>
            <span class="skill-tag">Event Management</span>
          </div>
        </div>
      </div>
    </div>
  </div>

</div>

<div class="badge-row">
  <span class="badge badge-before">❌ Generic, no impact</span>
  <span class="badge badge-after">✅ ATS-ready, achievement-focused</span>
</div>

<div class="watermark">Powered by <span>Ava Resume Studio</span> · Professional Resume in 24 Hours · From RM7</div>

</body></html>"""

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=EDGE_PATH, headless=True)
        page = browser.new_page(viewport={"width": 900, "height": 700})
        page.set_content(HTML, wait_until="networkidle")
        path = r"${PROJECT_ROOT}\resume-ai\templates\before_after.png"
        page.screenshot(path=path, full_page=True)
        print(f"[OK] Saved: {path}")
        browser.close()

if __name__ == "__main__":
    main()
