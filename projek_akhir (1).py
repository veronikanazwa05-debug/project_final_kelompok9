import psycopg2
from psycopg2 import extras, Error
from getpass import getpass
from datetime import datetime
import os

# =====================================================
# KONFIGURASI DATABASE
# =====================================================

DB_CONFIG = {
    'host': '127.0.0.1',
    'database': 'SeedMart',
    'user': 'postgres',
    'password': '12345',
    'port': '5432'
}

# Global variable untuk user yang login
CURRENT_USER = None

# =====================================================
# FUNGSI KONEKSI DATABASE
# =====================================================
def connect_db():
    """Membuat koneksi ke database PostgreSQL"""
    try:
        connection = psycopg2.connect(**DB_CONFIG)
        return connection
    except psycopg2.Error as e:
        print(f"❌ Gagal koneksi ke database: {e}")
        return None

def fetch_data(query, params=None, fetch_one=False):
    """Mengambil data dari database"""
    connection = connect_db()
    if connection is None:
        return [] if not fetch_one else None

    try:
        with connection.cursor(cursor_factory=extras.RealDictCursor) as cursor:
            cursor.execute(query, params)
            if fetch_one:
                return cursor.fetchone()
            else:
                return cursor.fetchall()
    except psycopg2.Error as e:
        print(f"❌ Error saat eksekusi query: {e}")
        return [] if not fetch_one else None
    finally:
        if connection:
            connection.close()

def execute_query(query, params=None, fetch_id=False):
    """Menjalankan query INSERT/UPDATE/DELETE ke database"""
    connection = connect_db()
    if connection is None:
        return False

    return_id = None
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            if fetch_id:
                result = cursor.fetchone()
                if result:
                    return_id = result[0]
            connection.commit()
    except psycopg2.Error as e:
        connection.rollback()
        print(f"❌ Error saat eksekusi query: {e}")
        return False
    finally:
        if connection:
            connection.close()
    
    return return_id if fetch_id else True

# =====================================================
# FUNGSI UTILITY
# =====================================================
def clear_screen():
    """Fungsi untuk membersihkan layar"""
    os.system('cls' if os.name == 'nt' else 'clear')

def tampilkan_header(judul):
    """Fungsi untuk menampilkan header"""
    print("=" * 70)
    print(f" {judul}")
    print("=" * 70)
    print()

def validasi_angka(nama_field, tipe='int', min_val=1):
    """Fungsi untuk validasi input harus angka"""
    while True:
        try:
            nilai = input(f"{nama_field}: ").strip()
            
            if not nilai:
                print("❌ Input tidak boleh kosong!")
                continue
            
            if tipe == 'int':
                angka = int(nilai)
                if angka < min_val:
                    print(f"❌ Nilai harus minimal {min_val}!")
                    continue
                return angka
            elif tipe == 'float':
                angka = float(nilai)
                if angka < min_val:
                    print(f"❌ Nilai harus minimal {min_val}!")
                    continue
                return angka
        except ValueError:
            print("❌ Input harus berupa angka! Silakan coba lagi.")

# =====================================================
# MODUL LOGIN
# =====================================================
def login():
    """Fungsi untuk melakukan login"""
    global CURRENT_USER
    
    clear_screen()
    print("""
    ███████╗███████╗███████╗██████╗ ███╗   ███╗ █████╗ ██████╗ ████████╗
    ██╔════╝██╔════╝██╔════╝██╔══██╗████╗ ████║██╔══██╗██╔══██╗╚══██╔══╝
    ███████╗█████╗  █████╗  ██║  ██║██╔████╔██║███████║██████╔╝   ██║   
    ╚════██║██╔══╝  ██╔══╝  ██║  ██║██║╚██╔╝██║██╔══██║██╔══██╗   ██║   
    ███████║███████╗███████╗██████╔╝██║ ╚═╝ ██║██║  ██║██║  ██║   ██║   
    ╚══════╝╚══════╝╚══════╝╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   
    """)
    tampilkan_header("SISTEM LOGIN KASIR SEEDMART")
    
    username = input("Username: ").strip()
    password = getpass("Password: ")

    query = """
    SELECT u.id_user, u.username, u.email, ur.id_role, r.nama_role
    FROM users u
    JOIN user_role ur ON u.id_user = ur.id_user
    JOIN roles r ON ur.id_role = r.id_role
    WHERE u.username = %s AND u.passwords = %s
    """
    user_data = fetch_data(query, (username, password), fetch_one=True)

    if user_data:
        CURRENT_USER = user_data
        print(f"\n✅ Login berhasil! Selamat datang, {CURRENT_USER['username']}!")
        print(f"Role: {CURRENT_USER['nama_role']}")
        input("\nTekan Enter untuk melanjutkan...")
        return True
    else:
        print("\n❌ Login gagal. Username atau Password salah.")
        return False

