<?php
// api/db_config.php
// BU DOSYA SADECE VERİTABANI BAĞLANTISI YAPAR.
// HİÇBİR HTML VEYA JSON HEADER'I GÖNDERMEZ.

// --- BU BİLGİLERİ KENDİ HOSTING BİLGİLERİNLE DEĞİŞTİR ---
$servername = "localhost";
$username = "pikselan_plate";
$password = "KWw7m#]mid4O@Gt-";
$dbname = "pikselan_plate";
// -----------------------------------------------------------

// Bağlantı oluştur
$conn = new mysqli($servername, $username, $password, $dbname);

// Bağlantıyı UTF-8 olarak ayarla
$conn->set_charset("utf8mb4");

// Bağlantıyı kontrol et
if ($conn->connect_error) {
    // Hata varsa, detaylı bir mesajla programı durdur.
    // Bu hatayı hem PHP panelinde hem de API loglarında görebileceksin.
    die("Veritabanı Bağlantısı Başarısız: " . $conn->connect_error);
}
?>