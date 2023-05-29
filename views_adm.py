from flask import render_template, request, redirect, session, flash, url_for
from biblioteca import application, banco_de_dados
from models import Usuarios, Administradores
from tools import login_adm_required, FormularioAdministrador
from tools import FormularioCadastroUsuarios
from flask_bcrypt import generate_password_hash
from envia_emails import send_email
import threading


# Renderização da página de login do administrador
@application.route("/login-adm")
def login_adm():
    proxima = request.args.get("proxima")
    form = FormularioAdministrador()
    if proxima is None:
        proxima = url_for("index")
    return render_template("login.html", proxima=proxima, form=form)


# Processo de autenticação do administrador
@application.route("/autenticar-adm", methods=["POST"])
def auth_adm():
    form = FormularioAdministrador()
    user = Administradores.query.filter_by(nome=form.nome.data).first()
    proxima_pagina = request.form["proxima"]
    if proxima_pagina is None:
        proxima_pagina = url_for("index")

    if not user or form.senha.data != user.senha:
        flash("Não foi possível logar, verifique o nome e a senha", "danger")
        return redirect(url_for("login_adm"))

    session.clear()
    session["admnistrador_logado"] = user.nome
    flash(f"{user.nome} logado com sucesso", "info")
    proxima_pagina = request.form.get("proxima", None)
    return redirect(proxima_pagina)


@application.route("/cadastro-alunos")
@login_adm_required
def cadastro_alunos():
    form = FormularioCadastroUsuarios()
    return render_template("cadastro_alunos.html", form=form)


@application.route("/criar-aluno", methods=["POST"])
def criar_usuario():
    form = FormularioCadastroUsuarios(request.form)
    if not form.validate_on_submit():
        flash("Não foi possível criar um cadastro verifique as informações inseridas e tente novamente.", "danger")
        return redirect(url_for("cadastro_alunos"))
    ra = form.ra.data
    aluno = Usuarios.query.filter_by(ra=ra).first()

    if aluno:
        flash("Usuário já existente!", "info")
        return redirect(url_for("cadastro_alunos"))

    nome = form.nome.data
    email = form.email.data
    senha = generate_password_hash(form.senha.data)

    send_email("<div style='width: 750px;'><img src='cid:image1' width='100%' alt='Logo da Faculdade'></div>"
                f"<p>Prezado(a) <b>{nome.upper()}</b>,</p>"
                "<p>Sua conta na biblioteca da Faculdade Univesp no polo de Itapevi foi criada com sucesso! Damos as boas-vindas como nosso novo membro!</p>"
                "<p>Estamos muito satisfeitos em tê-lo como parte da nossa comunidade acadêmica e queremos garantir que você aproveite ao máximo todos os recursos disponíveis em nossa biblioteca. Temos um acervo diversificado de livros e materiais acadêmicos para auxiliar em seus estudos. Sinta-se à vontade para explorar nosso acervo!</p>"
                f"<p><b>Registro Acadêmico:</b> {ra}</p>"
                f"<p><b>Senha:</b> <i>{form.senha.data}</i></p><hr>"
                "<p>Atenciosamente,<br><b>Biblioteca Univesp</b></p><br>"
                "<div style='width: 750px;'><img src='cid:image2' width='100%' alt='Assinatura da Faculdade'></div>",
               email, "Bem-vindo à Biblioteca Univesp!",
               "static/img/univesp_email.jpg",
               "static/img/univesp_email2.jpg")

    novo_aluno = Usuarios(nome=nome, email=email, ra=ra, senha=senha)
    banco_de_dados.session.add(novo_aluno)
    banco_de_dados.session.commit()

    flash(f"Usuário para {nome} criado com sucesso!", "success")
    return redirect(url_for("lista_alunos"))


@application.route("/editar-aluno/<int:id_bd>")
@login_adm_required
def editar_aluno(id_bd):
    aluno = Usuarios.query.filter_by(id_bd=id_bd).first()
    if aluno is None:
        flash("Aluno não encontrado!", "danger")
        return redirect(url_for("lista_alunos"))

    form = FormularioCadastroUsuarios()
    form.nome.data = aluno.nome
    form.email.data = aluno.email
    form.ra.data = aluno.ra

    return render_template("editar_alunos.html", form=form, ra=form.ra.data)


@application.route("/atualizar-alunos", methods=["POST"])
def atualizar_alunos():
    form = FormularioCadastroUsuarios(request.form)
    if form.validate_on_submit():
        ra_antigo = request.form["ra_current"]
        print(ra_antigo)
        aluno = Usuarios.query.filter_by(ra=ra_antigo).first()
        if aluno is None:
            flash("Aluno não encontrado!", "warning")
            return redirect(url_for("lista_alunos"))

        novo_ra = form.ra.data
        if Usuarios.query.filter_by(ra=novo_ra).first() and int(aluno.ra) != int(novo_ra):
            flash(f"Não é possivel utilizar o código {novo_ra}.", "success")
            return redirect(url_for("lista_alunos"))

        aluno.ra = novo_ra
        aluno.nome = form.nome.data
        aluno.email = form.email.data
        aluno.senha = generate_password_hash(form.senha.data)

        banco_de_dados.session.add(aluno)
        banco_de_dados.session.commit()

    else:
        flash(f"Não foi possivel editar o perfil do aluno verifique as informações inseridas e tente novamente!", "warning")

    return redirect(url_for("lista_alunos"))

