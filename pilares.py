# Os pilares na árvore de arquivos: herança, polimorfismo, abstração e interface.
# Rodar no terminal: python3 pilares.py
#
# O Item da Aula 08 tinha um booleano (eh_pasta) e vários "if eh_pasta".
# Aqui ele vira três classes: Item (o geral), Pasta e Arquivo (os específicos),
# e quem usa a árvore deixa de perguntar "você é pasta?".
from abc import ABC, abstractmethod


# INTERFACE: contrato puro, sem estado e sem implementação.
# Quem assina promete saber dizer o próprio tamanho em bytes.
class Medivel(ABC):
    __slots__ = ()

    @abstractmethod
    def tamanho(self):
        pass


# ABSTRAÇÃO + HERANÇA: o que toda pasta e todo arquivo têm em comum.
# Não dá para criar um Item "solto": ele é só o recorte do essencial.
class Item(Medivel):
    __slots__ = ("__nome", "__pai")

    def __init__(self, nome, pai=None):
        self.__validar_nome(nome)
        self.__nome = nome
        self.__pai = None

        if pai is not None:
            self.mover_para(pai)

    def __validar_nome(self, nome):
        if nome == "" or "/" in nome:
            raise ValueError("nome inválido: " + repr(nome))

    @property
    def nome(self):
        return self.__nome

    @nome.setter
    def nome(self, novo_nome):
        self.__validar_nome(novo_nome)
        self.__nome = novo_nome

    @property
    def pai(self):
        return self.__pai

    def mover_para(self, destino):
        if destino is self.__pai:
            return

        destino._receber(self)          # cada tipo decide se aceita
        if self.__pai is not None:
            self.__pai._soltar(self)
        self.__pai = destino

    # PROTEGIDO: o gancho que as filhas sobrescrevem. Por padrão, recusa.
    def _receber(self, item):
        raise ValueError(self.__nome + " é um arquivo, não pode conter itens")

    def caminho(self):
        if self.__pai is None:
            return self.__nome
        return self.__pai.caminho() + "/" + self.__nome

    def profundidade(self):
        if self.__pai is None:
            return 0
        return self.__pai.profundidade() + 1

    @abstractmethod
    def mostrar(self):
        pass


class Arquivo(Item):
    __slots__ = ("__bytes",)

    def __init__(self, nome, tamanho_bytes, pai=None):
        if tamanho_bytes < 0:
            raise ValueError("tamanho não pode ser negativo")
        self.__bytes = tamanho_bytes
        super().__init__(nome, pai)

    def tamanho(self):
        return self.__bytes

    def mostrar(self):
        recuo = "    " * self.profundidade()
        print(recuo + self.nome + " (" + str(self.tamanho()) + " B)")


class Pasta(Item):
    __slots__ = ("__filhos",)

    def __init__(self, nome, pai=None):
        self.__filhos = []
        super().__init__(nome, pai)

    @property
    def filhos(self):
        return tuple(self.__filhos)

    # OVERRIDE do gancho protegido: a pasta aceita, desde que não crie um ciclo.
    def _receber(self, item):
        ancestral = self
        while ancestral is not None:
            if ancestral is item:
                raise ValueError("não dá para mover " + item.nome + " para dentro dela mesma")
            ancestral = ancestral.pai
        self.__filhos.append(item)

    def _soltar(self, item):
        self.__filhos.remove(item)

    # POLIMORFISMO: a pasta soma o que tem dentro; nenhum filho é perguntado
    # se é pasta ou arquivo, cada um responde do seu jeito.
    def tamanho(self):
        total = 0
        for filho in self.__filhos:
            total = total + filho.tamanho()
        return total

    def mostrar(self):
        recuo = "    " * self.profundidade()
        print(recuo + self.nome + "/ (" + str(self.tamanho()) + " B)")
        for filho in self.__filhos:
            filho.mostrar()


class Atalho(Item):
    # Encapsulamento: o destino é um atributo privado (__destino) declarado em __slots__
    __slots__ = ("__destino",)

    # Herança: reaproveita a inicialização de nome e pai da superclasse Item
    def __init__(self, nome, destino, pai=None):
        super().__init__(nome, pai)
        self.redirecionar(destino)

    # Encapsulamento: permite a leitura do destino sem expor setter direto
    @property
    def destino(self):
        return self.__destino

    # Única forma de alterar o destino; impede ciclo consigo mesmo ou com pastas ancestrais
    def redirecionar(self, novo_destino):
        if novo_destino is self:
            raise ValueError("um atalho não pode apontar para si mesmo")

        ancestral = self.pai
        while ancestral is not None:
            if ancestral is novo_destino:
                raise ValueError("um atalho não pode apontar para uma pasta que o contém")
            ancestral = ancestral.pai

        self.__destino = novo_destino

    # Polimorfismo: um atalho ocupa tamanho fixo de 1 byte
    def tamanho(self):
        return 1

    # Polimorfismo: exibe o atalho no formato 'nome -> caminho' respeitando o recuo
    def mostrar(self):
        recuo = "    " * self.profundidade()
        print(recuo + self.nome + " -> " + self.__destino.caminho())


# Outra classe que assina o contrato SEM ser da árvore: a Lixeira.
class Lixeira(Medivel):
    __slots__ = ("__descartados",)

    def __init__(self):
        self.__descartados = []

    def descartar(self, arquivo):
        self.__descartados.append(arquivo)

    def tamanho(self):
        total = 0
        for arquivo in self.__descartados:
            total = total + arquivo.tamanho()
        return total


# Quem usa o contrato não sabe (nem quer saber) quem está do outro lado.
def espaco_total(coisas):
    total = 0
    for coisa in coisas:
        total = total + coisa.tamanho()
    return total


def tentar(rotulo, acao):
    try:
        acao()
        print(rotulo, "-> passou (!)")
    except Exception as erro:
        print(rotulo, "->", type(erro).__name__ + ":", erro)


# --- Testes da árvore com o Atalho -------------------------------------------
disco = Pasta("C:")
usuarios = Pasta("Users", disco)
gustavo = Pasta("Gustavo", usuarios)
desktop = Pasta("Desktop", gustavo)
documentos = Pasta("Documentos", gustavo)

anotacoes = Arquivo("anotacoes.txt", 150, desktop)
projeto = Arquivo("projeto.py", 800, documentos)

atalho_projeto = Atalho("atalho_projeto.lnk", projeto, desktop)
atalho_documentos = Atalho("atalho_documentos.lnk", documentos, desktop)

# 1. Mostra a árvore completa
disco.mostrar()

# 2. Espaço total de lista contendo arquivo, pasta com atalho dentro e lixeira
lixeira = Lixeira()
lixeira.descartar(Arquivo("temp.log", 50))
print("Espaço total:", espaco_total([projeto, desktop, lixeira]))

# 3. Três tentativas que devem falhar e capturar o erro
tentar("atalho.destino = outro item", lambda: setattr(atalho_projeto, "destino", anotacoes))
tentar("um atalho apontando para si mesmo", lambda: atalho_projeto.redirecionar(atalho_projeto))
tentar("um atalho apontando para a pasta onde ele esta", lambda: atalho_projeto.redirecionar(desktop))
