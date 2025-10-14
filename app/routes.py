import os
import platform
import psutil
from flask import render_template, request, jsonify, Blueprint, abort
from werkzeug.exceptions import abort
from . import db  
from .models import LogAcesso, SistemaOperacional
from sqlalchemy import func
from sqlalchemy.orm import joinedload

bp = Blueprint('main', __name__)

def obter_info_so():
    """Retorna o nome e a versão do SO do servidor/contêiner."""
    return {
        'nome': platform.system(),
        'versao': platform.release()
    }

def registrar_log():
    """Registra o acesso de qualquer rota, o SO do servidor e o User-Agent do cliente."""
    
    # 1. Obter e registrar o SO do servidor (Lógica 1:N)
    info_so = obter_info_so()
    nome_so_atual = info_so['nome']
    versao_so_atual = info_so['versao']

    so_existente = db.session.execute(
        db.select(SistemaOperacional).filter_by(nome_so=nome_so_atual, versao_so=versao_so_atual)
    ).scalar_one_or_none()

    if so_existente is None:
        novo_so = SistemaOperacional(nome_so=nome_so_atual, versao_so=versao_so_atual)
        db.session.add(novo_so)
        db.session.commit() 
        so_id_usar = novo_so.id
    else:
        so_id_usar = so_existente.id

    # 2. CAPTURA DE IP (PRIORIDADE AO remote_addr)
    # Ignora headers de proxy complexos para garantir estabilidade no ambiente Docker/WSL.
    ip_usuario_registro = request.remote_addr
    
    # 3. CAPTURA DO USER-AGENT DO CLIENTE
    user_agent = request.headers.get('User-Agent')

    # 4. Criação do Log
    novo_log = LogAcesso(
        caminho_acessado=request.path,
        ip_usuario=ip_usuario_registro,
        user_agent=user_agent, # Corrigido para o nome curto do models.py
        so_id=so_id_usar
    )
    db.session.add(novo_log)
    db.session.commit()
    
    # Retorna o ID do log recém-criado
    return novo_log.id 

@bp.route('/logs')
def visualizar_logs():
    registrar_log()
    
    logs = db.session.execute(
        db.select(LogAcesso)
          .options(joinedload(LogAcesso.sistema_operacional)) 
          .order_by(LogAcesso.data_acesso.desc())
          .limit(500)
    ).scalars()
    
    return render_template('logs.html', logs=logs)

# Rota / (raiz) e /<path:caminho> - O Explorador de Arquivos
@bp.route('/', defaults={'caminho': ''})
@bp.route('/<path:caminho>')
def listar_conteudo(caminho):
    log_id = registrar_log()
    
    RAIZ_EXPLORADOR = os.getcwd()
    caminho_absoluto = os.path.join(RAIZ_EXPLORADOR, caminho)

    if not os.path.exists(caminho_absoluto):
        abort(404)

    if os.path.isdir(caminho_absoluto):
        items = []
        try:
            for item_nome in os.listdir(caminho_absoluto):
                item_caminho = os.path.join(caminho_absoluto, item_nome)
                is_dir = os.path.isdir(item_caminho)
                caminho_url = os.path.join(caminho, item_nome).replace('\\', '/') 
                items.append({
                    'nome': item_nome,
                    'is_dir': is_dir,
                    'caminho_completo': caminho_url
                })
        except PermissionError:
            return render_template('erro.html', erro="Permissão Negada"), 403

        caminho_completo_lista = []
        partes = caminho.split('/')
        caminho_atual = ''
        for parte in partes:
            if parte:
                caminho_atual = os.path.join(caminho_atual, parte)
                caminho_completo_lista.append({'nome': parte, 'caminho': caminho_atual.replace('\\', '/')})

        return render_template('index.html', log_id=log_id, caminho=caminho, items=items, caminho_completo_lista=caminho_completo_lista)
    else:
        conteudo_lido = ""
        try:
            with open(caminho_absoluto, 'r', encoding='utf-8', errors='ignore') as f:
                conteudo_lido = f.read()
        except PermissionError:
            return render_template('erro.html', erro=f"Permissão negada para ler o arquivo: {caminho}"), 403
        except Exception as e:
            conteudo_lido = f"ERRO: Não foi possível ler o arquivo. Motivo: {e}"
        return render_template('arquivo.html', nome_arquivo=os.path.basename(caminho), conteudo=conteudo_lido)

# Rota /info (Métricas do Sistema e Logs Totais)
@bp.route('/info')
def info():
    registrar_log()
    total_logs = db.session.execute(
        db.select(func.count(LogAcesso.id))
    ).scalar_one()
    memoria = psutil.virtual_memory()
    memoria_total_gb = f"{memoria.total / (1024 ** 3):.2f} GB"

    dados = {
        "os": platform.system(),
        "version": platform.release(),
        "memory": memoria_total_gb,
        "total_acessos": total_logs
    }
    return jsonify(dados)

# Rota /echo (Teste de POST)
@bp.route('/echo', methods=['POST'])
def msg():
    registrar_log()
    try:
        data = request.get_json()
        if 'msg' in data:
            return jsonify({"resposta": f"Você disse: {data['msg']}"}), 200
        else:
            return jsonify({"erro": "JSON inválido. Esperado {'msg': 'texto'}"}), 400
    except Exception:
        return jsonify({"erro": "Requisição precisa ser JSON válido"}), 400

# Rota /sistemas (Visualiza Tabela 1:N)
@bp.route('/sistemas')
def visualizar_sistemas():
    registrar_log()
    sistemas = db.session.execute(
        db.select(SistemaOperacional)
          .order_by(SistemaOperacional.nome_so, SistemaOperacional.versao_so)
    ).scalars()
    return render_template('sistemas.html', sistemas=sistemas)

# Rota /meu_ip (Para teste de depuração com prioridade)
@bp.route('/meu_ip', methods=['GET'])
def mostrar_ip():
    # Esta rota reflete a prioridade: o que o Flask vê diretamente
    ip_interno = request.remote_addr
    user_agent = request.headers.get('User-Agent')
        
    return jsonify({
        'ip_capturado_servidor': ip_interno, 
        'user_agent': user_agent,
        'headers': dict(request.headers)
    })