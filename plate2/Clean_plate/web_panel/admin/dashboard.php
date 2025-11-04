<?php
session_start();
if (!isset($_SESSION['loggedin']) || $_SESSION['loggedin'] !== true) {
    header('Location: index.php');
    exit;
}
require '../api/db_config.php';

// --- GELİŞMİŞ FİLTRELEME MANTIĞI ---
$where_clauses = []; $params = []; $types = '';
$search_term_get = isset($_GET['search']) ? trim($_GET['search']) : '';
$status_get = isset($_GET['status']) ? $_GET['status'] : '';
$gate_get = isset($_GET['gate']) ? $_GET['gate'] : '';
$start_date_get = isset($_GET['start_date']) ? $_GET['start_date'] : '';
$end_date_get = isset($_GET['end_date']) ? $_GET['end_date'] : '';

if (!empty($search_term_get)) {
    $where_clauses[] = "(l.plaka LIKE ? OR k.ad LIKE ? OR k.soyad LIKE ?)";
    $search_like = '%' . $search_term_get . '%';
    array_push($params, $search_like, $search_like, $search_like);
    $types .= 'sss';
}
if ($status_get === 'registered') { $where_clauses[] = "l.arac_id IS NOT NULL"; } 
elseif ($status_get === 'unregistered') { $where_clauses[] = "l.arac_id IS NULL"; }
if (!empty($gate_get)) {
    $where_clauses[] = "l.islem_tipi = ?"; $params[] = $gate_get; $types .= 's';
}
if (!empty($start_date_get) && !empty($end_date_get)) {
    $where_clauses[] = "DATE(l.islem_zamani) BETWEEN ? AND ?";
    array_push($params, $start_date_get, $end_date_get); $types .= 'ss';
}

$sql = "SELECT l.id as log_id, l.plaka, l.islem_tipi, l.islem_zamani, l.resim_yolu, l.arac_id, k.ad, k.soyad
        FROM giris_cikis_loglari l
        LEFT JOIN araclar a ON l.arac_id = a.id
        LEFT JOIN kullanicilar k ON a.kullanici_id = k.id";
if (!empty($where_clauses)) { $sql .= " WHERE " . implode(' AND ', $where_clauses); }
$sql .= " ORDER BY l.islem_zamani DESC";

