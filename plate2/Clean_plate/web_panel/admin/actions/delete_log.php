<?php
session_start();
if (!isset($_SESSION['loggedin']) || $_SESSION['loggedin'] !== true) { exit('Erişim Reddedildi.'); }
require '../../api/db_config.php';

if (isset($_GET['id'])) {
    $log_id = intval($_GET['id']);
    $stmt_select = $conn->prepare("SELECT resim_yolu FROM giris_cikis_loglari WHERE id = ?");
    $stmt_select->bind_param("i", $log_id); $stmt_select->execute();
    $result = $stmt_select->get_result(); $log = $result->fetch_assoc();
    $stmt_select->close();

    $stmt_delete = $conn->prepare("DELETE FROM giris_cikis_loglari WHERE id = ?");
    $stmt_delete->bind_param("i", $log_id);
    if ($stmt_delete->execute()) {
        if ($log && !empty($log['resim_yolu'])) {
            $file_path = '../../' . $log['resim_yolu'];
            if (file_exists($file_path)) { @unlink($file_path); }
        }
        header('Location: ../dashboard.php?status=log_deleted');
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