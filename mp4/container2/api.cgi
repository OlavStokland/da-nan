#!/bin/bash
read BODY

db_path=../diktbase.db
url_path=$REQUEST_URI
url_end=$(basename "$url_path") #prints the last element of a filepath
cookie=$HTTP_COOKIE
state_email=""
state_session_id=""
session_id=""
logged_in="0"
response=""
length=""

#sjekker om bruker er logget inn
function check_login() {

	IFS="=" #input field separator for hver read -OBS: The default value is <space><tab><newline>
	read -a cookie_string <<<$cookie
	IFS='\'

	cookie_session=${cookie_string[1]}

	db_session=$(sqlite3 $db_path "SELECT * FROM Sesjon WHERE sesjonsID = '$cookie_session';") #henter ut sesjonsID fra database

	if [ -z $db_session ]; then #hvis database er tom er ikke bruker innlogget
		logged_in="0"

	else
		#hvis man er logget inn, så henter man sesjonsid og epost
		IFS="|"
		read state_session_id state_email <<<"$db_session"
		IFS='\'

		logged_in="1"
	fi
}

#fra string til bytes
function character_to_byte() {
	oLang=$LANG oLcAll=$LC_ALL
	LANG=C LC_ALL=C
	length=${#1}
	LANG=$oLang LC_ALL=$oLcAll
}

#get respons for å hente ut dikt
function get_all_response() { #legger en response for hver request
	response="<?xml version='1.0' encoding='UTF-8'?>"
	response+="<?xml-stylesheet type='text/xsl' href='http://10.35.20.4:8081/diktbase.xsl'?>" #change for hosts
	response+="<!DOCTYPE response SYSTEM 'http://10.35.20.4:8082/diktbase.dtd'>"
	response+="<diktbase>"$1"</diktbase>"
character_to_byte "$response"
}

#respons med parametre

function get_response() { #legger til en response for error requests
	response="<?xml version='1.0' encoding='UTF-8'?>"
	response+="<!DOCTYPE response SYSTEM 'http://10.35.20.4:8082/response.dtd'>" #change for hosts
	response+="<response><status>"$1"</status><statustext>"$2"</statustext><sessionid>"$3"</sessionid><mail>"$4"</mail><firstname>"$5"</firstname><lastname>"$6"</lastname></response>"
character_to_byte "$response"
}

#Henter 1 ett eller flere dikt
if [ "$REQUEST_METHOD" = "GET" ]; then

	IFS='/'
	read -a request_string <<<"$url_path" # leser urlog legger til en array som skilles med /
	IFS='\'


	#Get request, vi finner alle dikt
#hvis 3 er dikt og 4 er tom så vet vi at vi har kommet til slutten
	if [ ${request_string[3]} = "Dikt" -a -z "${request_string[4]}" ]; then
		allpoems=$(sqlite3 $db_path "SELECT * FROM Dikt;")

	        poems_in_xml=""

		IFS=$'\n'
		for poem in $allpoems;
		do
			poems_in_xml+=$(echo "<Dikt>") #få data ut fra database, fjerner unødvendig data
			poems_in_xml+=$(echo "<diktID>$(echo $poem | cut -d '|' -f1)</diktID>")
			poems_in_xml+=$(echo -e "<tekst>$(echo $poem | cut -d '|' -f2)</tekst>")
			poems_in_xml+=$(echo "<epost>$(echo $poem | cut -d '|' -f3)</epost>")
			poems_in_xml+=$(echo "</Dikt>")
		done
		IFS='\'
#send tilbake respons
		get_all_response "$poems_in_xml"

	# vi finner 1 dikt
elif [ ${request_string[3]} = "Dikt" -a ${request_string[4]} = $url_end ]; then #hvis 3 er dikt og 4 er lik siste /
		one_poem=$(sqlite3 $db_path "SELECT * FROM Dikt WHERE diktID=$url_end;")
#les diktet fram til |
		if [ ${#one_poem} -gt 0 ]; then
			IFS="|"
			read -a poem_array <<<$one_poem
			IFS='\'

			get_all_response "<Dikt><diktID>"${poem_array[0]}"</diktID><tekst>"${poem_array[1]}"</tekst><epost>"${poem_array[2]}"</epost></Dikt>" #send tilbake lest data fra database
		else
			get_response "0" "Dikt med id $url_end eksisterer ikke!" # dikt id er ikke funnet og diktet blir ikke returnert
		fi
	fi
fi


if [ "$REQUEST_METHOD" = "POST" ]; then

	check_login

	IFS='/'
	read -a request_string <<<"$url_path"
	IFS='\'

	#tester login
	if [ ${request_string[3]} = "login" ]; then

		if [ $logged_in = 0 ]; then

			xml_data=$BODY
			username=$(xmllint --xpath "//username/text()" - <<<"$xml_data") # Parsing xml user
			password=$(xmllint --xpath "//password/text()" - <<<"$xml_data") # Parsing xml password

			user_exist=$(sqlite3 $db_path "SELECT * FROM Bruker WHERE epost='$username';") #henter potensiell bruker fra databasen
# bruker eksisterer ikke
			if [ -z $user_exist ]; then
				get_response "0" "bruker eksisterer ikke"

			else
				#bruker eksisterer
				IFS='|'
				read user_exists_email user_exists_password user_exists_firstname user_exists_lastname <<< "$user_exist"
				IFS='\'

				encrypted_password=$(echo -n $password | sha512sum | head -n 1 )
#hvis passord stemmer så selecter man riktig sesjonsID  utifra sesjonsid til bruker
				if [ $encrypted_password = $user_exists_password ]; then
					session_id=$(uuidgen -r) #HVis passord riktig sett sesjonsid

					existing_sessions=$(sqlite3 $db_path "SELECT sesjonsID FROM Sesjon WHERE sesjonsID='$session_id';")
					does_session_exist=${#existing_sessions} #kopierer sesjonsID fra database til å bruke som eksisterende sesjon
					 #hvis sesjonsid ikke eksisterer, så inserter vi inn i database
					if [ $does_session_exist = 0 ]; then
						sqlite3 $db_path "INSERT INTO Sesjon (sesjonsID,epost) \
						VALUES('$session_id','$user_exists_email');"

						get_response "1" "Du er logget inn som" "$session_id" "$user_exists_email" "$user_exists_firstname" "$user_exists_lastname"
					else
						#  hvis sesjonsid eksisterer så forsikrer vi oss om at det ikke blir duplikater
						get_response "0" "duplikat sesjonsid"
					fi

				else
					#passord ikke riktig så får bruker feilmelding om det
					get_response "0" "Brukernavn eller passord er feil"
				fi
			fi
		else
			# bruker er allerede logget inn
			get_response "0" "bruker er allrede logget inn"
	fi



	#Logg ut, sletter sesjonsid fra database
elif [ ${request_string[3]} = 'logout' ]; then

		if [ $logged_in = 1 ]; then

			xml_data=$BODY
			logged_in_session_id=$(xmllint --xpath "//sessionid/text()" - <<<"$xml_input") #Getting sessionid from bodyparameter in xml

			sqlite3 $db_path "DELETE FROM Sesjon WHERE sesjonsID='$state_session_id';"

			get_response "1" "Bruker logget ut" "$state_session_id" "$state_email"
		else
			get_response "0" "Bruker må være innlogget for å logge ut duuuh"
		fi

	elif [ ${request_string[3]} = "Dikt" ]; then #Post metode mot diktbase.db/Dikt
		# Post for å lage nytt dikt i databasen

		if [ $logged_in = 1 ]; then

			xml_data=$BODY #leser kropp
			poem_new=$(xmllint --xpath "//tekst/text()" - <<<"$xml_data") # får nytt dikt fra body parameteret i xml

			previous_id=$(sqlite3 $db_path "SELECT diktID FROM Dikt ORDER BY diktID DESC LIMIT 1;") #finner siste diktID i databasen
			new_id="$previous_id + 1"

			sqlite3 $db_path "INSERT INTO Dikt VALUES('$new_id','$poem_new','$state_email');" #inserter nytt dikt til databasen

			get_response "1" "nytt dikt er lagret :)" "$state_session_id" "$state_email" #satt inn for innlogget bruker

		else
			get_response "0" "du må ha rettigheter: permission denied "
		fi
	else
		get_response "0" "noe er feil med url"
	fi
fi

if [ "$REQUEST_METHOD" = "PUT" ]; then

	check_login

				IFS='/' #delimiter
        read -a request_string <<<$url_path
        IFS='\'

	if [ $logged_in = 1 ]; then
	#hvis logget inn

		if [ ${request_string[4]} = $url_end ]; then

			owner=$(sqlite3 $db_path "SELECT epost FROM dikt WHERE diktID='$url_end';") #finn epostadresse som har riktig ID

			if [ "$owner" == "$state_email" ]; then

				xml_data=$BODY
				change=$(xmllint --xpath "//tekst/text()" - <<<"$xml_data")

				sqlite3 $db_path "UPDATE Dikt SET dikt='$change' WHERE diktID = '$url_end' AND epost='$state_email';"

				get_response "1" "Diktnr $url_end er endret" "$logged_in_session_id" "$state_email"
			else
				get_response "0" "Du er ikke eier: permission denied"
			fi
		else
			get_response "feil URL ved endring av dikt"
		fi

	else
		get_response "0" "du må logge inn"
	fi
fi
#delete funksjonen som sletter dikt fra databasen både eget dikt og alle egne dikt

if [ "$REQUEST_METHOD" = "DELETE" ]; then

	check_login

	IFS='/' #delimiter
	read -a request_string <<<"$url_path"
	IFS='\'

	if [ $logged_in = 1 ]; then
	#hvis logget inn

		if [ ${request_string[3]} = "Dikt" -a -z "${request_string[4]}" ]; then

			sqlite3 $db_path "DELETE FROM Dikt WHERE epost='$state_email';"

			get_response "1" "alle dikt som er tilknyttet $state_email er slettet" "$logged_in_session_id" "$state_email"
# sletter dikt gitt diktID
		elif [ ${request_String[3]} = "dikt" -a ${request_string[4]} = $url_end ]; then
			 # sletter dikt gitt diktID
				owner=$(sqlite3 $db_path "SELECT epost FROM Dikt WHERE diktID= '$url_end';") # siste del av url er sesjonsid

				if [ "$owner" == "$state_email" ]; then
				 #er epost like så er det sikkert at det er egen ID basert på sjekken i databasen

					sqlite3 $db_path "DELETE FROM Dikt WHERE DiktID '=$url_end';"

					get_response "1" "Dikt $url_end slettet fra følgende bruker:" "$logged_in_session_id" "$state_email"
				else
					get_response "0" "Permission denied"
				fi
		else
				get_response "0" "feil i url"
		fi
	else
			get_response "0" "DU må være innlogget..."
	fi
fi

# sessionid eksisterer og dette blir sendt
if [ ${#session_id} -gt "0" ]; then
	echo "Set-Cookie: session_id="$session_id"; Max-Age=7200; Path=/;"
	echo "Content-Length: "$length
	echo "Content-type:text/xml;charset=utf-8"
	echo "Access-Control-Allow-Origin: http://localhost"
	echo "Access-Control-Allow-Credentials: true"
	echo "Access-Control-Allow-Methods: POST,PUT,DELETE,GET"
	echo
	echo $response
#sessionid eksisterer ikke og denne blir da sendt
else
	echo "Content-Length: "$length
	echo "Content-type:text/xml;charset=utf-8"
	echo "Access-Control-Allow-Origin: http://localhost"
	echo "Access-Control-Allow-Credentials: true"
	echo "Access-Control-Allow-Methods: POST,PUT,DELETE,GET"
	echo
	echo $response
fi
