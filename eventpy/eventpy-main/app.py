import os
import uuid
import hashlib
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, g
from flask_mail import Mail, Message
from functools import wraps
from datetime import datetime
from dotenv import load_dotenv
from peewee import *

# Import models and database
from models import *
from config.database_config import db

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_USERNAME")

mail = Mail(app)

# Inicializar base de dados
# Initialize database on app startup
with app.app_context():
    try:
        db.connect()
        # Create tables if they don't exist
        db.create_tables([
            Utilizador, 
            TipoResiduo, 
            PontoRecolha, 
            PontoRecolhaTiposResiduo,
            Notificacao, 
            Contato
        ], safe=True)
        print("Database initialized successfully")
    except Exception as e:
        print(f"Database initialization error: {e}")
    finally:
        if not db.is_closed():
            db.close()

@app.before_request
def ensure_db_connection():
    """Ensure database is connected for each request"""
    try:
        if db.is_closed():
            db.connect()
    except Exception as e:
        print(f"Database connection error: {e}")
        # Try to reconnect
        try:
            db.close()
            db.connect()
        except Exception as e2:
            print(f"Failed to reconnect: {e2}")

@app.before_request
def carregar_utilizador():
    user_id = session.get("user_id")
    if user_id:
        try:
            g.utilizador = Utilizador.get(Utilizador.id == user_id)
        except Utilizador.DoesNotExist:
            g.utilizador = None
    else:
        g.utilizador = None

# Variaveis globais para templates, por algum motivo nao funciona se colocar no base
@app.context_processor
def inject_current_year():
    return {"current_year": datetime.now().year}

@app.route("/")
def index():
    """Página inicial com mapa interativo"""
    # Os pontos são carregados dinamicamente via API no frontend
    return render_template("index.html")

@app.route("/api/pontos_recolha")
def api_pontos_recolha():
    """API para retornar pontos de recolha em formato JSON"""
    try:
        # Ensure database connection
        if db.is_closed():
            db.connect()
        
        # Query all active points
        pontos = list(PontoRecolha.select().where(PontoRecolha.ativo == True))
        
        pontos_json = []
        for ponto in pontos:
            pontos_json.append({
                'id': ponto.id,
                'nome': ponto.nome,
                'morada': ponto.morada,
                'freguesia': ponto.freguesia,
                'bairro': ponto.bairro,
                'latitude': float(ponto.latitude),
                'longitude': float(ponto.longitude),
                'tipo_ponto': ponto.tipo_ponto,
                'horario_abertura': str(ponto.horario_abertura),
                'horario_fecho': str(ponto.horario_fecho),
                'dias_funcionamento': ponto.dias_funcionamento,
                'telefone': ponto.telefone,
                'email': ponto.email,
                'website': ponto.website,
                'observacoes': ponto.observacoes
            })
        
        return jsonify(pontos_json)
        
    except Exception as e:
        print(f"Error in API: {e}")
        return jsonify({'error': str(e), 'points': []})


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]
        try:
            user = Utilizador.get(Utilizador.email == email)
            
            # Verificar se o email está validado
            if not user.email_validado:
                flash("Por favor, valide o seu email antes de fazer login. Verifique a sua caixa de entrada.", "warning")
                return redirect(url_for("login"))
            
            if user.verificar_senha(senha):
                session["user_id"] = user.id
                return redirect(url_for("utilizador"))
            else:
                flash("Email ou palavra-passe incorretos.", "danger")
        except Utilizador.DoesNotExist:
            flash("Email ou palavra-passe incorretos.", "danger")
            
    return render_template("login.html")


