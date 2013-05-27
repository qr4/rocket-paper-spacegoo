Programmierspiel GPN13
======================

Worum es geht: 2 Spieler spielen solange bis maximale Anzahl von Runden
erreicht wurde oder einer der Spieler keine Raumschiffe und Planeten mehr
besitzt. Jeder Spieler hat zu Spielbeginn mindestens einen Startplaneten.
Jeder Planet hat eine feste Produktion, welche angibt, wieviele Raumschiffe
pro Runde dort dazukommen. 

Beide Spieler verbinden sich per TCP Socket zum zentralen Spielserver. Sobald
2 oder mehrere Spieler verfuegbar sind, werden diese in ein Spiel geschickt.
Pro Runde bekommt jeder der beiden Spieler den kompletten Spielzustand als
JSON gesendet. Es gibt 2 gueltige Spielzuege: Es kann von einem der eigenen
Planeten eine Menge von Raumschiffen zu einem anderen Planet losgeschickt
werden. Oder es kann in der Runde keine Aktion stattfinden. Wird innerhalb von
3 Sekunden kein Spielzug uebermittelt, so wird der Spieler dafuer
disqualifiziert.

Flotten bewegen mehrere Runden, bis sie ihren Zielplanet erreichen. Die
Flugzeit haengt von der Entfernung zwischen den Planeten ab. Kommen Flotten
auf einem Planet an, so kaempfen diese, bis ein Spieger uebrig bleibt. Gewinnt
der Angreifer, so geht der Planet in den Besitz des Angreifers ueber.

