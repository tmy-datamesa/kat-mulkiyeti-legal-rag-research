"""
Streamlit Web Arayüzü - Legal-RAG (Refactored)

Bu uygulama, Kat Mülkiyeti Kanunu hakkında soru-cevap yapmanızı sağlar.
Sadece kanun metnine dayanarak cevap verir.
"""

import streamlit as st
from src import config
from src.ingestion import get_vectorstore
from src.rag import LegalRAG

# ============================================================================
# SAYFA YAPILANDIRMASI
# ============================================================================

st.set_page_config(
    page_title="Legal-RAG: Kat Mülkiyeti Kanunu",
    page_icon="⚖️",
    layout="wide"
)

# ============================================================================
# BAŞLIK VE AÇIKLAMA
# ============================================================================

st.title("⚖️ Legal-RAG: Kat Mülkiyeti Kanunu Asistanı")
st.markdown("""
Bu sistem, **634 Sayılı Kat Mülkiyeti Kanunu** hakkında sorularınızı yanıtlar.

> ⚠️ **Not:** Hukuki tavsiye vermez, bilgilendirme amaçlıdır.
""")

st.divider()

# ============================================================================
# SİSTEM HAZIRLIĞI (SESSION STATE)
# ============================================================================

# Model bilgisi
st.caption(f"Model: {config.LLM_MODEL_NAME} | Embedding: {config.EMBEDDING_MODEL_NAME}")

if 'rag_system' not in st.session_state:
    with st.spinner("Sistem başlatılıyor..."):
        try:
            # 1. Vektör Veritabanı Hazırlığı
            # get_vectorstore fonksiyonu akıllı yükleme yapar:
            # Varsa yükler (Hızlı), yoksa oluşturur (Yavaş)
            vectorstore = get_vectorstore(force_recreate=False)
            
            # 2. RAG Motorunun Başlatılması
            rag_system = LegalRAG(vectorstore)
            
            # 3. Session State Kaydı
            # Streamlit her etkileşimde kodu baştan çalıştırır.
            # Sistemin sıfırlanmaması için session_state kullanılır.
            st.session_state.vectorstore = vectorstore
            st.session_state.rag_system = rag_system
            
            st.success("Sistem hazır.")
            
        except Exception as e:
            st.error(f"Sistem hatası: {str(e)}")
            st.stop()

# ============================================================================
# SORU-CEVAP ARAYÜZÜ
# ============================================================================

soru = st.text_input(
    "💬 Sorunuzu yazın:",
    placeholder="Örnek: Apartman yöneticisi nasıl seçilir?",
    help="Kat Mülkiyeti Kanunu çerçevesinde sorular sorabilirsiniz."
)

# Cevapla butonu
if st.button("🔍 Cevapla", type="primary"):
    if not soru:
        st.warning("Lütfen bir soru giriniz.")
    else:
        with st.spinner("🤔 Kanun maddeleri inceleniyor ve cevap hazırlanıyor..."):
            # RAG sistemini kullanarak cevap al
            result = st.session_state.rag_system.get_answer(soru)
            
            answer = result.get("answer", "")
            source_docs = result.get("source_documents", [])
            
            # Cevabı Göster
            st.markdown("### Cevap")
            if "Hatası" in answer or "Kotası" in answer:
                st.warning(answer)
            else:
                st.info(answer)
            
            # Kaynak Dokümanları Göster (Şeffaflık için)
            if source_docs:
                with st.expander(f"Kaynak Dokümanlar ({len(source_docs)} adet)"):
                    for i, doc in enumerate(source_docs, 1):
                        st.markdown(f"**Kaynak {i}:**")
                        st.text(doc.page_content)
                        st.divider()

# ============================================================================
# FOOTER
# ============================================================================

st.divider()
st.caption("⚖️ Legal-RAG | Refactored Architecture | src/structure")

