import re
from flask import Flask, request, jsonify, send_from_directory
from mysql.connector import pooling, Error
import logging

# Loglama yapılandırması
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# MySQL bağlantı havuzu yapılandırması
db_config = {
    'host': '127.0.0.1',
    'port': 3307,
    'user': 'root',
    'password': 'my-secret-pw',
    'database': 'testdb',
    'charset': 'utf8mb4',
    'use_unicode': True,
    'pool_name': 'mypool',
    'pool_size': 5
}

# Bağlantı havuzu oluştur
try:
    connection_pool = pooling.MySQLConnectionPool(**db_config)
    logger.info("Bağlantı havuzu başarıyla oluşturuldu")
except Error as e:
    logger.error(f"Bağlantı havuzu oluşturma hatası: {e}")
    raise

app = Flask(__name__, static_folder='static', static_url_path='')

@app.route('/', methods=['GET'])
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/search-domain', methods=['GET'])
def search_domain():
    try:
        # Domain parametresini al ve doğrula
        domain = request.args.get('domain', '').strip()
        if not domain:
            return jsonify(error='domain parametresi boş bırakılamaz'), 400
        
        # Havuzdan bağlantı al
        conn = connection_pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            # Regex pattern'i bir kez derle
            pattern = re.compile(re.escape(domain), re.IGNORECASE)
            
            # SQL sorgusunu parametrelerle hazırla
            like_term = f"%{domain}%"
            sql = """
                SELECT dosya_adi,
                       CONVERT(icerik USING utf8mb4) AS icerik
                FROM dosyalar
                WHERE CONVERT(icerik USING utf8mb4) LIKE %s
            """
            
            # Sorguyu çalıştır
            cursor.execute(sql, (like_term,))
            rows = cursor.fetchall()
            
            # Sonuçları işle
            db_name = conn.database
            results = []
            
            for row in rows:
                # İçeriği satırlara böl
                lines = row['icerik'].splitlines()
                matched_lines = []
                
                for line in lines:
                    if pattern.search(line):
                        matched_lines.append(line.strip())
                
                if matched_lines:
                    results.append({
                        'dosya_adi': row['dosya_adi'],
                        'match_count': len(matched_lines),
                        'matched_lines': matched_lines
                    })
            
            return jsonify(
                database=db_name,
                domain_searched=domain,
                results=results
            ), 200
            
        finally:
            cursor.close()
            conn.close()
            
    except Error as e:
        logger.error(f"Veritabanı hatası: {e}")
        return jsonify(error=f"Veritabanı hatası: {str(e)}"), 500
    except Exception as e:
        logger.error(f"Beklenmeyen hata: {e}")
        return jsonify(error="Bir hata oluştu, lütfen daha sonra tekrar deneyin"), 500

# Yeni eklenen domain istatistikleri endpoint'i
@app.route('/domain-stats', methods=['GET'])
def domain_stats():
    try:
        conn = connection_pool.get_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            # 1️⃣ Sayaçlar
            stats = {
                'com.tr': 0,
                'szutest.com.tr': 0,
                'tupras.com.tr': 0,
                'bilyoner.com': 0,
            }

            # 2️⃣ Tüm içerikleri UTF‑8 olarak çek
            cursor.execute("SELECT CONVERT(icerik USING utf8mb4) AS icerik FROM dosyalar")

            # 3️⃣ Regex’leri derle (performans için)
            pattern_all   = re.compile(r'(?<![a-zA-Z0-9-])(?:[a-zA-Z0-9-]+\.)*com\.tr(?![a-zA-Z0-9-])', re.I)
            pattern_sz    = re.compile(r'(?<![a-zA-Z0-9-])(?:[a-zA-Z0-9-]+\.)?szutest\.com\.tr(?![a-zA-Z0-9-])', re.I)
            pattern_tu    = re.compile(r'(?<![a-zA-Z0-9-])(?:[a-zA-Z0-9-]+\.)?tupras\.com\.tr(?![a-zA-Z0-9-])', re.I)
            pattern_bily  = re.compile(r'(?<![a-zA-Z0-9-])(?:[a-zA-Z0-9-]+\.)?bilyoner\.com(?![a-zA-Z0-9-])', re.I)

            for row in cursor:
                raw = row['icerik'] or ''
                # bytes geldiyse güvenli decode
                if isinstance(raw, (bytes, bytearray)):
                    raw = raw.decode('utf-8', errors='ignore')

                stats['com.tr']         += len(pattern_all.findall(raw))
                stats['szutest.com.tr'] += len(pattern_sz.findall(raw))
                stats['tupras.com.tr']  += len(pattern_tu.findall(raw))
                stats['bilyoner.com']   += len(pattern_bily.findall(raw))

            total_domains = sum(stats.values())

            # Güncel zaman
            cursor.execute("SELECT NOW() AS ts")
            updated_at = cursor.fetchone()['ts']

            return jsonify({
                'stats': stats,
                'total': total_domains,
                'updated_at': updated_at.isoformat(),
                'database': conn.database
            }), 200

        finally:
            cursor.close()
            conn.close()

    except Exception as e:
        # Tam stack trace için
        logger.exception("Domain istatistikleri hesaplanırken hata oluştu")
        return jsonify(error=str(e)), 500

# Sağlık kontrolü endpoint'i
@app.route('/health', methods=['GET'])
def health_check():
    try:
        # Veritabanı bağlantısını test et
        conn = connection_pool.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify(status="healthy"), 200
    except Exception as e:
        logger.error(f"Sağlık kontrolü başarısız: {e}")
        return jsonify(status="unhealthy", error=str(e)), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)  # Üretin ortamında debug=False olmalı