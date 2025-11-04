<?php
session_start();
if (!isset($_SESSION['loggedin']) || $_SESSION['loggedin'] !== true) { exit('Erişim Reddedildi.'); }
require '../../api/db_config.php';

if (isset($_POST['log_ids']) && is_array($_POST['log_ids'])) {
    $log_ids = $_POST['log_ids'];
    $ids = array_map('intval', $log_ids);
    if (empty($ids)) { header('Location: ../dashboard.php'); exit(); }
    
    $placeholders = implode(',', array_fill(0, count($ids), '?'));
    $types = str_repeat('i', count($ids));
    
    $stmt_select = $conn->prepare("SELECT resim_yolu FROM giris_cikis_loglari WHERE id IN ($placeholders)");
    $stmt_select->bind_param($types, ...$ids); $stmt_select->execute();
    $result = $stmt_select->get_result(); $files_to_delete = [];
    while ($row = $result->fetch_assoc()) {
        if (!empty($row['resim_yolu'])) { $files_to_delete[] = '../../' . $row['resim_yolu']; }
    }
    $stmt_select->close();

    $stmt_delete = $conn->prepare("DELETE FROM giris_cikis_loglari WHERE id IN ($placeholders)");
    $stmt_delete->bind_param($types, ...$ids);
    if ($stmt_delete->execute()) {
        foreach ($files_to_delete as $file_path) {
            if (file_exists($file_path)) { @unlink($file_path); }
        }
        header("Location: ../dashboard.php?status=logs_deleted");
    } else {
        header('Location: ../dashboard.php?status=error');
    }
    $stmt_delete->close();
} else {
    header('Location: ../dashboard.php');
}
$conn->close();
exit();
?>