@app.route("/pesquisa")
def pesquisa():
    """Página de pesquisa de pontos de recolha"""
    # Parâmetros de pesquisa
    freguesia = request.args.get("freguesia", "")
    bairro = request.args.get("bairro", "")
    tipo_ponto = request.args.get("tipo_ponto", "")
    
    # Query base
    query = PontoRecolha.select().where(PontoRecolha.ativo == True)
    
    # Aplicar filtros
    if freguesia:
        query = query.where(PontoRecolha.freguesia.contains(freguesia))
    
    if bairro:
        query = query.where(PontoRecolha.bairro.contains(bairro))
    
    if tipo_ponto:
        query = query.where(PontoRecolha.tipo_ponto == tipo_ponto)
    
    # Obter todos os tipos de resíduos para o filtro
    tipos_residuo = TipoResiduo.select()
    
    # Obter lista única de freguesias para o filtro
    freguesias = PontoRecolha.select(PontoRecolha.freguesia).where(PontoRecolha.ativo == True).distinct()
    freguesias = [f.freguesia for f in freguesias]
    freguesias.sort()
    
    return render_template("pesquisa.html", 
                         pontos=query, 
                         tipos_residuo=tipos_residuo,
                         freguesias=freguesias,
                         freguesia=freguesia,
                         bairro=bairro,
                         tipo_ponto=tipo_ponto)

@app.route("/tipos_residuos")
def tipos_residuos():
    """Página informativa sobre tipos de resíduos eletrónicos"""
    tipos = TipoResiduo.select()
    return render_template("tipos_residuos.html", tipos=tipos)

@app.route("/sobre_lixo_eletronico")
def sobre_lixo_eletronico():
    """Página informativa sobre o problema do lixo eletrónico"""
    return render_template("sobre_lixo_eletronico.html")

@app.route("/deslogar")
def deslogar():
    if g.utilizador is not None:
        session.clear()
    return redirect(url_for("index"))

@app.route("/registro", methods=["GET", "POST"])
def registro():
    """Registo de novos utilizadores com validação por email"""
    if request.method == "POST":
        nome = request.form["nome"]
        email = request.form["email"]
        senha = request.form["senha"]
        confirmar_senha = request.form["confirmar_senha"]
        telefone = request.form.get("telefone", "") or "000000000"  # Default if empty
        documento_identificacao = request.form.get("documento_identificacao", "") or "N/A"  # Default if empty

        if senha != confirmar_senha:
            flash("As palavras-passe não coincidem.", "danger")
            return redirect(url_for("registro"))

        try:
            # Gerar token de validação
            token = gerar_token_validacao()
            
            # Criar utilizador com email não validado
            user = Utilizador.create(
                nome=nome,
                email=email,
                token_validacao=token,
                email_validado=False,
                senha_hash='temp_hash',  # Temporário, será substituído
                telefone=telefone,
                documento_identificacao=documento_identificacao
            )
            
            # Definir senha
            user.set_senha(senha)
            user.save()
            
            # Enviar email de validação
            if enviar_email_validacao(email, token):
                flash("Registo efetuado! Verifique o seu email para validar a conta.", "success")
            else:
                flash("Erro ao enviar email de validação. Configure as credenciais de email no arquivo .env", "danger")
                print(f"Token de validação manual: {token}")
                print(f"Link de validação: {url_for('validar_email', token=token, _external=True)}")
            
            return redirect(url_for("login"))
            
        except IntegrityError as e:
            # Verificar se é especificamente erro de email duplicado
            error_str = str(e).lower()
            if "email" in error_str or "unique" in error_str:
                flash("Este email já está registado. Tente outro ou recupere a conta.", "warning")
            else:
                flash("Erro de integridade da base de dados. Tente novamente.", "danger")
            print(f"IntegrityError: {e}")
            print(f"Tipo de erro: {type(e).__name__}")
            return redirect(url_for("registro"))
            
        except Exception as e:
            flash("Ocorreu um erro inesperado no registo.", "danger")
            print(f"Erro no registro: {e}")
            print(f"Tipo de erro: {type(e).__name__}")
            print(f"Args do erro: {e.args}")
            import traceback
            traceback.print_exc()

    return render_template("registro.html")

