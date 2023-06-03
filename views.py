import threading
import time
from flask import render_template, request, redirect, session, flash, url_for, send_from_directory
from biblioteca import application, banco_de_dados
from envia_emails import send_email
from models import Livros, Usuarios, Historico
from tools import login_adm_required, login_user_required, recupera_imagem, deletar_imagem, FormularioLivro, \
    get_dados_formulario, usuario_pode_reservar, get_datas, agendar_remocao_de_registros
from datetime import date, timedelta

application.jinja_env.globals.update(recupera_imagem=recupera_imagem)
application.jinja_env.globals.update(get_datas=get_datas)


@application.route("/")
@application.route("/home")
def home():
    lista_livros = Livros.query.order_by(Livros.id_bd.desc()).limit(3)
    return render_template("home.html", lista_livros=lista_livros)

# Renderiza página principal com a lista de livros
@application.route("/livros-tabela")
def index():
    agendar_remocao_de_registros()
    lista = Livros.query.order_by(Livros.id)
    return render_template("lista_livros_tabela.html", livros=lista)

@application.route("/livros-cards")
def lista_card():
    lista = Livros.query.order_by(Livros.id).paginate(per_page=9, error_out=True)
    return render_template("lista_livros_cards.html", livros=lista)


# Renderiza para admnistradores a lista de alunos com reservas.
@application.route("/lista-alunos")
@login_adm_required
def lista_alunos():
    lista = Usuarios.query.order_by(Usuarios.nome)
    return render_template("lista_alunos.html", alunos=lista)


# Renderiza página para criar um novo livro.
@application.route("/novo")
@login_adm_required
def novo_livro():
    form = FormularioLivro()
    return render_template("novo.html", form=form)


# URL intermediária usada no botão para criar livros
@application.route("/criar", methods=["POST"])
def criar():
    form = FormularioLivro(request.form)

    if not form.validate_on_submit():
        flash("Os dados inseridos são inválidos!", category="danger")
        return redirect(url_for("novo_livro"))

    dados_formulario = get_dados_formulario(form)
    livro = Livros.query.filter_by(id=dados_formulario["id"]).first()

    if livro:
        flash("Livro já existente!", "info")
        return redirect(url_for("novo_livro"))
    novo_livro = Livros(**dados_formulario)
    banco_de_dados.session.add(novo_livro)
    banco_de_dados.session.commit()

    arquivo = request.files["arquivo"]
    if arquivo.filename != "":
        dir_path = application.config["DIR_PATH"]
        timer = time.time()
        arquivo.save(f"{dir_path}/capa_{novo_livro.id_bd}-{timer}.jpg")

    flash("Livro adicionado com sucesso!", "success")
    return redirect(url_for("novo_livro"))


@application.route("/logout")
def logout():
    session.clear()
    flash("O usuário foi desconectado!", "success")
    return redirect(url_for("index"))


@application.route("/editar/<int:id>")
@login_adm_required
def editar(id):
    livro = Livros.query.filter_by(id=id).first()
    if livro is None:
        flash("Livro não encontrado!", "success")
        return redirect(url_for("novo_livro", id=id))

    form = FormularioLivro()
    form.id.data = livro.id
    form.nome.data = livro.nome
    form.categoria.data = livro.categoria
    form.autor.data = livro.autor
    form.descricao.data = livro.descricao
    form.quantidade.data = livro.quantidade

    capa_livro = recupera_imagem(livro.id_bd)
    return render_template("editar.html", id=id, capa_livro=capa_livro, form=form)


@application.route("/atualizar", methods=["POST"])
def atualizar():
    form = FormularioLivro(request.form)
    if form.validate_on_submit():
        id_antigo = request.form["codigo"]
        livro = Livros.query.filter_by(id=id_antigo).first()
        if livro is None:
            flash("Livro não encontrado!", "success")
            return redirect(url_for("novo_livro"))

        novo_id = form.id.data
        if Livros.query.filter_by(id=novo_id).first() and int(livro.id) != int(novo_id):
            flash(f"Não é possivel utilizar o código {novo_id}.", "success")
            return redirect(url_for("editar", id=livro.id))

        livro.id = novo_id
        livro.nome = form.nome.data
        livro.categoria = form.categoria.data
        livro.autor = form.autor.data
        livro.descricao = form.descricao.data
        livro.quantidade = form.quantidade.data
        livro.quantidade_original = form.quantidade.data

        banco_de_dados.session.add(livro)
        banco_de_dados.session.commit()

        arquivo = request.files["arquivo"]
        dir_path = application.config["DIR_PATH"]
        if arquivo.filename != "":
            timer = time.time()
            deletar_imagem(livro.id_bd)
            arquivo.save(f"{dir_path}/capa_{livro.id_bd}-{timer}.jpg")
    else:
        flash(f"Não foi possivel editar o livro verifique as informações inseridas e tente novamente!", "warning")
        return redirect(url_for("editar", id=request.form["codigo"]))

    return redirect(url_for("livro_completo", id=novo_id))