def logout():
    """Fungsi untuk logout"""
    global CURRENT_USER
    if CURRENT_USER:
        print(f"\n✅ Logout berhasil. Sampai jumpa, {CURRENT_USER['username']}!")
        CURRENT_USER = None
    else:
        print("\n❌ Anda belum login.")

# =====================================================
# MODUL ADMIN - MANAJEMEN PENGGUNA
# =====================================================
def admin_show_users():
    """Lihat semua pengguna"""
    clear_screen()
    tampilkan_header("DATA PENGGUNA")
    
    query = """
    SELECT u.id_user, u.username, u.email, r.nama_role
    FROM users u
    JOIN user_role ur ON u.id_user = ur.id_user
    JOIN roles r ON ur.id_role = r.id_role
    ORDER BY u.id_user
    """
    users = fetch_data(query)
    
    if not users:
        print("Belum ada data pengguna.")
        return

    print(f"{'ID':<5} {'Username':<20} {'Email':<30} {'Role':<20}")
    print("-" * 70)
    for user in users:
        print(f"{user['id_user']:<5} {user['username']:<20} {user['email']:<30} {user['nama_role']:<20}")

def admin_add_user():
    """Tambah pengguna baru"""
    clear_screen()
    tampilkan_header("TAMBAH PENGGUNA BARU")
    
    username = input("Username Baru: ").strip()
    password = getpass("Password: ")
    email = input("Email: ").strip()
    
    print("\nPilih Role:")
    print("1. Admin")
    print("2. Pengelola Toko")
    print("3. Kasir")
    role_id = validasi_angka("ID Role (1-3)", 'int', 1)
    
    if role_id not in [1, 2, 3]:
        print("❌ Role ID tidak valid!")
        return

    # Cek username
    if fetch_data("SELECT id_user FROM users WHERE username = %s", (username,), fetch_one=True):
        print("❌ Username sudah terdaftar.")
        return
    
    # Insert user
    query_user = """
    INSERT INTO users (username, passwords, email, id_alamat)
    VALUES (%s, %s, %s, 1)
    RETURNING id_user;
    """
    new_user_id = execute_query(query_user, (username, password, email), fetch_id=True)

    if new_user_id:
        query_role = "INSERT INTO user_role (id_user, id_role) VALUES (%s, %s);"
        if execute_query(query_role, (new_user_id, role_id)):
            print(f"✅ Pengguna '{username}' berhasil ditambahkan dengan ID: {new_user_id}.")
        else:
            print("❌ Gagal menambahkan role pengguna.")
            execute_query("DELETE FROM users WHERE id_user = %s", (new_user_id,))
    else:
        print("❌ Gagal menambahkan pengguna.")

def admin_edit_user():
    """Edit data pengguna"""
    clear_screen()
    tampilkan_header("EDIT PENGGUNA")

    user_id = validasi_angka("Masukkan ID User yang ingin diedit", 'int', 1)

    # Ambil data user lama
    query = """
    SELECT u.username, u.email, ur.id_role 
    FROM users u
    JOIN user_role ur ON u.id_user = ur.id_user
    WHERE u.id_user = %s
    """
    user = fetch_data(query, (user_id,), fetch_one=True)

    if not user:
        print("❌ User tidak ditemukan!")
        return

    print("\nTekan ENTER untuk melewati (tidak diubah)")
    print(f"Username saat ini : {user['username']}")
    new_username = input("Username baru: ").strip()
    if new_username == "":
        new_username = user['username']

    print(f"Email saat ini    : {user['email']}")
    new_email = input("Email baru: ").strip()
    if new_email == "":
        new_email = user['email']

    print(f"Role saat ini     : {user['id_role']}")
    print("1. Admin\n2. Pengelola Toko\n3. Kasir")
    new_role = input("Role baru (1-3): ").strip()
    if new_role == "":
        new_role = user['id_role']
    else:
        new_role = int(new_role)

    # Update User
    q_user = "UPDATE users SET username=%s, email=%s WHERE id_user=%s"
    execute_query(q_user, (new_username, new_email, user_id))

    # Update Role
    q_role = "UPDATE user_role SET id_role=%s WHERE id_user=%s"
    execute_query(q_role, (new_role, user_id))

    print(f"\n✅ Data user ID {user_id} berhasil diperbarui!")


