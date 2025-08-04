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
				<h1>Rejestracja</h1>	
			</div>				
<!-- MAIN -->	
			<div class="panel-body">
<?php
    if (!empty($_POST)){
		if (!empty($_POST['login']) && !empty($_POST['pass']) && !empty($_POST['pass2']) && !empty($_POST['email'])){
				$login = vtxt($_POST['login']);
				$pass = vtxt($_POST['pass']);
				$email = vtxt($_POST['email']);
				
				if (strlen($login) < 3 || strlen($login) >25) echo 'Login nie mieści się w zakresie.';
				elseif (strlen($pass) < 6 || strlen($pass) >20) echo 'Hasło nie mieści się w zakresie.';
				elseif (strlen($email) < 8 || strlen($email) >35) echo 'Hasło nie mieści się w zakresie.';
				elseif($login == $pass) echo 'Login nie może być takie samo jak hasło.';
				elseif($pass != $_POST['pass2']) echo 'Podane hasła nie są identyczne.';
				else{
					if (ctype_alnum($login)){
						if (filter_var($email, FILTER_VALIDATE_EMAIL)){
							$pass = md5($pass);
							$istnieje =row("SELECT ID FROM users WHERE login = '$login' OR email = '$email'");
							if ($istnieje) echo 'Istnieje już tak gracz';
							else{
								call("INSERT INTO users (login, password, email) VALUES ('$login', '$pass', '$email')");
								header('Location: index.php?a=login');
							}
						} else echo 'Nieprawidłowy email.';
					} else echo 'Login zawiera niedozwolone znaki.';
				}
		}else echo '<center><b>Wypełnij pola poprawnie.</b></center>';
	}
?>
 <div class="well">
        <form class="form-horizontal" action="index.php?a=register" method="POST"> <!-- Formularz wprowadzania danych do rejestracji -->
				
                <div class="form-group" align="center">
                    <div class="col-lg-2"></div>
                    <div class="col-lg-8">
                        <input type="text" class="form-control" name="login" placeholder="Login">
                        <span class="help-block">Od 3 do 25 znaków.</span>
                    </div>
                </div>
                <div class="form-group" align="center">
                    <div class="col-lg-2"></div>
                    <div class="col-lg-8">
                        <input type="password" class="form-control" name="pass" placeholder="Hasło">
						<span class="help-block">Od 6 do 20 znaków.</span>
                    </div>
                </div>
                <div class="form-group" align="center">
                    <div class="col-lg-2"></div>
                    <div class="col-lg-8">
                        <input type="password" class="form-control" name="pass2" placeholder="Powtórz hasło">
                        <span class="help-block">Od 6 do 20 znaków.</span>
                    </div>
                </div>
                <div class="form-group" align="center">
                    <div class="col-lg-2"></div>
                    <div class="col-lg-8">
                        <input type="text" class="form-control" name="email" placeholder="E-mail">
                        <span class="help-block">Od 8 do 50 znaków.</span>
                    </div>
                </div>
                <div class="form-group">
                    <div class="col-lg-12 col-lg-offset-5">
					<br />
                        <center><button type="submit" class="btn btn-primary">Zatwierdź</button></center>
                    </div>
                </div>
        </form>
    </div>
</div>
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





