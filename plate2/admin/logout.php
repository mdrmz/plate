<?php
// admin/logout.php

session_start();
// Tüm session değişkenlerini temizle
$_SESSION = array();
// Session'ı yok et
session_destroy();
// Login sayfasına yönlendir
header('Location: index.php');
exit;
?>