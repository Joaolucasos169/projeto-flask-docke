import os
import platform
import psutil
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)
app.json.ensure_ascii = False
app.template_folder = os.path.join(os.path.dirname(__file__), 'templates')

@app.route('/', defaults={'caminho': ''})
@app.route('/<path:caminho>')
def listar_conteudo(caminho):
    try:
        caminho_base = os.path.abspath(os.path.dirname(__file__))
        caminho_atual = os.path.join(caminho_base, caminho)
        if not os.path.exists(caminho_atual):
            return render_template('erro.html', mensagem="Caminho não encontrado."), 404

        caminho_completo_lista = []
        if caminho:
            partes = caminho.split(os.sep)
            caminho_acumulado = ''
            for parte in partes:
                caminho_acumulado = os.path.join(caminho_acumulado, parte) if caminho_acumulado else parte
                caminho_completo_lista.append({'nome': parte, 'caminho': caminho_acumulado})

        if os.path.isfile(caminho_atual):
            try:
                with open(caminho_atual, 'r', encoding='utf-8') as f:
                    conteudo = f.read()
                return render_template('arquivo.html', nome_arquivo=os.path.basename(caminho_atual), conteudo=conteudo, caminho_completo_lista=caminho_completo_lista)
            except Exception as e:
                return render_template('erro.html', mensagem=f"Não foi possível ler o arquivo. Erro: {e}"), 500

        items = []
        with os.scandir(caminho_atual) as entries:
            for entry in sorted(entries, key=lambda e: (not e.is_dir(), e.name)):
                items.append({
                    'nome': entry.name,
                    'is_dir': entry.is_dir(),
                    'caminho_completo': os.path.join(caminho, entry.name)
                })
        return render_template('index.html', items=items, caminho=caminho_atual, caminho_completo_lista=caminho_completo_lista)
    except Exception as e:
        return f"Erro no código: {e}", 500

@app.route('/info') 
def infor():
    os_name = platform.system()
    os_version = platform.release()
    memoria = psutil.virtual_memory()
    
    memoria_gb = round(memoria.total / (1024.0 ** 3), 1) #arredondando os dados para ficar legivel
    
    dados = { #Criando dicionario com os dados obtidos
        "Sistema operacional": os_name,
        "Versão": os_version,
        "Memoria": f"{memoria_gb}GB"
    }
    return jsonify(dados)

@app.route('/echo', methods = ['POST'])
def msg():
    dados = request.get_json()
    
    if 'msg' in dados:
        msg_recebida = dados['msg']
        resposta = {"resposta": f"você disse {msg_recebida}"}
        return jsonify(resposta)
    else:
        return jsonify({"erro": "A chave 'msg' não foi encontrada no JSON"}), 400
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)