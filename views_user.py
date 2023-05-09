from biblioteca import application
from flask import render_template, request, redirect, session, flash, url_for
from models import Usuarios
from tools import FormularioLoginUsuarios


@application.route("/login-alunos")
def login_alunos():
    form = FormularioLoginUsuarios()
    proxima = request.args.get("proxima")
    if proxima is None:
        proxima = url_for("index")
    return render_template("login_alunos.html", proxima=proxima, form=form)

@application.route("/autenticar-usuario", methods=["POST"])
def auth_user():
    user = Usuarios.query.filter_by(ra=request.form["ra"]).first()

    if not user or request.form["senha"] != user.senha:
        flash("Não foi possível logar, verifique o RA e a senha", "danger")
        return redirect(url_for("login_alunos"))

    session.clear()
    session["usuario_logado"] = user.ra
    session["nome_usuario"] = user.nome
    flash(f"Bem-Vindo {user.nome}", "info")
    proxima_pagina = request.form.get("proxima", None)
    return redirect(proxima_pagina or url_for("index"))