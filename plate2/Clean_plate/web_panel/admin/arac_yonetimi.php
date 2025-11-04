<?php
session_start();
if (!isset($_SESSION['loggedin']) || $_SESSION['loggedin'] !== true) { header('Location: index.php'); exit; }
require '../api/db_config.php';

$message = ''; $message_type = 'success';
if (isset($_GET['status']) && $_GET['status'] == 'user_updated') { $message = 'Kullanıcı bilgileri başarıyla güncellendi.'; }

if ($_SERVER['REQUEST_METHOD'] == 'POST' && isset($_POST['action'])) {
    if ($_POST['action'] == 'add_user') {
        $ad = trim($_POST['ad']); $soyad = trim($_POST['soyad']); $telefon = trim($_POST['telefon']);
        $stmt = $conn->prepare("INSERT INTO kullanicilar (ad, soyad, telefon) VALUES (?, ?, ?)");
        $stmt->bind_param("sss", $ad, $soyad, $telefon);
        if($stmt->execute()) { $message = "Yeni kullanıcı başarıyla eklendi."; } else { $message = "Hata: Kullanıcı eklenemedi."; $message_type = 'danger'; }
        $stmt->close();
    } elseif ($_POST['action'] == 'add_vehicle') {
        $kullanici_id = $_POST['kullanici_id']; $plaka = strtoupper(trim($_POST['plaka'])); $ozel_erisim = isset($_POST['ozel_erisim']) ? 1 : 0;
        $stmt = $conn->prepare("INSERT INTO araclar (kullanici_id, plaka, ozel_erisim) VALUES (?, ?, ?)");
        $stmt->bind_param("isi", $kullanici_id, $plaka, $ozel_erisim);
        if($stmt->execute()) { $message = "Yeni araç başarıyla eklendi."; } else { $message = "Hata: Araç eklenemedi. Bu plaka zaten kayıtlı olabilir."; $message_type = 'danger'; }
        $stmt->close();
    }
}

if (isset($_GET['action'])) {
    if ($_GET['action'] == 'delete_user' && isset($_GET['id'])) {
        $id = $_GET['id']; $stmt = $conn->prepare("DELETE FROM kullanicilar WHERE id = ?"); $stmt->bind_param("i", $id);
        if($stmt->execute()) { $message = "Kullanıcı ve ilişkili araçları silindi."; } else { $message = "Hata: Kullanıcı silinemedi."; $message_type = 'danger'; }
        $stmt->close();
    } elseif ($_GET['action'] == 'delete_vehicle' && isset($_GET['id'])) {
        $id = $_GET['id']; $stmt = $conn->prepare("DELETE FROM araclar WHERE id = ?"); $stmt->bind_param("i", $id);
        if($stmt->execute()) { $message = "Araç silindi."; } else { $message = "Hata: Araç silinemedi."; $message_type = 'danger'; }
        $stmt->close();
    }
}

$kullanicilar_sql = "SELECT id, ad, soyad FROM kullanicilar ORDER BY ad ASC";
$kullanicilar_result = $conn->query($kullanicilar_sql);
$listeleme_sql = "SELECT k.id as kullanici_id, k.ad, k.soyad, k.telefon, a.id as arac_id, a.plaka, a.ozel_erisim 
                  FROM kullanicilar k LEFT JOIN araclar a ON k.id = a.kullanici_id ORDER BY k.ad, k.soyad, a.plaka";