@app.route("/validar_email/<token>")
def validar_email(token):
    """Validação de email através do token"""
    try:
        user = Utilizador.get(Utilizador.token_validacao == token)
        user.email_validado = True
        user.token_validacao = None
        user.save()
        
        flash("Email validado com sucesso! Já pode iniciar sessão.", "success")
        return redirect(url_for("login"))
        
    except Utilizador.DoesNotExist:
        flash("Link de validação inválido ou expirado.", "danger")
        return redirect(url_for("index"))


@app.route("/contato", methods=["GET", "POST"])
def contato():
    """Formulário de contacto"""
    if request.method == "POST":
        nome = request.form["nome"]
        email = request.form["email"]
        assunto = request.form["assunto"]
        mensagem = request.form["mensagem"]

        # Guardar mensagem na base de dados
        Contato.create(
            nome=nome,
            email=email,
            assunto=assunto,
            mensagem=mensagem
        )

        # Enviar email para o admin
        msg_admin = Message(
            subject=f"[Contato] {assunto}",
            recipients=["admin@reciclagem.pt"],
            body=f"""
Nova mensagem de contacto

Nome: {nome}
Email: {email}
Assunto: {assunto}

Mensagem:
{mensagem}
"""
        )

        # Enviar confirmação para o utilizador
        msg_user = Message(
            subject="Recebemos a sua mensagem",
            recipients=[email],
            body="Obrigado pelo contacto. A nossa equipa irá responder em breve."
        )

        try:
            mail.send(msg_admin)
            mail.send(msg_user)
            flash("Mensagem enviada com sucesso.", "success")
        except Exception as e:
            flash("Erro ao enviar mensagem. Tente novamente.", "danger")
        
        return redirect(url_for("contato"))

    return render_template("contato.html")

@app.route("/utilizador")
def utilizador():
    """Página do utilizador com notificações"""
    if g.utilizador is None:
        flash("Precisa de iniciar sessão para aceder ao perfil.", "warning")
        return redirect(url_for("login"))
    
    # Obter notificações não lidas
    notificacoes = Notificacao.select().where(
        (Notificacao.utilizador == g.utilizador) & 
        (Notificacao.lida == False)
    ).order_by(Notificacao.enviada_em.desc())
    
    return render_template("utilizador.html", 
                         utilizador=g.utilizador, 
                         notificacoes=notificacoes)

@app.route("/marcar_notificacao_lida/<int:notificacao_id>")
def marcar_notificacao_lida(notificacao_id):
    """Marcar notificação como lida"""
    if g.utilizador is None:
        return redirect(url_for("login"))
    
    try:
        notificacao = Notificacao.get(
            (Notificacao.id == notificacao_id) & 
            (Notificacao.utilizador == g.utilizador)
        )
        notificacao.lida = True
        notificacao.save()
        
    except Notificacao.DoesNotExist:
        pass
    
    return redirect(url_for("utilizador"))


@app.route("/apagar_conta", methods=["POST"])
def apagar_conta():
    if g.utilizador is None:
        flash("Precisa de iniciar sessão para apagar a conta.", "warning")
        return redirect(url_for("login"))

    user = g.utilizador
    session.pop("user_id", None)
    user.delete_instance()
    flash("Conta apagada com sucesso.", "success")
    return redirect(url_for("login"))

@app.route("/editar_conta", methods=["POST"])
def editar_conta():
    if g.utilizador is None:
        flash("Precisa de iniciar sessão.", "warning")
        return redirect(url_for("login"))

    user = g.utilizador

    user.nome = request.form["nome"]
    user.email = request.form["email"]
    user.telefone = request.form.get("telefone")
    user.documento_identificacao = request.form.get("documento_identificacao")

    nova_senha = request.form.get("senha")
    if nova_senha:
        user.set_senha(nova_senha)

    user.save()

    flash("Dados atualizados com sucesso.", "success")
    return redirect(url_for("utilizador"))

