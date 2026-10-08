"""
Verificador Lógico - Introdução aos Circuitos Lógicos (ENEL 1)

Usa apenas a biblioteca padrão do Python, então roda igual no VS Code e no Colab.

Precedência (da MAIOR para a MENOR):
    1. ~  / não          (negação)
    2. e  / ^  / &       (conjunção)
    3. xor               (ou exclusivo)
    4. ou / v  / |       (disjunção)
    5. ->                (condicional, associativo à direita)
    6. <->               (bicondicional)
Proposições: UMA letra maiúscula (P, Q, R...). Operadores em minúsculas.
"""
import itertools


class ErroSintaxe(Exception):
    """Levantada quando a expressão digitada é inválida."""


# ----------------------------------------------------------------------
# 1. TOKENIZADOR: transforma o texto em uma lista de tokens
# ----------------------------------------------------------------------
PALAVRAS = {"e": "and", "ou": "or", "v": "or", "xor": "xor",
            "nao": "not", "não": "not"}
SIMBOLOS = {"~": "not", "!": "not", "^": "and", "&": "and", "|": "or"}


def tokenizar(texto):
    tokens, i = [], 0
    while i < len(texto):
        c = texto[i]
        if c.isspace():
            i += 1
        elif texto.startswith("<->", i):
            tokens.append(("bicond", None)); i += 3
        elif texto.startswith("->", i):
            tokens.append(("impl", None)); i += 2
        elif c == "(":
            tokens.append(("(", None)); i += 1
        elif c == ")":
            tokens.append((")", None)); i += 1
        elif c in SIMBOLOS:
            tokens.append((SIMBOLOS[c], None)); i += 1
        elif c.isalpha():
            j = i
            while j < len(texto) and texto[j].isalpha():
                j += 1
            palavra = texto[i:j]
            if len(palavra) == 1 and palavra.isupper():
                tokens.append(("var", palavra))
            elif palavra.lower() in PALAVRAS:
                tokens.append((PALAVRAS[palavra.lower()], None))
            else:
                raise ErroSintaxe(
                    f"'{palavra}' não é válido. Proposições são UMA letra "
                    f"maiúscula (P, Q, R...) e operadores são e, ou, v, xor, não.")
            i = j
        else:
            raise ErroSintaxe(f"Caractere inválido: '{c}'")
    return tokens


# ----------------------------------------------------------------------
# 2. PARSER (descida recursiva) -> árvore em tuplas
#    ('var','P') | ('not',x) | ('and',a,b) | ('or',a,b) | ('xor',a,b)
#    | ('impl',a,b) | ('bicond',a,b)
# ----------------------------------------------------------------------
class Parser:
    def __init__(self, tokens):
        self.t, self.pos = tokens, 0

    def atual(self):
        return self.t[self.pos][0] if self.pos < len(self.t) else None

    def consumir(self):
        tok = self.t[self.pos]
        self.pos += 1
        return tok

    def bicond(self):                      # menor precedência
        no = self.impl()
        while self.atual() == "bicond":
            self.consumir()
            no = ("bicond", no, self.impl())
        return no

    def impl(self):                        # associativo à direita
        no = self.ou()
        if self.atual() == "impl":
            self.consumir()
            return ("impl", no, self.impl())
        return no

    def ou(self):
        no = self.xor()
        while self.atual() == "or":
            self.consumir()
            no = ("or", no, self.xor())
        return no

    def xor(self):
        no = self.e()
        while self.atual() == "xor":
            self.consumir()
            no = ("xor", no, self.e())
        return no

    def e(self):
        no = self.nao()
        while self.atual() == "and":
            self.consumir()
            no = ("and", no, self.nao())
        return no

    def nao(self):                         # maior precedência
        if self.atual() == "not":
            self.consumir()
            return ("not", self.nao())
        return self.atomo()

    def atomo(self):
        tipo = self.atual()
        if tipo == "var":
            return ("var", self.consumir()[1])
        if tipo == "(":
            self.consumir()
            no = self.bicond()
            if self.atual() != ")":
                raise ErroSintaxe("Faltou fechar parêntese ')'.")
            self.consumir()
            return no
        if tipo is None:
            raise ErroSintaxe("A expressão terminou antes do esperado "
                              "(falta um operando).")
        raise ErroSintaxe(f"Esperava uma proposição ou '(' mas achei '{tipo}'.")


