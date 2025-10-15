<?php
// admin/index.php

session_start();
$error = '';

// Eğer kullanıcı zaten giriş yapmışsa, dashboard'a yönlendir
if (isset($_SESSION['loggedin']) && $_SESSION['loggedin'] === true) {
    header('Location: dashboard.php');
    exit;
}

// Form gönderildiğinde
if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    // Gerçek bir projede kullanıcı adı ve şifreyi veritabanından kontrol etmelisiniz.
    // Şimdilik basit bir kontrol yapıyoruz.
    $valid_username = 'admin';
    $valid_password = '123'; // Lütfen bu şifreyi daha sonra değiştirin!

    if (isset($_POST['username']) && isset($_POST['password'])) {
        if ($_POST['username'] == $valid_username && $_POST['password'] == $valid_password) {
            // Bilgiler doğru, session başlat
            $_SESSION['loggedin'] = true;
            $_SESSION['username'] = $valid_username;
            header('Location: dashboard.php');
            exit;
        } else {
            $error = 'Geçersiz kullanıcı adı veya şifre!';
        }
    }
}
?>
<!DOCTYPE html>
<html>
<head>
    <title>Giriş Yap</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
<div class="container login-container">
    <h1>Yönetim Paneli Girişi</h1>
    <form method="post" action="index.php">
        <input type="text" name="username" placeholder="Kullanıcı Adı" required>
        <input type="password" name="password" placeholder="Şifre" required>
        <?php if ($error): ?>
            <p class="error"><?php echo $error; ?></p>
        <?php endif; ?>
        <button type="submit" class="button">Giriş Yap</button>
    </form>
</div>
</body>
</html>