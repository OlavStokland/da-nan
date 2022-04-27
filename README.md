# da-nan

Containere og filer for DA-NAN3000-prosjekt vår 2022.
Prosjektet består av en komplett webserver, database for dikt, API, webside og brukerfunksjonalitet for å gjøre transaksjoner mot databasen.
Prosjektet er bygget etter et tre-lags DBMS-prinsipp og de ulike delene er fordelt på 3 containere:

Container 1: Webserver og statiske filer
- localhost:80
- Unshare-busybox container 
  - Webserver kodet i c
  - Hjemmeside. HTML/XML/CSS
  - Webapplikasjon for database-transaksjoner. Kjøres direkte i nettleser. HTML/javascript/CSS/XML/JSON
  - Statiske filer nyttet av container 2 og 3 (CSS, DTD etc.)

Container 2: Database og API
- localhost:8081
- Docker-container
  - Diktdatabase. SQLlite
  - Apache webserver
  - RESTful-API. CGI-script/DTD/XML

Container 3: Web-grensesnitt
- localhost:8082
- Docker-container
  - Apache webserver
  - Web-grensesnitt for database-transaksjoner. CGI-skript/CSS/DTD/XML
