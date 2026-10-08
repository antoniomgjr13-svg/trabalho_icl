"""
Interface web do Verificador Lógico (bônus).
Instalar:  pip install streamlit
Rodar:     streamlit run app_streamlit.py
Precisa estar na mesma pasta que verificador_logico.py.
"""
import streamlit as st
import streamlit.components.v1 as components
import verificador_logico as v

st.set_page_config(page_title="Verificador Lógico", layout="wide")
st.title("Verificador Lógico")
st.caption("Operadores: ~ / não, e / ^, ou / v, xor, ->, <->  |  "
           "Proposições: uma letra maiúscula (P, Q, R...)")


def linhas(texto):
    """Quebra um campo de texto em sentenças (uma por linha)."""
    return [l.strip() for l in texto.splitlines() if l.strip()]


def mostrar_val(val):
    return ", ".join(f"{k}={v.VF(x)}" for k, x in val.items())


aba1, aba2, aba3, aba4, aba5 = st.tabs(
    ["Tabela-verdade", "Equivalência", "Argumento", "Resolver problema",
     "Soma de produtos / Produto de somas"])

# ---------------- Tarefa 1 ----------------
with aba1:
    expr = st.text_input("Sentença", "(P e ~Q) -> R", key="t1")
    if st.button("Gerar tabela", key="b1"):
        try:
            arv = v.parse(expr)
            vs = v.variaveis(arv)
            cols = [(x, ("var", x)) for x in vs] + \
                   [(v.texto_no(s), s) for s in v.subexpressoes(arv)]
            tabela = [{nome: v.VF(v.avaliar(no, val)) for nome, no in cols}
                      for val in v.valoracoes(vs)]
            st.dataframe(tabela, use_container_width=True)
            st.success(f"Classificação: {v.classificar(expr)}")
        except v.ErroSintaxe as e:
            st.error(f"Expressão inválida: {e}")

# ---------------- Tarefa 2a ----------------
with aba2:
    a = st.text_input("Sentença 1", "P -> Q", key="t2a")
    b = st.text_input("Sentença 2", "~P ou Q", key="t2b")
    if st.button("Verificar equivalência", key="b2"):
        try:
            ok, val = v.equivalentes(a, b)
            if ok:
                st.success("São logicamente equivalentes.")
            else:
                st.error(f"Não são equivalentes. Diferem em: {mostrar_val(val)}")
        except v.ErroSintaxe as e:
            st.error(f"Expressão inválida: {e}")

# ---------------- Tarefa 2b ----------------
with aba3:
    prem = st.text_area("Premissas (uma por linha)", "P -> Q\nQ", key="t3p")
    conc = st.text_input("Conclusão", "P", key="t3c")
    if st.button("Verificar argumento", key="b3"):
        try:
            ok, val = v.argumento_valido(linhas(prem), conc)
            if ok:
                st.success("Argumento VÁLIDO.")
            else:
                st.error("Argumento INVÁLIDO. Contraexemplo (premissas V, "
                         f"conclusão F): {mostrar_val(val)}")
        except v.ErroSintaxe as e:
            st.error(f"Expressão inválida: {e}")

# ---------------- Tarefa 3 ----------------
with aba4:
    conds = st.text_area("Condições (uma por linha)", "A -> B\nA", key="t4")
    modo = st.radio("Restrição", ["Todas verdadeiras", "Apenas um mentiu",
                                  "Exatamente uma verdadeira",
                                  "Exatamente k verdadeiras"], key="modo")
    k = st.number_input("k", min_value=0, value=1, step=1) \
        if modo == "Exatamente k verdadeiras" else None
    if st.button("Resolver", key="b4"):
        try:
            ss = linhas(conds)
            if modo == "Apenas um mentiu":
                vs, sol = v.apenas_um_mentiu(ss)
            elif modo == "Exatamente uma verdadeira":
                vs, sol = v.exatamente_uma_verdadeira(ss)
            elif k is not None:
                vs, sol = v.resolver(ss, int(k))
            else:
                vs, sol = v.resolver(ss)
            if not sol:
                st.error("Nenhuma valoração satisfaz: condições inconsistentes.")
            else:
                st.dataframe([{x: v.VF(val[x]) for x in vs} for val in sol])
                if len(sol) == 1:
                    st.success("Solução única do problema.")
                else:
                    st.info(f"{len(sol)} valorações possíveis.")
        except v.ErroSintaxe as e:
            st.error(f"Expressão inválida: {e}")

# ---------------- Bônus ----------------
with aba5:
    e5 = st.text_input("Sentença", "P xor Q", key="t5")
    if st.button("Gerar formas normais e circuitos", key="b5"):
        try:
            st.subheader("Soma de produtos")
            st.code(v.soma_de_produtos(e5))
            components.html(v.circuito_svg(e5, "sop"), height=420, scrolling=True)
            st.subheader("Produto de somas")
            st.code(v.produto_de_somas(e5))
            components.html(v.circuito_svg(e5, "pos"), height=420, scrolling=True)
        except v.ErroSintaxe as e:
            st.error(f"Expressão inválida: {e}")
