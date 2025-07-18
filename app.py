
from flask import Flask, request, jsonify, send_file
import json
import io
from flask_cors import CORS
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

app = Flask(__name__)
CORS(app)
# Load the SNP annotation database
with open("snp_annotations.json") as f:
    snp_db = json.load(f)

@app.route("/")
def home():
    return "🧬 GeneTrace SNP Annotation API is running."

@app.route("/annotate-snps", methods=["POST"])
def annotate_snps():
    user_snps = request.get_json()
    annotated = {}

    for snp_id, genotype in user_snps.items():
        if snp_id in snp_db:
            trait_info = snp_db[snp_id]
            risk = trait_info["impact"].get(genotype, "Unknown genotype")
            annotated[snp_id] = {
                "trait": trait_info["trait"],
                "genotype": genotype,
                "risk": risk
            }
        else:
            annotated[snp_id] = {
                "trait": "Unknown SNP",
                "genotype": genotype,
                "risk": "No data available"
            }

    return jsonify(annotated)

@app.route("/generate-pdf", methods=["POST"])
def generate_pdf():
    data = request.json

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    from datetime import datetime
    y = height - 60

    # Title
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, y, "🧬 GeneTrace Lite - Genetic Trait Report")
    y -= 20

    # Date
    c.setFont("Helvetica", 10)
    c.drawString(50, y, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    y -= 10

    # Divider
    c.line(50, y, width - 50, y)
    y -= 30

    # SNP Results
    for snp, info in data.items():
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, f"{info['trait']} ({snp})")

        y -= 18
        c.setFont("Helvetica", 11)
        c.drawString(70, y, f"Genotype: {info['genotype']}")
        y -= 15
        c.drawString(70, y, f"Risk Level: {info['risk']}")
        y -= 30

        if y < 150:
            c.showPage()
            y = height - 60

    # Attribution
    c.setFont("Helvetica", 11)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(50, y, "Developed by: Kshitij G")
    y -= 25

    # Disclaimer
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Disclaimer:")
    y -= 18
    c.setFont("Helvetica", 10)
    disclaimer_lines = [
        "This report is part of an academic/technical project (GeneTrace Lite) and does not constitute medical advice.",
        "The insights presented are for demonstration purposes only. For accurate genetic or health assessments, consult a certified",
        "medical genetics laboratory or a healthcare professional.",
        "This project emphasizes technical integration and SNP-based annotation logic, not clinical reliability."
    ]
    for line in disclaimer_lines:
        c.drawString(50, y, line)
        y -= 14

    y -= 10

    # References
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Scientific References:")
    y -= 16
    c.setFont("Helvetica", 10)
    refs = [
        "- National Center for Biotechnology Information (NCBI)",
        "- MyVariant.info (Human genetic variant annotation API)",
        "- dbSNP: NCBI Database of Single Nucleotide Polymorphisms",
        "- Genetic Association Database (GAD)",
    ]
    for ref in refs:
        c.drawString(50, y, ref)
        y -= 14

    # Footer
    c.setFont("Helvetica-Oblique", 9)
    c.setFillColorRGB(0.5, 0.5, 0.5)
    c.drawString(50, 40, "Generated by GeneTrace Lite — A Technical Trait Risk Profiler")

    c.save()
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="GeneTrace_Report.pdf",
        mimetype="application/pdf"
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