def parse(texto):
    if not texto.strip():
        raise ErroSintaxe("Expressão vazia.")
    p = Parser(tokenizar(texto))
    arvore = p.bicond()
    if p.pos != len(p.t):
        raise ErroSintaxe("Sobrou texto no fim (parêntese ')' extra ou "
                          "falta de operador entre proposições).")
    return arvore


# ----------------------------------------------------------------------
# 3. AVALIAÇÃO E UTILIDADES
# ----------------------------------------------------------------------
SIMB_TXT = {"and": "e", "or": "ou", "xor": "xor", "impl": "->", "bicond": "<->"}


def avaliar(no, val):
    """Calcula o valor (True/False) de uma árvore dada uma valoração."""
    k = no[0]
    if k == "var":    return val[no[1]]
    if k == "not":    return not avaliar(no[1], val)
    a, b = avaliar(no[1], val), avaliar(no[2], val)
    if k == "and":    return a and b
    if k == "or":     return a or b
    if k == "xor":    return a != b
    if k == "impl":   return (not a) or b      # só falsa em V -> F
    if k == "bicond": return a == b


def texto_no(no, raiz=True):
    """Converte a árvore de volta em texto, com parênteses explícitos."""
    k = no[0]
    if k == "var":
        return no[1]
    if k == "not":
        return "~" + texto_no(no[1], False)
    s = f"{texto_no(no[1], False)} {SIMB_TXT[k]} {texto_no(no[2], False)}"
    return s if raiz else f"({s})"


def variaveis(*arvores):
    achadas = set()
    def percorre(n):
        if n[0] == "var": achadas.add(n[1])
        else:
            for filho in n[1:]: percorre(filho)
    for a in arvores: percorre(a)
    return sorted(achadas)


def subexpressoes(no):
    """Subexpressões em ordem de cálculo (filhos antes dos pais), sem repetir."""
    lista = []
    def percorre(n):
        if n[0] == "var": return
        for filho in n[1:]: percorre(filho)
        if n not in lista: lista.append(n)
    percorre(no)
    return lista


def valoracoes(vars_):
    """Todas as combinações, começando por V (padrão de tabela-verdade)."""
    for combo in itertools.product([True, False], repeat=len(vars_)):
        yield dict(zip(vars_, combo))


def VF(b):
    return "V" if b else "F"


# ----------------------------------------------------------------------
# 4. TAREFA 1: tabela-verdade e classificação
# ----------------------------------------------------------------------
def tabela_verdade(texto, imprimir=True):
    arvore = parse(texto)
    vs = variaveis(arvore)
    colunas = [(v, ("var", v)) for v in vs] + \
              [(texto_no(s), s) for s in subexpressoes(arvore)]
    linhas = []
    for val in valoracoes(vs):
        linhas.append([avaliar(n, val) for _, n in colunas])
    if imprimir:
        larg = [max(len(nome), 1) for nome, _ in colunas]
        print(" | ".join(n.center(w) for (n, _), w in zip(colunas, larg)))
        print("-+-".join("-" * w for w in larg))
        for l in linhas:
            print(" | ".join(VF(x).center(w) for x, w in zip(l, larg)))
    return [l[-1] for l in linhas]          # coluna final (resultado)


def classificar(texto):
    res = tabela_verdade(texto, imprimir=False)
    if all(res):     return "tautologia"
    if not any(res): return "contradição"
    return "contingência"


# ----------------------------------------------------------------------
# 5. TAREFA 2: equivalência e validade de argumentos
# ----------------------------------------------------------------------
def equivalentes(t1, t2):
    a, b = parse(t1), parse(t2)
    vs = variaveis(a, b)
    for val in valoracoes(vs):
        if avaliar(a, val) != avaliar(b, val):
            return False, val           # val = valoração que diferencia
    return True, None


def argumento_valido(premissas, conclusao):
    ps = [parse(p) for p in premissas]
    c = parse(conclusao)
    vs = variaveis(*ps, c)
    for val in valoracoes(vs):
        if all(avaliar(p, val) for p in ps) and not avaliar(c, val):
            return False, val           # contraexemplo
    return True, None


