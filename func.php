<?php
	// Wywołanie zapytania do bazy
	function call($sql){ 
		return mysql_query($sql);
	}
	// Funkcja zabezpieczająca dane wysyłane do bazy
	function vtxt($var){ 
		return trim(mysql_real_escape_string(strip_tags($var)));
	}
	// Funkcja wybierająca cały szereg danych wyciąganych z bazy
	function row($sql){ 
		return @mysql_fetch_assoc(mysql_query($sql));
	}
	// Funkcja wybierająca szereg danych o graczu z podanym ID
	function getUser($id){ 
		return row("SELECT * FROM users WHERE ID = '$id'");
	}
	function checkUser($sid){
		if (empty($sid)){
			return header("Location: index.php?a=login");
		}
		else {
			return $sid = (int)$sid;
		}
	}
?>