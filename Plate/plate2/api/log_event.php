<?php
require 'db_config.php';

// Metin verisi $_POST'tan, dosya verisi $_FILES'tan gelir.
if (!isset($_POST['plate']) || empty($_POST['plate'])) {
    echo json_encode(["success" => false, "message" => "Plaka bilgisi eksik."]);
    exit();
}

$plate = strtoupper(trim($_POST['plate']));
$image_path = null;

// --- GÖRÜNTÜ YÜKLEME İŞLEMİ ---
if (isset($_FILES['image']) && $_FILES['image']['error'] == 0) {
    $upload_dir = 'uploads/'; // Resimlerin kaydedileceği klasör
    // Benzersiz bir dosya adı oluştur: plaka_zaman_damgasi.jpg
    $filename = $plate . '_' . time() . '.jpg';
    $target_file = $upload_dir . $filename;

    if (move_uploaded_file($_FILES['image']['tmp_name'], $target_file)) {
        $image_path = $target_file; // Veritabanına kaydedilecek dosya yolu
    }
}
// --------------------------------

// --- VERİTABANI İŞLEMLERİ (Öncekiyle aynı mantık) ---
$stmt = $conn->prepare("SELECT id, owner_firstname, owner_lastname, status FROM vehicles WHERE plate = ?");
$stmt->bind_param("s", $plate);
$stmt->execute();
$result = $stmt->get_result();
$vehicle_id = null;
$vehicle_status_message = "";

if ($result->num_rows > 0) {
    $vehicle = $result->fetch_assoc();
    $vehicle_id = $vehicle['id'];
    $owner_full_name = $vehicle['owner_firstname'] . ' ' . $vehicle['owner_lastname'];
    $vehicle_status_message = ($vehicle['status'] == 'registered') ? "Kayıtlı Araç ($owner_full_name)" : "Misafir Araç";
} else {
    $stmt_insert = $conn->prepare("INSERT INTO vehicles (plate, owner_firstname, owner_lastname, status) VALUES (?, 'Bilinmeyen', 'Misafir', 'guest')");
    $stmt_insert->bind_param("s", $plate);
    $stmt_insert->execute();
    $vehicle_id = $stmt_insert->insert_id;
    $stmt_insert->close();
    $vehicle_status_message = "Yeni Misafir Araç";
}
$stmt->close();

$stmt_log = $conn->prepare("SELECT id FROM logs WHERE vehicle_id = ? AND status = 'inside'");
$stmt_log->bind_param("i", $vehicle_id);
$stmt_log->execute();
$log_result = $stmt_log->get_result();

if ($log_result->num_rows > 0) {
    // ÇIKIŞ İŞLEMİ: Çıkış resmini ve zamanını güncelle
    $log = $log_result->fetch_assoc();
    $log_id = $log['id'];

    $stmt_update = $conn->prepare("UPDATE logs SET exit_time = CURRENT_TIMESTAMP, status = 'outside', exit_image_path = ? WHERE id = ?");
    $stmt_update->bind_param("si", $image_path, $log_id);
    if ($stmt_update->execute()) {
        echo json_encode(["success" => true, "message" => "$vehicle_status_message ($plate) çıkış yaptı."]);
    }
    $stmt_update->close();
} else {
    // GİRİŞ İŞLEMİ: Giriş resmini ve zamanını ekle
    $stmt_insert_log = $conn->prepare("INSERT INTO logs (vehicle_id, entry_time, entry_image_path, status) VALUES (?, CURRENT_TIMESTAMP, ?, 'inside')");
    $stmt_insert_log->bind_param("is", $vehicle_id, $image_path);
    if ($stmt_insert_log->execute()) {
        echo json_encode(["success" => true, "message" => "$vehicle_status_message ($plate) giriş yaptı."]);
    }
    $stmt_insert_log->close();
}
$conn->close();
?>