# ----------------------------------------------------------------------
# 6. TAREFA 3: resolução de problemas
# ----------------------------------------------------------------------
def resolver(sentencas, exatamente=None):
    """
    Lista as valorações que satisfazem as condições.
    - exatamente=None : todas as sentenças devem ser verdadeiras.
    - exatamente=k    : exatamente k sentenças verdadeiras
                        ("apenas um mentiu" => k = n-1;
                         "exatamente uma é verdadeira" => k = 1).
    """
    arvs = [parse(s) for s in sentencas]
    vs = variaveis(*arvs)
    sol = []
    for val in valoracoes(vs):
        verdadeiras = sum(avaliar(a, val) for a in arvs)
        ok = (verdadeiras == len(arvs)) if exatamente is None \
            else (verdadeiras == exatamente)
        if ok:
            sol.append(val)
    return vs, sol


def apenas_um_mentiu(sentencas):
    return resolver(sentencas, exatamente=len(sentencas) - 1)


def exatamente_uma_verdadeira(sentencas):
    return resolver(sentencas, exatamente=1)


# ----------------------------------------------------------------------
# 7. BÔNUS: soma de produtos e portas lógicas
# ----------------------------------------------------------------------
def soma_de_produtos(texto):
    """
    Bônus: soma de produtos (forma normal disjuntiva) a partir das linhas
    da tabela-verdade em que a sentença é VERDADEIRA (mintermos).
    """
    arvore = parse(texto)
    vs = variaveis(arvore)
    mint = [" . ".join(v if val[v] else f"~{v}" for v in vs)
            for val in valoracoes(vs) if avaliar(arvore, val)]
    if not mint:
        return "0 (contradição)"
    return " + ".join(f"({m})" if len(vs) > 1 else m for m in mint)


def produto_de_somas(texto):
    """
    Bônus: produto de somas (forma normal conjuntiva) a partir das linhas
    da tabela-verdade em que a sentença é FALSA (maxtermos).
    Em cada linha falsa, a variável V entra negada e a F entra normal.
    """
    arvore = parse(texto)
    vs = variaveis(arvore)
    maxt = [" + ".join(f"~{v}" if val[v] else v for v in vs)
            for val in valoracoes(vs) if not avaliar(arvore, val)]
    if not maxt:
        return "1 (tautologia)"
    return " . ".join(f"({m})" if len(vs) > 1 else m for m in maxt)


TRACO = 'stroke="#222" stroke-width="2" fill="none"'


def _porta(tipo, x, y0, h):
    """Desenha uma porta AND ou OR (largura 50) e devolve o SVG dela."""
    if tipo == "and":
        d = (f"M {x} {y0} L {x + 25} {y0} A 25 {h / 2} 0 0 1 {x + 25} {y0 + h} "
             f"L {x} {y0 + h} Z")
    else:
        d = (f"M {x} {y0} Q {x + 14} {y0 + h / 2} {x} {y0 + h} "
             f"Q {x + 35} {y0 + h} {x + 50} {y0 + h / 2} "
             f"Q {x + 35} {y0} {x} {y0} Z")
    rotulo = tipo.upper()
    return (f'<path d="{d}" {TRACO}/>'
            f'<text x="{x + 10}" y="{y0 + h / 2 + 4}" fill="#222" '
            f'font-size="11">{rotulo}</text>')


