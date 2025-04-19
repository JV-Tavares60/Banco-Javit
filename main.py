# 1. Importações
from datetime import datetime
import uuid
import json
import os


# 2. Constantes globais
SENHA_ADMIN = "1234"  # Você pode trocar por qualquer senha secreta
saldo = 0
saque_limite = 500
extrato = ""
saque_quant = 0
saque_quant_limite= 3


# 3. Funções utilitárias
def data_hora_atual():
    agora = datetime.now()
    return agora.strftime("[%d/%m/%Y %H:%M]")
def validar_cpf_basico(cpf):
    return cpf.isdigit() and len(cpf) == 11
def salvar_dados(usuarios, arquivo="usuarios.json"):
    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(usuarios, f, ensure_ascii=False, indent=4)
def carregar_dados(arquivo="usuarios.json"):
    if os.path.exists(arquivo):
        with open(arquivo, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}  # Se não existir, retorna um dicionário vazio
def editar_chave_pix(usuarios, id_usuario):
    while True:
        nova_chave = input("Digite a nova chave PIX: ")

        # Verifica se já existe alguma chave igual em outro usuário
        chave_existente = any(
            nova_chave == usuario.get("chave_pix") and uid != id_usuario
            for uid, usuario in usuarios.items()
        )

        if chave_existente:
            print("Essa chave PIX já está em uso por outro usuário. Tente outra.")
        else:
            usuarios[id_usuario]["chave_pix"] = nova_chave
            salvar_dados(usuarios)
            print("Chave PIX atualizada com sucesso!")
            break



# 4. Funções de operações bancárias
def realizar_deposito(saldo, extrato):
    try:
        valor = float(input("Digite o valor do deposito:"))

        if valor > 0:
            saldo += valor
            extrato += f"{data_hora_atual()} Depositado: R$ {valor:.2f}\n"

            print("A operação foi um sucesso! Verifique seu extrato para ver o saldo.")

        else:
            print("A operação falhou! O valor inserido não é válido.")
    except ValueError:
        print("Valor inválido! Por favor, digite um número.")
    return saldo, extrato
def realizar_saque(saldo, extrato, saque_quant, saque_limite, saque_quant_limite):
    try:
        valor = float(input("Digite o valor de saque: "))
    except ValueError:
        print("Valor inválido! Por favor, digite um número.")
        return saldo, extrato, saque_quant
    
    if valor > saldo:
        print("A operação falhou! Saldo insuficiente.")
    elif valor > saque_limite:
        print("A operação falhou! O valor excede o limite por saque.")
    elif saque_quant >= saque_quant_limite:
        print("A operação falhou! Limite diário de saques atingido.")
    elif valor > 0:
        saldo -= valor
        extrato += f"{data_hora_atual()} Saque: R$ {valor:.2f}\n"
        saque_quant += 1
        print("Saque realizado com sucesso!")
    else:
        print("A operação falhou! Valor inválido.")
    
    return saldo, extrato, saque_quant
def mostrar_extrato(saldo, extrato):
    print(("\n================ EXTRATO ================"))
    print("Nenhuma movimentação foi feita nesta conta." if not extrato else extrato)
    print(f"\nSaldo final: R$ {saldo:.2f}")
    print("==========================================")
def realizae_pix(usuarios, id_remetente):
    chave_destino = input("Digite a chave pix de quem vai receber: ")
    valor = float(input("Digite o valor que vai ser transferido: "))

    remetente = usuarios[id_remetente]
    
    #Busca do destinatario pela chave pix
    destinatario_id = None
    for uid, info in usuarios.items():
        if info.get("chave_pix") == chave_destino and uid != id_remetente:
            destinatario_id = uid
            break
    if not destinatario_id:
        print("Chave pix não encontrada ou inválida.")
        return
    if valor <= 0:
        print("Valor inválido.")
        return
    if remetente["saldo"] < valor:
        print("Saldo insuficiente.")
        return
    
    #Atualizar dados
    destinatario = usuarios[destinatario_id]
    remetente["saldo"] -= valor
    destinatario["saldo"] += valor

    mensagem = f"{data_hora_atual()} PIX enviado para {destinatario["nome"]} (chave: {chave_destino}) - R$ {valor:.2f}\n"
    remetente["extrato"] += mensagem

    mensagem_recebido = f"{data_hora_atual()} PIX recebido de {remetente['nome']} - R$ {valor:.2f}\n"
    destinatario["extrato"] += mensagem_recebido

    salvar_dados(usuarios)
    print("Transferência realizada com sucesso!")


# 5. Funções de menu
def menu_principal():
    return input("""
==================== Olá, querido cliente! ====================
================== Bem vindo ao Banco Javit! ==================
                 
[1] Cadastro
[2] Login
[3] Admin
[4] Finalizar

 """)
def menu_opcoes():
    return input("""
  Por favor selecione a opção que deseja acessar em sua conta  

[1] Depósito
[2] Saque
[3] PIX
[4] Extrato
[5] Finalizar

=> """)
def menu_admin():
    return input("""
====== MENU ADMIN ======

[1] Listar todos os usuários
[2] Ver dados de um usuário
[3] Deletar um usuário
[4] Resetar todos os usuários
[5] Voltar ao menu principal

=> """)
def menu_pix():
    return input("""
========= PIX =========

[1] Realizar PIX
[2] Editar chave PIX
[0] Voltar

=> """)


