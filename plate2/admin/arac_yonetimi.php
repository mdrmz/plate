<?php
// admin/arac_yonetimi.php

session_start();
if (!isset($_SESSION['loggedin']) || $_SESSION['loggedin'] !== true) {
    header('Location: index.php');
    exit;
}
require '../api/db_config.php';

$message = '';

// --- FORM İŞLEMLERİ ---
if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    if (isset($_POST['action'])) {
        // YENİ KULLANICI EKLEME
        if ($_POST['action'] == 'add_user') {
            $ad = trim($_POST['ad']);
            $soyad = trim($_POST['soyad']);
            $telefon = trim($_POST['telefon']);
            $stmt = $conn->prepare("INSERT INTO kullanicilar (ad, soyad, telefon) VALUES (?, ?, ?)");
            $stmt->bind_param("sss", $ad, $soyad, $telefon);
            if($stmt->execute()) $message = "Yeni kullanıcı başarıyla eklendi.";
            else $message = "Hata: Kullanıcı eklenemedi.";
            $stmt->close();
        }
        // YENİ ARAÇ EKLEME
        elseif ($_POST['action'] == 'add_vehicle') {
            $kullanici_id = $_POST['kullanici_id'];
            $plaka = strtoupper(trim($_POST['plaka']));
            $stmt = $conn->prepare("INSERT INTO araclar (kullanici_id, plaka) VALUES (?, ?)");
            $stmt->bind_param("is", $kullanici_id, $plaka);
            if($stmt->execute()) $message = "Yeni araç başarıyla eklendi.";
            else $message = "Hata: Araç eklenemedi. Bu plaka zaten kayıtlı olabilir.";
            $stmt->close();
        }
    }
}

// --- SİLME İŞLEMLERİ ---
if (isset($_GET['action'])) {
    // KULLANICI SİLME
    if ($_GET['action'] == 'delete_user' && isset($_GET['id'])) {
        $id = $_GET['id'];
        $stmt = $conn->prepare("DELETE FROM kullanicilar WHERE id = ?");
        $stmt->bind_param("i", $id);
        if($stmt->execute()) $message = "Kullanıcı ve ilişkili araçları silindi.";
        else $message = "Hata: Kullanıcı silinemedi.";
        $stmt->close();
    }
    // ARAÇ SİLME
    elseif ($_GET['action'] == 'delete_vehicle' && isset($_GET['id'])) {
        $id = $_GET['id'];
        $stmt = $conn->prepare("DELETE FROM araclar WHERE id = ?");
        $stmt->bind_param("i", $id);
        if($stmt->execute()) $message = "Araç silindi.";
        else $message = "Hata: Araç silinemedi.";
        $stmt->close();
    }
}


// --- LİSTELEME İÇİN VERİ ÇEKME ---
$kullanicilar_sql = "SELECT id, ad, soyad FROM kullanicilar ORDER BY ad ASC";
$kullanicilar_result = $conn->query($kullanicilar_sql);
$listeleme_sql = "SELECT k.id as kullanici_id, k.ad, k.soyad, k.telefon, a.id as arac_id, a.plaka 
                  FROM kullanicilar k LEFT JOIN araclar a ON k.id = a.kullanici_id ORDER BY k.ad, k.soyad, a.plaka";
$listeleme_result = $conn->query($listeleme_sql);
$kullanici_araclari = [];
while($row = $listeleme_result->fetch_assoc()) {
    $k_id = $row['kullanici_id'];
    if (!isset($kullanici_araclari[$k_id])) {
        $kullanici_araclari[$k_id] = ['bilgi' => ['ad' => $row['ad'], 'soyad' => $row['soyad'], 'telefon' => $row['telefon']], 'araclar' => []];
    }
    if ($row['arac_id']) {
        $kullanici_araclari[$k_id]['araclar'][] = ['arac_id' => $row['arac_id'], 'plaka' => $row['plaka']];
    }
}

