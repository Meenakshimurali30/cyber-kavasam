"""
generate_architecture_diagram.py: Generates docs/architecture.png
using Matplotlib with Latin text only (ensuring clean cross-platform rendering).
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def generate_diagram():
    fig, ax = plt.subplots(figsize=(14, 8), dpi=300)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8)
    ax.axis('off')

    # Background color
    fig.patch.set_facecolor('#0f172a')
    ax.set_facecolor('#0f172a')

    # Color definitions
    card_bg = '#1e293b'
    border_col = '#38bdf8'
    text_main = '#f8fafc'
    text_sub = '#94a3b8'
    accent_green = '#34d399'
    accent_amber = '#fbbf24'
    accent_blue = '#60a5fa'
    accent_red = '#f87171'

    # Title
    ax.text(7, 7.6, "CYBER KAVASAM - SYSTEM ARCHITECTURE", 
            ha='center', va='center', fontsize=18, fontweight='bold', color='#38bdf8')
    ax.text(7, 7.25, "Citizen Scam Detection & Reporting Assistant (Hybrid Heuristic + ML Engine)", 
            ha='center', va='center', fontsize=11, color=text_sub)

    def draw_box(x, y, w, h, title, subtitle="", border=border_col, bg=card_bg):
        rect = patches.FancyBboxPatch((x, y), w, h,
                                      boxstyle="round,pad=0.1,rounding_size=0.15",
                                      facecolor=bg, edgecolor=border, linewidth=1.5)
        ax.add_patch(rect)
        if subtitle:
            ax.text(x + w/2, y + h*0.62, title, ha='center', va='center',
                    fontsize=10, fontweight='bold', color=text_main)
            ax.text(x + w/2, y + h*0.32, subtitle, ha='center', va='center',
                    fontsize=8, color=text_sub)
        else:
            ax.text(x + w/2, y + h/2, title, ha='center', va='center',
                    fontsize=9.5, fontweight='bold', color=text_main)

    def draw_arrow(x1, y1, x2, y2, color='#38bdf8', label=""):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", color=color, lw=1.5, mutation_scale=12))
        if label:
            mx, my = (x1 + x2)/2, (y1 + y2)/2
            ax.text(mx, my + 0.15, label, ha='center', va='bottom', fontsize=8, color='#cbd5e1')

    # 1. User & Client Layer (Left)
    draw_box(0.5, 5.2, 2.8, 1.4, "USER INPUT TIER", "SMS / WhatsApp Text\n(Tamil, Tanglish, English)", accent_blue)
    draw_box(0.5, 3.2, 2.8, 1.5, "FRONTEND UI (No Framework)", "Vanilla HTML5 / CSS3 / ES6\nTheme Switcher & Bilingual I18n\nAria-live & Zero InnerHTML", accent_green)
    draw_box(0.5, 1.0, 2.8, 1.6, "REPORTING ACTIONS", "Direct 1930 Helpline Dial\nChakshu (sancharsaathi.gov.in)\n1-Click Cybercrime Complaint Draft", accent_red)

    # 2. Gateway Layer
    draw_box(4.0, 3.2, 2.6, 3.4, "GATEWAY & SECURITY", "Waitress WSGI Server\nFlask REST API (JSON)\nCSP & NoSniff & Frame-Deny\nIn-Memory Rate Limiter\nPrivacy Logging (No Text)", border_col)

    # 3. Detection Engine (Center)
    draw_box(7.3, 5.1, 3.4, 1.5, "HEURISTIC RULE ENGINE", "26+ Weighted Regex Rules\nNoisy-OR Combining: 1 - Prod(1 - w)\nURL Inspector (Allowlist, IP, TLD)\nSafe Signal Deductor", accent_amber)
    draw_box(7.3, 3.1, 3.4, 1.5, "MACHINE LEARNING ENGINE", "Scikit-Learn Char n-gram TF-IDF\nanalyzer='char_wb', ngram=(2,5)\nLogistic Regression (C=2.5)\nSHA256 Hash Guard / Reload", accent_blue)
    draw_box(7.3, 1.0, 3.4, 1.6, "HYBRID ARBITER", "Final Score = 60% Rules + 40% ML\nSafe Signal Suppression\nStrict Scam Force Overrides\nVerdicts: Safe / Suspicious / Scam", accent_green)

    # 4. Output & Knowledge Base (Right)
    draw_box(11.3, 4.4, 2.3, 2.2, "BILINGUAL EXPLAINER", "Top 5 Matched Red Flags\nSpecific Scam Family Advice\n(Digital Arrest, TNEB, KYC)\nTamil & English Explanations", border_col)
    draw_box(11.3, 1.0, 2.3, 2.8, "PERSISTENCE & BENCHMARK", "models/kavasam.joblib\nmodels/metrics.json\nRedacted feedback.csv\n(Anti-PII & CSV Injection Guard)\nGold Test Benchmark (75 Items)", accent_amber)

    # Arrows
    draw_arrow(1.9, 5.2, 1.9, 4.7)
    draw_arrow(3.3, 4.0, 4.0, 4.0, label="POST /check")
    draw_arrow(6.6, 5.8, 7.3, 5.8, label="Rules")
    draw_arrow(6.6, 3.8, 7.3, 3.8, label="ML")
    draw_arrow(9.0, 5.1, 9.0, 4.6)
    draw_arrow(9.0, 3.1, 9.0, 2.6)
    draw_arrow(10.7, 1.8, 11.3, 1.8)
    draw_arrow(10.7, 5.5, 11.3, 5.5)
    draw_arrow(12.4, 4.4, 12.4, 3.8)
    draw_arrow(7.3, 1.8, 6.6, 3.3, label="JSON Result")
    draw_arrow(4.0, 3.3, 1.9, 2.6, label="Render UI")

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "architecture.png")
    plt.tight_layout()
    plt.savefig(out_path, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"Architecture diagram successfully saved to {out_path}")

if __name__ == "__main__":
    generate_diagram()
