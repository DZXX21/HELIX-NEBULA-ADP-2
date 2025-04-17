#!/usr/bin/env python3
import os
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

# Default ayarlar
DEFAULT_MAX_MB = 500
BUFFER_SIZE = 4 * 1024 * 1024  # 4 MB
MAX_WORKERS = min(32, (os.cpu_count() or 1) + 4)

def split_file(filepath, max_bytes):
    """
    1) 500 MB üstündeyse,
    2) BUFFER_SIZE’lık parçalara bölerek,
    3) part1/part2/... sufiksli dosyalar oluşturur.
    """
    total_size = os.path.getsize(filepath)
    if total_size <= max_bytes:
        return f"SKIP: {os.path.basename(filepath)} ({total_size} B)"

    base, ext = os.path.splitext(filepath)
    part_num = 1
    bytes_written = 0
    out = None

    try:
        with open(filepath, 'rb') as src:
            # ilk part dosyasını aç
            out = open(f"{base}_part{part_num}{ext}", 'wb')
            while True:
                chunk = src.read(BUFFER_SIZE)
                if not chunk:
                    break

                # bu chunk mevcut part'ı aşıyorsa, yeni part dosyasına geç
                if bytes_written + len(chunk) > max_bytes:
                    out.close()
                    part_num += 1
                    bytes_written = 0
                    out = open(f"{base}_part{part_num}{ext}", 'wb')

                out.write(chunk)
                bytes_written += len(chunk)

    finally:
        if out and not out.closed:
            out.close()
    return f"SPLIT: {os.path.basename(filepath)} → {part_num} parçaya bölündü"

def main():
    p = argparse.ArgumentParser(
        description="Dizindeki tüm dosyaları 500 MB üstündeyse parçalara böler"
    )
    p.add_argument(
        "-d", "--directory",
        default=".",
        help="Tarancak dizin (default: çalışılan dizin)"
    )
    p.add_argument(
        "-s", "--size-mb",
        type=int,
        default=DEFAULT_MAX_MB,
        help=f"Maksimum parça boyutu MB cinsinden (default: {DEFAULT_MAX_MB})"
    )
    p.add_argument(
        "-w", "--workers",
        type=int,
        default=MAX_WORKERS,
        help=f"Paralel iş parçacığı sayısı (default: {MAX_WORKERS})"
    )
    args = p.parse_args()

    max_bytes = args.size_mb * 1024 * 1024

    # Taranacak dosyalar
    paths = []
    for entry in os.scandir(args.directory):
        if entry.is_file():
            paths.append(entry.path)

    if not paths:
        print("Hiç dosya bulunamadı.")
        return

    # ThreadPool ile paralel bölme
    with ThreadPoolExecutor(max_workers=args.workers) as exe:
        futures = {
            exe.submit(split_file, path, max_bytes): path
            for path in paths
        }
        for fut in as_completed(futures):
            print(fut.result())

if __name__ == "__main__":
    main()
