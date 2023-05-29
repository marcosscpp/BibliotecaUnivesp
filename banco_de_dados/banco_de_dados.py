import mysql.connector
import json

print("Realizando a conexão com o bando de dados...")

with open("dados.json", "r") as bd_conn:
    conn_data = json.load(bd_conn)
    conn = mysql.connector.connect(
        host=conn_data["host"],
        user=conn_data["user"],
        password=conn_data["password"])

    cursor = conn.cursor()
    cursor.execute("DROP DATABASE IF EXISTS biblioteca;")
    cursor.execute("CREATE DATABASE IF NOT EXISTS `biblioteca`;")
    cursor.execute("USE `biblioteca`;")

    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS `livros` (
                    `id_bd` int(5) NOT NULL AUTO_INCREMENT,
                    `id` int(5) NOT NULL,
                    `nome` varchar(80) NOT NULL,
                    `categoria` varchar(30) NOT NULL,
                    `autor` varchar(50) NOT NULL,
                    `descricao` varchar(3000),
                    `disponibilidade` BOOLEAN NOT NULL DEFAULT TRUE,
                    `quantidade` TINYINT(2) NOT NULL DEFAULT 1, 
                    PRIMARY KEY (`id_bd`)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;''')

    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS `usuarios` (
                    `id_bd` int(5) NOT NULL AUTO_INCREMENT,
                    `nome` varchar(40) NOT NULL,
                    `ra` INT(10) NOT NULL,
                    `email` VARCHAR(100) NOT NULL,
                    `senha` varchar(100) NOT NULL,
                    `id_livro` int(5) NOT NULL DEFAULT 0,
                    `id_livro_quantidade` int(5) NOT NULL DEFAULT 0,
                    `pode_reservar` BOOLEAN NOT NULL DEFAULT TRUE,
                    PRIMARY KEY (`id_bd`)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;''')

    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS `administradores` (
                    `id_bd` tinyint(1) NOT NULL AUTO_INCREMENT,
                    `nome` varchar(40) NOT NULL,
                    `senha` varchar(100) NOT NULL,
                    PRIMARY KEY (`id_bd`)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;''')

    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS `historico` (
                    `id_bd` int(9) NOT NULL AUTO_INCREMENT,
                    `ra` INT(10) NOT NULL,
                    `id` int(5) NOT NULL,
                    `data_saida` DATE NOT NULL,
                    `data_retorno` DATE,
                     PRIMARY KEY (`id_bd`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
''')

    cursor.execute('''INSERT INTO `administradores` (`nome`, `senha`) VALUES ('teste', 'teste');''')

    cursor.execute('''INSERT INTO `livros` (`id_bd`, `id`, `nome`, `categoria`, `autor`, `descricao`, `disponibilidade`, `quantidade`) VALUES 
                       (1, 1, 'O Senhor dos Anéis', 'Fantasia', 'J.R.R. Tolkien', 'Uma grande aventura épica na Terra-média', true, 1),
                       (2, 2, '1984', 'Ficção Científica', 'George Orwell', 'Uma história sombria sobre o controle totalitário do Estado', true, 1),
                       (3, 3, 'Cem Anos de Solidão', 'Ficção Literária', 'Gabriel García Márquez', 'A saga de uma família através de gerações numa aldeia imaginária na América Latina', true, 2),
                       (4, 4, 'A Guerra dos Tronos', 'Fantasia', 'George R.R. Martin', 'A história de várias famílias nobres lutando pelo controle do Trono de Ferro', true, 4),
                       (5, 5, 'A Revolução dos Bichos', 'Fábula', 'George Orwell', 'Uma história sobre animais que se revoltam contra os seus donos humanos', true, 1),
                       (6, 6, 'O Sol é para Todos', 'Ficção Literária', 'Harper Lee', 'Um livro sobre racismo e injustiça nos EUA dos anos 30', true, 1),
                       (7, 7, 'Dom Quixote', 'Romance', 'Miguel de Cervantes', 'As aventuras de um sonhador que se torna cavaleiro', true, 1),
                       (8, 8, 'O Apanhador no Campo de Centeio', 'Ficção Literária', 'J.D. Salinger', 'A história de um adolescente em conflito com a sociedade em que vive', true, 2),
                       (9, 9, 'A Montanha Mágica', 'Romance', 'Thomas Mann', 'A história de um jovem que vai a um sanatório nos Alpes suíços e se envolve em discussões filosóficas', true, 3),
                       (10, 10, 'A Insustentável Leveza do Ser', 'Ficção Literária', 'Milan Kundera', 'Um romance filosófico sobre amor, sexo, política e a vida em geral', true, 2);
                       ''')

    conn.commit()
    cursor.close()
    conn.close()

    print("Criação do banco de dados feita com sucesso!")
