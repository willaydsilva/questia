"""Cria o dados.json com alunos, professores e escolas FICTÍCIOS para a demonstração.

Como usar (dentro da pasta Projeto):
    python3 popular_dados.py

Todos os nomes são inventados. A senha de todo mundo é a SENHA_DEMO abaixo.
"""
import gerenciar_dados as g

SENHA_DEMO = "1234"

ESCOLAS = [
    ("Pernambuco", "Recife", "Escola Modelo Aprender"),
]

PROFESSORES = [
    # nome, escola, matéria, turma
    ("Helena Barbosa", "Escola Modelo Aprender", "Matemática", "7A"),
    ("Rafael Montenegro", "Escola Modelo Aprender", "Português", "7B"),
    ("Patrícia Cavalcanti", "Escola Modelo Aprender", "Ciências", "8A"),
]

ALUNOS = [
    # nome, escola, turma, professor, ano, trilha, pontos
    ("Ana Beatriz Souza", "Escola Modelo Aprender", "7A", "Helena Barbosa", "7º ano", "Frações", 120),
    ("Bruno Henrique Lima", "Escola Modelo Aprender", "7A", "Helena Barbosa", "7º ano", "Frações", 85),
    ("Camila Ferreira", "Escola Modelo Aprender", "7A", "Helena Barbosa", "7º ano", "Geometria", 200),
    ("Davi Albuquerque", "Escola Modelo Aprender", "7A", "Helena Barbosa", "7º ano", "Frações", 40),
    ("Eduarda Pires", "Escola Modelo Aprender", "7B", "Rafael Montenegro", "7º ano", "Interpretação de texto", 150),
    ("Felipe Andrade", "Escola Modelo Aprender", "7B", "Rafael Montenegro", "7º ano", "Gramática", 95),
    ("Gabriela Neves", "Escola Modelo Aprender", "7B", "Rafael Montenegro", "7º ano", "Interpretação de texto", 175),
    ("Heitor Vasconcelos", "Escola Modelo Aprender", "7B", "Rafael Montenegro", "7º ano", "Gramática", 60),
    ("Isabela Rocha", "Escola Modelo Aprender", "8A", "Patrícia Cavalcanti", "8º ano", "Corpo humano", 130),
    ("João Pedro Melo", "Escola Modelo Aprender", "8A", "Patrícia Cavalcanti", "8º ano", "Ecologia", 110),
    ("Larissa Duarte", "Escola Modelo Aprender", "8A", "Patrícia Cavalcanti", "8º ano", "Corpo humano", 210),
    ("Mateus Cordeiro", "Escola Modelo Aprender", "8A", "Patrícia Cavalcanti", "8º ano", "Ecologia", 70),
]


def popular():
    """Apaga o dados.json atual e cria os dados fictícios do zero."""
    g.salvar_dados({"usuarios": [], "escolas": []})
    senha_hash = g.gerar_hash_senha(SENHA_DEMO)

    for estado, cidade, escola in ESCOLAS:
        g.adicionar_escola(estado, cidade, escola)

    for nome, escola, materia, turma in PROFESSORES:
        g.adicionar_usuario({"nome": nome, "tipo": "professor", "escola": escola,
                             "materia": materia, "turma": turma, "senha": senha_hash})

    for nome, escola, turma, professor, ano, trilha, pontos in ALUNOS:
        g.adicionar_usuario({"nome": nome, "tipo": "aluno", "escola": escola,
                             "turma": turma, "professor": professor, "ano": ano,
                             "trilha": trilha, "pontos": pontos, "senha": senha_hash})


def main():
    resposta = input("Isso APAGA o dados.json atual e cria dados fictícios. Continuar? (sim/não) ")
    if g.normalizar(resposta) not in ("sim", "s"):
        print("Nada foi alterado.")
        return
    popular()
    print(f"Pronto! {len(PROFESSORES)} professores, {len(ALUNOS)} alunos e {len(ESCOLAS)} escolas criados.")
    print(f"Senha de todos: {SENHA_DEMO}")
    print("Para testar, entre com: Helena Barbosa (professora) ou Ana Beatriz Souza (aluna).")


if __name__ == "__main__":
    main()