def circuito_svg(texto, forma="sop"):
    """
    Bônus: desenha o circuito lógico e devolve o desenho em SVG.
      forma="sop": soma de produtos  -> portas AND (1º nível) e OR (saída)
      forma="pos": produto de somas  -> portas OR  (1º nível) e AND (saída)
    """
    arvore = parse(texto)
    vs = variaveis(arvore)
    sop = (forma == "sop")
    # SOP usa as linhas V; POS usa as linhas F
    linhas = [val for val in valoracoes(vs) if avaliar(arvore, val) == sop]
    n, m = len(vs), len(linhas)
    nivel1, final = ("and", "or") if sop else ("or", "and")
    if m == 0:
        msg = ("Contradição: saída sempre 0 (sem portas)" if sop
               else "Tautologia: saída sempre 1 (sem portas)")
        return ('<svg xmlns="http://www.w3.org/2000/svg" width="340" height="60">'
                '<rect width="100%" height="100%" fill="white"/>'
                f'<text x="10" y="35" font-size="16" fill="#222">{msg}</text></svg>')
    xv = {v: 60 + i * 60 for i, v in enumerate(vs)}      # barramento da variável
    xn = {v: xv[v] + 30 for v in vs}                       # barramento negado
    topo, linha_h = 110, 20 * n + 40
    gx = 60 + n * 60 + 40
    base = topo + m * linha_h
    larg = gx + 90 + m * 6 + 50 + 90
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{larg}" '
         f'height="{base + 20}" font-family="sans-serif" font-size="13">',
         '<rect width="100%" height="100%" fill="white"/>']
    # entradas, inversores e barramentos
    for v in vs:
        s.append(f'<text x="{xv[v] - 4}" y="22" fill="#222" font-weight="bold">{v}</text>')
        s.append(f'<line x1="{xv[v]}" y1="30" x2="{xv[v]}" y2="{base}" {TRACO}/>')
        s.append(f'<polyline points="{xv[v]},42 {xn[v]},42 {xn[v]},48" {TRACO}/>')
        s.append(f'<polygon points="{xn[v] - 8},48 {xn[v] + 8},48 {xn[v]},64" {TRACO}/>')
        s.append(f'<circle cx="{xn[v]}" cy="68" r="4" {TRACO}/>')
        s.append(f'<line x1="{xn[v]}" y1="72" x2="{xn[v]}" y2="{base}" {TRACO}/>')
        s.append(f'<circle cx="{xv[v]}" cy="42" r="3" fill="#222"/>')
    saidas = []
    for j, val in enumerate(linhas):
        y0 = topo + j * linha_h + 10
        h = linha_h - 20
        passo = h / (n + 1)
        for i, v in enumerate(vs):
            yi = y0 + passo * (i + 1)
            # SOP: V usa a variável, F usa a negada. POS: o contrário.
            usa_normal = val[v] if sop else (not val[v])
            xb = xv[v] if usa_normal else xn[v]
            s.append(f'<line x1="{xb}" y1="{yi}" x2="{gx}" y2="{yi}" {TRACO}/>')
            s.append(f'<circle cx="{xb}" cy="{yi}" r="3" fill="#222"/>')
        if n > 1:
            s.append(_porta(nivel1, gx, y0, h))
        saidas.append((gx + (50 if n > 1 else 0), y0 + h / 2))
    # porta final (OR na soma de produtos, AND no produto de somas)
    if m > 1:
        xo = gx + 90 + m * 6
        ho = 22 * m + 10
        yo = topo + (m * linha_h) / 2 - ho / 2
        for k, (xs, ys) in enumerate(saidas):
            yin = yo + 12 + 22 * k
            xc = gx + 65 + k * 6
            s.append(f'<polyline points="{xs},{ys} {xc},{ys} {xc},{yin} {xo + 6},{yin}" {TRACO}/>')
        s.append(_porta(final, xo, yo, ho))
        xf, yf = xo + 50, yo + ho / 2
    else:
        xf, yf = saidas[0]
    s.append(f'<line x1="{xf}" y1="{yf}" x2="{xf + 40}" y2="{yf}" {TRACO}/>')
    s.append(f'<text x="{xf + 46}" y="{yf + 4}" fill="#222" font-weight="bold">S</text>')
    s.append('</svg>')
    return "".join(s)


# ----------------------------------------------------------------------
# 8. TESTES MÍNIMOS DA SEÇÃO 6
# ----------------------------------------------------------------------
def executar_testes():
    testes = [
        ("P ou ~P é tautologia",            classificar("P ou ~P") == "tautologia"),
        ("P e ~P é contradição",            classificar("P e ~P") == "contradição"),
        ("P->Q equiv. ~P ou Q",             equivalentes("P -> Q", "~P ou Q")[0]),
        ("P->Q equiv. ~Q->~P",              equivalentes("P -> Q", "~Q -> ~P")[0]),
        ("~(P e Q) equiv. ~P ou ~Q",        equivalentes("~(P e Q)", "~P ou ~Q")[0]),
        ("P->Q, P |- Q é válido",           argumento_valido(["P -> Q", "P"], "Q")[0]),
        ("P->Q, Q |- P é inválido",         not argumento_valido(["P -> Q", "Q"], "P")[0]),
        ("Precedência: P ou Q e R = P ou (Q e R)",
                                            equivalentes("P ou Q e R", "P ou (Q e R)")[0]),
        ("Condicional só falsa em V->F",    [avaliar(parse("P -> Q"), {"P": p, "Q": q})
                                             for p in (True, False) for q in (True, False)]
                                            == [True, False, True, True]),
    ]
    testes.append(("Produto de somas de P xor Q",
                   produto_de_somas("P xor Q") == "(~P + ~Q) . (P + Q)"))
    testes.append(("SOP e POS equivalentes a P -> Q", all(
        equivalentes("P -> Q", x)[0] for x in
        ["~P ou Q", "(~P e ~Q) ou (~P e Q) ou (P e Q)"])))
    for nome, ok in testes:
        print(("[OK]   " if ok else "[FALHA]"), nome)
    erros = ["(P e", "P Q", "P e e Q", "", "P -> ", "X1", "P )"]
    for e in erros:
        try:
            parse(e)
            print("[FALHA] deveria dar erro:", repr(e))
        except ErroSintaxe:
            print("[OK]    erro detectado em", repr(e))


