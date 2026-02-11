import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# ==============================================================================
# API AYARLARI
# ==============================================================================
API_KEY = os.getenv("GEMINI_API_KEY")

# ==============================================================================
# MODEL AYARLARI
# ==============================================================================
# Embedding Modeli (Google'ın çok dilli embedding modeli)
EMBEDDING_MODEL_NAME = "models/gemini-embedding-001"

# LLM Modeli (Hızlı ve uygun maliyetli)
# Kota sorunu yaşanırsa 1.5-flash tercih edilir
LLM_MODEL_NAME = "gemini-2.5-flash"

# ==============================================================================
# YOL AYARLARI (PATHS)
# ==============================================================================
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "kat-mulkiyeti-kanunu.pdf")
CHROMA_PERSIST_DIRECTORY = os.path.join(PROJECT_ROOT, "chroma_db")
COLLECTION_NAME = "kat_mulkiyeti"

# ==============================================================================
# RAG PARAMETRELERİ
# ==============================================================================
CHUNK_SIZE = 2000
CHUNK_OVERLAP = 400
RETRIEVER_K = 5  # API kotası için düşük tutuldu (15 -> 5)

# ==============================================================================
# PROMPT ŞABLONU (SYSTEM INSTRUCTION)
# ==============================================================================
SYSTEM_INSTRUCTION = """
Sen Türkiye Cumhuriyeti Kat Mülkiyeti Kanunu konusunda uzman, yardımcı bir hukuk asistanısın.
Görev: Kullanıcının sorusunu SADECE aşağıda verilen "KANUN METNİ"ni kullanarak cevapla.

Kurallar:
1. Asla kendi genel bilgini kullanma. Sadece verilen metne sadık kal.
2. Eğer verilen metinde sorunun cevabı yoksa, kesinlikle uydurma ve "Bu konuda verilen metinlerde bilgi bulunmamaktadır." de.
3. Cevabına ilgili madde numarasını belirterek başla (Örn: "Kat Mülkiyeti Kanunu Madde 34..."). Metinden madde numarasını tespit etmeye çalış.
4. Hukuki terimleri mümkün olduğunca sadeleştirerek, günlük dilde açıkla.
5. Cevabın net, anlaşılır ve profesyonel olsun.
6. Kullanıcı ile TÜRKÇE konuş.
"""
