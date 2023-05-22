from biblioteca import application
from flask import render_template, request, redirect, session, flash, url_for
from models import Usuarios
from tools import FormularioLoginUsuarios
from flask_bcrypt import check_password_hash

@application.route("/login-alunos")
def login_alunos():
    form = FormularioLoginUsuarios()
    proxima = request.args.get("proxima")
    if proxima is None:
        proxima = url_for("index")
    return render_template("login_alunos.html", proxima=proxima, form=form)

@application.route("/autenticar-usuario", methods=["POST"])
def auth_user():
    form = FormularioLoginUsuarios(request.form)
    user = Usuarios.query.filter_by(ra=form.ra.data).first()
    if user:
        validacao_senha = check_password_hash(user.senha, form.senha.data)
        if validacao_senha:
            session.clear()
            session["usuario_logado"] = user.ra
            session["nome_usuario"] = user.nome
            flash(f"Bem-Vindo {user.nome}", "info")
            proxima_pagina = request.form.get("proxima", None)
            return redirect(proxima_pagina or url_for("index"))

    flash("Não foi possível logar, verifique o RA e a senha", "danger")
    return redirect(url_for("login_alunos"))