# ----------------------------------------------------------------------
# 9. INTERFACE DE TEXTO (menu)
# ----------------------------------------------------------------------
def mostrar_val(val):
    return ", ".join(f"{k}={VF(v)}" for k, v in val.items())


def ler_expr(msg):
    """Pede uma expressão e repete até ser válida."""
    while True:
        t = input(msg).strip()
        try:
            parse(t)
            return t
        except ErroSintaxe as e:
            print("  Expressão inválida:", e)


def ler_lista(msg):
    print(msg, "(linha vazia para terminar)")
    lista = []
    while True:
        t = input(f"  {len(lista) + 1}> ").strip()
        if not t:
            return lista
        try:
            parse(t)
            lista.append(t)
        except ErroSintaxe as e:
            print("  Expressão inválida:", e)


def menu():
    while True:
        print("\n=== VERIFICADOR LÓGICO ===")
        print("1 - Tabela-verdade e classificação")
        print("2 - Equivalência de duas sentenças")
        print("3 - Validade de argumento (premissas e conclusão)")
        print("4 - Resolver problema (lista de condições)")
        print("5 - Soma de produtos, produto de somas e circuitos (bônus)")
        print("6 - Rodar testes mínimos")
        print("0 - Sair")
        op = input("Opção: ").strip()
        try:
            if op == "1":
                t = ler_expr("Sentença: ")
                tabela_verdade(t)
                print("Classificação:", classificar(t))
            elif op == "2":
                a, b = ler_expr("Sentença 1: "), ler_expr("Sentença 2: ")
                ok, val = equivalentes(a, b)
                print("São logicamente equivalentes." if ok else
                      f"NÃO são equivalentes. Diferem em: {mostrar_val(val)}")
            elif op == "3":
                ps = ler_lista("Premissas")
                c = ler_expr("Conclusão: ")
                ok, val = argumento_valido(ps, c)
                if ok:
                    print("Argumento VÁLIDO.")
                else:
                    print("Argumento INVÁLIDO. Contraexemplo (premissas V, "
                          f"conclusão F): {mostrar_val(val)}")
            elif op == "4":
                ss = ler_lista("Condições do problema")
                print("Modo: 1) todas verdadeiras  2) apenas um mentiu  "
                      "3) exatamente uma verdadeira  4) exatamente k verdadeiras")
                m = input("Modo [1]: ").strip() or "1"
                if m == "2":   vs, sol = apenas_um_mentiu(ss)
                elif m == "3": vs, sol = exatamente_uma_verdadeira(ss)
                elif m == "4": vs, sol = resolver(ss, int(input("k = ")))
                else:          vs, sol = resolver(ss)
                print(f"{len(sol)} valoração(ões) satisfazem:")
                for s in sol:
                    print("  ", mostrar_val(s))
                if len(sol) == 1:
                    print("=> Solução única do problema.")
                elif not sol:
                    print("=> Nenhuma valoração: condições inconsistentes.")
            elif op == "5":
                t = ler_expr("Sentença: ")
                print("Soma de produtos:", soma_de_produtos(t))
                print("Produto de somas:", produto_de_somas(t))
                for forma in ("sop", "pos"):
                    with open(f"circuito_{forma}.svg", "w", encoding="utf-8") as f:
                        f.write(circuito_svg(t, forma))
                print("Circuitos salvos em circuito_sop.svg e circuito_pos.svg "
                      "(abra no navegador ou no VS Code).")
            elif op == "6":
                executar_testes()
            elif op == "0":
                break
            else:
                print("Opção inválida.")
        except ValueError:
            print("Valor inválido.")


if __name__ == "__main__":
    menu()
