<?php
require 'db_config.php';

$response = ['status' => 'error', 'message' => 'Geçersiz istek.'];

if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    if (isset($_POST['plate']) && isset($_POST['gate']) && isset($_FILES['image'])) {
        $plate = strtoupper(trim($_POST['plate']));
        $gate = trim($_POST['gate']); // 'giris' veya 'cikis'
        $image_file = $_FILES['image'];
        $db_image_path = null;

        if ($image_file['error'] == 0) {
            $upload_dir = '../uploads/' . date('Y-m-d') . '/';
            if (!is_dir($upload_dir)) { @mkdir($upload_dir, 0777, true); }
            $image_name = uniqid() . '-' . preg_replace("/[^a-zA-Z0-9-_\.]/", "", basename($image_file['name']));
            $target_file = $upload_dir . $image_name;
            if (move_uploaded_file($image_file['tmp_name'], $target_file)) {
                $db_image_path = 'uploads/' . date('Y-m-d') . '/' . $image_name;
            }
        }
        
        $arac_id = null;
        $stmt_check_vehicle = $conn->prepare("SELECT id FROM araclar WHERE plaka = ?");
        $stmt_check_vehicle->bind_param("s", $plate);
        $stmt_check_vehicle->execute();
        $result = $stmt_check_vehicle->get_result();
        if ($result->num_rows > 0) {
            $arac = $result->fetch_assoc();
            $arac_id = $arac['id'];
        }
        $stmt_check_vehicle->close();
        
        $stmt_insert_log = $conn->prepare("INSERT INTO giris_cikis_loglari (plaka, arac_id, islem_tipi, resim_yolu) VALUES (?, ?, ?, ?)");
        $stmt_insert_log->bind_param("siss", $plate, $arac_id, $gate, $db_image_path);
        if ($stmt_insert_log->execute()) {
            $response = ['status' => 'success', 'message' => "Log başarıyla kaydedildi: Plaka=$plate, İşlem=$gate"];
        } else {
            $response['message'] = 'Veritabanına kayıt hatası: ' . $stmt_insert_log->error;
        }
        $stmt_insert_log->close();
    } else {
        $response['message'] = 'Eksik parametreler: plate, gate ve image gereklidir.';
    }
}
$conn->close();
echo json_encode($response);
?>