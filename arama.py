import mysql.connector
import re

db_config = {
    'host': '127.0.0.1',
    'port': 3307,
    'user': 'root',
    'password': 'my-secret-pw',
    'database': 'testdb'
}

def extract_szutest_entries():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Sadece "szutest.com.tr" geçen kayıtları seçiyoruz
    query = """
        SELECT dosya_adi,
               CONVERT(icerik USING utf8mb4) AS metin
          FROM dosyalar
         WHERE CONVERT(icerik USING utf8mb4) LIKE '%szutest.com.tr%'
    """
    cursor.execute(query)

    # Sadece szutest.com.tr içeren e‑posta veya URL parçalarını yakalamak için basit regex
    regex = r"(?:[a-zA-Z0-9._%+-]+@)?szutest\.com\.tr[^\s\"']*"

    toplam_eslesme = 0
    toplam_dosya = 0

    print("🔍 'szutest.com.tr' geçen veriler:")

    for dosya_adi, metin in cursor.fetchall():
        matches = re.findall(regex, metin)
        if matches:
            toplam_dosya += 1
            print(f"\n📄 Dosya: {dosya_adi} ({len(matches)} eşleşme)")
            for m in matches:
                print(f"   → {m}")
            toplam_eslesme += len(matches)

    print("\n📊 Özet")
    print(f"📁 'szutest.com.tr' geçen dosya sayısı: {toplam_dosya}")
    print(f"🔢 Toplam eşleşme sayısı: {toplam_eslesme}")

    cursor.close()
    conn.close()

if __name__ == '__main__':
    extract_szutest_entries()
