import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Dashboard Inteligente de Monitoramento Logístico",
    page_icon="🚚",
    layout="wide"
)

# ============ CARREGAMENTO DE DADOS ============
@st.cache_data
def load_data():
    df = pd.read_csv("dados.csv")
    df["Data"] = pd.to_datetime(df["Data"])
    df["Prazo Previsto"] = pd.to_datetime(df["Prazo Previsto"])
    df["Data Real"] = pd.to_datetime(df["Data Real"])
    return df

df = load_data()

# ============ SIDEBAR - FILTROS ============
st.sidebar.title("🔎 Filtros")

regioes = st.sidebar.multiselect(
    "Região",
    options=sorted(df["Região"].unique()),
    default=sorted(df["Região"].unique())
)

transportadoras = st.sidebar.multiselect(
    "Transportadora",
    options=sorted(df["Transportadora"].unique()),
    default=sorted(df["Transportadora"].unique())
)

status_opcoes = st.sidebar.radio(
    "Status da Entrega",
    options=["Todos", "No Prazo", "Atrasado"],
    index=0
)

data_min = df["Data"].min().date()
data_max = df["Data"].max().date()
periodo = st.sidebar.date_input(
    "Período",
    value=(data_min, data_max),
    min_value=data_min,
    max_value=data_max
)

# ============ APLICAÇÃO DOS FILTROS ============
df_f = df[
    (df["Região"].isin(regioes)) &
    (df["Transportadora"].isin(transportadoras))
]

if status_opcoes != "Todos":
    df_f = df_f[df_f["Status"] == status_opcoes]

if isinstance(periodo, tuple) and len(periodo) == 2:
    inicio, fim = periodo
    df_f = df_f[(df_f["Data"].dt.date >= inicio) & (df_f["Data"].dt.date <= fim)]

# ============ FUNÇÃO DE ALERTA (SEMÁFORO) ============
def status_cor(pct):
    if pct <= 5:
        return "🟢"
    elif pct <= 15:
        return "🟡"
    else:
        return "🔴"

# ============ CABEÇALHO / KPIs ============
st.title("🚚 Dashboard Inteligente de Monitoramento Logístico")
st.markdown("Monitoramento de atrasos em entregas por região e transportadora")

total_entregas = len(df_f)
total_atrasos = len(df_f[df_f["Status"] == "Atrasado"])
pct_atraso = (total_atrasos / total_entregas * 100) if total_entregas > 0 else 0

if total_entregas > 0:
    regiao_critica_serie = df_f.groupby("Região").apply(
        lambda x: (x["Status"] == "Atrasado").mean() * 100
    )
    regiao_critica = regiao_critica_serie.idxmax() if not regiao_critica_serie.empty else "-"

    transp_critica_serie = df_f.groupby("Transportadora").apply(
        lambda x: (x["Status"] == "Atrasado").mean() * 100
    )
    transp_critica = transp_critica_serie.idxmax() if not transp_critica_serie.empty else "-"
else:
    regiao_critica = "-"
    transp_critica = "-"

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total de Entregas", f"{total_entregas}")
col2.metric("Total de Atrasos", f"{total_atrasos}")
col3.metric("% de Atraso", f"{pct_atraso:.1f}% {status_cor(pct_atraso)}")
col4.metric("Região Mais Crítica", regiao_critica)
col5.metric("Transportadora Mais Crítica", transp_critica)

# Alerta geral
if pct_atraso > 15:
    st.error(f"🔴 Atenção: o percentual geral de atraso está em {pct_atraso:.1f}%, acima do limite crítico (15%).")
elif pct_atraso > 5:
    st.warning(f"🟡 Alerta: o percentual geral de atraso está em {pct_atraso:.1f}%, em zona de atenção.")
else:
    st.success(f"🟢 Operação dentro da meta: percentual de atraso em {pct_atraso:.1f}%.")

st.markdown("---")

# ============ GRÁFICOS ============

# 1. Comparação entre transportadoras
st.subheader("1️⃣ Comparação entre Transportadoras")
if total_entregas > 0:
    transp_stats = df_f.groupby("Transportadora").apply(
        lambda x: pd.Series({
            "Total": len(x),
            "Atrasos": (x["Status"] == "Atrasado").sum(),
            "% Atraso": (x["Status"] == "Atrasado").mean() * 100
        })
    ).reset_index().sort_values("% Atraso", ascending=False)

    transp_stats["Cor"] = transp_stats["% Atraso"].apply(
        lambda p: "Crítico (>15%)" if p > 15 else ("Atenção (5-15%)" if p > 5 else "OK (<5%)")
    )

    fig1 = px.bar(
        transp_stats,
        x="% Atraso",
        y="Transportadora",
        orientation="h",
        color="Cor",
        color_discrete_map={
            "OK (<5%)": "#2ecc71",
            "Atenção (5-15%)": "#f1c40f",
            "Crítico (>15%)": "#e74c3c"
        },
        text="% Atraso",
        title="Percentual de Atraso por Transportadora"
    )
    fig1.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig1.update_layout(yaxis=dict(categoryorder="total ascending"))
    st.plotly_chart(fig1, use_container_width=True)
