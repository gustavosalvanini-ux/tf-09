# Os Três Pilares da Orientação a Objetos no Atalho

- **Encapsulamento:** A interface expõe a leitura com a propriedade `destino` e a alteração via `redirecionar()`, enquanto a implementação oculta o atributo privado `__destino` e a validação contra ciclos em ancestrais.
- **Herança:** A interface do `Atalho` disponibiliza métodos como `caminho()` e `mover_para()`, enquanto a implementação reutiliza a estrutura herdada de `Item` sem duplicar código de movimentação ou caminho.
- **Polimorfismo:** A interface estabelece os métodos `tamanho()` e `mostrar()` comuns a qualquer `Item`, enquanto a implementação do `Atalho` responde com seu tamanho fixo de 1 byte e sua formatação própria `nome -> caminho`.
