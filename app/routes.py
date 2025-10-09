import os
import platform
import psutil
from flask import render_template, request, jsonify, Blueprint, request as app
from werkzeug.exceptions import abort
from . import db  
from .models import LogAcesso, SistemaOperacional # Importa o novo modelo
from sqlalchemy import func
from sqlalchemy.orm import joinedload # Importa para otimização de busca

bp = Blueprint('main', __name__)

# --- FUNÇÃO AUXILIAR PARA OBTER INFORMAÇÕES DO SO ---
def obter_info_so():
    """Retorna o nome e a versão do SO do servidor/contêiner."""
    # Nota: Em um ambiente Docker, isso retorna o SO do contêiner (Linux)
    return {
        'nome': platform.system(),
        'versao': platform.release()
    }

# --- FUNÇÃO DE REGISTRO MODIFICADA ---
def registrar_log():
    """Registra o acesso de qualquer rota e o SO associado no banco de dados."""
    
    # 1. Obter informações do SO
    info_so = obter_info_so()
    nome_so_atual = info_so['nome']
    versao_so_atual = info_so['versao']
    
    # 2. Verificar se o SO já existe (Busca no ORM)
    so_existente = db.session.execute(
        db.select(SistemaOperacional).filter_by(
            nome_so=nome_so_atual, 
            versao_so=versao_so_atual
        )
    ).scalar_one_or_none()
    
    # 3. Se não existe, cria o novo registro de SO
    if so_existente is None:
        novo_so = SistemaOperacional(nome_so=nome_so_atual, versao_so=versao_so_atual)
        db.session.add(novo_so)
        # Commit necessário para obter o ID (PK) antes de usá-lo como FK no LogAcesso
        db.session.commit() 
        so_id_usar = novo_so.id
    else:
        so_id_usar = so_existente.id # Usa o ID do registro existente
        
    # 4. Cria e salva o LogAcesso, usando a Chave Estrangeira (FK)
    novo_log = LogAcesso(
        caminho_acessado=request.path,
        ip_usuario=request.remote_addr,
        so_id=so_id_usar # SALVA A CHAVE ESTRANGEIRA AQUI
    )
    
    db.session.add(novo_log)
    db.session.commit()

# Rota /logs
@bp.route('/logs')
def visualizar_logs():
    registrar_log()
    
    # Usa joinedload para buscar os dados do SO com uma única query (otimização N+1)
    logs = db.session.execute(
        db.select(LogAcesso)
          .options(joinedload(LogAcesso.sistema_operacional)) 
          .order_by(LogAcesso.data_acesso.desc())
          .limit(500)
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
            
        except PermissionError:
            return render_template('erro.html', erro=f"Permissão negada para ler o arquivo: {caminho}"), 403
        except Exception as e:
            # Captura qualquer outro erro de leitura (ex: arquivo binário, erro de disco)
            conteudo_lido = f"ERRO: Não foi possível ler o arquivo. Motivo: {e}"
        
        # 2. Renderiza o template de visualização
        return render_template('arquivo.html', 
                               nome_arquivo=os.path.basename(caminho), 
                               conteudo=conteudo_lido)

# Rota /info
@bp.route('/info')
def info():
    registrar_log()
    
    # Conta o total de logs usando o ORM (func.count)
    total_logs = db.session.execute(
        db.select(func.count(LogAcesso.id))
    ).scalar_one()
    
    # Obtém a memória total do sistema
    memoria = psutil.virtual_memory()
    memoria_total_gb = f"{memoria.total / (1024 ** 3):.2f} GB"

    dados = {
        "os": platform.system(),
        "version": platform.release(),
        "memory": memoria_total_gb,
        "total_acessos": total_logs
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
    
@bp.route('/sistemas')
def visualizar_sistemas():
    registrar_log()
    
    sistemas = db.session.execute(
        db.select(SistemaOperacional)
          .order_by(SistemaOperacional.nome_so, SistemaOperacional.versao_so)
    ).scalars()
    
    return render_template('sistemas.html', sistemas=sistemas)