def admin_delete_user():
    """Hapus pengguna"""
    clear_screen()
    tampilkan_header("HAPUS PENGGUNA")
    
    user_id = validasi_angka("Masukkan ID Pengguna yang akan dihapus", 'int', 1)

    query_role = "DELETE FROM user_role WHERE id_user = %s"
    if execute_query(query_role, (user_id,)):
        query_user = "DELETE FROM users WHERE id_user = %s"
        if execute_query(query_user, (user_id,)):
            print(f"✅ Pengguna ID {user_id} berhasil dihapus.")
        else:
            print("❌ Gagal menghapus pengguna.")
    else:
        print("❌ Gagal menghapus role pengguna.")

def admin_view_products():
    """Lihat semua produk (tahan terhadap nilai NULL)"""
    clear_screen()
    tampilkan_header("DATA PRODUK")
    
    query = """
    SELECT p.id_produk, p.nama_produk, p.stok, p.harga, k.nama_kategori, 
           p.diskon, u.username as pemilik
    FROM produk p
    JOIN kategori k ON p.id_kategori = k.id_kategori
    JOIN users u ON p.id_user = u.id_user
    ORDER BY p.id_produk
    """
    products = fetch_data(query)

    if not products:
        print("Belum ada data produk.")
        return

    print(f"{'ID':<5} {'Nama Produk':<25} {'Stok':<8} {'Harga':<14} {'Kategori':<15} {'Pemilik':<15} {'Diskon':<8}")
    print("-" * 100)
    for p in products:
        idp = p.get('id_produk', 'N/A')
        nama = p.get('nama_produk', 'N/A')
        stok = p.get('stok')
        stok_str = str(stok) if stok is not None else '0'
        harga = p.get('harga')
        kategori = p.get('nama_kategori') or 'N/A'
        pemilik = p.get('pemilik') or 'N/A'
        diskon = p.get('diskon') if p.get('diskon') is not None else 0.0

        try:
            harga_str = f"Rp {harga:,.0f}" if harga is not None else "-"
        except Exception:
            harga_str = str(harga)

        try:
            diskon_pct = f"{diskon*100:.0f}%"
        except Exception:
            diskon_pct = str(diskon) if diskon is not None else "0%"

        print(f"{idp:<5} {nama:<25} {stok_str:<8} {harga_str:<14} {kategori:<15} {pemilik:<15} {diskon_pct:<8}")

def admin_view_transactions():
    """Lihat semua transaksi"""
    clear_screen()
    tampilkan_header("DATA TRANSAKSI")
    
    query = """
    SELECT 
        t.id_transaksi, 
        t.status, 
        t.total_harga, 
        dt.tanggal, 
        u.username AS kasir, 
        p.nama_produk, 
        dt.jumlah_produk, 
        m.nama_metode
    FROM transaksi t
    JOIN users u ON t.id_user = u.id_user
    JOIN detail_transaksi dt ON t.id_detail_transaksi = dt.id_detail_transaksi
    JOIN produk p ON dt.id_produk = p.id_produk
    JOIN metode_pembayaran m ON t.id_metode = m.id_metode
    ORDER BY dt.tanggal DESC
    LIMIT 50
    """
    transactions = fetch_data(query)

    if not transactions:
        print("Belum ada data transaksi.")
        return

    for t in transactions:
        print(f"\nID: {t['id_transaksi']} | Tgl: {t['tanggal']} | Status: {t['status']}")
        print(f"Kasir: {t['kasir']} | Produk: {t['nama_produk']} ({t['jumlah_produk']}x)")
        print(f"Total: Rp {t['total_harga']:,.0f} | Metode: {t['nama_metode']}")
        print("-" * 70)

