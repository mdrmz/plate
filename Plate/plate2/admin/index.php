<?php
session_start();
if (isset($_SESSION['loggedin']) && $_SESSION['loggedin'] === true) {
    header('Location: dashboard.php');
    exit;
}

$error = '';
if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    // Basitlik için şifre kontrolü. Gerçek projede veritabanından yapılmalı.
    if ($_POST['username'] == 'admin' && $_POST['password'] == '12345') {
        $_SESSION['loggedin'] = true;
        $_SESSION['username'] = 'admin';
        header('Location: dashboard.php');
        exit;
    } else {
        $error = 'Geçersiz kullanıcı adı veya şifre!';
    }
}
?>
<!DOCTYPE html>
<html>
<head>
    <title>Admin Girişi</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="login-container">
        <h2>Plaka Tanıma Sistemi - Yönetim Paneli</h2>
        <form action="index.php" method="post">
            <input type="text" name="username" placeholder="Kullanıcı Adı" required>
            <input type="password" name="password" placeholder="Şifre" required>
            <button type="submit">Giriş Yap</button>
            <?php if($error): ?><p class="error"><?php echo $error; ?></p><?php endif; ?>
        </form>
    </div>
</body>
</html>