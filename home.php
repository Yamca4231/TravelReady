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
			<form id="checklist-form">
			<ul id="checklist"></ul>
			</form>
			<p id="status" style="color: green;"></p>

			<?php
			/*
				// Pobieramy dane JSON z API działającego w aplikacji Python (Flask)
				// Upewnij się, że serwer Pythona działa i że adres jest poprawny (localhost lub IP)
				$data = file_get_contents("http://localhost:5000/api/checklist");

				// Dekodujemy JSON do tablicy PHP
				$items = json_decode($data, true);

				// Wyświetlamy nagłówek
				echo "<h2>Lista rzeczy do zabrania:</h2><ul>";

				 // Iterujemy przez listę i wyświetlamy każdy element jako <li>
				foreach ($items as $item) {
					// htmlspecialchars – zabezpieczenie przed XSS (np. gdyby w nazwie był <script>)
					echo "<li>" . htmlspecialchars($item) . "</li>";
				}

				 echo "</ul>";
			*/
			?>  

    	</div>
    		<script type="text/javascript">
				$(".bg").interactive_bg();
			</script>
		</div><!-- Container -->

		<script>
			document.addEventListener("DOMContentLoaded", function () {
			  async function fetchChecklist() {
				const [itemsRes, checkedRes] = await Promise.all([
				  fetch("http://192.168.1.21:5000/api/checklist"),
				  fetch("http://192.168.1.21:5000/api/checked")
				]);
				const items = await itemsRes.json();
				const checked = await checkedRes.json();

				const ul = document.getElementById("checklist");
				ul.innerHTML = "";

				items.forEach(item => {
				  const li = document.createElement("li");
				  const input = document.createElement("input");
				  input.type = "checkbox";
				  input.name = "item";
				  input.value = item;
				  input.checked = checked.includes(item);
				  input.addEventListener("change", saveChecklist);
				  li.appendChild(input);
				  li.append(" " + item);
				  ul.appendChild(li);
				});
			  }

			  async function saveChecklist() {
				const checked = Array.from(document.querySelectorAll("input[name='item']:checked"))
				  .map(cb => cb.value);

				const res = await fetch("http://192.168.1.21:5000/api/checked", {
				  method: "POST",
				  headers: { "Content-Type": "application/json" },
				  body: JSON.stringify(checked)
				});

				const status = document.getElementById("status");
				if (res.ok) {
				  status.textContent = "Zapisano!";
				} else {
				  status.textContent = "Błąd zapisu!";
				  status.style.color = "red";
				}
				setTimeout(() => status.textContent = "", 2000);
			  }

			  fetchChecklist();
			});
		</script>
	</body>
</html>