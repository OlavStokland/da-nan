#!/bin/sh

POST_STRING=$(cat) #indikerer at post stringen fra bruker utføres som cat

#echo $POST_STRING>test-xml ... en liten test
dbpath=../diktbase.db  #lokasjon til databasen

#Vi sjekker om bruker er innlogget basert på cookie (tilstand)

check_login () {
	sessionID=$(echo $HTTP_COOKIE | cut -d "=" -f 2) #kutter sesjonsid fra cookie generert
	echo "select epostadresse from Sesjon where sesjonsID='$sessionID';" | sqlite3 $dbpath
}


# logg inn metoden basert på epost og passordhash som input fra bruker, argument 1 og 2

logg_inn () {
	echo "select fornavn from Bruker where epostadresse='$1' AND passordhash='$2';" | sqlite3 $dbpath
}

# login skal jo være basert på sesjonsID så denne må settes inn i db ved innlogging
session_login () {
	echo "INSERT INTO Sesjon (sesjonsID, epostadresse) VALUES ('$1', '$2');" | sqlite3 $dbpath
}


#en enkel test for å få info fra tabeller basert på primary key
test () {
	key=$(echo -n "pragma table_info("$1");" | sqlite3 $dbpath)
	echo $key
}

# get the primary key

get_primary_key () {

	while read data; do
	key=$(echo $data | rev | cut -d "|" -f 1)
		if [ "$key" = "1" ]; then
			keyfield=$(echo $data | cut -d "|" -f 2)
			echo $keyfield
		fi
	done
}

# vi må omgjøre sql resultatet til xml for å resending tilbake til klient, this is very api

sql_to_xml () {

	while read data; do
		if [ -z "$data" ]; then
			echo " 		</"$1">"
		else
			if [ -z "$prev" ]; then
				echo "		<"$1">"
			fi
			column=$(echo $data | cut -d " " -f 1)
			value=$(echo $data | cut -d " " -f 3-)
			echo " 			<"$column">"$value"</"column">"
		fi
		prev=$data
	done
}

# uri forespørselen deles opp i deler for å brukes i metodene, basert på /

database=$(echo $REQUEST_URI | cut -d "/" -f 2)
table=$(echo $REQUEST_URI | cut -d "/" -f 3)
field=$(echo $REQUEST_URI | cut -d "/" -f 4 )


 # POST metoden

 if [ "$REQUEST_METHOD" = "POST" ]; then # hvis metoden er POST

	sessionID=$(echo $HTTP_COOKIE | cut -d "=" -f 2) # sett sesjonsID basert på cookie

	echo "Content-type: text/plain;charset=utf-8"
	echo

	case $table in
			Sesjon) # switch cases for tabeller i database
				epostadresse=$(echo $POST_STRING | xmlstarlet sel -t -v "//epostadresse" -n) #epost
				passord=$(echo $POST_STRING | xmlstarlet sel -t -v "//passordhash" -n) #passord
				hash=$(echo $passord | sha1sum | cut -d ' ' -f1) #hashet passord

				loginbruker= $(check_login) #sjekker bruker om innlogget
				if [ -z "$loginbruker" ]; then # hvis ikke, så logger man inn bruker
					loginbruker=$(logg_inn $epostadresse $hash)
					if [ -z "$loginbruker" ]; then
						echo "login failed"
					else
						session_login $sessionID $epostadresse
						echo "success"
					fi
				else
					echo "login failed"
				fi
				;;
			Dikt)

				epostadresse=$(check_login)
				if [ -z "$epostadresse" ]; then
					echo "Epost ble ikke verifisert"
				else
					unencoded=$(echo $POST_STRING | xmlstarlet sel -t -v "//dikt" -n) #finner stien til dikt i databasen
					dikt=$(echo $unencoded | sed 's/+/ /g')
					echo "insert into Dikt (dikt, epostadresse) values ('$dikt', '$epostadresse');" | sqlite3 $dbpath
					echo "dikt lagret i database"
				fi
				;;
	esac

fi


if [ "$REQUEST_METHOD" = "PUT" ]; then
	sessionID=$(echo $HTTP_COOKIE | cut -d "=" -f 2)

	echo "Content-type: text/plain;charset=utf-8"
	echo
	epostadresse=$(check_login)
	if [ -z "epostadresse" ]; then
		echo "ikke logget inn"
	else
		diktowner=$(echo "select epostadresse from dikt where diktID='$field';" | sqlite3 $dbpath)
		currentUser=$(echo "select epostadresse from sesjon where sesjonsID ='$sessionID';" | sqlite3 $dbpath)

		if [ "$diktowner" = "$currentUser" ]; then
			unencoded=$(echo $POST_STRING | xmlstarlet sel -t -v "login/Dikt/dikt" -n)
			dikt=$(echo $unencoded | sed 's/+/ /g')
			echo "update dikt set dikt='$dikt' where diktid='$field';" | sqlite3 $dbpath
		else
			echo "Dette er faen ikke ditt dikt"
		fi
	fi
fi

if ["$REQUEST_METHOD" = "DELETE" ]; then
	echo "Content-type: text/plain;charset=utf-8"
	echo "Access-Control-Allow-Origin: INSERT-IPADRESS"
	echo "Access-Control-Allow-Credentials: true"
	echo "Access-Control-Allow-Methods: POST,PUT,DELETE,GET"
    echo

	epostadresse=$(check_login)
	if [ -z "$epostadresse" ]; then
		var=$(echo "Du er fortsatt ikke logget inn")
	else
		case $table in
				sesjon)

						sessionID=$(echo $HTTP_COOKIE | cut -d "=" -f 2)
						echo "delete from sesjon where  sesjonsid='$sessionID';" | sqlite3 $dbpath
						;;
				Dikt)
						if [ -z "$field" ]; then
							echo "delete from dikt where epostadresse='$epostadresse';" | sqlite3 $dbpath
						else
							diktowner=$(echo "select epostadresse from dikt where diktid='$field';" | sqlite3 $dbpath)
							if [ "$diktowner" = "$epostadresse" ]; then
								echo "delete from dikt where diktid='$field';" | sqlite3 $dbpath
							else
								echo "failed deleting"
							fi
						fi
		esac
	fi
fi


if [ "$REQUEST_METHOD" = "OPTIONS" ]; then
	echo
fi



if [ "$REQUEST_METHOD" = "GET" ]; then
	echo "Content-type:text/xml;charset=utf-8"
	echo
	echo '<?xml version="1.0"?>'

	echo '<root
	xml:xsi="http://www.w3.org/2001/XMLSchema-instance"
	xsi:noNameSpaceSchemaLocation="https://10.35.20.4:8082/schema.xsd">'


	echo " <"$database">"

	if [ -< "$field" ]; then
		echo -n 'select * from '$table';' | sqlite3 $dbpath -line | sql_to_xml $table
	else
		spesifisertfelt=$(echo 'pragma table_info('$table');' | sqlite3 $dbpath | get_primary_key)
		echo -n "select * from "$table" where "$spesifisertfelt"='"$field"';" | sqlite3 $dbpath -line | sql_to_xml $table
	fi
	echo " 	</"$table">"
	echo "	</"$database">"
	echo "</root>"
