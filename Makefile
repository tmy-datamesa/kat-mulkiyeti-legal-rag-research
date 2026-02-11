# Makefile: Proje Yönetim Kısayolları

# Sistemdeki aktif Python yorumlayıcısını kullan
PYTHON = python3
PIP = pip

.PHONY: help setup ingest run clean

# Varsayılan hedef (help)
help:
	@echo "🛠️  Mevcut Komutlar:"
	@echo "  make setup   : Gerekli kütüphaneleri yükle (requirements.txt)"
	@echo "  make ingest  : Vektör veritabanını sıfırdan oluştur (Force Recreate)"
	@echo "  make run     : Uygulamayı çalıştır (Streamlit)"
	@echo "  make clean   : Geçici dosyaları temizle (Önbellek, DB)"

# Kurulum (Setup)
setup:
	@echo "📦 Kütüphaneler yükleniyor..."
	$(PIP) install -r requirements.txt
	@echo "✅ Kurulum tamamlandı! Çalıştırmak için: make run"

# Veri Yükleme (Ingestion - Force Recreate)
ingest:
	@echo "🔄 Vektör veritabanı yeniden oluşturuluyor..."
	$(PYTHON) -c "from src.ingestion import get_vectorstore; get_vectorstore(force_recreate=True)"
	@echo "✅ Veritabanı hazır."

# Çalıştırma (Run)
run:
	@echo "🚀 Uygulama başlatılıyor..."
	streamlit run app.py

# Temizlik (Clean)
clean:
	@echo "🧹 Temizlik yapılıyor..."
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf chroma_db
	find . -type d -name "__pycache__" -exec rm -rf {} +
	@echo "✅ Temizlik bitti."
