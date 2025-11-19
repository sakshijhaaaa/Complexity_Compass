import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# --------------------------------
# Mathematical Backend
# --------------------------------
n = sp.Symbol('n', real=True, positive=True)

allowed_funcs = {
    'log': sp.log,
    'ln': sp.log,
    'exp': sp.exp,
    'sqrt': sp.sqrt
}

def parse_function(func_str):
    try:
        f = sp.sympify(func_str, locals=allowed_funcs)
        return f
    except:
        return None

# ------------------- Dominant Term & Asymptotic Analysis ----------------
def dominant_term(f):
    f = sp.expand(sp.simplify(f))
    if not isinstance(f, sp.Add):
        return sp.simplify(f)

    terms = list(f.as_ordered_terms())
    dom = terms[0]

    for t in terms[1:]:
        try:
            L = sp.limit(sp.simplify(t / dom), n, sp.oo)
            if L.is_infinite:
                dom = t
        except:
            try:
                n_val = 10**6
                t_val = float(t.subs(n, n_val).evalf())
                dom_val = float(dom.subs(n, n_val).evalf())
                if t_val > dom_val:
                    dom = t
            except:
                pass

    return sp.simplify(dom)

def check_asymptotic_definitions(f, g):
    try:
        ratio = sp.simplify(f / g)
        L = sp.limit(ratio, n, sp.oo)
        if L == 0:
            return {'O': True, 'Omega': False, 'Theta': False,
                    'c_O': str(L), 'c_Omega': str(L), 'n0': 'symbolic'}
        elif getattr(L, "is_infinite", False):
            return {'O': False, 'Omega': True, 'Theta': False,
                    'c_O': str(L), 'c_Omega': str(L), 'n0': 'symbolic'}
        else:
            return {'O': True, 'Omega': True, 'Theta': True,
                    'c_O': str(L), 'c_Omega': str(L), 'n0': 'symbolic'}
    except:
        return {'O': False, 'Omega': False, 'Theta': False,
                'c_O': "undefined", 'c_Omega': "undefined", 'n0': "undefined"}


# ------------------- Plotting ----------------
def plot_bounds(f, g, c_O, c_Omega):
    n_vals = np.linspace(1, 80, 400)
    f_lambda = sp.lambdify(n, f, "numpy")
    g_lambda = sp.lambdify(n, g, "numpy")
    f_vals = f_lambda(n_vals)
    g_vals = g_lambda(n_vals)

    sns.set_style("whitegrid")
    fig, ax = plt.subplots(figsize=(10, 6))

    # GREEN main function line
    ax.plot(n_vals, f_vals, label=f"f(n) = {f}", linewidth=3, color="#2e8b57")

    try:
        cO = float(c_O)
        cOm = float(c_Omega)
    except:
        cO = cOm = 1

    ax.plot(n_vals, cO * g_vals, "--", label=f"{cO} * g(n) (O)", linewidth=2.5, color="#ff7f0e")
    ax.plot(n_vals, cOm * g_vals, "--", label=f"{cOm} * g(n) (Ω)", linewidth=2.5, color="#2ca02c")

    ax.set_title("Asymptotic Bounds Visualization", fontsize=18, fontweight="bold")
    ax.set_xlabel("n", fontsize=14, fontweight="bold")
    ax.set_ylabel("Function Value", fontsize=14, fontweight="bold")
    ax.tick_params(axis='both', labelsize=12)
    ax.legend(fontsize=13)
    st.pyplot(fig)

# ------------------- Streamlit GUI ----------------
st.set_page_config(page_title="Complexity Compass", layout="wide")

# MAIN TITLE → Green
st.markdown("<h1 style='text-align: center; color: #2e8b57; font-size: 40px;'>📈 Complexity Compass</h1>", unsafe_allow_html=True)

# SUBTITLE → Dark Green
st.markdown("<h4 style='text-align: center; color: #1b5e20;'>Visualize Big O, Ω, and Θ with interactive graphs</h4>", unsafe_allow_html=True)

st.write("---")

# Sidebar for Input
st.sidebar.header("Function Input & Analysis")
func_str = st.sidebar.text_input("Enter f(n):", placeholder="n**2 + 3*n*log(n)")

if st.sidebar.button("Analyze Function"):
    f = parse_function(func_str)
    if f is None:
        st.sidebar.warning("⚠️ Invalid function syntax. Use allowed symbols: n, +, -, *, /, ^, log, ln, sqrt, exp")
    else:
        g = dominant_term(f)
        results = check_asymptotic_definitions(f, g)
        st.session_state["f"] = f
        st.session_state["g"] = g
        st.session_state["results"] = results
        st.sidebar.success("✅ Function analyzed successfully!")

# Main Tabs
tab1, tab2 = st.tabs(["Analysis Result", "Graph Visualization"])

with tab1:
    if "f" in st.session_state:

        # f(n) heading → green
        st.markdown(f"<h3 style='color:#2e8b57;'>f(n) = {st.session_state['f']}</h3>", unsafe_allow_html=True)

        st.markdown(f"<h4 style='color:#ff7f0e;'>Dominant term g(n) = {st.session_state['g']}</h4>", unsafe_allow_html=True)

        res = st.session_state["results"]

        colO, colOm, colT = st.columns(3)
        colO.metric("Big-O", str(res['O']))
        colOm.metric("Big-Omega", str(res['Omega']))
        colT.metric("Big-Theta", str(res['Theta']))

    else:
        st.info("Analyze a function using the sidebar to see results.")

with tab2:
    if "f" in st.session_state:
        if st.button("Show Graph"):
            plot_bounds(st.session_state["f"], st.session_state["g"],
                        st.session_state["results"]["c_O"], st.session_state["results"]["c_Omega"])
    else:
        st.info("Analyze a function first to see the graph.")