$listeleme_result = $conn->query($listeleme_sql);
$kullanici_araclari = [];
if ($listeleme_result) {
    while($row = $listeleme_result->fetch_assoc()) {
        $k_id = $row['kullanici_id'];
        if (!isset($kullanici_araclari[$k_id])) {
            $kullanici_araclari[$k_id] = ['bilgi' => ['ad' => $row['ad'], 'soyad' => $row['soyad'], 'telefon' => $row['telefon']], 'araclar' => []];
        }
        if ($row['arac_id']) { $kullanici_araclari[$k_id]['araclar'][] = ['arac_id' => $row['arac_id'], 'plaka' => $row['plaka'], 'ozel_erisim' => $row['ozel_erisim']]; }
    }
}
$gelen_plaka = isset($_GET['plaka']) ? htmlspecialchars($_GET['plaka']) : '';
?>
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kullanıcı ve Araç Yönetimi</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark sticky-top"></nav>
    <main class="container mt-4">
        <h1 class="mb-4">Kullanıcı ve Araç Yönetimi</h1>
        <?php if($message): ?>
            <div class="alert alert-<?php echo $message_type === 'success' ? 'success' : 'danger'; ?> alert-dismissible fade show" role="alert">
                <?php echo $message; ?>
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        <?php endif; ?>
        <div class="row g-4">
            <div class="col-md-5">
                <div class="card shadow-sm">
                    <div class="card-header"><h2>Yeni Kullanıcı Ekle</h2></div>
                    <div class="card-body">
                        <form action="arac_yonetimi.php" method="post">
                            <input type="hidden" name="action" value="add_user">
                            <div class="mb-3"><label class="form-label">Ad</label><input type="text" name="ad" class="form-control" required></div>
                            <div class="mb-3"><label class="form-label">Soyad</label><input type="text" name="soyad" class="form-control" required></div>
                            <div class="mb-3"><label class="form-label">Telefon</label><input type="text" name="telefon" class="form-control"></div>
                            <button type="submit" class="btn btn-primary w-100">Kullanıcı Ekle</button>
                        </form>
                    </div>
                </div>
            </div>
            <div class="col-md-7">
                <div class="card shadow-sm">
                    <div class="card-header"><h2>Yeni Araç Ekle</h2></div>
                    <div class="card-body">
                        <form action="arac_yonetimi.php" method="post">
                            <input type="hidden" name="action" value="add_vehicle">
                            <div class="mb-3"><label class="form-label">Araç Sahibi</label>
                                <select name="kullanici_id" class="form-select" required>
                                    <option value="" disabled selected>-- Sahip Seçin --</option>
                                    <?php mysqli_data_seek($kullanicilar_result, 0); ?>
                                    <?php while($kullanici = $kullanicilar_result->fetch_assoc()): ?>
                                        <option value="<?php echo $kullanici['id']; ?>"><?php echo $kullanici['ad'] . ' ' . $kullanici['soyad']; ?></option>
                                    <?php endwhile; ?>
                                </select>
                            </div>
                            <div class="mb-3"><label class="form-label">Plaka</label><input type="text" name="plaka" class="form-control" value="<?php echo $gelen_plaka; ?>" required></div>
                            <div class="form-check mb-3">
                                <input class="form-check-input" type="checkbox" name="ozel_erisim" value="1" id="ozelErisimCheck">
                                <label class="form-check-label" for="ozelErisimCheck">Kapı Açma Yetkisi (Özel Erişim)</label>
                            </div>
                            <button type="submit" class="btn btn-success w-100">Araç Ekle</button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
        <h2 class="mt-5">Mevcut Kullanıcılar ve Araçları</h2>
        <div class="table-responsive shadow-sm bg-white p-3 rounded">
            <table class="table table-striped table-hover table-bordered">
                <thead class="table-dark"><tr><th>Ad Soyad</th><th>Telefon</th><th>Araçları</th><th>İşlemler</th></tr></thead>
                <tbody>
                    <?php if (count($kullanici_araclari) > 0): ?>
                        <?php foreach ($kullanici_araclari as $k_id => $data): ?>
                            <tr>
                                <td><?php echo $data['bilgi']['ad'] . ' ' . $data['bilgi']['soyad']; ?></td>
                                <td><?php echo $data['bilgi']['telefon']; ?></td>
                                <td>
                                    <?php if (count($data['araclar']) > 0): ?>
                                        <ul class="list-unstyled mb-0">
                                        <?php foreach($data['araclar'] as $arac): ?>
                                            <li>
                                                <span class="badge <?php echo $arac['ozel_erisim'] ? 'bg-success' : 'bg-secondary'; ?> me-2"><?php echo htmlspecialchars($arac['plaka']); ?></span>
                                                <?php if($arac['ozel_erisim']): ?><span class="badge bg-info">Yetkili</span><?php endif; ?>
                                                <a href="arac_yonetimi.php?action=delete_vehicle&id=<?php echo $arac['arac_id']; ?>" onclick="return confirm('Bu aracı silmek istediğinizden emin misiniz?');" class="text-danger ms-2">[Sil]</a>
                                            </li>
                                        <?php endforeach; ?>
                                        </ul>
                                    <?php else: echo '<span class="text-muted">Kayıtlı araç yok</span>'; endif; ?>
                                </td>
                                <td>
                                    <a href="edit_user.php?id=<?php echo $k_id; ?>" class="btn btn-sm btn-warning">Düzenle</a>
                                    <a href="arac_yonetimi.php?action=delete_user&id=<?php echo $k_id; ?>" onclick="return confirm('DİKKAT! Kullanıcı ve tüm araçları silinecektir. Emin misiniz?');" class="btn btn-sm btn-danger ms-1">Sil</a>
                                </td>
                            </tr>
                        <?php endforeach; ?>
                    <?php else: ?>
                        <tr><td colspan="4" class="text-center">Kayıtlı kullanıcı bulunmamaktadır.</td></tr>
                    <?php endif; ?>
                </tbody>
            </table>
        </div>
    </main>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
<?php $conn->close(); ?>