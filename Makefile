# Makefile: Proje Yönetim Kısayolları

# Python yorumlayıcısı
PYTHON = python3
VENV = .venv
PIP = $(VENV)/bin/pip
PY = $(VENV)/bin/python

.PHONY: help setup ingest run clean docker-build docker-run

# Varsayılan hedef (help)
help:
	@echo "🛠️  Mevcut Komutlar:"
	@echo "  make setup        : Sanal ortamı kur ve kütüphaneleri yükle"
	@echo "  make ingest       : Vektör veritabanını oluştur (Force recreate)"
	@echo "  make run          : Uygulamayı çalıştır (Streamlit)"
	@echo "  make clean        : Geçici dosyaları ve sanal ortamı temizle"
	@echo "  make docker-build : Docker imajını oluştur"
	@echo "  make docker-run   : Docker konteynerini çalıştır"

# Kurulum (Setup)
setup:
	@echo "📦 Sanal ortam oluşturuluyor..."
	$(PYTHON) -m venv $(VENV)
	@echo "📥 Kütüphaneler yükleniyor..."
	$(PIP) install -r requirements.txt
	@echo "✅ Kurulum tamamlandı! Çalıştırmak için: make run"

# Veri Yükleme (Ingestion - Force Recreate)
ingest:
	@echo "🔄 Vektör veritabanı yeniden oluşturuluyor..."
	$(PY) -c "from src.ingestion import get_vectorstore; get_vectorstore(force_recreate=True)"
	@echo "✅ Veritabanı hazır."

# Çalıştırma (Run)
run:
	@echo "🚀 Uygulama başlatılıyor..."
	streamlit run app.py

# Temizlik (Clean)
clean:
	@echo "🧹 Temizlik yapılıyor..."
	rm -rf $(VENV)
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf chroma_db
	find . -type d -name "__pycache__" -exec rm -rf {} +
	@echo "✅ Temizlik bitti."

# Docker Komutları
docker-build:
	@echo "🐳 Docker imajı oluşturuluyor..."
	docker build -t legal-rag-app .

docker-run:
	@echo "🚀 Docker konteyneri başlatılıyor..."
	docker run -p 8501:8501 --env-file .env legal-rag-app
