from flask import render_template, request, redirect, url_for, jsonify

class SobreController:
    @staticmethod
    def index():
        with open('README.md', 'r', encoding='utf-8') as readme:
                readme_content = readme.read()

        # Percorre linha a linha do readme e substitui as tags de markdown pelas tags HTML correspondentes
        readme_content_html = ''
        card = False
        for line in readme_content.split('\n'):
            
            if line.startswith('# '):
                line = line.replace('# ', f'<h2 class="mb-2">{line[2:]}</h2>')
            
            elif line.startswith('## '):
                if card:
                    line = line.replace('## ', f'</div></div><div class="card mb-3"><div class="card-header"><div class="card-title">{line[3:]}</div></div><div class="card-body">')
                else:
                    line = line.replace('## ', f'<div class="card"><div class="card-header"><div class="card-title">{line[3:]}</div></div><div class="card-body">')
                    card = True
                
            elif line.startswith('### '):
                line = line.replace('### ', f'<h4 class="mt-4">{line[4:]}</h4>')
                
            elif line.startswith('#### '):
                line = line.replace('#### ', f'<h5 class="mt-4">{line[5:]}</h5>')
                
            elif line.startswith('##### '):
                line = line.replace('#####', f'<h6 class="mt-4">{line[6:]}</h6>')
            elif line.strip().startswith('```bash'):
                line = line.replace('```bash', '<pre class="bg-light rounded text-primary">')
            elif line.strip().endswith('```'):
                line = line.replace('```', '</pre>')
            
            if '**' in line:
                while '**' in line:
                    line = line.replace('**', '<strong class="text-black">', 1)
                    line = line.replace('**', '</strong>', 1)
            
            readme_content_html += line + '<br>'    
                
        return render_template('sobre.html', readme_content=readme_content_html)