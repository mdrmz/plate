<?php
session_start();
if (!isset($_SESSION['loggedin']) || $_SESSION['loggedin'] !== true) { header('Location: index.php'); exit; }
require '../api/db_config.php';

$message = ''; $message_type = 'success'; $user_id = null;

if ($_SERVER['REQUEST_METHOD'] == 'POST' && isset($_POST['id'])) {
    // --- KULLANICI GÜNCELLEME İŞLEMİ ---
    $user_id = $_POST['id'];
    $ad = trim($_POST['ad']); $soyad = trim($_POST['soyad']); $telefon = trim($_POST['telefon']);
    $stmt = $conn->prepare("UPDATE kullanicilar SET ad = ?, soyad = ?, telefon = ? WHERE id = ?");
    $stmt->bind_param("sssi", $ad, $soyad, $telefon, $user_id);
    if($stmt->execute()) { $message = 'Kullanıcı bilgileri güncellendi.'; }
    else { $message = 'Hata: Kullanıcı güncellenemedi.'; $message_type = 'danger'; }
    $stmt->close();

    // --- ARAÇ YETKİLERİNİ GÜNCELLEME İŞLEMİ ---
    // Önce bu kullanıcıya ait tüm araçların yetkisini SIFIRLA
    $stmt_reset = $conn->prepare("UPDATE araclar SET ozel_erisim = 0 WHERE kullanici_id = ?");
    $stmt_reset->bind_param("i", $user_id);
    $stmt_reset->execute();
    $stmt_reset->close();
    
    // Şimdi sadece formda seçili gelen araçlara yetki VER
    if (isset($_POST['ozel_erisim_araclar']) && is_array($_POST['ozel_erisim_araclar'])) {
        $yetkili_araclar = $_POST['ozel_erisim_araclar'];
        $placeholders = implode(',', array_fill(0, count($yetkili_araclar), '?'));
        $types = str_repeat('i', count($yetkili_araclar));
        
        $stmt_set = $conn->prepare("UPDATE araclar SET ozel_erisim = 1 WHERE kullanici_id = ? AND id IN ($placeholders)");
        $stmt_set->bind_param("i" . $types, $user_id, ...$yetkili_araclar);
        $stmt_set->execute();
        $stmt_set->close();
        $message .= ' Araç yetkileri güncellendi.';
    }
}

// --- BİLGİLERİ GETİRME (Sayfa ilk açıldığında) ---
if (isset($_GET['id'])) { $user_id = $_GET['id']; }
if ($user_id === null) { header('Location: arac_yonetimi.php'); exit; }

$stmt = $conn->prepare("SELECT * FROM kullanicilar WHERE id = ?");
$stmt->bind_param("i", $user_id); $stmt->execute();
$result = $stmt->get_result(); $user = $result->fetch_assoc();
$stmt->close();
if (!$user) { header('Location: arac_yonetimi.php'); exit; }

// Kullanıcıya ait araçları çek
$stmt_araclar = $conn->prepare("SELECT id, plaka, ozel_erisim FROM araclar WHERE kullanici_id = ? ORDER BY plaka");
$stmt_araclar->bind_param("i", $user_id);
$stmt_araclar->execute();
$araclar = $stmt_araclar->get_result();
?>
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kullanıcı Düzenle</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark sticky-top"></nav>
    <main class="container mt-4">
        <h1 class="mb-4">Kullanıcı Bilgilerini Düzenle</h1>
        <p><a href="arac_yonetimi.php" class="btn btn-secondary">← Yönetim Paneline Geri Dön</a></p>
        <?php if($message): ?>
            <div class="alert alert-<?php echo $message_type; ?> alert-dismissible fade show" role="alert">
                <?php echo $message; ?>
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        <?php endif; ?>
        <form action="edit_user.php" method="post">
            <input type="hidden" name="id" value="<?php echo $user['id']; ?>">
            <div class="row">
                <div class="col-md-6">
                    <div class="card shadow-sm">
                        <div class="card-header"><h2>Kullanıcı Bilgileri</h2></div>
                        <div class="card-body">
                            <div class="mb-3"><label class="form-label">Ad</label><input type="text" name="ad" class="form-control" value="<?php echo htmlspecialchars($user['ad']); ?>" required></div>
                            <div class="mb-3"><label class="form-label">Soyad</label><input type="text" name="soyad" class="form-control" value="<?php echo htmlspecialchars($user['soyad']); ?>" required></div>
                            <div class="mb-3"><label class="form-label">Telefon</label><input type="text" name="telefon" class="form-control" value="<?php echo htmlspecialchars($user['telefon']); ?>"></div>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card shadow-sm">
                        <div class="card-header"><h2>Araç Yetkileri</h2></div>
                        <div class="card-body">
                            <h6>Kapı Açma Yetkisi Olan Araçlar</h6>
                            <p class="text-muted">Kapıyı açmasını istediğiniz araçları seçin.</p>
                            <?php if ($araclar->num_rows > 0): ?>
                                <?php while($arac = $araclar->fetch_assoc()): ?>
                                    <div class="form-check">
                                        <input class="form-check-input" type="checkbox" 
                                               name="ozel_erisim_araclar[]" 
                                               value="<?php echo $arac['id']; ?>" 
                                               id="arac_<?php echo $arac['id']; ?>"
                                               <?php if($arac['ozel_erisim'] == 1) echo 'checked'; ?>>
                                        <label class="form-check-label" for="arac_<?php echo $arac['id']; ?>">
                                            <?php echo htmlspecialchars($arac['plaka']); ?>
                                        </label>
                                    </div>
                                <?php endwhile; ?>
                            <?php else: ?>
                                <p class="text-muted">Bu kullanıcıya ait kayıtlı araç bulunmamaktadır.</p>
                            <?php endif; ?>
                        </div>
                    </div>
                </div>
            </div>
            <div class="mt-4">
                <button type="submit" class="btn btn-success btn-lg w-100">Tüm Bilgileri Güncelle</button>
            </div>
        </form>
    </main>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
<?php $conn->close(); ?>