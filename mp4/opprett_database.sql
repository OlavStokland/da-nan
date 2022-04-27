PRAGMA foreign_keys = ON; -- For å håndheve referanseintegriteten for databasen, slipper da for checks..

CREATE TABLE IF NOT EXISTS Bruker (
	epost TEXT NOT NULL,
	passordhash TEXT,
	fornavn TEXT,
	etternavn TEXT,
	PRIMARY KEY (epost)
);

CREATE TABLE IF NOT EXISTS Sesjon (
	sesjonsID TEXT NOT NULL,
	epost TEXT,
	PRIMARY KEY (sesjonsID),
	FOREIGN KEY (epost) REFERENCES Bruker(epost)
);

CREATE TABLE IF NOT EXISTS Dikt (
	diktID NUMBER NOT NULL,
	dikt TEXT,
	epost TEXT,
	PRIMARY KEY (diktID),
	FOREIGN KEY (epost) REFERENCES Bruker(epost)
);

/* sha512sum - idiot */
INSERT INTO Bruker(epost,passordhash,fornavn,etternavn)
VALUES( 'olavstokk@danan.no','05331e25d57db8dcaf36507557f7516970f2ad3eae1ee37fb0d2845cad60f21f97cdae72bbb14e285719cedd2a3dde67ec0392fb831ba7072c6049c4aa69ecd8  -','olav','stokland');

INSERT INTO Bruker(epost,passordhash,fornavn,etternavn)
VALUES( 'espend@danan.no','9899053c4e70d897c9cbb826be62c71904d6b3850686cf93cdcb5e7518243d6686841d69992012a35753d03757812d5b06ab8c70af0e4218158bfc4666ba2cfb  -','espen','disch');

INSERT INTO Dikt(diktID,dikt,epost)
VALUES(1, 'Det heiter ikkje: eg – no lenger.Heretter heiter det: vi.Eig du lykka så er ho ikkje lengerberre di.Alt det som bror din kan ta imot av lykka di, må du gi.','olavstokk@danan.no');

INSERT INTO Dikt(diktID,dikt,epost)
VALUES(2, 'Mellom bakkar og berg utve havet. Satt Trollmannen og skriv eit brev ellernoe sånt','espend@danan.no');

INSERT INTO Dikt(diktID,dikt,epost)
VALUES(3, 'Du skal ikke sitte å si, det er sørgelig stakkars dem','espend@danan.no');