def admin_report():
    """Laporan transaksi"""
    clear_screen()
    tampilkan_header("LAPORAN TRANSAKSI")
    
    print("Pilih Periode Laporan:")
    print("1. Harian")
    print("2. Mingguan")
    print("3. Bulanan")
    print("4. Barang Terlaris (Semua Waktu)")    # <<< tambahan menu 4
    choice = input("Pilih opsi (1-4): ").strip()

    params = None
    date_filter = None
    
    # ================= Periode Tanggal =================
    if choice == '1':
        date_param = input("Masukkan Tanggal (YYYY-MM-DD): ")
        date_filter = "CAST(dt.tanggal AS DATE) = %s"
        params = (date_param,)

    elif choice == '2':
        week_param = input("Masukkan Nomor Minggu (YYYY-WW): ")
        date_filter = "TO_CHAR(CAST(dt.tanggal AS DATE), 'YYYY-WW') = %s"
        params = (week_param,)

    elif choice == '3':
        month_param = input("Masukkan Bulan (YYYY-MM): ")
        date_filter = "TO_CHAR(CAST(dt.tanggal AS DATE), 'YYYY-MM') = %s"
        params = (month_param,)

    elif choice == '4':   # ================= Barang Terlaris =================
        clear_screen()
        tampilkan_header("BARANG TERLARIS")

        query_top = """
        SELECT p.id_produk, p.nama_produk, COALESCE(SUM(dt.jumlah_produk),0) AS total_terjual
        FROM produk p
        LEFT JOIN detail_transaksi dt ON p.id_produk = dt.id_produk
        GROUP BY p.id_produk, p.nama_produk
        ORDER BY total_terjual DESC;
        """
        data = fetch_data(query_top)

        if not data:
            print("Belum ada data produk atau transaksi.")
            return

        print(f"{'ID':<5} {'Nama Produk':<30} {'Terjual':<10}")
        print("-"*50)
        for item in data:
            print(f"{item['id_produk']:<5} {item['nama_produk']:<30} {item['total_terjual']:<10}")
        
        input("\nTekan Enter untuk kembali...")
        return

    else:
        print("Pilihan tidak valid.")
        return
    
    # ================= Laporan Transaksi =================
    query = f"""
    SELECT 
        COUNT(t.id_transaksi) AS total_transaksi,
        SUM(t.total_harga) AS total_penghasilan,
        COUNT(CASE WHEN t.status = 'Selesai' THEN 1 END) AS transaksi_selesai,
        COUNT(CASE WHEN t.status = 'Gagal' THEN 1 END) AS transaksi_gagal
    FROM transaksi t
    JOIN detail_transaksi dt ON t.id_detail_transaksi = dt.id_detail_transaksi
    WHERE {date_filter}
    """
    
    report = fetch_data(query, params, fetch_one=True)

    if report and report['total_transaksi']:
        print(f"\nTotal Transaksi : {report['total_transaksi']}")
        print(f"Total Penghasilan : Rp {report['total_penghasilan']:,.0f}")
        print(f"Transaksi Selesai : {report['transaksi_selesai']}")
        print(f"Transaksi Gagal   : {report['transaksi_gagal']}")

        # ========== tampilkan barang terlaris sesuai periode yg dipilih ==========
        print("\n--- Barang Terlaris Pada Periode Ini ---")

        query_top_period = f"""
        SELECT p.nama_produk, SUM(dt.jumlah_produk) AS total_terjual
        FROM detail_transaksi dt
        JOIN produk p ON p.id_produk = dt.id_produk
        WHERE {date_filter}
        GROUP BY p.nama_produk
        ORDER BY total_terjual DESC
        LIMIT 5;   -- tampilkan 5 besar
        """
        
        terlaris = fetch_data(query_top_period, params)

        if terlaris:
            print(f"{'Produk':<30} {'Terjual':<10}")
            print("-"*45)
            for row in terlaris:
                print(f"{row['nama_produk']:<30} {row['total_terjual']:<10}")
        else:
            print("Belum ada transaksi produk pada periode ini.")

    else:
        print("Tidak ada data transaksi untuk periode ini.")
        
    input("\nTekan Enter untuk kembali...")


def admin_barang_terlaris():
    """Menampilkan daftar barang terlaris berdasarkan total penjualan"""
    clear_screen()
    tampilkan_header("BARANG TERLARIS")

    query = """
    SELECT p.id_produk, p.nama_produk, COALESCE(SUM(dt.jumlah_produk),0) AS total_terjual
    FROM produk p
    LEFT JOIN detail_transaksi dt ON dt.id_produk = p.id_produk
    GROUP BY p.id_produk, p.nama_produk
    ORDER BY total_terjual DESC;
    """

    data = fetch_data(query)

    if not data:
        print("Belum ada produk atau transaksi.")
        return

    print(f"{'ID':<5} {'Nama Produk':<30} {'Total Terjual':<15}")
    print("-" * 60)

    for row in data:
        print(f"{row['id_produk']:<5} {row['nama_produk']:<30} {row['total_terjual']:<15}")


