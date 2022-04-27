Container 1 - MP1/2 og 5

Denne mappen inneholder alle nødvendige filer for oppsett og kjøring av webserver, hjemmeside og web-applikasjon på container 1 med riktig lenking av statiske filer, samt skript for opptstart, restart og nedstengning.

Statiske filer nyttet av de andre containerene, samt javascript-kode befinner seg også i denne containeren.

NB: webserver.c kompileres og starter som en del av container-initialiseringen, kjør derfor kun skript som beskrevet nedenfor:

- Kjør sudo ./cont.sh med opsjon:
	1: initierer container med filsystemet som ligger i var/ (med undermapper), samt kompilerer og starter webserver (med init som foreldreprosess)
	2: sletter container, dreper prosesser og initierer container på nytt
	3. sletter container og dreper prosesser

- Webtjeneren og hjemmesiden når du på http://localhost - Tut og kjør!
