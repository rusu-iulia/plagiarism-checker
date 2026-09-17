import os
import uuid

from dotenv import load_dotenv
from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename

load_dotenv()

from services.extractor import extract_text_from_file
from services.phrases import extract_random_phrases
from services.report import build_pdf_report
from services.scraper import fetch_and_clean
from services.search import SearXNGSearchProvider
from services.similarity import best_snippet_match

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024 # 20 mb upload limit

UPLOAD_EXTENSIONS = {".docx", ".pdf", ".txt"}
NUM_PHRASES = int(os.environ.get("NUM_PHRASES",8))
RESULTS_PER_PHRASE = int(os.environ.get("RESULTS_PER_PHRASE", 5))
MATCH_THRESHOLD = float(os.environ.get("MATCH_THRESHOLD", 0.6)) # if a snippet has a similarity score above 60%, it will be considered a possible plagiarism match

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORTS_DIR = os.path.join(BASE_DIR, "generated_reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

# using a simple in-memory cache for faster access to the generated reports
REPORT_CACHE = {}
search_provider = SearXNGSearchProvider()

def run_plagiarism_check(text, filename):
    phrases = extract_random_phrases(text, num_phrases = NUM_PHRASES)
    matches = []
    errors = []

    # looping through each phrase and searching for it online
    for phrase in phrases:
        try:
            search_results = search_provider.search(phrase, num_results=RESULTS_PER_PHRASE)
        except Exception as e:
            errors.append(f"Search failed for phrase '{phrase[:40]}...': {e}")
            continue

        for result in search_results:
            url = result.get("url")
            if not url:
                continue
            page_text = fetch_and_clean(url)
            if not page_text:
                continue

            # running the similarity check between the phrase and the fetched page text
            # if the similarity ratio is above the threshold, consider it a potential plagiarism match
            ratio, snippet = best_snippet_match(phrase, page_text)
            if ratio >= MATCH_THRESHOLD:
                matches.append({
                                    "phrase": phrase,
                                    "similarity": round(ratio * 100, 1),
                                    "url": url,
                                    "title": result.get("title") or url,
                                    "snippet": snippet,
                                })

    matched_phrase_count = len({m["phrase"] for m in matches})
    overall_percent = round((matched_phrase_count / len(phrases)) * 100, 1) if phrases else 0.0

    if overall_percent >= 50:
        risk_level = "High"
    elif overall_percent >= 20:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    # sorting the matches by similarity score in descending order for better presentation in the report
    matches.sort(key=lambda m: m["similarity"], reverse = True)

    return {
        "filename": filename,
        "phrases_checked": phrases,
        "overall_percent": overall_percent,
        "risk_level": risk_level,
        "matches": matches,
        "errors": errors,
    }

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

# this route handles the file upload and plagiarism checking process
@app.route("/check", methods=["POST"])
def check():
    uploaded_file = request.files.get("document")
    if not uploaded_file or not uploaded_file.filename:
        return render_template("index.html", error="No file selected.")

    file_type = os.path.splitext(uploaded_file.filename)[1].lower()
    if file_type not in UPLOAD_EXTENSIONS:
        return render_template("index.html", error=f"Unsupported file type '{file_type}'. Upload a .docx, .pdf, or .txt file.")

    try:
        text = extract_text_from_file(uploaded_file)
    except Exception as e:
        return render_template("index.html", error=f"Failed to extract text from the uploaded file.")

    if not text.strip():
        return render_template("index.html", error="The uploaded file does not contain any readable text.")

    filename = secure_filename(uploaded_file.filename)
    results = run_plagiarism_check(text, filename)

    report_id = str(uuid.uuid4())
    REPORT_CACHE[report_id] = results

    return render_template("results.html", results = results, report_id = report_id)

# this route allows users to download the generated plagiarism report as a PDF
@app.route("/report/<report_id>.pdf")
def download_report(report_id):
    results = REPORT_CACHE.get(report_id)
    if not results:
        return render_template("index.html", error="Report not found or has expired.")

    output_path = os.path.join(REPORTS_DIR, f"{report_id}.pdf")
    if not os.path.exists(output_path):
        build_pdf_report(
                    output_path,
                    filename=results["filename"],
                    overall_percent=results["overall_percent"],
                    risk_level=results["risk_level"],
                    matches=results["matches"],
                )
        
        return send_file(output_path, as_attachment=True, download_name="plagiarism_report.pdf")
        
        
if __name__ == "__main__":
    app.run(port=5000, debug=True)
        