def admin_menu():
    """Menu admin"""
    while True:
        clear_screen()
        tampilkan_header(f"DASHBOARD ADMIN - {CURRENT_USER['username']}")
        
        print("1. Manajemen Pengguna")
        print("2. Lihat Data Produk")
        print("3. Lihat Data Transaksi")
        print("4. Laporan Transaksi")
        print("0. Logout")
        print("=" * 70)

        choice = input("Pilih menu: ").strip()

        if choice == '1':
            admin_user_management()
        elif choice == '2':
            admin_view_products()
            input("\nTekan Enter untuk kembali...")
        elif choice == '3':
            admin_view_transactions()
            input("\nTekan Enter untuk kembali...")
        elif choice == '4':
            admin_report()
            input("\nTekan Enter untuk kembali...")
        elif choice == '0':
            break
        else:
            print("Pilihan tidak valid.")
            input("\nTekan Enter untuk kembali...")

def admin_user_management():
    """Sub-menu manajemen pengguna"""
    while True:
        clear_screen()
        tampilkan_header("MANAJEMEN PENGGUNA")
        
        print("1. Lihat Semua Pengguna")
        print("2. Tambah Pengguna")
        print("3. Hapus Pengguna")
        print("4. Edit Pengguna")  # <-- Tambahkan ini
        print("0. Kembali")
        print("=" * 70)

        choice = input("Pilih menu: ").strip()

        if choice == '1':
            admin_show_users()
            input("\nTekan Enter untuk kembali...")
        elif choice == '2':
            admin_add_user()
            input("\nTekan Enter untuk kembali...")
        elif choice == '3':
            admin_delete_user()
            input("\nTekan Enter untuk kembali...")
        elif choice == '4':
            admin_edit_user()      # <-- Panggilan fungsi edit
            input("\nTekan Enter untuk kembali...")
        elif choice == '0':
            break
        else:
            print("Pilihan tidak valid.")
            input("\nTekan Enter untuk kembali...")


# =====================================================
# MODUL PENGELOLA - MANAJEMEN PRODUK
# =====================================================
def pengelola_lihat_produk():
    """Lihat produk milik pengelola"""
    clear_screen()
    tampilkan_header("DAFTAR PRODUK ANDA")

    query = """
    SELECT p.id_produk, p.nama_produk, p.stok, p.harga, k.nama_kategori, p.diskon
    FROM produk p
    JOIN kategori k ON p.id_kategori = k.id_kategori
    WHERE p.id_user = %s
    ORDER BY p.id_produk
    """
    products = fetch_data(query, (CURRENT_USER['id_user'],))

    if not products:
        print("Belum ada produk.")
        return

    print(f"{'ID':<5} {'Nama Produk':<25} {'Stok':<8} {'Harga':<12} {'Kategori':<15} {'Diskon':<10}")
    print("-" * 80)
    for p in products:
        diskon = p['diskon'] if p.get('diskon') is not None else 0
        # tampilkan diskon dalam persen (misal 10%)
        print(f"{p['id_produk']:<5} {p['nama_produk']:<25} {p['stok']:<8} {p['harga']:<12} {p['nama_kategori']:<15} {diskon*100:>6.0f}%")

