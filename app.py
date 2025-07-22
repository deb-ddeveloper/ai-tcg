from flask import Flask, render_template, request, send_file
import os, uuid, json
from utils import parse_template, generate_testcase_file, extract_text_from_image, generate_testcases_from_text

app = Flask(__name__)
os.makedirs('uploads/images', exist_ok=True)
os.makedirs('uploads/templates', exist_ok=True)
os.makedirs('generated', exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    try:
        feature = request.form['feature']
        test_type = request.form['test_type']
        test_count = int(request.form['test_count'])

        img = request.files['image']
        img_path = os.path.join('uploads/images', img.filename)
        img.save(img_path)

        tmpl = request.files['template']
        tmpl_path = os.path.join('uploads/templates', tmpl.filename)
        tmpl.save(tmpl_path)

        extracted_text = extract_text_from_image(img_path)
        cases = generate_testcases_from_text(extracted_text, test_count)

        for c in cases:
            c.setdefault('feature', feature)
            c.setdefault('type', test_type)

        cols = parse_template(tmpl_path)
        outfile = os.path.join('generated', f"testcases_{uuid.uuid4().hex[:8]}.xlsx")
        generate_testcase_file(cases, cols, outfile)

        return send_file(outfile, as_attachment=True)
    except Exception as e:
        return f"Internal Server Error: {str(e)}", 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)