<?php
// admin/dashboard.php

session_start();
if (!isset($_SESSION['loggedin']) || $_SESSION['loggedin'] !== true) {
    header('Location: index.php');
    exit;
}
require '../api/db_config.php';

$sql = "SELECT
            l.id as log_id, l.plaka, l.islem_tipi, l.islem_zamani, l.resim_yolu, l.arac_id,
            k.ad, k.soyad
        FROM giris_cikis_loglari l
        LEFT JOIN araclar a ON l.arac_id = a.id
        LEFT JOIN kullanicilar k ON a.kullanici_id = k.id
        ORDER BY l.islem_zamani DESC";
$result = $conn->query($sql);
?>
    <!DOCTYPE html>
    <html>
    <head>
        <title>Yönetim Paneli</title>
        <link rel="stylesheet" href="style.css">
    </head>
    <body>
    <div class="container">
        <h1>Giriş/Çıkış Kayıtları</h1>
        <p>Hoşgeldin, <?php echo htmlspecialchars($_SESSION['username']); ?>! | <a href="arac_yonetimi.php">Araç/Kullanıcı Yönetimi</a> | <a href="logout.php">Çıkış Yap</a></p>

        <table>
            <thead>
            <tr>
                <th>Durum</th>
                <th>Plaka</th>
                <th>Araç Sahibi</th>
                <th>İşlem Tipi</th>
                <th>İşlem Zamanı</th>
                <th>Görüntü</th>
            </tr>
            </thead>
            <tbody>
            <?php if ($result->num_rows > 0): ?>
                <?php while($row = $result->fetch_assoc()): ?>
                    <tr class="<?php echo ($row['arac_id']) ? 'registered-row' : 'unregistered-row'; ?>">
                        <td>
                            <?php if($row['arac_id']): ?>
                                <span class="status registered">Kayıtlı</span>
                            <?php else: ?>
                                <span class="status unregistered">Yabancı</span>
                            <?php endif; ?>
                        </td>
                        <td><?php echo htmlspecialchars($row['plaka']); ?></td>
                        <td>
                            <?php
                            if($row['ad']) {
                                echo htmlspecialchars($row['ad'] . ' ' . $row['soyad']);
                            } else {
                                echo '<a href="arac_yonetimi.php?action=add_vehicle&plaka=' . urlencode($row['plaka']) . '">Bu Plakayı Kaydet</a>';
                            }
                            ?>
                        </td>
                        <td><?php echo ucfirst($row['islem_tipi']); ?></td>
                        <td><?php echo $row['islem_zamani']; ?></td>
                        <td>
                            <?php if($row['resim_yolu']): ?>
                                <a href="../<?php echo $row['resim_yolu']; ?>" target="_blank">
                                    <img src="../<?php echo $row['resim_yolu']; ?>" width="100">
                                </a>
                            <?php endif; ?>
                        </td>
                    </tr>
                <?php endwhile; ?>
            <?php else: ?>
                <tr><td colspan="6">Henüz kayıt bulunmamaktadır.</td></tr>
            <?php endif; ?>
            </tbody>
        </table>
    </div>
    </body>
    </html>
<?php $conn->close(); ?>