def pengelola_tambah_produk():
    """Tambah produk baru"""
    clear_screen()
    tampilkan_header("TAMBAH PRODUK BARU")
    
    nama = input("Nama produk: ").strip()
    stok = validasi_angka("Stok", 'int', 0)
    harga = validasi_angka("Harga", 'int', 1)
    
    # Tampilkan kategori
    categories = fetch_data("SELECT id_kategori, nama_kategori FROM kategori ORDER BY id_kategori")
    print("\nKategori yang tersedia:")
    for cat in categories:
        print(f"{cat['id_kategori']}. {cat['nama_kategori']}")
    
    id_kategori = validasi_angka("ID kategori", 'int', 1)
    diskon = validasi_angka("Diskon (0-100%)", 'float', 0) / 100

    query = """
    INSERT INTO produk (nama_produk, stok, harga, id_kategori, id_user, diskon)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    if execute_query(query, (nama, stok, harga, id_kategori, CURRENT_USER['id_user'], diskon)):
        print("✅ Produk berhasil ditambahkan.")
    else:
        print("❌ Gagal menambahkan produk.")

def pengelola_edit_produk():
    """Edit produk"""
    clear_screen()
    tampilkan_header("EDIT PRODUK")
    
    id_produk = validasi_angka("Masukkan ID produk yang ingin diedit", 'int', 1)

    # Ambil data lama
    query = """
    SELECT nama_produk, stok, harga, id_kategori, diskon
    FROM produk
    WHERE id_produk = %s AND id_user = %s
    """
    product = fetch_data(query, (id_produk, CURRENT_USER['id_user']), fetch_one=True)

    if not product:
        print("❌ Produk tidak ditemukan atau bukan milik Anda.")
        return

    print(f"\nProduk: {product['nama_produk']}")
    print("Tekan ENTER untuk tidak mengubah field.\n")

    nama = input(f"Nama produk ({product['nama_produk']}): ").strip() or product['nama_produk']
    
    stok_input = input(f"Stok ({product['stok']}): ").strip()
    stok = int(stok_input) if stok_input else product['stok']
    
    harga_input = input(f"Harga ({product['harga']}): ").strip()
    harga = int(harga_input) if harga_input else product['harga']
    
    kategori_input = input(f"ID kategori ({product['id_kategori']}): ").strip()
    id_kategori = int(kategori_input) if kategori_input else product['id_kategori']
    
    current_diskon = product['diskon'] if product.get('diskon') is not None else 0
    diskon_input = input(f"Diskon ({current_diskon*100:.0f}%): ").strip()
    diskon = float(diskon_input)/100 if diskon_input else current_diskon

    query = """
    UPDATE produk
    SET nama_produk = %s, stok = %s, harga = %s, id_kategori = %s, diskon = %s
    WHERE id_produk = %s AND id_user = %s
    """
    if execute_query(query, (nama, stok, harga, id_kategori, diskon, id_produk, CURRENT_USER['id_user'])):
        print("✅ Produk berhasil diupdate.")
    else:
        print("❌ Gagal mengupdate produk.")

def pengelola_hapus_produk():
    """Hapus produk"""
    clear_screen()
    tampilkan_header("HAPUS PRODUK")
    
    id_produk = validasi_angka("Masukkan ID produk yang ingin dihapus", 'int', 1)

    # Cek kepemilikan
    if not fetch_data("SELECT id_produk FROM produk WHERE id_produk = %s AND id_user = %s",
                      (id_produk, CURRENT_USER['id_user']), fetch_one=True):
        print("❌ Produk tidak ditemukan atau bukan milik Anda.")
        return

    konfirmasi = input("Yakin ingin menghapus? (y/n): ").lower()
    if konfirmasi == 'y':
        if execute_query("DELETE FROM produk WHERE id_produk = %s AND id_user = %s",
                        (id_produk, CURRENT_USER['id_user'])):
            print("✅ Produk berhasil dihapus.")
        else:
            print("❌ Gagal menghapus produk.")

def pengelola_menu():
    """Menu pengelola"""
    while True:
        clear_screen()
        tampilkan_header(f"DASHBOARD PENGELOLA - {CURRENT_USER['username']}")
        
        print("1. Lihat Produk")
        print("2. Tambah Produk")
        print("3. Edit Produk")
        print("4. Hapus Produk")
        print("0. Logout")
        print("=" * 70)

        choice = input("Pilih menu: ").strip()

        if choice == '1':
            pengelola_lihat_produk()
            input("\nTekan Enter untuk kembali...")
        elif choice == '2':
            pengelola_tambah_produk()
            input("\nTekan Enter untuk kembali...")
        elif choice == '3':
            pengelola_edit_produk()
            input("\nTekan Enter untuk kembali...")
        elif choice == '4':
            pengelola_hapus_produk()
            input("\nTekan Enter untuk kembali...")
        elif choice == '0':
            break
        else:
            print("Pilihan tidak valid.")
            input("\nTekan Enter untuk kembali...")

# =====================================================
# MODUL KASIR - TRANSAKSI
# =====================================================
def kasir_lihat_produk():
    """Lihat daftar produk untuk transaksi (tahan terhadap NULL diskon/harga)"""
    clear_screen()
    tampilkan_header("DAFTAR PRODUK TERSEDIA")
    
    query = """
    SELECT p.id_produk, p.nama_produk, p.stok, p.harga, k.nama_kategori, p.diskon
    FROM produk p
    JOIN kategori k ON p.id_kategori = k.id_kategori
    WHERE p.stok > 0
    ORDER BY p.id_produk
    """
    products = fetch_data(query)

    if not products:
        print("Tidak ada produk tersedia.")
        return []

    print(f"{'ID':<5} {'Nama Produk':<30} {'Stok':<8} {'Harga (diskon)':<18} {'Diskon':<8}")
    print("-" * 75)
    for p in products:
        # fallback untuk kolom yang mungkin NULL
        idp = p.get('id_produk', 'N/A')
        nama = p.get('nama_produk', 'N/A')
        stok = p.get('stok')
        stok_str = str(stok) if stok is not None else '0'
        harga = p.get('harga')
        diskon = p.get('diskon') if p.get('diskon') is not None else 0.0

        # hitung harga setelah diskon dengan aman
        try:
            harga_val = harga if harga is not None else 0
            harga_diskon_val = harga_val * (1 - float(diskon))
            harga_diskon_str = f"Rp {harga_diskon_val:,.0f}"
        except Exception:
            harga_diskon_str = "-" if harga is None else str(harga)

        # tampilkan persentase diskon
        try:
            diskon_pct = f"{diskon*100:.0f}%"
        except Exception:
            diskon_pct = str(diskon)

        print(f"{idp:<5} {nama:<30} {stok_str:<8} {harga_diskon_str:<18} {diskon_pct:<8}")
    
    return products

def kasir_tambah_transaksi():
    """Proses transaksi baru"""
    clear_screen()
    tampilkan_header("TRANSAKSI BARU")
    
    products = kasir_lihat_produk()
    if not products:
        return
    
    print("\n" + "=" * 70)
    items = []
    
    while True:
        print(f"\nItem ke-{len(items) + 1}")
        id_produk = validasi_angka("ID Produk (0 untuk selesai)", 'int', 0)
        
        if id_produk == 0:
            if len(items) == 0:
                print("Minimal harus ada 1 item!")
                continue
            break
        
        # Cari produk
        produk = next((p for p in products if p['id_produk'] == id_produk), None)
        if not produk:
            print("❌ Produk tidak ditemukan!")
            continue
        
        print(f"Produk: {produk['nama_produk']}")
        print(f"Stok tersedia: {produk['stok']}")
        diskon = produk['diskon'] if produk.get('diskon') is not None else 0
        print(f"Harga: Rp {produk['harga']:,.0f} (Diskon {diskon*100:.0f}%)")
        
        jumlah = validasi_angka("Jumlah", 'int', 1)
        
        if jumlah > produk['stok']:
            print("❌ Stok tidak mencukupi!")
            continue
        
        harga_final = produk['harga'] * (1 - diskon)
        total_item = jumlah * harga_final
        
        items.append({
            'id_produk': id_produk,
            'nama_produk': produk['nama_produk'],
            'jumlah': jumlah,
            'harga': harga_final,
            'total': total_item
        })
        
        print(f"✅ Item ditambahkan: {produk['nama_produk']} x {jumlah} = Rp {total_item:,.0f}")
    
    if not items:
        return
    
    # Pilih metode pembayaran
    print("\n" + "=" * 70)
    print("METODE PEMBAYARAN:")
    metode_list = fetch_data("SELECT id_metode, nama_metode FROM metode_pembayaran ORDER BY id_metode")
    for m in metode_list:
        print(f"{m['id_metode']}. {m['nama_metode']}")
    
    id_metode = validasi_angka("Pilih metode pembayaran", 'int', 1)
    
    # Hitung total
    total_harga = sum(item['total'] for item in items)
    
    # Tampilkan ringkasan
    clear_screen()
    tampilkan_header("RINGKASAN TRANSAKSI")
    print(f"{'Produk':<30} {'Qty':<8} {'Harga':<12} {'Total':<12}")
    print("-" * 70)
    for item in items:
        print(f"{item['nama_produk']:<30} {item['jumlah']:<8} {item['harga']:>10,.0f} {item['total']:>10,.0f}")
    print("-" * 70)
    print(f"{'TOTAL':<56} {total_harga:>10,.0f}")
    
    konfirmasi = input("\nProses transaksi? (y/n): ").lower()
    if konfirmasi != 'y':
        print("Transaksi dibatalkan.")
        return
    
    # Simpan ke database
    conn = connect_db()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Insert setiap item
        for item in items:
            # Insert detail_transaksi
            cursor.execute("""
                INSERT INTO detail_transaksi (tanggal, id_produk, jumlah_produk)
                VALUES (%s, %s, %s)
                RETURNING id_detail_transaksi;
            """, (datetime.now(), item['id_produk'], item['jumlah']))
            
            id_detail = cursor.fetchone()[0]
            
            # Insert transaksi
            cursor.execute("""
                INSERT INTO transaksi (id_user, id_detail_transaksi, id_metode, status, total_harga)
                VALUES (%s, %s, %s, 'Selesai', %s)
            """, (CURRENT_USER['id_user'], id_detail, id_metode, item['total']))
            
            # Update stok
            cursor.execute("""
                UPDATE produk SET stok = stok - %s WHERE id_produk = %s
            """, (item['jumlah'], item['id_produk']))
        
        conn.commit()
        print("\n✅ Transaksi berhasil disimpan!")
        
        # Cetak struk
        print("\n" + "=" * 70)
        print(" STRUK PEMBAYARAN - SEEDMART")
        print("=" * 70)
        print(f"Tanggal: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
        print(f"Kasir: {CURRENT_USER['username']}")
        print("-" * 70)
        print(f"{'Produk':<30} {'Qty':<8} {'Harga':<12} {'Total':<12}")
        print("-" * 70)
        for item in items:
            print(f"{item['nama_produk']:<30} {item['jumlah']:<8} {item['harga']:>10,.0f} {item['total']:>10,.0f}")
        print("-" * 70)
        print(f"{'TOTAL':<56} Rp {total_harga:>10,.0f}")
        print("=" * 70)
        print(" TERIMA KASIH ATAS KUNJUNGAN ANDA!")
        print("=" * 70)
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error saat menyimpan transaksi: {e}")
    finally:
        cursor.close()
        conn.close()

def kasir_lihat_transaksi_hari_ini():
    """Lihat transaksi hari ini"""
    clear_screen()
    tampilkan_header("TRANSAKSI HARI INI")
    
    query = """
    SELECT 
        t.id_transaksi,
        dt.tanggal,
        p.nama_produk,
        dt.jumlah_produk,
        t.total_harga,
        m.nama_metode,
        t.status
    FROM transaksi t
    JOIN detail_transaksi dt ON t.id_detail_transaksi = dt.id_detail_transaksi
    JOIN produk p ON dt.id_produk = p.id_produk
    JOIN metode_pembayaran m ON t.id_metode = m.id_metode
    WHERE t.id_user = %s AND CAST(dt.tanggal AS DATE) = CURRENT_DATE
    ORDER BY dt.tanggal DESC
    """
    transactions = fetch_data(query, (CURRENT_USER['id_user'],))

    if not transactions:
        print("Belum ada transaksi hari ini.")
        return

    total_pendapatan = 0
    for t in transactions:
        print(f"\nID: {t['id_transaksi']} | Waktu: {t['tanggal']}")
        print(f"Produk: {t['nama_produk']} ({t['jumlah_produk']}x)")
        print(f"Total: Rp {t['total_harga']:,.0f} | Metode: {t['nama_metode']} | Status: {t['status']}")
        print("-" * 70)
        total_pendapatan += t['total_harga']
    
    print(f"\nTotal Pendapatan Hari Ini: Rp {total_pendapatan:,.0f}")

def kasir_menu():
    """Menu kasir"""
    while True:
        clear_screen()
        tampilkan_header(f"DASHBOARD KASIR - {CURRENT_USER['username']}")
        
        print("1. Lihat Produk")
        print("2. Tambah Transaksi")
        print("3. Lihat Transaksi Hari Ini")
        print("0. Logout")
        print("=" * 70)

        choice = input("Pilih menu: ").strip()

        if choice == '1':
            kasir_lihat_produk()
            input("\nTekan Enter untuk kembali...")
        elif choice == '2':
            kasir_tambah_transaksi()
            input("\nTekan Enter untuk kembali...")
        elif choice == '3':
            kasir_lihat_transaksi_hari_ini()
            input("\nTekan Enter untuk kembali...")
        elif choice == '0':
            break
        else:
            print("Pilihan tidak valid.")
            input("\nTekan Enter untuk kembali...")

# =====================================================
# FUNGSI UTAMA
# =====================================================
def main():
    """Fungsi utama program"""
    while True:
        if login():
            # Arahkan ke menu sesuai role
            if CURRENT_USER['id_role'] == 1:  # Admin
                admin_menu()
            elif CURRENT_USER['id_role'] == 2:  # Pengelola
                pengelola_menu()
            elif CURRENT_USER['id_role'] == 3:  # Kasir
                kasir_menu()
            
            logout()
            
            coba_lagi = input("\nLogin dengan akun lain? (y/n): ").lower()
            if coba_lagi != 'y':
                print("\nTerima kasih telah menggunakan Sistem SeedMart!")
                break
        else:
            coba_lagi = input("\nCoba login lagi? (y/n): ").lower()
            if coba_lagi != 'y':
                print("\nTerima kasih!")
                break

if __name__ == "__main__":
    clear_screen()
    print("\n" + "=" * 70)
    print(" SELAMAT DATANG DI SISTEM SEEDMART")
    print("=" * 70)
    print("\nSistem Manajemen Toko Terintegrasi")
    print("Role: Admin | Pengelola Toko | Kasir")
    print("-" * 70)
    input("\nTekan Enter untuk memulai...")
    
    main()