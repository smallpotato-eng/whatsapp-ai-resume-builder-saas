"""Generate preview PNG images from HTML resume templates using Playwright."""
import sys, os
sys.stdout.reconfigure(encoding='utf-8')

from playwright.sync_api import sync_playwright

TEMPLATES_DIR = r'${PROJECT_ROOT}\resume-ai\templates'
OUTPUT_DIR    = r'${PROJECT_ROOT}\resume-ai\templates'

def generate():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={'width': 794, 'height': 1123})
        for i in range(1, 7):
            html_path = os.path.join(TEMPLATES_DIR, f'template_{i}.html')
            out_path  = os.path.join(OUTPUT_DIR,    f'preview_{i}.png')
            page.goto(f'file:///{html_path.replace(chr(92), "/")}')
            page.wait_for_timeout(500)
            page.screenshot(path=out_path, full_page=False, clip={'x':0,'y':0,'width':794,'height':1123})
            print(f'✅ preview_{i}.png saved')
        browser.close()

if __name__ == '__main__':
    generate()
    print('\nAll 6 previews generated.')
