import streamlit as st
from google.cloud import firestore
from google.oauth2 import service_account
from datetime import datetime

# --- 1. Configuração da Página ---
st.set_page_config(
    page_title="Contrato Didático da Turma",
    page_icon="📜",
    layout="centered"
)

# --- Conexão Direta e Estável com o Firestore ---


@st.cache_resource
def init_firestore():
    if "firebase" not in st.secrets:
        st.error("⚠️ Configurações do Firestore não encontradas no `st.secrets`!")
        st.stop()

    key_dict = dict(st.secrets["firebase"])

    # Corrige a chave privada caso venha sanitizada do arquivo TOML
    if "private_key" in key_dict and isinstance(key_dict["private_key"], str):
        key_dict["private_key"] = key_dict["private_key"].replace("\\n", "\n")

    # Autenticação nativa com Service Account
    credentials = service_account.Credentials.from_service_account_info(
        key_dict)
    return firestore.Client(credentials=credentials, project=key_dict.get("project_id"))


# Inicializa o cliente do banco de dados
try:
    db = init_firestore()
except Exception as e:
    st.error(f"Erro ao conectar com o Firestore: {e}")
    st.stop()

st.title("📜 Contrato Didático e Combinados da Turma")
st.caption("Monte o acordo coletivo, defina os responsáveis pelas regras e gere o contrato para impressão!")

# --- Helper Function: Gerador de HTML para Impressão ---


