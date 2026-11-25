
"""Adiciona dados fictícios ao QuestiAI sem apagar cadastros existentes."""

import gerenciar_dados as g

SENHA_DEMO = "1234"

# Estado, cidade, nome
ESCOLAS = [
    ("Pernambuco", "Recife", "Modelo Aprender"),
    ("Pernambuco", "Recife", "CESAR School"),
    ("Pernambuco", "Recife", "Horizonte do Saber"),
]

# Nome, escola, matéria, turma
PROFESSORES = [
    ("Helena Barbosa", "Modelo Aprender", "Matemática", "7A"),
    ("Rafael Montenegro", "Modelo Aprender", "Português", "7B"),
    ("Patrícia Cavalcanti", "Modelo Aprender", "Ciências", "8A"),

    ("Mariana Costa", "CESAR School", "Matemática", "7A"),
    ("Lucas Almeida", "CESAR School", "Português", "7B"),
    ("Beatriz Nogueira", "CESAR School", "Ciências", "8A"),

    ("Fernanda Ribeiro", "Horizonte do Saber", "Matemática", "7A"),
    ("André Martins", "Horizonte do Saber", "Português", "7B"),
    ("Juliana Freitas", "Horizonte do Saber", "Ciências", "8A"),
]

# Nome, escola, turma, professor, ano, trilha, pontos
ALUNOS = [
    # MODELO APRENDER - 12 alunos
    ("Ana Beatriz Souza", "Modelo Aprender", "7A", "Helena Barbosa", "7º ano", "Frações", 120),
    ("Bruno Henrique Lima", "Modelo Aprender", "7A", "Helena Barbosa", "7º ano", "Frações", 85),
    ("Camila Ferreira", "Modelo Aprender", "7A", "Helena Barbosa", "7º ano", "Geometria", 200),
    ("Davi Albuquerque", "Modelo Aprender", "7A", "Helena Barbosa", "7º ano", "Frações", 40),
    ("Eduarda Pires", "Modelo Aprender", "7B", "Rafael Montenegro", "7º ano", "Interpretação de texto", 150),
    ("Felipe Andrade", "Modelo Aprender", "7B", "Rafael Montenegro", "7º ano", "Gramática", 95),
    ("Gabriela Neves", "Modelo Aprender", "7B", "Rafael Montenegro", "7º ano", "Interpretação de texto", 175),
    ("Heitor Vasconcelos", "Modelo Aprender", "7B", "Rafael Montenegro", "7º ano", "Gramática", 60),
    ("Isabela Rocha", "Modelo Aprender", "8A", "Patrícia Cavalcanti", "8º ano", "Corpo humano", 130),
    ("João Pedro Melo", "Modelo Aprender", "8A", "Patrícia Cavalcanti", "8º ano", "Ecologia", 110),
    ("Larissa Duarte", "Modelo Aprender", "8A", "Patrícia Cavalcanti", "8º ano", "Corpo humano", 210),
    ("Mateus Cordeiro", "Modelo Aprender", "8A", "Patrícia Cavalcanti", "8º ano", "Ecologia", 70),

    # CESAR SCHOOL - 12 alunos
    ("Alice Moura", "CESAR School", "7A", "Mariana Costa", "7º ano", "Frações", 110),
    ("Bernardo Silva", "CESAR School", "7A", "Mariana Costa", "7º ano", "Geometria", 95),
    ("Clara Oliveira", "CESAR School", "7A", "Mariana Costa", "7º ano", "Frações", 140),
    ("Daniel Castro", "CESAR School", "7A", "Mariana Costa", "7º ano", "Geometria", 80),
    ("Elisa Gomes", "CESAR School", "7B", "Lucas Almeida", "7º ano", "Gramática", 125),
    ("Gabriel Teixeira", "CESAR School", "7B", "Lucas Almeida", "7º ano", "Interpretação de texto", 100),
    ("Helena Duarte", "CESAR School", "7B", "Lucas Almeida", "7º ano", "Gramática", 160),
    ("Igor Carvalho", "CESAR School", "7B", "Lucas Almeida", "7º ano", "Interpretação de texto", 75),
    ("Laura Mendes", "CESAR School", "8A", "Beatriz Nogueira", "8º ano", "Ecologia", 130),
    ("Miguel Rocha", "CESAR School", "8A", "Beatriz Nogueira", "8º ano", "Corpo humano", 90),
    ("Nina Barbosa", "CESAR School", "8A", "Beatriz Nogueira", "8º ano", "Ecologia", 170),
    ("Otávio Lima", "CESAR School", "8A", "Beatriz Nogueira", "8º ano", "Corpo humano", 115),

    # HORIZONTE DO SABER - 12 alunos
    ("Pedro Henrique Alves", "Horizonte do Saber", "7A", "Fernanda Ribeiro", "7º ano", "Frações", 105),
    ("Rafaela Souza", "Horizonte do Saber", "7A", "Fernanda Ribeiro", "7º ano", "Geometria", 145),
    ("Samuel Ferreira", "Horizonte do Saber", "7A", "Fernanda Ribeiro", "7º ano", "Frações", 85),
    ("Talita Azevedo", "Horizonte do Saber", "7A", "Fernanda Ribeiro", "7º ano", "Geometria", 120),
    ("Vitor Cardoso", "Horizonte do Saber", "7B", "André Martins", "7º ano", "Gramática", 100),
    ("Yasmin Correia", "Horizonte do Saber", "7B", "André Martins", "7º ano", "Interpretação de texto", 155),
    ("Arthur Pacheco", "Horizonte do Saber", "7B", "André Martins", "7º ano", "Gramática", 70),
    ("Bianca Farias", "Horizonte do Saber", "7B", "André Martins", "7º ano", "Interpretação de texto", 135),
    ("Caio Batista", "Horizonte do Saber", "8A", "Juliana Freitas", "8º ano", "Ecologia", 115),
    ("Débora Campos", "Horizonte do Saber", "8A", "Juliana Freitas", "8º ano", "Corpo humano", 180),
    ("Enzo Moreira", "Horizonte do Saber", "8A", "Juliana Freitas", "8º ano", "Ecologia", 90),
    ("Flora Tavares", "Horizonte do Saber", "8A", "Juliana Freitas", "8º ano", "Corpo humano", 150),
]


