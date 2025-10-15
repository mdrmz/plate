<?php
// JSON formatında cevap vereceğimizi ve karakter setini belirtiyoruz.
header("Content-Type: application/json; charset=UTF-8");

// --- BU BİLGİLERİ KENDİ HOSTING BİLGİLERİNİZLE DEĞİŞTİRİN ---
$servername = "localhost"; // Genellikle localhost'tur.
$username = "pikselan_plate";
$password = "KWw7m#]mid4O@Gt-";
$dbname = "pikselan_plate";
// -----------------------------------------------------------

$conn = new mysqli($servername, $username, $password, $dbname);

if ($conn->connect_error) {
    echo json_encode(["success" => false, "message" => "Veritabanı bağlantı hatası."]);
    exit();
}
$conn->set_charset("utf8mb4");
?>