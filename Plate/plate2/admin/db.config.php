<?php
// Bu dosya SADECE admin paneli tarafından kullanılacak.

// --- BU BİLGİLERİ KENDİ HOSTING BİLGİLERİNİZLE DEĞİŞTİRİN ---
$servername = "localhost"; // Genellikle localhost'tur.
$username = "pikselan_plate";
$password = "KWw7m#]mid4O@Gt-";
$dbname = "pikselan_plate";
// -----------------------------------------------------------

$conn = new mysqli($servername, $username, $password, $dbname);

if ($conn->connect_error) {
    // Tarayıcıda hata göster, json formatına gerek yok.
    die("Veritabanı bağlantı hatası: " . $conn->connect_error);
}
$conn->set_charset("utf8mb4");
?>