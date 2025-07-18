import os
import re
from flask import Flask, request, render_template, send_from_directory
from werkzeug.utils import secure_filename
from markdown import markdown
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
GENERATED_FOLDER = 'generated'
ALLOWED_EXTENSIONS = {'md'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['GENERATED_FOLDER'] = GENERATED_FOLDER

# フォルダがなければ作成
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(GENERATED_FOLDER, exist_ok=True)

# Mermaid拡張クラス
class MermaidExtension(Extension):
    def extendMarkdown(self, md):
        md.preprocessors.register(MermaidPreprocessor(md), 'mermaid', 175)

class MermaidPreprocessor(Preprocessor):
    def run(self, lines):
        new_lines = []
        in_mermaid = False
        mermaid_content = []
        
        for line in lines:
            if line.strip() == '```mermaid':
                in_mermaid = True
                mermaid_content = []
            elif line.strip() == '```' and in_mermaid:
                in_mermaid = False
                mermaid_html = self.convert_mermaid_to_html('\n'.join(mermaid_content))
                new_lines.append(mermaid_html)
                mermaid_content = []
            elif in_mermaid:
                mermaid_content.append(line)
            else:
                new_lines.append(line)
        
        return new_lines
    
    def convert_mermaid_to_html(self, mermaid_code):
        return f'''<div class="mermaid">
{mermaid_code}
</div>'''

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def insert_blank_lines_before_lists(text: str) -> str:
    lines = text.splitlines()
    new_lines = []
    in_code_block = False

    for i, line in enumerate(lines):
        stripped = line.strip()

        # コードブロックのトグル（``` や ~~~）
        if re.match(r'^(```|~~~)', stripped):
            in_code_block = not in_code_block
            new_lines.append(line)
            continue

        # コードブロック内、または4スペース/タブから始まる行はスキップ
        if in_code_block or re.match(r'^(    |\t)', line):
            new_lines.append(line)
            continue

        # 現在行がリスト項目で、前の行が空白でない → 空行を追加
        if re.match(r'^\s*[-+*] ', line):
            if i > 0:
                prev_line = lines[i - 1].strip()
                # 前の行が表の区切りラインではないことも確認
                if prev_line != "" and not re.match(r'^\s*\|?.*\|.*$', prev_line):
                    new_lines.append("")
        new_lines.append(line)

    return "\n".join(new_lines)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        uploaded_file = request.files.get('file')
        if uploaded_file and allowed_file(uploaded_file.filename):
            # ファイルを保存
            filename = secure_filename(uploaded_file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            uploaded_file.save(filepath)

            # Markdown → HTMLの本文へ変換（Mermaid対応）
            with open(filepath, encoding='utf-8') as f:
                md_text = f.read()
            md_text = insert_blank_lines_before_lists(md_text)
            
            # Mermaid拡張を含むMarkdown変換
            html_body = markdown(md_text, extensions=[
                MermaidExtension(),
                'pymdownx.extra', 
                'pymdownx.tilde',
                'tables',
                'codehilite'
            ])

            # 完全なHTML5ページをJinja2テンプレートから生成
            html_filename = filename.rsplit('.', 1)[0] + '.html'
            html_path = os.path.join(app.config['GENERATED_FOLDER'], html_filename)
            # ファイル保存用（リンクなし）
            full_html = render_template('result.html', content=html_body, filename=html_filename, show_download_link=False)
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(full_html)

            # ブラウザ表示用（リンクあり）
            return render_template('result.html', content=html_body, filename=html_filename, show_download_link=True)

        return "無効なファイル形式です（.md のみ対応）", 400

    # 初期表示（アップロードフォーム）
    return render_template('upload.html')

@app.route('/download/<filename>')
def download_html(filename):
    return send_from_directory(app.config['GENERATED_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)