@application.route("/deletar/<int:id>")
@login_adm_required
def deletar(id):
    livro = Livros.query.filter_by(id=id).first()
    if livro is None:
        flash("Livro não encontrado!", "danger")
        return redirect(url_for("index"))

    deletar_imagem(livro.id_bd)
    banco_de_dados.session.delete(livro)
    banco_de_dados.session.commit()

    flash("Livro deletado com sucesso!", "success")

    return redirect(url_for("index"))


@application.route("/uploads/<nome_arquivo>")
def imagem(nome_arquivo):
    return send_from_directory("imagens", nome_arquivo)


@application.route("/detalhes/<int:id>")
def livro_completo(id):
    livro = Livros.query.filter_by(id=id).first()
    if livro is None:
        flash(f"O livro com o código {id} não existe!", category="warning")
        return redirect(url_for("index"))
    url = request.base_url
    capa_livro = recupera_imagem(livro.id_bd)
    return render_template("detalhes.html", livro=livro, capa_livro=capa_livro, url=url)


@application.route("/reservar/<int:id>")
@login_user_required
@usuario_pode_reservar
def reservar_livro(id):
    usuario_atual = Usuarios.query.filter_by(ra=session["usuario_logado"]).first()

    livro = Livros.query.filter_by(id=id).first()

    if livro is None:
        flash("Livro não encontrado!", "success")
        return redirect(url_for("index"))

    if not livro.disponibilidade:
        flash(f"O livro {livro.nome} não está disponivel!", "success")
        return redirect(url_for("index"))

    if usuario_atual.id_livro == livro.id:
        flash(f"Você já reservou esse livro!", "success")
        return redirect(url_for("index"))


    if usuario_atual.id_livro == 0:
        usuario_atual.id_livro_quantidade = id + livro.quantidade_original - livro.quantidade
        livro.quantidade -= 1
        usuario_atual.id_livro = id
    else:
        livro_antigo = Livros.query.filter_by(id=usuario_atual.id_livro).first()
        livro_antigo.quantidade += 1
        usuario_atual.id_livro_quantidade = id + livro.quantidade_original - livro.quantidade
        livro.quantidade -= 1
        usuario_atual.id_livro = id
        if livro_antigo.quantidade > 0:
            livro_antigo.disponibilidade = True

    if livro.quantidade == 0:
        livro.disponibilidade = False

    banco_de_dados.session.commit()
    flash(f"Livro {livro.nome} reservado com sucesso!", "success")
    return redirect(url_for("index"))


@application.route("/limpar-reserva")
@login_user_required
@usuario_pode_reservar
def limpar_reserva():
    usuario_atual = Usuarios.query.filter_by(ra=session["usuario_logado"]).first()

    if usuario_atual.id_livro != 0:
        livro = Livros.query.filter_by(id=usuario_atual.id_livro).first()
        livro.quantidade += 1
        if livro.quantidade > 0:
            livro.disponibilidade = True
        usuario_atual.id_livro_quantidade = 0
        usuario_atual.id_livro = 0

        banco_de_dados.session.commit()
        flash(f"Retirando reserva para o livro {livro.nome}!", "success")
    else:
        flash("Você não possui reservas!", "success")

    return redirect(url_for("index"))


