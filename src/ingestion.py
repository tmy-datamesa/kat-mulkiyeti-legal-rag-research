import os
import shutil
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from src import config

def load_pdf(pdf_path):
    """PDF dosyasından metin çıkarır."""
    print(f"PDF okunuyor: {pdf_path}")
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    print(f"{len(reader.pages)} sayfa okundu. Toplam karakter: {len(text)}")
    return text

def create_chunks(text):
    """
    RAG performansı için metni mantıksal parçalara böler.
    Hukuki metin yapılarına (Madde, Bölüm vb.) göre bölme işlemi yapar.
    """
    print("Metin parçalanıyor...")
    # Hukuki metin bütünlüğünü korumak için özel ayırıcılar
    legal_separators = [
        "\nBÖLÜM ", "\nMadde ", "\nEk Madde ", "\nGeçici Madde ",
        "\n[IVXLM]+ –", "\n\n", "\n", " "
    ]
    text_splitter = RecursiveCharacterTextSplitter(
        separators=legal_separators,
        chunk_size=config.CHUNK_SIZE,     # Her parçanın yaklaşık boyutu
        chunk_overlap=config.CHUNK_OVERLAP, # Bağlam kaybını önlemek için örtüşme
        add_start_index=True,
        is_separator_regex=True
    )
    chunks = text_splitter.split_text(text)
    print(f"{len(chunks)} parça oluşturuldu")
    return chunks

def get_vectorstore(force_recreate=False):
    """
    Vektör veritabanını yönetir.
    Verimlilik için: Varsa yükler, yoksa oluşturur.
    """
    persist_directory = config.CHROMA_PERSIST_DIRECTORY
    
    # Embedding modelini başlat (Metni sayısal vektöre çevirir)
    embeddings = GoogleGenerativeAIEmbeddings(
        model=config.EMBEDDING_MODEL_NAME,
        google_api_key=config.API_KEY,
        task_type="retrieval_document"
    )

    # 1. Mevcut veritabanını kontrol et
    if os.path.exists(persist_directory) and not force_recreate:
        print(f"Mevcut vektör veritabanı bulundu: {persist_directory}")
        try:
            vectorstore = Chroma(
                persist_directory=persist_directory,
                embedding_function=embeddings,
                collection_name=config.COLLECTION_NAME
            )
            # Veritabanı boş mu kontrolü
            if vectorstore._collection.count() > 0:
                print("Veritabanı başarıyla yüklendi.")
                return vectorstore
            else:
                print("Veritabanı boş, yeniden oluşturuluyor...")
        except Exception as e:
            print(f"Veritabanı yüklenirken hata: {e}")
            print("Yeniden oluşturulacak...")

    # 2. Sıfırdan oluşturma (Sadece ilk kurulumda veya sorun olduğunda çalışır)
    print("Vektör veritabanı SIFIRDAN oluşturuluyor...")
    
    # Temiz başlangıç için eski dosyaları sil
    if os.path.exists(persist_directory):
        shutil.rmtree(persist_directory)
        print("Eski veritabanı temizlendi.")
    
    # PDF işleme adımları
    if not os.path.exists(config.DATA_PATH):
        raise FileNotFoundError(f"PDF bulunamadı: {config.DATA_PATH}")
        
    raw_text = load_pdf(config.DATA_PATH)
    chunks = create_chunks(raw_text)
    
    # Chunkların vektöre dönüştürülmesi ve kaydedilmesi
    print(f"{len(chunks)} parça işleniyor (API isteği gönderiliyor)...")
    vectorstore = Chroma.from_texts(
        texts=chunks,
        embedding=embeddings,
        collection_name=config.COLLECTION_NAME,
        persist_directory=persist_directory
    )
    
    print("İşlem tamamlandı. Veritabanı kaydedildi.")
    return vectorstore
