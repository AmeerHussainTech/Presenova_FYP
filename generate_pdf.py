"""
Generate high-quality PDF: PRESENOVA_ARCHITECTURE_VIVA_GUIDE.pdf
Using fpdf2 modern API + Unicode sanitization + clean tables and cards.
"""

import os
import re
from fpdf import FPDF
from fpdf.enums import XPos, YPos

def clean_text(text: str) -> str:
    """Normalize unicode characters to ensure 100% compatibility with standard PDF fonts."""
    if not text:
        return ""
    replacements = {
        "\u2014": " - ", # em-dash
        "\u2013": "-",   # en-dash
        "\u2018": "'",   # left single quote
        "\u2019": "'",   # right single quote
        "\u201c": '"',   # left double quote
        "\u201d": '"',   # right double quote
        "\u2022": "*",   # bullet
        "\u2026": "...", # ellipsis
        "\u00a0": " ",   # non-breaking space
        "–": "-",
        "—": " - ",
        "’": "'",
        "‘": "'",
        "“": '"',
        "”": '"',
        "•": "*",
        "…": "...",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    # Ensure latin-1 safe
    return text.encode("latin-1", "replace").decode("latin-1")

class VivaGuidePDF(FPDF):
    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.set_auto_page_break(auto=True, margin=18)
        self.main_font = "Helvetica"

    def header(self):
        if self.page_no() == 1:
            return
        self.set_font(self.main_font, "I", 8)
        self.set_text_color(100, 116, 139) # Slate 500
        self.cell(100, 6, "Presenova FYP: Architecture, Decisions & Viva Defense Manual", align="L")
        self.cell(80, 6, "Confidential / FYP Defense", align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_draw_color(226, 232, 240)
        self.set_line_width(0.3)
        self.line(15, 14, 195, 14)
        self.ln(3)

    def footer(self):
        self.set_y(-14)
        self.set_draw_color(226, 232, 240)
        self.set_line_width(0.3)
        self.line(15, self.get_y() - 1, 195, self.get_y() - 1)
        self.set_font(self.main_font, "", 8)
        self.set_text_color(148, 163, 184)
        self.cell(0, 8, f"Presenova Defense Guide | Page {self.page_no()}", align="C")

    def render_title_banner(self, title, subtitle, edition):
        self.set_fill_color(15, 23, 42) # Slate 900
        self.rect(15, 15, 180, 40, "F")
        
        self.set_xy(20, 20)
        self.set_font(self.main_font, "B", 16)
        self.set_text_color(255, 255, 255)
        self.cell(170, 8, clean_text(title), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        self.set_x(20)
        self.set_font(self.main_font, "B", 10.5)
        self.set_text_color(56, 189, 248) # Sky blue
        self.cell(170, 7, clean_text(subtitle), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        self.set_x(20)
        self.set_font(self.main_font, "I", 8.5)
        self.set_text_color(203, 213, 225) # Slate 300
        self.cell(170, 6, clean_text(edition), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        self.set_y(60)

    def section_h1(self, text):
        self.ln(3)
        self.set_font(self.main_font, "B", 11.5)
        self.set_text_color(30, 58, 138) # Dark Blue
        self.set_fill_color(238, 242, 255) # Indigo tint
        self.cell(180, 7.5, f"  {clean_text(text)}", fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_draw_color(99, 102, 241) # Indigo line
        self.set_line_width(0.6)
        self.line(15, self.get_y(), 195, self.get_y())
        self.ln(2.5)

    def qa_card(self, question, answer):
        self.set_font(self.main_font, "B", 9.5)
        self.set_text_color(29, 78, 216) # Blue 700
        q_label = clean_text(question)
        if not q_label.startswith("Q"):
            q_label = f"Q: {q_label}"
        self.multi_cell(180, 5, q_label)
        self.ln(1)
        
        self.set_font(self.main_font, "", 8.5)
        self.set_text_color(51, 65, 85) # Slate 700
        self.multi_cell(180, 4.5, clean_text(answer))
        self.ln(3)

    def render_table(self, headers, rows, col_widths):
        self.set_font(self.main_font, "B", 8)
        clean_headers = [clean_text(h) for h in headers]
        clean_rows = [[clean_text(cell) for cell in r] for r in rows]
        
        with self.table(col_widths=col_widths, line_height=4.5) as table:
            header_row = table.row()
            for h in clean_headers:
                header_row.cell(h)
            
            self.set_font(self.main_font, "", 7.8)
            for r in clean_rows:
                data_row = table.row()
                for d in r:
                    data_row.cell(d)
        self.ln(3)


def main():
    pdf = VivaGuidePDF()
    pdf.set_margins(15, 15, 15)
    pdf.add_page()
    
    # Hero Title
    pdf.render_title_banner(
        title="Presenova: Architecture & Viva Defense Guide",
        subtitle="Kya, Kaise, Kyun & Tech Alternatives (FYP Reference Manual)",
        edition="Release 1.1.0 - Final Year Project (FYP) Comprehensive Viva Edition"
    )
    
    # 1. Executive Summary
    pdf.section_h1("1. Project Overview & Core Mission")
    pdf.qa_card(
        "Presenova kya hai aur kis problem ko solve karta hai?",
        "Presenova ek multi-modal AI presentation rehearsal, telemetry aur real-time coaching platform hai. "
        "Yeh slide decks, speech acoustics, live camera posture, eye contact aur viva cross-examination ko quantitatively evaluate karta hai.\n"
        "Problem Solved: Human feedback hamesha subjective, inconsistent aur biased hota hai. Students ko defense se pehle pata nahi hota ke unka pacing kaisa hai, gaze kahan hai, filler words kitne hain, aur slides standard rules (jaise 6x6 rule) follow karti hain ya nahi. Presenova ise mathematical aur visual telemetry me convert karta hai."
    )
    
    # 2. Frontend
    pdf.section_h1("2. Frontend Web: React 18 + Vite")
    pdf.qa_card(
        "Frontend me kya aur kaise ho raha hai?",
        "Single Page Application (SPA) jo user authentication, file uploads, real-time live webcam/mic stream, teleprompter, interactive radar charts (Recharts) aur slide diffs render karti hai. "
        "React hooks (useLiveSession.ts) browser ke MediaDevices API se camera frames (3 FPS) aur audio chunks (3-sec interval) capture karke WebSocket ke zariye backend ko push karte hain."
    )
    pdf.render_table(
        ["Framework", "Decision", "Key Technical Evaluation & Rejection Reason"],
        [
            ["React 18 + Vite", "SELECTED", "Pure client-side SPA, instant HMR (esbuild), seamless webcam/audio stream integration, zero hydration mismatch."],
            ["Next.js (App Router)", "REJECTED", "SSR causes hydration mismatch with window/MediaStream/WebSockets. No SEO benefit for private authenticated portals."],
            ["Vue.js / Angular", "REJECTED", "Smaller chart ecosystem for complex radar/diff visualization; unnecessary framework migration overhead."],
            ["Vanilla JS / HTML", "REJECTED", "478 face mesh stats, audio level meters, dynamic hints, and scorecards cause severe DOM spaghetti and race conditions."]
        ],
        (38, 28, 114)
    )
    
    # 3. Backend Hub
    pdf.section_h1("3. Backend API Hub: Python Flask + Blueprints")
    pdf.qa_card(
        "Backend me kya aur kaise ho raha hai?",
        "Central REST API aur WebSocket server jo authentication, upload verification, AI pipelines aur document processing ko coordinate karta hai. "
        "Flask Blueprints ke zariye modular architecture hai with strict rate limiting, JWT token security, and dual database routers."
    )
    pdf.render_table(
        ["Backend Stack", "Decision", "Key Technical Evaluation & Rejection Reason"],
        [
            ["Flask + Blueprints", "SELECTED", "Zero-bloat micro-framework, native Python AI model access, rock-solid Gevent/Threading WebSocket concurrency."],
            ["FastAPI (ASGI)", "REJECTED", "Async event loop blocks on CPU-heavy C-extensions (OpenCV, MediaPipe, Scikit-Learn) unless complex executor pools are managed."],
            ["Django", "REJECTED", "Heavy monolithic bloat. Built-in ORM, admin panel, and template engines are unneeded for serverless NoSQL/Firestore."],
            ["Node.js (Express)", "REJECTED", "Requires slow IPC (child_process) bridges to execute Python AI/CV models, doubling RAM usage and response latency."]
        ],
        (38, 28, 114)
    )
    
    # 4. Real-Time Streaming
    pdf.section_h1("4. Real-Time Streaming: Flask-SocketIO & WebSockets")
    pdf.qa_card(
        "Real-time live coaching me kya aur kaise ho raha hai?",
        "3 FPS camera frames (base64 JPEG) aur 3-second audio chunks full-duplex WebSocket connection (/ws/live-session) par stream hote hain. "
        "Server gaze deviation, posture, aur filler words detect karke real-time hints ('Look at camera', 'Pacing too fast') wapis push karta hai."
    )
    pdf.render_table(
        ["Protocol", "Decision", "Key Technical Evaluation & Rejection Reason"],
        [
            ["WebSockets (Socket.IO)", "SELECTED", "Full-duplex bi-directional, < 50ms latency, zero repeated HTTP header overhead, native Python frame decoding."],
            ["HTTP Polling", "REJECTED", "Huge HTTP cookie/header overhead at 3 FPS; causes high network congestion and connection exhaustion."],
            ["WebRTC", "REJECTED", "Designed for P2P streaming. Server-side Python frame analysis requires complex STUN/TURN and C++ media bridges (Janus)."],
            ["Server-Sent Events", "REJECTED", "Unidirectional (server-to-client only). Client cannot stream video frames or audio chunks upstream."]
        ],
        (38, 28, 114)
    )
    
    # 5. Computer Vision
    pdf.section_h1("5. Computer Vision: MediaPipe Face Mesh (478 Landmarks)")
    pdf.qa_card(
        "Vision pipeline me eye contact aur posture kaise track hota hai?",
        "MediaPipe Face Mesh 478 3D landmarks extract karta hai. Landmarks 468-477 iris (pupil) ke hain. "
        "Iris center point aur eye corners (canthi) ke darmiyan Euclidean distance measure karke gaze direction (Center, Left, Right, Down) calculate hoti hai. "
        "Head pose estimation pitch, yaw aur roll se tilt aur posture composure track karti hai."
    )
    pdf.render_table(
        ["Vision Library", "Decision", "Key Technical Evaluation & Rejection Reason"],
        [
            ["MediaPipe Face Mesh", "SELECTED", "478 3D points including 10 iris refinement landmarks (468-477); runs blazingly fast at 30+ FPS on commodity laptop CPU."],
            ["OpenCV Haar Cascades", "REJECTED (Fallback)", "Only returns 2D face bounding box rectangle. Completely incapable of detecting iris pupil or gaze direction."],
            ["Dlib (68 Landmarks)", "REJECTED", "No iris pupil points; requires C++ CMake compiler toolchain; poor CPU performance without CUDA GPU."],
            ["YOLOv8-Face", "REJECTED", "Object detector rather than facial mesh; requires heavy PyTorch runtime and dedicated VRAM; container bloat."]
        ],
        (38, 28, 114)
    )
    
    # 6. Speech Analysis
    pdf.section_h1("6. Speech-to-Text (STT) & Audio: Groq Whisper LPU")
    pdf.qa_card(
        "Speech analysis me kya aur kaise ho raha hai?",
        "Audio chunks Groq Whisper API (whisper-large-v3) par pass hote hain jo specialized LPU hardware par chalti hai. "
        "Sub-400ms me transcript wapis aati hai jisse speech pace (WPM), filler words count (um, uh, actually), clarity aur articulation calculate hoti hai."
    )
    pdf.render_table(
        ["STT Provider", "Decision", "Key Technical Evaluation & Rejection Reason"],
        [
            ["Groq Whisper Large-v3", "SELECTED", "Sub-400ms inference on custom LPU hardware; SOTA transcription accuracy on diverse accents with zero local GPU."],
            ["Local Whisper (PyTorch)", "REJECTED", "Takes 8-12 seconds per 3-second chunk on CPU, making real-time teleprompter completely impossible."],
            ["Google Cloud Speech", "REJECTED", "High per-minute API cost; higher error rate on South Asian/Pakistani technical academic English accents."],
            ["Browser Web Speech API", "REJECTED", "Fails on Firefox and Safari; cannot provide raw audio bytes or timestamps for acoustic analysis."]
        ],
        (38, 28, 114)
    )
    
    # 7. Scoring Engine
    pdf.section_h1("7. Scoring Engine: Scikit-Learn Random Forest Regressor")
    pdf.qa_card(
        "7Cs scoring kaise hoti hai aur LLM se direct score kyun nahi karwaya?",
        "nlp_module 19 handcrafted linguistic features extract karta hai (Flesch-Kincaid readability, lexical diversity/TTR, passive ratio, bullet density). "
        "RandomForestRegressor ensemble in features ko 7Cs communication scores (0-100) me map karta hai.\n"
        "LLM Direct Prompting Kyun Reject Hua? 1) Inconsistency: Har dafa alag score deta hai (hallucination). 2) Speed: LLM call 3-5s leti hai jabke Random Forest < 3ms me evaluate karta hai. 3) Cost & Offline: Random Forest 100% offline chalta hai. 4) Academic Value: Genuine ML engineering."
    )
    
    # 8. RAG & Viva Question Generator
    pdf.section_h1("8. Viva Question Generator: SentenceTransformers + FAISS")
    pdf.qa_card(
        "Viva question generator kaise kaam karta hai aur FAISS kyun choose kiya?",
        "Presentation text 200-word passages me chunk hota hai. all-MiniLM-L6-v2 se 384-dimensional dense vectors bante hain. "
        "FAISS (IndexFlatIP) cosine similarity se critical technical claims retrieve karta hai aur methodology, claims, architecture aur edge-case questions banata hai.\n"
        "Pinecone/Cloud DBs Kyun Reject Hue? FAISS CPU RAM ke andar chalta hai with zero network latency (< 2ms) aur zero cloud subscription cost."
    )
    
    # 9. Slide Rewriter
    pdf.section_h1("9. Slide Deck Rewriter: spaCy Dependency Parsing")
    pdf.qa_card(
        "Slide rewriter me kya ho raha hai aur spaCy kyun use hua?",
        "spaCy (en_core_web_sm) dependency tree parser grammatical tags nikalta hai: nsubjpass (passive subject), auxpass (auxiliary verb), aur agent (by-clause). "
        "Inhe systematically active voice me convert kiya jata hai baghair content change kiye, aur 6x6 rule enforce hota hai.\n"
        "Regex grammar context nahi samajh sakta aur LLMs technical terms distort kar dete hain. spaCy provides exact syntactic precision."
    )
    
    # 10. Document Parsing & Security
    pdf.section_h1("10. Document Parsing & Binary Security Verification")
    pdf.qa_card(
        "Document extraction kaise hoti hai aur security kaise ensure ki gayi hai?",
        "Multi-format extraction: python-pptx (XML shapes & tables), pypdf (text streams), python-docx.\n"
        "Security Defense: Magic-Byte Binary Signature Verification. Extension check (.endswith('.pptx')) dangerous hota hai kyunki attacker executable script ka naam badal sakta hai. "
        "Presenova raw binary bytes check karta hai (PK\\x03\\x04 for PPTX, %PDF- for PDF) taake Remote Code Execution (RCE) block ho."
    )
    
    # 11. Database Architecture
    pdf.section_h1("11. Database Strategy: Dual-Engine Persistence")
    pdf.qa_card(
        "Dual-engine database kya hai aur iska FYP me kya faida hai?",
        "models.py me custom DBRouter hai. Primary: Google Cloud Firestore (NoSQL cloud persistence). Fallback: Thread-Locked In-Memory Store (_MEMORY_STORE).\n"
        "Viva Winning Feature: Aksar presentation ke waqt Wi-Fi drop ho jata hai ya system clock skew hone par Google Cloud credentials fail ho jate hain (invalid_grant). "
        "Normal apps 500 error de kar crash ho jati hain; Presenova < 0.5s me auto-switch ho kar in-memory store par demo seamlessly continue rakhta hai."
    )
    
    # 12. Top 10 Killer Viva Questions
    pdf.section_h1("12. Top 10 Killer FYP Defense Questions & Model Answers")
    
    top_questions = [
        ("Q1: Aapke system me AI kahan hai aur Rules kahan hain?",
         "System hybrid hai. AI perception aur evaluation ke liye hai (MediaPipe 478 landmarks, Groq Whisper STT, Random Forest 7Cs regressor, FAISS dense embeddings). Rules guardrails aur structure ke liye hain (6x6 rule enforcement, magic-byte file signature validation, spaCy syntactic voice inversion, WPM mathematical formulas)."),
        
        ("Q2: MediaPipe me iris landmarks (468-477) se gaze kaise calculate hoti hai?",
         "Eye corner landmarks (inner/outer canthus) ke 3D coordinates se center point calculate hota hai. Phir iris center landmark (468 left, 473 right) ka horizontal/vertical Euclidean displacement measure hota hai. Threshold se zyada deviation gaze-off alert trigger karti hai."),
        
        ("Q3: Live session me audio chunk 3-second ka kyun rakha?",
         "1-second chunk me 1-2 words aate hain jisse Whisper acoustic context samajh nahi pata aur filler phrases kat jati hain. 10-second me teleprompter feedback 10s late ho jata hai. 3 seconds is the mathematical sweet spot (6-8 words, full context, sub-400ms latency)."),
        
        ("Q4: Agar Google Firestore disconnect ho jaye to data ka kya banta hai?",
         "DBRouter auto-failover mechanism use karta hai. Firestore connection drop hote hi system thread-locked _MEMORY_STORE me write karna shuru kar deta hai. User ko koi error 500 nazar nahi aata aur demo seamlessly chalta rehta hai."),
        
        ("Q5: Groq Whisper API use karne ka kya fayda jab OpenAI ki API bhi maujood hai?",
         "Dono whisper-large-v3 architecture use karti hain, lekin OpenAI standard GPUs par chalta hai (latency 2-4 seconds). Groq custom LPUs par high-bandwidth tensor streaming karta hai jo wahi transcription 350-400ms me return karta hai."),
        
        ("Q6: 7Cs scoring ke liye Random Forest ko Deep Neural Network par tarjeeh kyun di?",
         "Feature vector tabular hai (19 handcrafted features). Tabular data par Multi-Layer Perceptrons overfit hote hain aur GPU maangte hain. Random Forest ensemble 100 decision trees ka vote leta hai, non-linear correlations ko gracefully handle karta hai, aur CPU par 3ms me execute hota hai."),
        
        ("Q7: Slide rewriter me passive-to-active voice convert karne ke liye LLM prompt kyun nahi likha?",
         "LLMs unpredictable hote hain - wo slide ka context badal dete hain, technical terms hallucinate kar lete hain, aur slide formatting ruin kar dete hain. spaCy dependency parsing exact grammatical subject (nsubjpass), verb aur agent ko mathematically swap karti hai baghair meaning badle."),
        
        ("Q8: FAISS vector database ko chalane ke liye GPU chahiye?",
         "Nahi, FAISS CPU-optimized index (IndexFlatIP) use kiya gaya hai. Normal presentations me 100 se kam chunks hote hain. Is scale par FAISS CPU ke AVX2 instructions par memory-mapped vectors ko sub-millisecond me search kar leta hai."),
        
        ("Q9: Security ke aitbar se file upload me sab se bara threat kya hota hai aur kaise roka?",
         "Sab se bara threat Unrestricted File Upload / Remote Code Execution hota hai. Humne Magic-Byte Binary Signature Verification lagai hai jo extension par trust kiye baghair raw binary bytes check karti hai (PK\\x03\\x04 for PPTX, %PDF- for PDF)."),
        
        ("Q10: Live cross-examination interruption feature kis base par trigger hota hai?",
         "Do triggers hain: 1) High Filler Density (agar speaker 3-second chunks me excessive filler words use kare ya nervous ho). 2) Periodic Presentation Checkpoint (regular intervals par simulated senior professor AI user se presentation content ke mutabiq direct defense question puchti hai).")
    ]
    
    for q, a in top_questions:
        pdf.qa_card(q, a)
        
    output_pdf_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "PRESENOVA_ARCHITECTURE_VIVA_GUIDE.pdf")
    pdf.output(output_pdf_path)
    print(f"SUCCESS: PDF generated successfully at: {output_pdf_path}")
    print(f"File Size: {os.path.getsize(output_pdf_path)} bytes")

if __name__ == "__main__":
    main()