// URL'den gelen plaka bilgisini al (dashboard'daki "Bu Plakayı Kaydet" linki için)
$gelen_plaka = isset($_GET['plaka']) ? htmlspecialchars($_GET['plaka']) : '';
?>
    <!DOCTYPE html>
    <html>
    <head>
        <title>Kullanıcı ve Araç Yönetimi</title>
        <link rel="stylesheet" href="style.css">
    </head>
    <body>
    <div class="container">
        <h1>Kullanıcı ve Araç Yönetimi</h1>
        <p><a href="dashboard.php">Ana Panele Dön</a></p>
        <?php if($message): ?><p class="message"><?php echo $message; ?></p><?php endif; ?>

        <div style="display: flex; gap: 20px; margin-bottom: 30px;">
            <div class="form-container" style="flex: 1;">
                <h2>Yeni Kullanıcı Ekle</h2>
                <form action="arac_yonetimi.php" method="post">
                    <input type="hidden" name="action" value="add_user">
                    <input type="text" name="ad" placeholder="Ad" required> <input type="text" name="soyad" placeholder="Soyad" required>
                    <input type="text" name="telefon" placeholder="Telefon">
                    <button type="submit" class="button">Kullanıcı Ekle</button>
                </form>
            </div>
            <div class="form-container" style="flex: 1;">
                <h2>Yeni Araç Ekle</h2>
                <form action="arac_yonetimi.php" method="post">
                    <input type="hidden" name="action" value="add_vehicle">
                    <select name="kullanici_id" required>
                        <option value="">-- Araç Sahibini Seçin --</option>
                        <?php mysqli_data_seek($kullanicilar_result, 0); // İmleci başa al ?>
                        <?php while($kullanici = $kullanicilar_result->fetch_assoc()): ?>
                            <option value="<?php echo $kullanici['id']; ?>"><?php echo $kullanici['ad'] . ' ' . $kullanici['soyad']; ?></option>
                        <?php endwhile; ?>
                    </select>
                    <input type="text" name="plaka" placeholder="Plaka" value="<?php echo $gelen_plaka; ?>" required>
                    <button type="submit" class="button">Araç Ekle</button>
                </form>
            </div>
        </div>

        <h2>Mevcut Kullanıcılar ve Araçları</h2>
        <table>
            <thead><tr><th>Ad Soyad</th><th>Telefon</th><th>Araçları (Plaka)</th><th>İşlemler</th></tr></thead>
            <tbody>
            <?php foreach ($kullanici_araclari as $k_id => $data): ?>
                <tr>
                    <td><?php echo $data['bilgi']['ad'] . ' ' . $data['bilgi']['soyad']; ?></td>
                    <td><?php echo $data['bilgi']['telefon']; ?></td>
                    <td>
                        <?php if (count($data['araclar']) > 0): ?>
                            <?php foreach($data['araclar'] as $arac): ?>
                                <?php echo htmlspecialchars($arac['plaka']); ?>
                                (<a href="arac_yonetimi.php?action=delete_vehicle&id=<?php echo $arac['arac_id']; ?>" onclick="return confirm('Bu aracı silmek istediğinizden emin misiniz?');" style="color:red;">Sil</a>)<br>
                            <?php endforeach; ?>
                        <?php else: echo 'Araç yok'; endif; ?>
                    </td>
                    <td>
                        <a href="edit_user.php?id=<?php echo $k_id; ?>">Kullanıcıyı Düzenle</a><br>
                        <a href="arac_yonetimi.php?action=delete_user&id=<?php echo $k_id; ?>" onclick="return confirm('DİKKAT! Bu kullanıcıyı ve tüm araçlarını silmek istediğinizden emin misiniz?');" style="color:red; margin-top:5px; display:inline-block;">Kullanıcıyı Sil</a>
                    </td>
                </tr>
            <?php endforeach; ?>
            </tbody>
        </table>
    </div>
    </body>
    </html>
<?php $conn->close(); ?>