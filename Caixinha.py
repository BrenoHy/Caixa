# Módulo de data
from datetime import datetime

# Inicializando o dicionário de contas
contas = {}

def mostrar_menu():
    print("\nBem-vindo ao Bork!")
    print("1. Consultar Saldo")
    print("2. Sacar")
    print("3. Depósito")
    print("4. Transferência")
    print("5. Histórico de Movimentações")
    print("6. Sair")

def criar_conta(contas):
    usuario = input("Escolha um nome de usuário: ")

    if usuario in contas:
        print("Nome de usuário já existe! Tente novamente!")
    else:
        senha = input("Digite sua senha: ")
        contas[usuario] = {"senha": senha, "saldo": 0.0, "historico": []}  # Nova entrada no dicionário 'contas', com senha, saldo inicial e histórico
        print("Conta criada com sucesso!")

def consultar_saldo(usuario, contas):
    saldo = contas[usuario]['saldo']
    timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')  # Formata a data e hora atual no padrão brasileiro
    print(f"\nSaldo atual: R$ {saldo:.2f}")
    contas[usuario]['historico'].append(f"[{timestamp}] Consulta de saldo: R$ {saldo:.2f}")

def sacar_dinheiro(usuario, contas):
    saldo = contas[usuario]['saldo']
    try:
        valor = float(input("Digite o valor que deseja sacar: "))
        if valor <= 0:
            print("O valor deve ser maior que zero.")
        elif valor > saldo:
            print("Saldo insuficiente.")
        else:
            saldo -= valor
            contas[usuario]['saldo'] = saldo  # Atualiza o saldo no dicionário
            timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')  # Formata a data e hora atual no padrão brasileiro
            print(f"Saque de R$ {valor:.2f} realizado com sucesso!")
            contas[usuario]['historico'].append(f"[{timestamp}] Saque de R$ {valor:.2f}")  # Adiciona a transação com timestamp
    except ValueError:
        print("Por favor, digite um número válido.")
    return contas

def depositar_dinheiro(usuario, contas):
    saldo = contas[usuario]['saldo']
    try:
        valor = float(input("Digite o valor de depósito: "))
        if valor <= 0:
            print("O valor deve ser maior que zero.")
        else:
            saldo += valor
            contas[usuario]['saldo'] = saldo  # Atualiza o saldo no dicionário
            timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')  # Formata a data e hora atual no padrão brasileiro
            print(f"Depósito de R$ {valor:.2f} recebido!")
            contas[usuario]['historico'].append(f"[{timestamp}] Depósito de R$ {valor:.2f}")  # Adiciona a transação com timestamp
    except ValueError:
        print("Por favor, digite um número válido.")
    return contas

def ver_historico(usuario, contas):
    historico = contas[usuario]['historico']
    print("\nHistórico de Movimentações:")
    if not historico:
        print("Nenhuma movimentação realizada.")
    else:
        for movimento in historico:
            print(movimento)  # Mostra cada transação registrada no histórico

def transferir_dinheiro(usuario, contas):
    saldo = contas[usuario]['saldo']
    destinatario = input('Digite o nome de usuário da conta de destino: ')

    if destinatario not in contas:
        print('Conta de destino não encontrada.')
        return contas
    
    try:
        valor = float(input('Digite o valor: '))
        if valor <= 0:
            print('O valor deve ser maior que zero.')
        elif valor > saldo:
            print('Saldo insuficiente.')
        else: 
            saldo -= valor
            contas[usuario]['saldo'] = saldo
            contas[destinatario]['saldo'] += valor

            timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            print(f'Transferência de R$ {valor:.2f} para {destinatario} realizada com sucesso!')
            contas[usuario]['historico'].append(f'[{timestamp}] Transferência de R$ {valor:.2f} de {usuario}')
            contas[destinatario]['historico'].append(f'[{timestamp}] Transferência recebida no valor de R$ {valor:.2f} de {usuario}')
    except ValueError:
        print('Por favor, digite um número válido.')

    return contas

def main():
    global contas  # Declara 'contas' como variável global dentro da função main

    while True:
        print("\n1. Criar Conta\n2. Login\n3. Sair")
        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            criar_conta(contas)
        elif opcao == '2':
            usuario = input("Nome de usuário: ")
            senha = input("Senha: ")

            if usuario in contas and contas[usuario]['senha'] == senha:
                print(f"\nBem-vindo, {usuario}!")
                while True:
                    mostrar_menu()
                    opcao_usuario = input("Escolha uma opção: ")

                    if opcao_usuario == '1':
                        consultar_saldo(usuario, contas)
                    elif opcao_usuario == '2':
                        contas = sacar_dinheiro(usuario, contas)
                    elif opcao_usuario == '3':
                        contas = depositar_dinheiro(usuario, contas)
                    elif opcao_usuario == '4':
                        contas = transferir_dinheiro(usuario, contas)
                    elif opcao_usuario == '5':
                        ver_historico(usuario, contas)
                    elif opcao_usuario == '6':
                        print("Obrigado por usar o Bork. Até logo!")
                        break
                    else:
                        print("Opção inválida! Por favor, selecione outra opção.")
            else:
                print("Nome de usuário ou senha incorretos.")
        elif opcao == '3':
            print("Saindo... Até logo!")
            break
        else:
            print("Opção inválida! Por favor, escolha outra opção.")

if __name__ == "__main__":
    main()

