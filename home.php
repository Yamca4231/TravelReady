<!DOCTYPE html>
<html lang="en" class="no-js demo5">
	<head>
		<meta charset="UTF-8" />
		<meta name="viewport" content="width=device-width, initial-scale=1.0"> 
		
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
					echo '<span class="right"><a class="nav-icon icon-left" href="index.php?a=login"><span>Zaloguj się</span></a></span>
					<span class="right"><a class="nav-icon icon-th" href="index.php?a=register"><span>Zarejestruj się</span></a></span>';}
				else {
					echo '<span class="right"><a class="nav-icon icon-left" href="index.php?a=log_out"><span>Wyloguj się</span></a></span>
				<span class="right"><a class="nav-icon icon-th" href="index.php?a=info"><span>Info</span></a></span>';}        
			?>
			</div>

			<div class="header">
				<h1>Travel Ready</h1>	
			</div>

			<div class="menu">
				<a href="index.php?a=home">Podstrony 1</a>
				<a href="index.php?a=home">Podstrony 2</a>
				<a href="index.php?a=home">Podstrony 3</a>
				<a href="index.php?a=home">Podstrony 4</a>
				<a class="active" href="index.php?a=home">Home</a>
			</div>
		
    	<div class="main">
			<h2>✈️ Twoja osobista lista pakowania na wakacje</h2>
		
			<p id="status" style="color: green;"></p>

		 

    	</div>
    		<script type="text/javascript">
				$(".bg").interactive_bg();
			</script>
		</div><!-- Container -->
	</body>
</html>