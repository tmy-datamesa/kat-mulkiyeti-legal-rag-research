import google.generativeai as genai
from src import config

class LegalRAG:
    """
    RAG (Retrieval-Augmented Generation) Mantığı
    Hukuki sorulara cevap vermek için retrieval ve generation adımlarını yönetir.
    """
    
    def __init__(self, vectorstore):
        """
        Başlatıcı.
        
        Girdi:
            vectorstore: ChromaDB vektör veritabanı nesnesi
        """
        self.vectorstore = vectorstore
        self._setup_llm()
        
    def _setup_llm(self):
        """LLM modelini yapılandırır."""
        print(f"LLM ({config.LLM_MODEL_NAME}) hazırlanıyor...")
        genai.configure(api_key=config.API_KEY)
        self.model = genai.GenerativeModel(config.LLM_MODEL_NAME)
        print("LLM hazır.")

    def get_relevant_docs(self, query):
        """
        Soruyla anlamsal olarak en benzer doküman parçalarını bulur.
        'Retrieval' aşamasıdır.
        """
        # Veritabanından en benzer k adet parçayı getir
        docs = self.vectorstore.similarity_search(query, k=config.RETRIEVER_K)
        return docs

    def get_answer(self, query):
        """
        RAG Akışı: Retrieval -> Context -> Prompt -> Generation
        """
        # 1. Retrieval
        docs = self.get_relevant_docs(query)
        
        if not docs:
            return {
                "answer": "Üzgünüm, kanun metninde bu konuyla ilgili bilgi bulamadım.",
                "source_documents": []
            }
        
        # 2. Context: Parçaları tek bir metin haline getir
        context_text = "\n\n".join([
            f"--- İLGİLİ METİN PARÇASI {i+1} ---\n{doc.page_content}" 
            for i, doc in enumerate(docs)
        ])
        
        # 3. Prompt: Sistem talimatı, bağlam ve soruyu birleştir
        system_instruction = config.SYSTEM_INSTRUCTION
        full_prompt = f"{system_instruction}\n\nKANUN METNİ:\n{context_text}\n\nSORU: {query}\nCEVAP:"
        
        # 4. Generation: LLM'e gönder ve cevap üret
        try:
            response = self.model.generate_content(full_prompt)
            answer_text = response.text
        except Exception as e:
            answer_text = f"Hata oluştu: {str(e)}"
            if "429" in str(e):
                answer_text = "API Kotası aşıldı (429). Lütfen kısa süre bekleyin."

        return {
            "answer": answer_text,
            "source_documents": docs
        }
