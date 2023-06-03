import os
from datetime import timedelta, datetime
from functools import wraps
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import smtplib, email.message


from flask import redirect, url_for, session, flash
from flask_wtf import FlaskForm
from wtforms import IntegerField, EmailField, TextAreaField, StringField, SubmitField, PasswordField, validators, \
    SelectField

from biblioteca import application, banco_de_dados
from models import Usuarios, Historico

lista_categorias = [("Computação", "Computação"), ("História", "História"), ("Informática", "Informática"),
                    ("Literatura", "Literatura"), ("Matemática", "Matemática"), ("Pedagogia", "Pedagogia"),
                    ("Português", "Português")]


# Classes de formulários
class FormularioLivro(FlaskForm):
    id = IntegerField("Código do Livro", [validators.data_required(), validators.NumberRange(min=1, max=99999)])
    nome = StringField("Nome do Livro", [validators.data_required(), validators.Length(min=1, max=80)])
    categoria = SelectField("Categoria", choices=lista_categorias)
    autor = StringField("Autor", [validators.data_required(), validators.Length(min=1, max=50)])
    descricao = TextAreaField('Descrição', [validators.optional(), validators.Length(max=3000)])
    quantidade = IntegerField("Quantidade", [validators.data_required(), validators.NumberRange(min=1, max=99)])
    salvar = SubmitField("Salvar")


class FormularioAdministrador(FlaskForm):
    nome = StringField("Nome", [validators.data_required(), validators.Length(min=1, max=40)])
    senha = PasswordField("Senha", [validators.data_required(), validators.Length(min=1, max=100)])
    login = SubmitField("Login")


class FormularioLoginUsuarios(FlaskForm):
    ra = IntegerField("RA", [validators.data_required(), validators.NumberRange(min=5, max=99999999)])
    senha = PasswordField("Senha", [validators.data_required(), validators.Length(min=6, max=100)])
    login = SubmitField("Login")


class FormularioCadastroUsuarios(FlaskForm):
    nome = StringField("Nome Completo", [validators.data_required(), validators.Length(min=5, max=40)])
    ra = IntegerField("Registro Acadêmico (RA)", [validators.data_required(), validators.NumberRange(min=5, max=99999999)])
    email = EmailField("Email", [validators.data_required(), validators.Email(), validators.Length(min=6, max=100)])
    senha = PasswordField("Senha", [validators.data_required(), validators.Length(min=6, max=100)])
    login = SubmitField("Cadastrar Aluno")


# Função auxiliar para obter dados de formulário
def get_dados_formulario(form):
    return {
        "id": form.id.data,
        "nome": form.nome.data,
        "categoria": form.categoria.data,
        "autor": form.autor.data,
        "descricao": form.descricao.data,
        "quantidade": form.quantidade.data,
        "quantidade_original": form.quantidade.data,
    }


# Decoradores
def login_adm_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "admnistrador_logado" not in session or session["admnistrador_logado"] is None:
            proxima = url_for(func.__name__, id=kwargs.get("id"))
            flash("Faça login como administrador para acessar esta página", "danger")
            return redirect(url_for("login_adm", proxima=proxima))
        return func(*args, **kwargs)

    return wrapper


def login_user_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "usuario_logado" not in session or session["usuario_logado"] is None:
            proxima = url_for(func.__name__, id=kwargs.get("id"))
            flash("Faça login como aluno para acessar esta página", "danger")
            return redirect(url_for("login_alunos", proxima=proxima))
        return func(*args, **kwargs)

    return wrapper


def usuario_pode_reservar(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        usuario_atual = Usuarios.query.filter_by(ra=session["usuario_logado"]).first()
        if not usuario_atual or not usuario_atual.pode_reservar:
            flash(f"Para realizar essa operação devolva o livro primeiro!", "danger")
            return redirect(url_for("index"))
        return func(*args, **kwargs)

    return wrapper


# Funções auxiliares
def recupera_imagem(id_bd):
    for nome_arquivo in os.listdir(application.config["DIR_PATH"]):
        if f"capa_{id_bd}-" in nome_arquivo:
            return nome_arquivo
    return "capa_padrao.jpg"


def deletar_imagem(id_bd):
    img_delete = recupera_imagem(id_bd)
    if img_delete != "capa_padrao.jpg":
        os.remove(os.path.join(application.config["DIR_PATH"], img_delete))

def remover_registros_antigos():
    um_ano_atras = datetime.utcnow() - timedelta(days=365)
    registros_antigos = Historico.query.filter(Historico.data_retorno < um_ano_atras).all()
    for registro in registros_antigos:
        banco_de_dados.session.delete(registro)
    banco_de_dados.session.commit()
def agendar_remocao_de_registros():
    scheduler = BackgroundScheduler()
    trigger = CronTrigger(month='*/3')
    scheduler.add_job(remover_registros_antigos, trigger=trigger)
    scheduler.start()

def get_datas(ra):
    user = Usuarios.query.filter_by(ra=ra).first().pode_reservar
    if not user:
        data = Historico.query.filter(Historico.ra == ra, Historico.data_retorno.is_(None)).first().data_saida
        data_retorno_maximo = (data + timedelta(days=15)).strftime('%d/%m/%Y')
        return str(data_retorno_maximo)
    else:
        return "O usuário não tem livros pendentes"
