<?php
    $user = 'root'; // Nazwa użytkownika bazy danych
    $pass = ''; // Hasło użytkownika bazy danych
    $host = 'localhost'; // Nazwa hosta (serwera) bazy danych
    $db = 'seabattle'; // Nazwa naszej bazy danych

    $link = mysqli_connect($host, $user, $pass);
    if (!$link) {
        die("Błąd połączenia: " . mysqli_connect_error());
    }

    if (!mysqli_select_db($link, $db)) {
        die("Nie znaleziono takiej bazy danych: " . mysqli_error($link));
    }

    require_once('func.php'); // Pobranie pliku z funkcjami
?>
