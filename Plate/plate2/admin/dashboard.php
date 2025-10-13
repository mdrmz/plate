<?php
session_start();
if (!isset($_SESSION['loggedin']) || $_SESSION['loggedin'] !== true) {
    header('Location: index.php');
    exit;
}
require '../api/db_config.php'; // Veritabanı bağlantısını bir üst dizindeki api klasöründen al

// Veritabanından tüm logları, araç bilgileriyle birleştirerek çek
$sql = "SELECT
            l.entry_time,
            l.exit_time,
            l.entry_image_path,
            v.plate,
            v.owner_firstname,
            v.owner_lastname,
            v.owner_phone
        FROM logs l
        JOIN vehicles v ON l.vehicle_id = v.id
        ORDER BY l.entry_time DESC";
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
        <p>Hoşgeldin, <?php echo $_SESSION['username']; ?>! <a href="logout.php">Çıkış Yap</a></p>

        <table>
            <thead>
                <tr>
                    <th>Plaka</th>
                    <th>Sahip Adı Soyadı</th>
                    <th>Telefon</th>
                    <th>Giriş Zamanı</th>
                    <th>Giriş Görüntüsü</th>
                    <th>Çıkış Zamanı</th>
                </tr>
            </thead>
            <tbody>
                <?php if ($result->num_rows > 0): ?>
                    <?php while($row = $result->fetch_assoc()): ?>
                        <tr>
                            <td><?php echo $row['plate']; ?></td>
                            <td><?php echo $row['owner_firstname'] . ' ' . $row['owner_lastname']; ?></td>
                            <td><?php echo $row['owner_phone']; ?></td>
                            <td><?php echo $row['entry_time']; ?></td>
                            <td>
                                <?php if($row['entry_image_path']): ?>
                                    <a href="../api/<?php echo $row['entry_image_path']; ?>" target="_blank">
                                        <img src="../api/<?php echo $row['entry_image_path']; ?>" width="100">
                                    </a>
                                <?php else: ?>
                                    Görüntü Yok
                                <?php endif; ?>
                            </td>
                            <td><?php echo $row['exit_time'] ? $row['exit_time'] : 'Henüz Çıkmadı'; ?></td>
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