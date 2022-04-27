#!/bin/bash
read BODY

#echo "Content-type:application/xml;charset=utf-8"
#echo

### Variables ###
database_path=../diktbase.db
url_path=$REQUEST_URI
url_base=$(basename "$url_path") #last part of url, after last /
cookie=$HTTP_COOKIE
current_email=""
current_session_id=""
session_id=""
is_logged_in="0"
response=""
length=""


#Function to check if user is logged in
function check_if_logged_in() {

	IFS="=" #Set delimeter
	read -a cookie_array <<<$cookie
	IFS='\' #Reset delimeter

	cookie_session_id=${cookie_array[1]}

	database_session=$(sqlite3 $database_path "SELECT * FROM sesjon WHERE sesjonsID = '$cookie_session_id';")

	if [ -z $database_session ]; then #If not logged in
		is_logged_in="0"

	else	#If logged in
		IFS="|"
		read current_session_id current_email <<<"$database_session"
		IFS='\'

		is_logged_in="1"
	fi
}

#Function to change the length of string to length in bytes
function get_length_in_bytes() {
	oLang=$LANG oLcAll=$LC_ALL
	LANG=C LC_ALL=C
	length=${#1}
	LANG=$oLang LC_ALL=$oLcAll
}

#Function to create response for get poems/poem
function create_get_response() {
	response="<?xml version='1.0' encoding='UTF-8'?>"
	response+="<?xml-stylesheet type='text/xsl' href='http://localhost:8180/diktbase.xsl'?>"
	response+="<!DOCTYPE response SYSTEM 'http://localhost/diktbase.dtd'>"
	response+="<diktbase>"$1"</diktbase>"
	get_length_in_bytes "$response"
}

#Function to create response with up to 4 parameters
function create_response() {
	response="<?xml version='1.0' encoding='UTF-8'?>"
	response+="<!DOCTYPE response SYSTEM 'http://localhost/response.dtd'>"
	response+="<response><status>"$1"</status><statustext>"$2"</statustext><sessionid>"$3"</sessionid><useremail>"$4"</useremail><userfname>"$5"</userfname><userlname>"$6"</userlname></response>"
	get_length_in_bytes "$response"
}


if [ "$REQUEST_METHOD" = "GET" ]; then

	IFS='/' #Set delimeter
	read -a url_array <<<"$url_path" 	#Making an array of url: parts on every /
	IFS='\' #Reset delimeter


	#Get all poems
	if [ ${url_array[3]} = "dikt" -a -z "${url_array[4]}" ]; then				#if index 3 is "dikt" and index 4 is empty string
		poems=$(sqlite3 $database_path "SELECT * FROM dikt;")

		all_poems_in_xml=""

		IFS=$'\n'
		for poem in $poems;
		do
			all_poems_in_xml+=$(echo "<dikt>")
			all_poems_in_xml+=$(echo "<diktID>$(echo $poem | cut -d '|' -f1)</diktID>")
			all_poems_in_xml+=$(echo -e "<tekst>$(echo $poem | cut -d '|' -f2)</tekst>")
			all_poems_in_xml+=$(echo "<epostadresse>$(echo $poem | cut -d '|' -f3)</epostadresse>")
			all_poems_in_xml+=$(echo "</dikt>")
		done
		IFS='\'

		create_get_response "$all_poems_in_xml"

	#Get one poem
	elif [ ${url_array[3]} = "dikt" -a ${url_array[4]} = $url_base ]; then		#if index 3 is "dikt" and index 4 is equal to last /something
		one_poem=$(sqlite3 $database_path "SELECT * FROM dikt WHERE diktID=$url_base;")

		if [ ${#one_poem} -gt 0 ]; then
			IFS="|"
			read -a poem_array <<<$one_poem
			IFS='\'

			create_get_response "<dikt><diktID>"${poem_array[0]}"</diktID><tekst>"${poem_array[1]}"</tekst><epostadresse>"${poem_array[2]}"</epostadresse></dikt>"
		else
			create_response "0" "Dikt med id $url_base eksisterer ikke"
		fi
	fi
fi

if [ "$REQUEST_METHOD" = "POST" ]; then

	check_if_logged_in

	IFS='/' #Set delimeter
	read -a url_array <<<"$url_path"
	IFS='\' #Reset delimeter


	#Login
	if [ ${url_array[3]} = "login" ]; then

		if [ $is_logged_in = 0 ]; then

			xml_input=$BODY
			username=$(xmllint --xpath "//username/text()" - <<<"$xml_input") # Parsing xml user
			password=$(xmllint --xpath "//password/text()" - <<<"$xml_input") # Parsing xml password

			user=$(sqlite3 $database_path "SELECT * FROM bruker WHERE epostadresse='$username';")

			if [ -z $user ]; then	#If user does not exist
				create_response "0" "Brukernavn eller passord er feil"

			else					#If user exist
				IFS='|'
				read user_email user_password user_fname user_lname <<< "$user"
				IFS='\'

				hash_password=$(echo -n $password | sha512sum | head -n 1 )

				if [ $hash_password = $user_password ]; then		#If password is correct
					session_id=$(uuidgen -r)

					existing_sessions=$(sqlite3 $database_path "SELECT sesjonsID FROM sesjon WHERE sesjonsID='$session_id';")
					does_session_exist=${#existing_sessions}

					if [ $does_session_exist = 0 ]; then				#If sessionId does not exist
						sqlite3 $database_path "INSERT INTO sesjon (sesjonsID,epostadresse) \
						VALUES('$session_id','$user_email');"

						create_response "1" "Du er logget inn" "$session_id" "$user_email" "$user_fname" "$user_lname"

					else	#If sessionId does exist, so duplicates doesn't happen
						create_response "0" "Noe gikk galt, prøv igjen"
					fi

				else	#If password is not correct
					create_response "0" "Brukernavn eller passord er feil"
				fi
			fi
		else
			create_response "0" "Bruker er allerede logget inn"
		fi

	#Log out
	elif [ ${url_array[3]} = 'logout' ]; then

		if [ $is_logged_in = 1 ]; then

			#xml_input=$BODY
			#logged_in_session_id=$(xmllint --xpath "//sessionid/text()" - <<<"$xml_input") #Getting sessionid from bodyparameter in xml

			sqlite3 $database_path "DELETE FROM sesjon WHERE sesjonsID='$current_session_id';"

			create_response "1" "Bruker logget ut" "$current_session_id" "$current_email"

		else
			create_response "0" "Bruker må være logget inn for å gjennomføre denne handlingen"
		fi


	#Create poem
	elif [ ${url_array[3]} = "dikt" ]; then	#Post to make new poem localhost/cgi-bin/diktbase.cgi/dikt

		if [ $is_logged_in = 1 ]; then

			xml_input=$BODY
			new_poem=$(xmllint --xpath "//tekst/text()" - <<<"$xml_input")		#Getting new poem from bodyparameter in xml

			last_id=$(sqlite3 $database_path "SELECT diktID FROM dikt ORDER BY diktID DESC LIMIT 1;")	#Getting last id that exists
			let "new_id = $last_id + 1"																	#Making new id from last id

			sqlite3 $database_path "INSERT INTO dikt VALUES('$new_id', '$new_poem', '$current_email');"	#Inserting the new poem

			create_response "1" "Nytt dikt lagret" "$current_session_id" "$current_email"
		else
			create_response "0" "Bruker må være logget inn for å gjennomføre denne handlingen"
		fi
	else
		create_response "0" "Feil url"
	fi
fi


#PUT
if [ "$REQUEST_METHOD" = "PUT" ]; then

	check_if_logged_in

	IFS='/' #Set delimeter
	read -a url_array <<<"$url_path"
	IFS='\' #Reset delimeter

	if [ $is_logged_in = 1 ]; then

		#Change poem
		if [ ${url_array[4]} = $url_base ]; then

			poem_owner=$(sqlite3 $database_path "SELECT epostadresse FROM dikt WHERE diktID='$url_base';")

			if [ "$poem_owner" == "$current_email" ]; then

				xml_input=$BODY
				poem_changed=$(xmllint --xpath "//tekst/text()" - <<<"$xml_input")

				sqlite3 $database_path "UPDATE dikt SET dikt='$poem_changed' WHERE diktID='$url_base' AND epostadresse='$current_email';"

				create_response "1" "Dikt $url_base endret" "$logged_in_session_id" "$current_email"
			else
				create_response "0" "Du er ikke eier av dette diktet og kan derfor ikke endre det"
			fi
		else
			create_response "0" "Feil url"
		fi

	else
		create_response "0" "Bruker må være logget inn for å gjennomføre denne handlingen"
	fi
fi

#Delete
if [ "$REQUEST_METHOD" = "DELETE" ]; then

	check_if_logged_in

	IFS='/' #Set delimeter
	read -a url_array <<<"$url_path"
	IFS='\' #Reset delimeter


	if [ $is_logged_in = 1 ]; then
		#Slett alle egne dikt
		if [ ${url_array[3]} = "dikt" -a -z "${url_array[4]}" ]; then

			sqlite3 $database_path "DELETE FROM dikt WHERE epostadresse='$current_email';"

			create_response "1" "Alle dikt som tilhører $current_email slettet" "$logged_in_session_id" "$current_email"


		#Slett dikt med $id
		elif [ ${url_array[3]} = "dikt" -a ${url_array[4]} = $url_base ]; then

			poem_owner=$(sqlite3 $database_path "SELECT epostadresse FROM dikt WHERE diktID='$url_base';")

			if [ "$poem_owner" == "$current_email" ]; then

				sqlite3 $database_path "DELETE FROM dikt WHERE diktID='$url_base';"

				create_response "1" "Dikt $url_base slettet" "$logged_in_session_id" "$current_email"
			else
				create_response "0" "Du er ikke eier av dette diktet og kan derfor ikke slette det"
			fi
		#Hvis url ikke eksisterer
		else
			create_response "0" "Feil url"
		fi
	else
		create_response "0" "Bruker må være logget inn for å gjennomføre denne handlingen"
	fi
fi

#If sessionid exist send this header (When logging in)
if [ ${#session_id} -gt "0" ]; then
	echo "Set-Cookie: session_id="$session_id"; Max-Age=7200; Path=/;"
	echo "Content-Length: "$length
	echo "Content-type:text/xml;charset=utf-8"
	echo "Access-Control-Allow-Origin: http://localhost"
	echo "Access-Control-Allow-Credentials: true"
	echo "Access-Control-Allow-Methods: POST,PUT,DELETE,GET"
	echo
	echo $response
#If sessionid does not exist send this header
else
	echo "Content-Length: "$length
	echo "Content-type:text/xml;charset=utf-8"
	echo "Access-Control-Allow-Origin: http://localhost"
	echo "Access-Control-Allow-Credentials: true"
	echo "Access-Control-Allow-Methods: POST,PUT,DELETE,GET"
	echo
	echo $response
fi