# Rotas Admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.utilizador is None or not g.utilizador.is_admin:
            flash("Acesso não autorizado.", "danger")
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/admin")
@admin_required
def admin_dashboard():
    # Estatísticas simples
    total_pontos = PontoRecolha.select().where(PontoRecolha.ativo == True).count()
    total_utilizadores = Utilizador.select().count()
    total_contatos = Contato.select().where(Contato.respondido == False).count()
    
    return render_template("admin/dashboard.html", 
                           total_pontos=total_pontos, 
                           total_utilizadores=total_utilizadores,
                           total_contatos=total_contatos)

@app.route("/admin/tipo_residuo/novo", methods=["GET", "POST"])
@admin_required
def admin_novo_tipo_residuo():
    if request.method == "POST":
        try:
            tipo = TipoResiduo.create(
                nome=request.form["nome"],
                descricao=request.form["descricao"],
                icone=request.form["icone"],
                exemplos=request.form["exemplos"]
            )
            flash("Tipo de resíduo criado com sucesso!", "success")
            
            # Notificar todos os utilizadores sobre o novo tipo de resíduo
            notificar_utilizadores_novo_tipo_residuo(tipo)
            
            return redirect(url_for("admin_dashboard"))
        except Exception as e:
            flash(f"Erro ao criar tipo de resíduo: {e}", "danger")
            
    return render_template("admin/form_tipo_residuo.html", tipo=None)

@app.route("/admin/ponto/novo", methods=["GET", "POST"])
@admin_required
def admin_novo_ponto():
    """Adicionar novo ponto de recolha via interface admin"""
    if request.method == "POST":
        try:
            # Criar novo ponto de recolha
            ponto = PontoRecolha.create(
                nome=request.form["nome"],
                morada=request.form["morada"],
                freguesia=request.form["freguesia"],
                bairro=request.form.get("bairro"),
                latitude=float(request.form["latitude"]),
                longitude=float(request.form["longitude"]),
                tipo_ponto=request.form["tipo_ponto"],
                horario_abertura=request.form["horario_abertura"],
                horario_fecho=request.form["horario_fecho"],
                dias_funcionamento=request.form["dias_funcionamento"],
                telefone=request.form.get("telefone"),
                email=request.form.get("email"),
                website=request.form.get("website"),
                observacoes=request.form.get("observacoes"),
                criado_por=g.utilizador
            )
            
            flash("Ponto de recolha criado com sucesso!", "success")
            
            # Notificar utilizadores sobre o novo ponto
            notificar_utilizadores_novo_ponto_recolha(ponto)
            
            return redirect(url_for("admin_dashboard"))
        except Exception as e:
            flash(f"Erro ao criar ponto de recolha: {e}", "danger")
            
    return render_template("admin/form_ponto.html")

@app.route("/admin/utilizadores")
@admin_required
def admin_utilizadores():
    """Listar todos os utilizadores"""
    utilizadores = Utilizador.select().order_by(Utilizador.criado_em.desc())
    return render_template("admin/utilizadores.html", utilizadores=utilizadores)

@app.route("/admin/utilizador/apagar/<int:user_id>", methods=["POST"])
@admin_required
def admin_apagar_utilizador(user_id):
    """Apagar conta de utilizador"""
    try:
        # Impedir que admin apague a si mesmo
        if user_id == g.utilizador.id:
            flash("Não pode apagar a sua própria conta!", "danger")
            return redirect(url_for("admin_utilizadores"))
        
        user = Utilizador.get_by_id(user_id)
        nome_user = user.nome
        user.delete_instance()
        
        flash(f"Utilizador '{nome_user}' apagado com sucesso!", "success")
        
    except Utilizador.DoesNotExist:
        flash("Utilizador não encontrado!", "danger")
    except Exception as e:
        flash(f"Erro ao apagar utilizador: {e}", "danger")
    
    return redirect(url_for("admin_utilizadores"))

def gerar_token_validacao():
    """Gerar token único para validação de email"""
    return str(uuid.uuid4())

