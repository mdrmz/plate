<?php
// admin/index.php
session_start();
require '../api/db_config.php'; // Veritabanı bağlantısı
$error = '';

// Eğer kullanıcı zaten giriş yapmışsa, dashboard'a yönlendir
if (isset($_SESSION['loggedin']) && $_SESSION['loggedin'] === true) {
    header('Location: dashboard.php');
    exit;
}

// Form gönderildiğinde
if ($_SERVER['REQUEST_METHOD'] == 'POST' && isset($_POST['username']) && isset($_POST['password'])) {
    $username = $_POST['username'];
    
    // Kullanıcıyı veritabanından bul (admin_kullanicilar tablosundan)
    $stmt = $conn->prepare("SELECT sifre FROM admin_kullanicilar WHERE kullanici_adi = ?");
    $stmt->bind_param("s", $username);
    $stmt->execute();
    $result = $stmt->get_result();
    
    if ($result->num_rows === 1) {
        $user = $result->fetch_assoc();
        // Şifreyi doğrula (SQL'deki hash'lenmiş şifre ile)
        if (password_verify($_POST['password'], $user['sifre'])) {
            // Başarılı giriş
            $_SESSION['loggedin'] = true;
            $_SESSION['username'] = $username;
            header('Location: dashboard.php'); // Başarılı olunca dashboard'a git
            exit;
        } else {
            $error = 'Geçersiz kullanıcı adı veya şifre!';
        }
    } else {
        $error = 'Geçersiz kullanıcı adı veya şifre!';
    }
    $stmt->close();
}
$conn->close();
?>
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>Yönetim Paneli Girişi</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        html, body {
            height: 100%;
        }
        body {
            display: flex;
            align-items: center;
            justify-content: center;
            background-color: #f8f9fa;
        }
        .login-container {
            width: 100%;
            max-width: 400px;
            padding: 2.5rem;
            background: #ffffff;
            border-radius: 10px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        }
        .login-container h2 {
            font-weight: 700;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <h2 class="text-center mb-4">🅿️ Admin Girişi</h2>
        <form method="post" action="index.php">
            <div class="mb-3">
                <label for="username" class="form-label">Kullanıcı Adı</label>
                <input type="text" class="form-control" id="username" name="username" required>
            </div>
            <div class="mb-3">
                <label for="password" class="form-label">Şifre</label>
                <input type="password" class="form-control" id="password" name="password" required>
            </div>
            <?php if ($error): ?>
                <div class="alert alert-danger" role="alert"><?php echo $error; ?></div>
            <?php endif; ?>
            <button type="submit" class="btn btn-primary w-100 btn-lg">Giriş Yap</button>
        </form>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>