# 6. Funções de cadastro/login
def cadastrar_usuario(usuarios):
    nome = input("Nome: ")
    
    while True:
        cpf = input("CPF (somente números): ")
        if validar_cpf_basico(cpf):
            break
        else:
            print("CPF inválido! Certifique-se de digitar exatamente 11 números.")

    senha = input("Crie uma senha: ")
    while True:
        chave_pix = input("Crie uma chave pix para transações (ex: email, número de telefone, apelido)")

        # Verifica se já existe alguma chave igual
        chave_existente = any(
            chave_pix == usuario.get("chave_pix") for usuario in usuarios.values()
    )

        if chave_existente:
            print("Essa chave PIX já está sendo usada. Por favor, escolha outra.")
        else:
            break


    id_usuario = str(uuid.uuid4())

    usuarios[id_usuario] = {
        "nome": nome,
        "cpf": cpf,
        "senha": senha,
        "chave_pix": chave_pix,
        "saldo": 0,
        "extrato": "",
        "saques_realizados": 0
    }
    salvar_dados(usuarios)
    print(f"\nUsuário cadastrado com sucesso! ID de acesso: {id_usuario}")
def realizar_login(usuarios):
    cpf = input("Digite seu CPF: ")
    senha = input("Digite sua senha: ")

    for id_usuario, dados in usuarios.items():
        if dados["cpf"] == cpf and dados["senha"] == senha:
            print(f"\nLogin bem-sucedido! Bem-vindo(a), {dados['nome']}!")
            return id_usuario  # Retorna o ID do usuário logado

    print("Login falhou. CPF ou senha inválidos.")
    return None


# 7. Funções do menu admin (resetar, listar, deletar etc)
def listar_usuarios(usuarios):
    if not usuarios:
        print("Nenhum usuário cadastrado.")
        return
    print("\n=== Lista de Usuários ===")
    for id_usuario, dados in usuarios.items():
        print(f"ID: {id_usuario} | Nome: {dados['nome']} | CPF: {dados['cpf']}")
def ver_dados_usuario(usuarios):
    cpf = input("Digite o CPF do usuário: ")
    for id_usuario, dados in usuarios.items():
        if dados["cpf"] == cpf:
            print(f"\nID: {id_usuario}")
            for chave, valor in dados.items():
                print(f"{chave.capitalize()}: {valor}")
            return
    print("Usuário não encontrado.")
def deletar_usuario(usuarios):
    cpf = input("Digite o CPF do usuário a ser deletado: ")
    for id_usuario in list(usuarios.keys()):
        if usuarios[id_usuario]["cpf"] == cpf:
            confirm = input(f"Tem certeza que deseja deletar o usuário {usuarios[id_usuario]['nome']}? Digite 's' ou 'n'): ")
            if confirm.lower() == "s":
                del usuarios[id_usuario]
                salvar_dados(usuarios)
                print("Usuário deletado com sucesso.")
            return
    print("Usuário não encontrado.")
def resetar_usuarios():
    confirm = input("Tem certeza que deseja apagar TODOS os dados? Digite 's' ou 'n': ")
    if confirm.lower() == "s":
        with open("usuarios.json", "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False, indent=4)
        print("Todos os usuários foram removidos.")


usuarios = carregar_dados()


while True:
    opcao = menu_principal()

    if opcao == "1":
        cadastrar_usuario(usuarios)

    elif opcao == "2":
        id_usuario = realizar_login(usuarios)

        if id_usuario:
            while True:
                opcao_secundaria = menu_opcoes()
                usuario = usuarios[id_usuario]  # atalho para evitar digitar muito

                if opcao_secundaria == "1":
                    usuario["saldo"], usuario["extrato"] = realizar_deposito(
                        usuario["saldo"], usuario["extrato"]
                    )
                    salvar_dados(usuarios)

                elif opcao_secundaria == "2":
                    usuario["saldo"], usuario["extrato"], usuario["saques_realizados"] = realizar_saque(
                        usuario["saldo"],
                        usuario["extrato"],
                        usuario["saques_realizados"],
                        saque_limite,
                        saque_quant_limite
                    )
                    salvar_dados(usuarios)

                elif opcao_secundaria == "3":
                    while True:
                        escolha_pix = menu_pix()

                        if escolha_pix == "1":
                            realizae_pix(usuarios, id_usuario)

                        elif escolha_pix == "2":
                            editar_chave_pix(usuarios, id_usuario)

                        elif escolha_pix == "0":
                            break

                        else:
                            print("Opção PIX inválida.")

                elif opcao_secundaria == "4":
                    mostrar_extrato(usuario["saldo"], usuario["extrato"])

                elif opcao_secundaria == "5":
                    print("Você saiu da sua conta.")
                    break

                else:
                    print("Opção inválida. Tente novamente.")
    
    elif opcao == "3":
        senha = input("Digite a senha de administrador: ")
        if senha == SENHA_ADMIN:
            while True:
                opcao_admin = menu_admin()

                if opcao_admin == "1":
                    listar_usuarios(usuarios)

                elif opcao_admin == "2":
                    ver_dados_usuario(usuarios)

                elif opcao_admin == "3":
                    deletar_usuario(usuarios)

                elif opcao_admin == "4":
                    resetar_usuarios()
                    usuarios = carregar_dados() #Atualiza na hora
                
                elif opcao_admin == "5":
                    print("Saindo do menu admin.")
                    break
                
                else:
                    print("Opção inválida.")
        else:
            print("Senha incorreta.")
            
    elif opcao == "4":
        print("Sessão finalizada. Até logo!")
        break

    else:
        print("Opção inválida. Tente novamente.")