def gerar_html_contrato(turma, professor, regras):
    linhas_tabela = ""
    for idx, item in enumerate(regras, 1):
        linhas_tabela += f"""<tr>
            <td style="text-align: center; font-weight: bold; padding: 8px; border: 1px solid #ddd;">{idx}</td>
            <td style="padding: 8px; border: 1px solid #ddd;">{item['texto']}</td>
            <td style="padding: 8px; border: 1px solid #ddd; font-weight: 500;">{item['responsavel']}</td>
        </tr>"""

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; padding: 20px; color: #333; }}
            .header {{ text-align: center; border-bottom: 2px solid #1e3a8a; padding-bottom: 10px; margin-bottom: 20px; }}
            .header h1 {{ color: #1e3a8a; margin: 0; font-size: 20pt; }}
            .info {{ background: #f3f4f6; padding: 10px 15px; border-left: 4px solid #2563eb; margin-bottom: 20px; }}
            table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
            th {{ background: #1e3a8a; color: white; padding: 8px; text-align: left; }}
            .pacto {{ background: #eff6ff; padding: 12px; border: 1px solid #bfdbfe; font-style: italic; text-align: center; margin-bottom: 30px; }}
            .sig-container {{ display: flex; justify-content: space-between; margin-top: 50px; }}
            .sig-box {{ width: 40%; text-align: center; border-top: 1px solid #333; padding-top: 5px; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>CONTRATO DIDÁTICO DE SALA DE AULA</h1>
            <p>Compromisso de Convivência e Aprendizado Coletivo</p>
        </div>
        <div class="info">
            <p style="margin: 3px 0;"><strong>Turma:</strong> {turma}</p>
            <p style="margin: 3px 0;"><strong>Professor(a):</strong> {professor}</p>
        </div>
        <table>
            <thead>
                <tr>
                    <th style="width: 8%; text-align: center;">#</th>
                    <th style="width: 62%;">Regra / Combinado</th>
                    <th style="width: 30%;">Responsável</th>
                </tr>
            </thead>
            <tbody>{linhas_tabela}</tbody>
        </table>
        <div class="pacto">
            "Declaramos que participamos ativamente da construção deste contrato didático. Toda a turma se compromete a respeitar os acordos firmados para garantir um ambiente produtivo, seguro e harmonioso para todos."
        </div>
        <div class="sig-container">
            <div class="sig-box">Representante da Turma</div>
            <div class="sig-box">Prof. {professor}</div>
        </div>
    </body>
    </html>
    """


# --- 2. Estrutura de Abas ---
tab_criar, tab_salvos = st.tabs(["📝 Criar Contrato", "📂 Contratos Salvos"])

# ==========================================
# ABA 1: CRIAR CONTRATO
# ==========================================
with tab_criar:
    REGRAS_PADRAO = [
        {"id": 1, "texto": "Respeitar os colegas e professores",
            "responsavel": "Toda a Turma", "votos": 0, "aprovada": True},
        {"id": 2, "texto": "Não interromper quando alguém estiver falando",
            "responsavel": "Toda a Turma", "votos": 0, "aprovada": True},
        {"id": 3, "texto": "Manter o tom de voz adequado (não gritar)",
         "responsavel": "Toda a Turma", "votos": 0, "aprovada": True},
        {"id": 4, "texto": "Usar obrigatoriamente os EPIs e equipamentos de segurança",
            "responsavel": "Toda a Turma", "votos": 0, "aprovada": True},
        {"id": 5, "texto": "Zelar pela organização e limpeza do espaço de aula",
            "responsavel": "Toda a Turma", "votos": 0, "aprovada": True},
        {"id": 6, "texto": "Utilizar computadores e celulares apenas para fins pedagógicos",
            "responsavel": "Toda a Turma", "votos": 0, "aprovada": True},
    ]

    if "regras" not in st.session_state:
        st.session_state.regras = [dict(r) for r in REGRAS_PADRAO]

    # --- Seleção da Turma ---
    st.subheader("🏫 Identificação da Turma")
    col_ano, col_letra, col_prof = st.columns([1.5, 1, 2.5])

    with col_ano:
        anos_opcoes = ["1° Ano", "2° Ano", "3° Ano", "4° Ano", "5° Ano"]
        ano_selecionado = st.selectbox("Ano Escolar:", anos_opcoes)
    with col_letra:
        letras_opcoes = ["A", "B", "C", "D", "E", "F"]
        letra_selecionada = st.selectbox("Turma / Letra:", letras_opcoes)
    with col_prof:
        nome_prof = st.text_input(
            "Nome do Professor(a):", value="Professor(a)")

    nome_turma_completo = f"{ano_selecionado} {letra_selecionada}"
    st.divider()

    # --- Formulário de Nova Regra ---
    st.subheader("➕ Adicionar Nova Regra ou Sugestão")
    with st.form("nova_regra_form", clear_on_submit=True):
        col_input, col_resp = st.columns([2.5, 1.5])
        with col_input:
            nova_regra_texto = st.text_input(
                "Regra / Combinado:", placeholder="Ex: Tirar dúvidas levantando a mão")
        with col_resp:
            novo_responsavel = st.text_input(
                "Responsável:", value="Toda a Turma", placeholder="Ex: Toda a Turma ou Grupo X")

        btn_adicionar = st.form_submit_button("➕ Adicionar Regra")

    if btn_adicionar and nova_regra_texto.strip():
        nova_id = max([r["id"]
                      for r in st.session_state.regras], default=0) + 1
        resp = novo_responsavel.strip() if novo_responsavel.strip() else "Toda a Turma"
        st.session_state.regras.append({
            "id": nova_id,
            "texto": nova_regra_texto,
            "responsavel": resp,
            "votos": 0,
            "aprovada": True
        })
        st.rerun()

    st.divider()

    # --- Termômetro ---
    aprovadas = [r for r in st.session_state.regras if r["aprovada"]]
    total = len(st.session_state.regras)
    progresso = len(aprovadas) / total if total > 0 else 0

    st.subheader(
        f"📊 Termômetro do Acordo ({len(aprovadas)} de {total} Aprovadas)")
    st.progress(progresso)
    st.divider()

    # --- Lista de Regras ---
    st.subheader(f"📋 Regras e Combinados — {nome_turma_completo}")
    item_para_remover = None

    for r in st.session_state.regras:
        with st.container(border=True):
            col_check, col_texto, col_resp, col_voto, col_del = st.columns(
                [0.5, 2.5, 1.5, 0.8, 0.5])
            with col_check:
                r["aprovada"] = st.checkbox(
                    "", value=r["aprovada"], key=f"chk_{r['id']}")
            with col_texto:
                if r["aprovada"]:
                    st.markdown(f"✅ **{r['texto']}**")
                else:
                    st.write(r['texto'])
            with col_resp:
                r["responsavel"] = st.text_input(
                    "Responsável", value=r["responsavel"], key=f"resp_{r['id']}", label_visibility="collapsed")
            with col_voto:
                if st.button(f"👍 {r['votos']}", key=f"btn_{r['id']}"):
                    r["votos"] += 1
                    st.rerun()
            with col_del:
                if st.button("❌", key=f"del_{r['id']}"):
                    item_para_remover = r["id"]

    if item_para_remover is not None:
        st.session_state.regras = [
            r for r in st.session_state.regras if r["id"] != item_para_remover]
        st.rerun()

    # --- Ações de Salvar e Baixar ---
    if aprovadas:
        st.divider()
        col_export, col_save = st.columns(2)

        with col_save:
            st.subheader("☁️ Salvar na Nuvem")
            st.caption("Armazena o contrato no Firestore.")
            if st.button("💾 Salvar no Firestore", use_container_width=True):
                try:
                    doc_ref = db.collection(
                        "contratos").document(nome_turma_completo)
                    doc_ref.set({
                        "turma": nome_turma_completo,
                        "professor": nome_prof,
                        "regras": aprovadas,
                        "data_atualizacao": firestore.SERVER_TIMESTAMP
                    })
                    st.success(
                        f"Contrato da turma **{nome_turma_completo}** salvo no Firestore!")
                except Exception as err:
                    st.error(f"Erro ao salvar documento: {err}")

        with col_export:
            st.subheader("📄 Exportar Contrato")
            st.caption("Baixe para impressão.")
            html_doc = gerar_html_contrato(
                nome_turma_completo, nome_prof, aprovadas)
            st.download_button(
                label="📥 Baixar Contrato HTML",
                data=html_doc,
                file_name=f"Contrato_{nome_turma_completo.replace(' ', '_')}.html",
                mime="text/html",
                use_container_width=True
            )

# ==========================================
# ABA 2: CONTRATOS SALVOS
# ==========================================
with tab_salvos:
    st.header("📂 Base de Contratos Salvos")
    st.write("Consulte ou baixe contratos salvos no banco de dados.")

    if st.button("🔄 Atualizar Lista"):
        st.rerun()

    try:
        contratos_ref = db.collection("contratos").stream()
        contratos_encontrados = False

        for doc in contratos_ref:
            contratos_encontrados = True
            dados = doc.to_dict()
            turma = dados.get("turma", "Turma Desconhecida")
            prof = dados.get("professor", "Não informado")
            regras_salvas = dados.get("regras", [])

            with st.expander(f"🏫 {turma} — Prof(a). {prof}"):
                for i, r in enumerate(regras_salvas, 1):
                    st.markdown(
                        f"**{i}.** {r.get('texto', '')} *(Responsável: {r.get('responsavel', '')})*")

                st.divider()
                html_salvo = gerar_html_contrato(turma, prof, regras_salvas)
                st.download_button(
                    label=f"📥 Baixar HTML ({turma})",
                    data=html_salvo,
                    file_name=f"Contrato_{turma.replace(' ', '_')}.html",
                    mime="text/html",
                    key=f"dl_{doc.id}"
                )

        if not contratos_encontrados:
            st.info("Nenhum contrato foi encontrado no Firestore ainda.")

    except Exception as err:
        st.error(f"Erro ao buscar contratos: {err}")