def popular():
    """Inclui dados fictícios sem apagar ou duplicar usuários."""

    # Valida os dados antes de começar a salvar.
    nomes_escolas = [g.normalizar(e[2]) for e in ESCOLAS]
    professores = {
        g.normalizar(nome): (escola, turma)
        for nome, escola, materia, turma in PROFESSORES
    }

    for nome, escola, turma, professor, ano, trilha, pontos in ALUNOS:
        if g.normalizar(escola) not in nomes_escolas:
            raise ValueError(f"Escola inválida para {nome}")

        vinculo = professores.get(g.normalizar(professor))

        if vinculo != (escola, turma):
            raise ValueError(f"Professor ou turma inválidos para {nome}")

    # Uma senha de demonstração para os novos usuários.
    senha_hash = g.gerar_hash_senha(SENHA_DEMO)

    novas_escolas = 0
    novos_professores = 0
    novos_alunos = 0

    # 1. Cadastra somente as escolas que faltam.
    for estado, cidade, escola in ESCOLAS:
        if g.adicionar_escola(estado, cidade, escola):
            novas_escolas += 1

    # 2. Cadastra somente os professores que faltam.
    for nome, escola, materia, turma in PROFESSORES:
        existente = g.buscar_usuario(nome)

        if existente:
            if (
                existente.get("tipo") != "professor"
                or g.normalizar(existente.get("escola", "")) != g.normalizar(escola)
                or existente.get("turma") != turma
            ):
                raise ValueError(f"Cadastro conflitante: {nome}")
            continue

        g.adicionar_usuario({
            "nome": nome,
            "tipo": "professor",
            "escola": escola,
            "materia": materia,
            "turma": turma,
            "senha": senha_hash
        })
        novos_professores += 1

    # 3. Cadastra somente os alunos que faltam.
    for nome, escola, turma, professor, ano, trilha, pontos in ALUNOS:
        existente = g.buscar_usuario(nome)

        if existente:
            if (
                existente.get("tipo") != "aluno"
                or g.normalizar(existente.get("escola", "")) != g.normalizar(escola)
                or existente.get("turma") != turma
                or g.normalizar(existente.get("professor", "")) != g.normalizar(professor)
            ):
                raise ValueError(f"Cadastro conflitante: {nome}")
            continue

        professor_cadastrado = g.buscar_professor(professor)

        if not professor_cadastrado:
            raise ValueError(f"Professor não encontrado: {professor}")

        if (
            g.normalizar(professor_cadastrado["escola"]) != g.normalizar(escola)
            or professor_cadastrado["turma"] != turma
        ):
            raise ValueError(f"Vínculo incorreto para {nome}")

        g.adicionar_usuario({
            "nome": nome,
            "tipo": "aluno",
            "escola": escola,
            "turma": turma,
            "professor": professor,
            "ano": ano,
            "trilha": trilha,
            "pontos": pontos,
            "senha": senha_hash
        })
        novos_alunos += 1

    print("\nCadastros adicionados:")
    print(f"Escolas: {novas_escolas}")
    print(f"Professores: {novos_professores}")
    print(f"Alunos: {novos_alunos}")

    # 4. Mostra um resumo do banco de dados.
    dados = g.carregar_dados()

    print("\nResumo por escola:")

    for escola in dados["escolas"]:
        nome = escola["escola"]

        alunos = sum(
            1 for u in dados["usuarios"]
            if u.get("tipo") == "aluno"
            and g.normalizar(u.get("escola", "")) == g.normalizar(nome)
        )

        professores = sum(
            1 for u in dados["usuarios"]
            if u.get("tipo") == "professor"
            and g.normalizar(u.get("escola", "")) == g.normalizar(nome)
        )

        print(f"{nome}: {alunos} alunos e {professores} professores")


def main():
    print("QuestiAI - Cadastro de dados fictícios")
    print("Os cadastros existentes serão preservados.")

    resposta = input("Deseja adicionar os dados que faltam? (sim/não): ")

    if g.normalizar(resposta) not in ("sim", "s"):
        print("Nenhum cadastro foi alterado.")
        return

    popular()
    print("\nProcesso concluído!")
    print("Senha dos novos usuários: 1234")


if __name__ == "__main__":
    main()
