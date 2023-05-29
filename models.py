from biblioteca import banco_de_dados

class Livros(banco_de_dados.Model):
    id_bd = banco_de_dados.Column(banco_de_dados.Integer, primary_key=True, autoincrement=True)
    id = banco_de_dados.Column(banco_de_dados.Integer, nullable=False)
    nome = banco_de_dados.Column(banco_de_dados.String(80), nullable=False)
    categoria = banco_de_dados.Column(banco_de_dados.String(30), nullable=False)
    autor = banco_de_dados.Column(banco_de_dados.String(50), nullable=False)
    descricao = banco_de_dados.Column(banco_de_dados.String(3000), nullable=False)
    disponibilidade = banco_de_dados.Column(banco_de_dados.Boolean, nullable=False, default=True)
    quantidade = banco_de_dados.Column(banco_de_dados.Integer, nullable=False, default=1)
    quantidade_original = banco_de_dados.Column(banco_de_dados.Integer, nullable=False, default=1)

    def __repr__(self):
        return "<Name %r>" % self.name

class Usuarios(banco_de_dados.Model):
    id_bd = banco_de_dados.Column(banco_de_dados.Integer, primary_key=True, autoincrement=True)
    nome = banco_de_dados.Column(banco_de_dados.String(40), nullable=False)
    ra = banco_de_dados.Column(banco_de_dados.Integer, nullable=False, primary_key=True)
    email = banco_de_dados.Column(banco_de_dados.String(100), nullable=False)
    senha = banco_de_dados.Column(banco_de_dados.String(100), nullable=False)
    id_livro = banco_de_dados.Column(banco_de_dados.Integer, nullable=False, default=0)
    id_livro_quantidade = banco_de_dados.Column(banco_de_dados.Integer, nullable=False, default=0)
    pode_reservar = banco_de_dados.Column(banco_de_dados.Boolean, nullable=False, default=True)

    def __repr__(self):
        return "<Name %r>" % self.name

class Administradores(banco_de_dados.Model):
    id_bd = banco_de_dados.Column(banco_de_dados.Integer, primary_key=True, autoincrement=True)
    nome = banco_de_dados.Column(banco_de_dados.String(40), nullable=False)
    senha = banco_de_dados.Column(banco_de_dados.String(100), nullable=False)

    def __repr__(self):
        return "<Name %r>" % self.name

class Historico(banco_de_dados.Model):
    id_bd = banco_de_dados.Column(banco_de_dados.Integer, primary_key=True, autoincrement=True)
    id = banco_de_dados.Column(banco_de_dados.Integer, nullable=False)
    ra = banco_de_dados.Column(banco_de_dados.Integer, nullable=False)
    data_saida = banco_de_dados.Column(banco_de_dados.Date, nullable=False)
    data_retorno = banco_de_dados.Column(banco_de_dados.Date)