else:
    st.info("Nenhum dado disponível para os filtros selecionados.")

# 2. Análise por região
st.subheader("2️⃣ Análise por Região")
if total_entregas > 0:
    regiao_stats = df_f.groupby("Região").apply(
        lambda x: pd.Series({
            "Total": len(x),
            "Atrasos": (x["Status"] == "Atrasado").sum(),
            "% Atraso": (x["Status"] == "Atrasado").mean() * 100
        })
    ).reset_index().sort_values("% Atraso", ascending=False)

    fig2 = px.bar(
        regiao_stats,
        x="Região",
        y="% Atraso",
        color="% Atraso",
        color_continuous_scale=["#2ecc71", "#f1c40f", "#e74c3c"],
        text="% Atraso",
        title="Percentual de Atraso por Região"
    )
    fig2.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("Nenhum dado disponível para os filtros selecionados.")

# 3. Entregas atrasadas (tabela)
st.subheader("3️⃣ Entregas Atrasadas (Detalhamento)")
df_atrasadas = df_f[df_f["Status"] == "Atrasado"].sort_values("Dias de Atraso", ascending=False)
if not df_atrasadas.empty:
    st.dataframe(
        df_atrasadas[["ID Entrega", "Data", "Região", "Transportadora",
                       "Prazo Previsto", "Data Real", "Dias de Atraso", "Status"]],
        use_container_width=True,
        hide_index=True
    )
else:
    st.success("Nenhuma entrega atrasada para os filtros selecionados. 🎉")

# 4. Ranking dos problemas
st.subheader("4️⃣ Ranking dos Problemas")
rcol1, rcol2, rcol3 = st.columns(3)

with rcol1:
    st.markdown("🚨 Top 5 Maiores Atrasos (dias)")
    top_atrasos = df_f.sort_values("Dias de Atraso", ascending=False).head(5)
    st.dataframe(
        top_atrasos[["ID Entrega", "Transportadora", "Região", "Dias de Atraso"]],
        hide_index=True, use_container_width=True
    )

with rcol2:
    st.markdown("🌎 Regiões Mais Problemáticas")
    if total_entregas > 0:
        rank_regiao = regiao_stats[["Região", "% Atraso"]].copy()
        rank_regiao["Alerta"] = rank_regiao["% Atraso"].apply(status_cor)
        rank_regiao["% Atraso"] = rank_regiao["% Atraso"].round(1)
        st.dataframe(rank_regiao, hide_index=True, use_container_width=True)

with rcol3:
    st.markdown("🚛 Transportadoras Críticas")
    if total_entregas > 0:
        rank_transp = transp_stats[["Transportadora", "% Atraso"]].copy()
        rank_transp["Alerta"] = rank_transp["% Atraso"].apply(status_cor)
        rank_transp["% Atraso"] = rank_transp["% Atraso"].round(1)
        st.dataframe(rank_transp, hide_index=True, use_container_width=True)

# 5. Tendência temporal
st.subheader("5️⃣ Tendência Temporal de Atrasos")
if total_entregas > 0:
    df_f["Mês"] = df_f["Data"].dt.to_period("M").astype(str)
    tendencia = df_f.groupby("Mês").apply(
        lambda x: pd.Series({
            "Total": len(x),
            "Atrasos": (x["Status"] == "Atrasado").sum(),
            "% Atraso": (x["Status"] == "Atrasado").mean() * 100
        })
    ).reset_index()

    fig5 = px.line(
        tendencia,
        x="Mês",
        y="% Atraso",
        markers=True,
        title="Evolução Mensal do Percentual de Atraso"
    )
    fig5.add_hline(y=5, line_dash="dash", line_color="green", annotation_text="Limite 🟢/🟡 (5%)")
    fig5.add_hline(y=15, line_dash="dash", line_color="red", annotation_text="Limite 🟡/🔴 (15%)")
    st.plotly_chart(fig5, use_container_width=True)
else:
    st.info("Nenhum dado disponível para os filtros selecionados.")

