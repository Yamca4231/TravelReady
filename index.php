<?php
ob_start(); // Rozpoczynamy pracę bufora
session_start(); // Rozpoczynamy lub przedłużamy pracę sesji
?>
<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8" /> <!-- Ustawienie kodowania na UTF-8 -->       
        <title>Travel Ready</title> <!-- Tytuł strony -->
    </head>
    <body>

<?php
require_once('inc.php'); // Żądamy pliku z ustawieniami bazy danych


//if (empty($_SESSION['ID'])){
//	echo '<center><a href="index.php?a=register">Zarejestruj się</a> | <a href="index.php?a=login">Zaloguj się</a></center></hr>';}
//else {
//    echo '<center><a href="index.php?a=info">Info</a> | <a href="index.php?a=log_out">Wyloguj się</a></center></hr>';} //poprawić game.php na index.php ?                 
				//PROBLEM ZE ZDEFINIOWANIEM A
switch($_GET['a'] ?? 'home'){ // Funkcja wybierania pliku do załadowania
    case 'home': require_once('home.php'); break; // Strona główna
    case 'login': require_once('login.php'); break; // Strona logowania
    case 'register': require_once('register.php'); break; // Strona rejestracji
    case 'game': require_once('game.php'); break; // Strona gry (po zalogowaniu)
	case 'log_out':{
		$_SESSION = array();
		session_destroy();
		header('Location: index.php');
		break;}
    default: require_once('home.php'); break; // Strona ładowana domyślnie
}			
?>
	
	
<?php
ob_end_flush(); // Kończymy pracę bufora
?>
	</body>
</html>