@application.route("/confirmar-reserva/<int:ra>")
@login_adm_required
def confirmar_reserva(ra):
    usuario = Usuarios.query.filter_by(ra=ra).first()
    if not usuario or usuario.id_livro == 0:
        flash(f"O aluno não reservou nenhum livro", "info")
        return redirect(url_for("lista_alunos"))

    if not usuario.pode_reservar:
        flash(f"A reserva já foi confirmada!", "info")
        return redirect(url_for("lista_alunos"))

    livro = Livros.query.filter_by(id=usuario.id_livro).first()

    thread = threading.Thread(target=lambda: send_email((
        "<div style='width: 100%;'><img src='cid:image1' width='100%' alt='Logo da Biblioteca'></div>"
        "<hr>"
        f"<h2 style='text-align: center; color: black;'>Livro Alugado com Sucesso</h2>"
        f"<h2 style='text-align: center; color: black;'>{livro.nome}</h2>"
        f"<h3 style='text-align: center;  color: black;'>Código do livro: {usuario.id_livro_quantidade}</h3>"
        "<p style='text-align: center;  color: black;'><img src='cid:image3' width='300px' alt='Imagem do livro'></p><hr>"
        f"<p style='color: black;'><b>Data de saída:</b> {date.today().strftime('%d/%m/%Y')}</p>"
        f"<p style='color: black;'><b>Prazo de devolução máximo:</b> {(date.today() + timedelta(days=15)).strftime('%d/%m/%Y')}</p>"
        "<div style='width: 100%;'><img src='cid:image2' width='100%' alt='Assinatura da Biblioteca'></div>"),
        usuario.email, "Livro Alugado com Sucesso!", "static/img/univesp_email.jpg", "static/img/univesp_email2.jpg",
        f"imagens/{recupera_imagem(livro.id_bd)}"))
    thread.start()

    novo_registro = Historico(id=usuario.id_livro_quantidade, ra=usuario.ra, data_saida=date.today())
    banco_de_dados.session.add(novo_registro)
    usuario.pode_reservar = False
    banco_de_dados.session.commit()

    flash(f"O {usuario.nome} reservou o livro de código {usuario.id_livro_quantidade}", "info")
    thread.join()
    return redirect(url_for("lista_alunos"))
@application.route("/confirmar-retorno/<int:ra>")
@login_adm_required
def confirmar_retorno(ra):
    usuario = Usuarios.query.filter_by(ra=ra).first()
    if usuario.pode_reservar:
        flash("Primeiro é necessário confirmar a reserva", "warning")
        return redirect(url_for("lista_alunos"))

    usuario.pode_reservar = True
    livro = Livros.query.filter_by(id=usuario.id_livro).first()


    Historico.query.filter_by(id=usuario.id_livro_quantidade, ra=usuario.ra).first().data_retorno = date.today()
    usuario.id_livro = 0
    usuario.id_livro_quantidade = 0

    if livro is None:
        banco_de_dados.session.commit()
        flash(f"O livro não existe ou foi deletado", "danger")
        return redirect(url_for("lista_alunos"))

    livro.disponibilidade = True
    livro.quantidade += 1

    banco_de_dados.session.commit()

    flash(f"O {usuario.nome} devolveu o livro!", "info")
    return redirect(url_for("lista_alunos"))



@application.route("/historico-aluno")
@application.route("/historico-aluno/<int:ra>")
def historico_aluno(**kwargs):
    if session.get("usuario_logado") is None:
        ra_aluno = kwargs.get("ra")
    else:
        ra_aluno = session['usuario_logado']
    historico = Historico.query.filter_by(ra=ra_aluno).all()
    return render_template("historico_aluno.html", historico=historico)

@application.route("/historico-alunos")
@login_adm_required
def historico_todos_alunos():
    hist = Historico.query.order_by(Historico.id_bd)
    return render_template("historico_global.html", historico=hist)

@application.route("/apagar-aluno/<int:id_bd>")
@login_adm_required
def apagar_aluno(id_bd):
    aluno = Usuarios.query.filter_by(id_bd=id_bd).first()
    if aluno is None:
        flash("Aluno não encontrado!", "danger")
        return redirect(url_for("lista_alunos"))

    if not aluno.pode_reservar:
        flash("Para realizar essa operação o aluno deve realizar a devolução do livro!", "danger")
        return redirect(url_for("lista_alunos"))

    banco_de_dados.session.delete(aluno)
    banco_de_dados.session.commit()

    flash("Aluno deletado com sucesso!", "success")

    return redirect(url_for("lista_alunos"))