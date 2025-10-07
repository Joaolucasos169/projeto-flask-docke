import os
import platform
import psutil
from flask import render_template, request, jsonify, Blueprint, request as app
from werkzeug.exceptions import abort
from . import db  # Importa a instância de SQLAlchemy
from .models import LogAcesso # Importa o modelo de Log

bp = Blueprint('main', __name__)
# --- Funções de Rota ---
def registrar_log():
    """Registra o acesso de qualquer rota no banco de dados."""
    # Cria uma nova instância do LogAcesso
    novo_log = LogAcesso(
        caminho_acessado=request.path,
        ip_usuario=request.remote_addr # Obtém o IP do usuário/cliente
)
    # Adiciona e salva no banco de dados
    db.session.add(novo_log)
    db.session.commit()

@bp.route('/logs')
def visualizar_logs():
    registrar_log()
    logs = db.session.execute(
        db.select(LogAcesso).order_by(LogAcesso.data_acesso.desc())
    ).scalars()
    return render_template('logs.html', logs=logs)

# Rota / (raiz) e /<caminho>
@bp.route('/', defaults={'caminho': ''})
@bp.route('/<path:caminho>')
def listar_conteudo(caminho):
    registrar_log() # REGISTRA O ACESSO

    RAIZ_EXPLORADOR = os.getcwd() # Isso será '/app' dentro do container
    caminho_absoluto = os.path.join(RAIZ_EXPLORADOR, caminho)

    if not os.path.exists(caminho_absoluto):
        abort(404)

    if os.path.isdir(caminho_absoluto):
        items = []
        try:
            for item_nome in os.listdir(caminho_absoluto):
                item_caminho = os.path.join(caminho_absoluto, item_nome)
                is_dir = os.path.isdir(item_caminho)
                
                # Para o explorador de arquivos funcionar, o caminho precisa ser relativo à raiz do app
                caminho_url = os.path.join(caminho, item_nome).replace('\\', '/') 
                
                items.append({
                    'nome': item_nome,
                    'is_dir': is_dir,
                    'caminho_completo': caminho_url
                })
        except PermissionError:
            # Lidar com pastas que o usuário não tem permissão para acessar
            return render_template('erro.html', erro="Permissão Negada"), 403

        # Lógica para o breadcrumb (navegação de caminho)
        caminho_completo_lista = []
        partes = caminho.split('/')
        caminho_atual = ''
        for parte in partes:
            if parte:
                caminho_atual = os.path.join(caminho_atual, parte)
                caminho_completo_lista.append({'nome': parte, 'caminho': caminho_atual.replace('\\', '/')})

        return render_template('index.html', caminho=caminho, items=items, caminho_completo_lista=caminho_completo_lista)
    else:
        # --- LÓGICA DE VISUALIZAÇÃO DE ARQUIVO ---
        
        # 1. Tenta ler o arquivo
        conteudo_lido = ""
        try:
            # Abre o arquivo para leitura ('r')
            # Usa 'utf-8' e 'errors='ignore'' para lidar com a maioria dos arquivos de texto
            with open(caminho_absoluto, 'r', encoding='utf-8', errors='ignore') as f:
                conteudo_lido = f.read()
                
            # print(f"Arquivo lido com sucesso. Tamanho: {len(conteudo_lido)} caracteres.") # Linha de DEBUG
            
        except PermissionError:
            return render_template('erro.html', erro=f"Permissão negada para ler o arquivo: {caminho}"), 403
        except Exception as e:
            # Captura qualquer outro erro de leitura (ex: arquivo binário, erro de disco)
            conteudo_lido = f"ERRO: Não foi possível ler o arquivo. Motivo: {e}"
        
        # 2. Renderiza o template de visualização
        return render_template('arquivo.html', # Certifique-se que o nome do template está correto (viewer.html ou arquivo.html)
                               nome_arquivo=os.path.basename(caminho), # Obtém apenas o nome
                               conteudo=conteudo_lido)

# Rota /info
@bp.route('/info')
def info():
    registrar_log() # REGISTRA O ACESSO
    
    # Obtém a memória total do sistema
    memoria = psutil.virtual_memory()
    memoria_total_gb = f"{memoria.total / (1024 ** 3):.2f} GB"

    dados = {
        "os": platform.system(),
        "version": platform.release(),
        "memory": memoria_total_gb
    }
    return jsonify(dados)

# Rota /echo
@bp.route('/echo', methods=['POST'])
def msg():
    registrar_log() # REGISTRA O ACESSO
    
    try:
        data = request.get_json()
        if 'msg' in data:
            return jsonify({"resposta": f"Você disse: {data['msg']}"}), 200
        else:
            return jsonify({"erro": "JSON inválido. Esperado {'msg': 'texto'}"}), 400
    except Exception:
        return jsonify({"erro": "Requisição precisa ser JSON válido"}), 400