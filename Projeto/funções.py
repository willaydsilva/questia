def criar_usuario():
    nome = input("Seu nome:")
    escola = input("Qual sua escola: ")
    ano = int(input("Qual seu ano: "))
    turma = input("Qual sua turma: ")
    professor = input("Qual é seu professor")
    return nome, escola, turma, professor, ano

def criar_professor():
    nome = input("Seu nome: ")
    escola = input("Em qual escola você dá aula: ")
    materia = input("Qual matéria você dá aula: ")
    turma = input("Em qual turma você dá aula: ")
    return nome, escola, materia, turma

def criar_escola():
    estado = input("Estado da sua escola: ")
    cidade = input("Cidade da sua escola: ")
    escola = input("Nome da sua escola: ")
    return estado, cidade, escola