$stmt = $conn->prepare($sql);
if (!empty($params)) { $stmt->bind_param($types, ...$params); }
$stmt->execute();
$result = $stmt->get_result();
?>
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Yönetim Paneli - Ana Sayfa</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark sticky-top">
        <div class="container-fluid">
            <a class="navbar-brand" href="#">🅿️ Piksel LPR Panel</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav me-auto mb-2 mb-lg-0">
                    <li class="nav-item"><a class="nav-link active" href="dashboard.php">Ana Panel</a></li>
                    <li class="nav-item"><a class="nav-link" href="arac_yonetimi.php">Araç/Kullanıcı Yönetimi</a></li>
                </ul>
                <span class="navbar-text text-white me-3">Hoşgeldin, <?php echo htmlspecialchars($_SESSION['username']); ?>!</span>
                <a href="logout.php" class="btn btn-outline-light">Çıkış Yap</a>
            </div>
        </div>
    </nav>

    <main class="container mt-4">
        <h1 class="mb-4">Giriş/Çıkış Hareketleri</h1>
        
        <div class="card mb-4">
            <div class="card-header">Filtreleme Seçenekleri</div>
            <div class="card-body">
                <form method="GET" action="dashboard.php" class="row g-3">
                    <div class="col-md-4">
                        <label class="form-label">Plaka veya İsim Ara</label>
                        <input type="text" class="form-control" name="search" value="<?php echo htmlspecialchars($search_term_get); ?>" placeholder="Plaka, ad, soyad...">
                    </div>
                    <div class="col-md-2"><label class="form-label">Durum</label>
                        <select name="status" class="form-select">
                            <option value="">Tümü</option>
                            <option value="registered" <?php if($status_get == 'registered') echo 'selected'; ?>>Kayıtlı</option>
                            <option value="unregistered" <?php if($status_get == 'unregistered') echo 'selected'; ?>>Yabancı</option>
                        </select>
                    </div>
                    <div class="col-md-2"><label class="form-label">İşlem Tipi</label>
                        <select name="gate" class="form-select">
                            <option value="">Tümü</option>
                            <option value="giris" <?php if($gate_get == 'giris') echo 'selected'; ?>>Giriş</option>
                            <option value="cikis" <?php if($gate_get == 'cikis') echo 'selected'; ?>>Çıkış</option>
                        </select>
                    </div>
                    <div class="col-md-2"><label class="form-label">Başlangıç</label><input type="date" class="form-control" name="start_date" value="<?php echo htmlspecialchars($start_date_get); ?>"></div>
                    <div class="col-md-2"><label class="form-label">Bitiş</label><input type="date" class="form-control" name="end_date" value="<?php echo htmlspecialchars($end_date_get); ?>"></div>
                    <div class="col-12 d-flex justify-content-end">
                        <a href="dashboard.php" class="btn btn-secondary me-2">Filtreyi Temizle</a>
                        <button type="submit" class="btn btn-primary">Filtrele</button>
                    </div>
                </form>
            </div>
        </div>
        
        <form id="bulk-delete-form" action="actions/delete_logs_bulk.php" method="post" onsubmit="return confirm('Seçili olan tüm kayıtları kalıcı olarak silmek istediğinizden emin misiniz?');">
            <div class="table-responsive shadow-sm bg-white p-3 rounded">
                <button type="submit" class="btn btn-danger mb-3">Seçili Olanları Sil</button>
                <table class="table table-striped table-hover table-bordered align-middle">
                    <thead class="table-dark">
                        <tr>
                            <th class="text-center"><input type="checkbox" id="select-all"></th>
                            <th>Durum</th><th>Plaka</th><th>Araç Sahibi</th>
                            <th>İşlem Tipi</th><th>İşlem Zamanı</th>
                            <th class="text-center">Görüntü</th><th class="text-center">İşlem</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php if ($result->num_rows > 0): ?>
                            <?php while($row = $result->fetch_assoc()): ?>
                                <tr>
                                    <td class="text-center"><input type="checkbox" name="log_ids[]" value="<?php echo $row['log_id']; ?>" class="log-checkbox"></td>
                                    <td class="text-center">
                                        <?php if($row['arac_id']): ?><span class="status-badge status-registered">Kayıtlı</span><?php else: ?><span class="status-badge status-unregistered">Yabancı</span><?php endif; ?>
                                    </td>
                                    <td><strong><?php echo htmlspecialchars($row['plaka']); ?></strong></td>
                                    <td>
                                        <?php 
                                        if($row['ad']) { echo htmlspecialchars($row['ad'].' '.$row['soyad']); } 
                                        else { echo '<a href="arac_yonetimi.php?plaka='.urlencode($row['plaka']).'" class="btn btn-sm btn-primary">Bu Plakayı Kaydet</a>'; }
                                        ?>
                                    </td>
                                    <td><?php echo ucfirst($row['islem_tipi']); ?></td>
                                    <td><?php echo date("d.m.Y H:i:s", strtotime($row['islem_zamani'])); ?></td>
                                    <td class="text-center">
                                        <?php if($row['resim_yolu']): ?>
                                            <a href="../<?php echo $row['resim_yolu']; ?>" target="_blank"><img src="../<?php echo $row['resim_yolu']; ?>" width="120" class="img-thumbnail"></a>
                                        <?php endif; ?>
                                    </td>
                                    <td class="text-center">
                                        <a href="actions/delete_log.php?id=<?php echo $row['log_id']; ?>" class="btn btn-sm btn-outline-danger" onclick="return confirm('Bu kaydı silmek istediğinizden emin misiniz?');">Sil</a>
                                    </td>
                                </tr>
                            <?php endwhile; ?>
                        <?php else: ?>
                            <tr><td colspan="8" class="text-center p-4">Filtreye uygun kayıt bulunamadı veya hiç kayıt yok.</td></tr>
                        <?php endif; ?>
                    </tbody>
                </table>
            </div>
        </form>
    </main>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        document.getElementById('select-all').addEventListener('click', function(event) {
            var checkboxes = document.querySelectorAll('.log-checkbox');
            for (var checkbox of checkboxes) {
                checkbox.checked = event.target.checked;
            }
        });
    </script>
</body>
</html>
<?php $conn->close(); ?>