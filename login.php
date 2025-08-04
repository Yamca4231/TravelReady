<!DOCTYPE html>
<html lang="en" class="no-js demo5">
	<head>
		<meta charset="UTF-8" />
		<meta name="viewport" content="width=device-width, initial-scale=1.0"> 
		<title>Create an Interactive Background with jQuery Interactive BG</title>
		<meta name="description" content="Parallax comes in many forms. The most common one is a parallax effect that reacts to the user’s scroll behavior." />
		<meta name="keywords" content="parallax, parallax background, interactive bg, jquery parallax" />
		<meta name="author" content="Author for Onextrapixel" />
		<link rel="shortcut icon" href="../file/favicon.gif"> 
    	<script type="text/javascript" src="http://code.jquery.com/jquery-1.9.1.js"></script>
		<link rel="stylesheet" type="text/css" href="css/default.css" />
   		<script type="text/javascript" src="js/jquery.interactive_bg.js"></script>
		<!-- Edit Below -->
		<link rel="stylesheet" type="text/css" href="css/style.css" />
		<script src="../file/js/modernizr.js"></script>
	</head>
	<body>
	  
		<div class="container bg" data-ibg-bg="bg.jpg">
			<!-- Top Navi -->
			<div class="nav-top clearfix">
			<?php
				if (empty($_SESSION['ID'])){
					echo '<span class="right"><a class="nav-icon icon-th" href="index.php?a=login"><span>Zaloguj się</span></a></span>
				<span class="right"><a class="nav-icon icon-left" href="index.php?a=register"><span>Zarejestruj się</span></a></span>';}
				else {
					echo '<span class="right"><a class="nav-icon icon-left" href="index.php?a=log_out"><span>Wyloguj się</span></a></span>
				<span class="right"><a class="nav-icon icon-th" href="index.php?a=info"><span>Info</span></a></span>';}        
			?>
			</div>

			<div class="menu">
				<a href="index.php?a=home">Podstrony 1</a>
				<a href="index.php?a=home">Podstrony 2</a>
				<a href="index.php?a=home">Podstrony 3</a>
				<a href="index.php?a=home">Podstrony 4</a>
				<a class="active" href="index.php?a=home">Home</a>
				
				<div class="header">
				<h1>Logowanie</h1>	
			</div>
<!-- MAIN -->				
    	<?php
require_once('func.php'); // Żądamy pliku z ustawieniami bazy danych
	
if (!empty($_POST)){
	if (!empty($_POST['login']) && !empty($_POST['pass'])){
		$login = vtxt($_POST['login']);
		//Problem z kodowaniem - nie moge zalogowac jak koduje
		$pass = vtxt(md5($_POST['pass']));
		//$pass = vtxt($pass);
		if (ctype_alnum($login)){
			$istnieje =row("SELECT * FROM users WHERE login = '$login' AND password = '$pass'");
			if ($istnieje){
				$_SESSION = array();
				$_SESSION['ID'] = $istnieje['ID'];
				header('Location: index.php?a=game');
			} else echo 'Niepoprawne hasło.';
		} else echo 'Niepoprawna nazwa użytkownika.';
	} else {
		echo '<center><b>Wypełnij pola poprawnie.</b></center>';
	}
}
?>
<form action="index.php?a=login" method="POST">
	<table align="center">
		<tr>
			<td><b>Login:</b></td>
			<td style="padding: 10px"><input type='text' name='login'/></td>
		</tr>
		<tr>
			<td><b>Hasło:</b></td>
			<td style="padding: 10px"><input type='password' name='pass'/></td>
		</tr>
		<tr>
			<td></td>
			<td><center><input type='submit' style="width: 100px" value='Zaloguj się'></center></td>
		</tr>
	</table>
</form> 
<!-- MAIN -->
			</div>
		
    	<div class="main"> 
    	</div>
    	<script type="text/javascript">
        $(".bg").interactive_bg();
      </script>
		</div><!-- Container -->
	</body>
</html>