def enviar_email_validacao(email, token):
    """Enviar email de validação real"""
    try:
        # Verificar se as credenciais estão configuradas
        if not app.config.get("MAIL_USERNAME") or app.config.get("MAIL_USERNAME") == "your_email@gmail.com":
            print("Credenciais de email não configuradas no arquivo .env")
            return False
        
        if not app.config.get("MAIL_PASSWORD") or app.config.get("MAIL_PASSWORD") == "your_app_password_here":
            print("App Password não configurada no arquivo .env")
            return False
        
        link_validacao = url_for("validar_email", token=token, _external=True)
        
        msg = Message(
            'Validação de Email - Reciclagem REEE',
            sender=app.config["MAIL_DEFAULT_SENDER"],
            recipients=[email]
        )
        
        msg.body = f"""
Olá!

Bem-vindo à plataforma Reciclagem REEE Lisboa!

Para validar o seu email e ativar a sua conta, clique no link abaixo:

{link_validacao}

Este link expira em 24 horas.

Se não se registou na nossa plataforma, por favor ignore este email.

Atenciosamente,
Equipa Reciclagem REEE Lisboa
        """
        
        msg.html = f"""
        <h2>Validação de Email - Reciclagem REEE</h2>
        <p>Olá!</p>
        <p>Bem-vindo à plataforma Reciclagem REEE Lisboa!</p>
        <p>Para validar o seu email e ativar a sua conta, clique no botão abaixo:</p>
        <p><a href="{link_validacao}" style="background-color: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Validar Email</a></p>
        <p>Este link expira em 24 horas.</p>
        <p>Se não se registou na nossa plataforma, por favor ignore este email.</p>
        <p>Atenciosamente,<br>Equipa Reciclagem REEE Lisboa</p>
        """
        
        mail.send(msg)
        print(f"Email enviado com sucesso para {email}")
        return True
        
    except Exception as e:
        print(f"Erro ao enviar email para {email}: {e}")
        print(f"Tipo de erro: {type(e).__name__}")
        
        # Verificar erros comuns
        if "authentication" in str(e).lower():
            print("Solução: Verifique App Password do Gmail")
        elif "connection" in str(e).lower():
            print("Solução: Verifique conexão com a internet")
        elif "smtp" in str(e).lower():
            print("Solução: Verifique configurações SMTP")
            
        return False

def notificar_utilizadores_novo_ponto_recolha(ponto):
    """Notificar todos os utilizadores sobre novo ponto de recolha"""
    try:
        utilizadores = Utilizador.select().where(Utilizador.email_validado == True)
        
        for utilizador in utilizadores:
            Notificacao.create(
                utilizador=utilizador,
                titulo=f"Novo Ponto de Recolha: {ponto.nome}",
                mensagem=f"Foi adicionado um novo ponto de recolha: {ponto.nome} em {ponto.morada}, {ponto.freguesia}. Tipo: {ponto.get_tipo_ponto_display()}.",
                tipo="success"
            )
        
        print(f"Notificações enviadas para {len(utilizadores)} utilizadores sobre novo ponto: {ponto.nome}")
        
    except Exception as e:
        print(f"Erro ao enviar notificações: {e}")

def notificar_utilizadores_novo_tipo_residuo(tipo):
    """Notificar todos os utilizadores sobre novo tipo de resíduo"""
    try:
        utilizadores = Utilizador.select().where(Utilizador.email_validado == True)
        
        for utilizador in utilizadores:
            Notificacao.create(
                utilizador=utilizador,
                titulo=f"Novo Tipo de Resíduo: {tipo.nome}",
                mensagem=f"Foi adicionado um novo tipo de resíduo: {tipo.nome}. {tipo.descricao}",
                tipo="info"
            )
            
        print(f"Notificações enviadas para {len(utilizadores)} utilizadores")
        
    except Exception as e:
        print(f"Erro ao enviar notificações: {e}")

if __name__ == "__main__":
    # Only run debug mode when FLASK_ENV is development
    if os.getenv("FLASK_ENV") == "development":
        app.run(debug=True, host="0.0.0.0", port=5000)
    else:
        app.run(debug=False, host="0.0.0.0", port=5000)
