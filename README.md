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

Protokoll
---------

Auf den Spielserver per TCP verbinden. Als erster Befehl muss

    login <username> <passwort>

geschickt werden. Beim ersten verbinden werden username/passwort gespeichert
und muessen dann beim naechsten Mal einloggen identisch wiederverwendet
werden. Es gibt kein Passwort reset oder Account loeschen.

Weitere beliebige Ausgaben folgen, bis irgendwann ein Spiel anfaengt. In
diesem Moment bekommen beide Spieler den kompletten Spielzustand per JSON
zugeschickt. Spielzustande sind immer per einleitendem '{' erkennbar.

Als Antwort auf einen Spielzustand muss innerhalb von 3 Sekunden eine Antwort
an den Server geschickt werden. Es gibt 2 Antworten:

    nop

gibt an, dass keinerlei Aktion stattfinden soll. 

    send <source_planet_id> <target_planet_id> <num_a> <num_b> <num_c>

gibt an, dass vom eigenen Planet source_planet_id die angegebene Anzahl von
Schffen zu Planet target_planet_id gesendet werden sollen.

Sobald beide Spieler ihren Spielzug gemacht haben, geht das Spiel in die
naechste Runde und beide Spiele bekommen wieder den kompletten Spielzustand
gesendet.

Ein Spielstand sieht folgendermassen aus:

    {
      "game_over": false,
      "winner": null,               // player_id
      "round": 2
      "max_rounds": 500,
      "fleets": [
        {
          "id": 0,                  
          "owner_id": 1,            // player_id
          "origin": 1,              // planet_id
          "target": 2,              // plane_id
          "ships": [ 3, 1, 1 ],     // Anzahlen Typ a, b, c
          "eta": 45                 // Ankunftsrunde (s.u.)
        },
        ...
      ],
      "players": [
        {
          "id": 1,
          "name": "dividuum",
          "itsme": true
        },
        {
          "id": 2,
          "name": "cupe",
          "itsme": false
        }
      ],
      "planets": [
        {
          "id": 0,
          "owner_id": 0,            // player_id
          "y": 0,                   
          "x": 0,
          "ships": [ 20, 20, 20 ],  // aktuelle Schiffsanzahl Typ a, b, c
          "production": [ 1, 1, 1 ] // Produktion/Runde Typ a, b, c
        },
        ...
      ],
    }

Das Spiel ist beendet, sobald in game_over true steht.  Nachdem ein solcher
State vom Spieler empfangen wurde, gilt das Spiel als beendet und der Spieler
wird vom Server getrennt. Der Spieler kann sich daraufhin direkt wieder neu
anmelden. 

Flotten kommen im Anschluss an die Runde am Zielplanet an. Beispiel: Ist eta
als Runde 10 angegeben, so kommt die Flotte nach Abgabe der Befehle fuer Runde
10 an. In Runde 11 existiert die Flotte dann nicht mehr.

Planeten gehoeren immer einem Spieler. Zu beginnt gehoert jedem Spieler
mindestens ein Planet. Die anderen Planeten gehoeren dem Spieler mit der
player_id 0. Auf Planeten die diesem NPC Spieler gehoeren ist zwar eine
Produktion angegeben, allerdings waechst die Anzahl der Schiffe dort nicht an.
Dies passiert erst, wenn einer der beiden echten Spieler den Planet
uebernimmt.

Client-Libraries
----------------

Haskell-Programmierer können das Haskell-Paket
[`haskell-spacegoo`](https://bitbucket.org/nomeata/haskell-spacegoo) verwenden,
um komfortabel Clients zu programmieren.

