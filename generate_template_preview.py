import argparse, re
from playwright.sync_api import sync_playwright

EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
TEMPLATE_PATH = r"${PROJECT_ROOT}\resume-ai\templates\resume_template.html"

COLOUR_MAP = {
    "1": {"accent": "#1B3A6B", "sidebar_bg": "#1B3A6B", "sidebar_text": "#ffffff"},
    "2": {"accent": "#2D2D2D", "sidebar_bg": "#2D2D2D", "sidebar_text": "#ffffff"},
    "3": {"accent": "#2A9D8F", "sidebar_bg": "#2A9D8F", "sidebar_text": "#ffffff"},
    "4": {"accent": "#C1121F", "sidebar_bg": "#C1121F", "sidebar_text": "#ffffff"},
    "5": {"accent": "#8B5E3C", "sidebar_bg": "#FDF0E0", "sidebar_text": "#5C3D1E"},
}
STYLE_MAP = {"I": "minimal", "II": "modern", "III": "bold"}

def generate_preview(layout: str, colour: str, style: str, output_path: str):
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    c = COLOUR_MAP[colour]
    html = html.replace("{{ACCENT}}", c["accent"])
    html = html.replace("{{SIDEBAR_BG}}", c["sidebar_bg"])
    html = html.replace("{{SIDEBAR_TEXT}}", c["sidebar_text"])
    html = html.replace("{{LAYOUT}}", layout)
    html = html.replace("{{STYLE_CLASS}}", STYLE_MAP[style])

    if layout == "A":
        html = html.replace("{{LAYOUT_A_START}}", "").replace("{{LAYOUT_A_END}}", "")
        html = re.sub(r'\{\{LAYOUT_B_START\}\}.*?\{\{LAYOUT_B_END\}\}', '', html, flags=re.DOTALL)
    else:
        html = html.replace("{{LAYOUT_B_START}}", "").replace("{{LAYOUT_B_END}}", "")
        html = re.sub(r'\{\{LAYOUT_A_START\}\}.*?\{\{LAYOUT_A_END\}\}', '', html, flags=re.DOTALL)

    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=EDGE_PATH, headless=True)
        page = browser.new_page(viewport={"width": 794, "height": 1123})
        page.set_content(html, wait_until="networkidle")
        page.screenshot(path=output_path, full_page=False)
        browser.close()
    print(f"[OK] Preview: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--layout", required=True, choices=["A", "B"])
    parser.add_argument("--colour", required=True, choices=["1","2","3","4","5"])
    parser.add_argument("--style",  required=True, choices=["I","II","III"])
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    generate_preview(args.layout, args.colour, args.style, args.output)
