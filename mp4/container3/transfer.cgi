#!/bin/bash

read BODY

# For konteinter 3. Skal kommunisere med database på konteinter 2 med http forespørsl
#setter opp noen variabler for bruk i de forskjellige metodene som kjører

lastname_login=""
firstname_login=""
email_login=""
html=""
output=""
session_id=""
status_user=""
current=""
cookie=$HTTP_COOKIE
database=http://10.35.20.4:8081/cgi-bin/api.cgi/


current=$(echo $cookie | cut -f2 -d'=')
#skriver ut header
html+=$(cat << EOF
	<!DOCTYPE html>
	<html>
	<head><link rel="stylesheet" href="http://10.35.20.4:8082/transfer.css"><title>diktbase</title></head>
	<body>
	<div class "divider">
		<h1 class="headline"> "Databasen til gruppe 3"</h1>
EOF
)
#hvis cookie ikke finnes, lag innloggingssiden
if [ -z $cookie ]; then
    html+=$(cat << EOF
					<form class="loginform" method="post" accept-charset="utf-8">
        		<input class="logininput" type="text" name="login" placeholder="email" id="email">
          	<input class="logininput" type="password" name="password" placeholder="Passord" id="passw">
          	<input class="loginlogoutbutton" type="submit" value="Logg inn">
        	</form>
        	</div>
        	<a class="homepageLink" href="http://10.35.20.4:80">Tilbake til hovedsiden</a>
          <br>
          <br>
EOF
		)
else #HVis cookie finnes, gi mulighet til å logge ut eller mulighet for å utføre operasjoner
    html+=$(
			cat << EOF
            <form class="logoutform" method="post" accept-charset="utf-8">
                <h4>$firstname_login</h4>
                <input class="loginlogoutbutton" type="submit" name="logout" value="logout">
            </form>
            </div>
            <a class="homepageLink" href="http://10.35.20.4:8082">Tilbake til hovedsiden</a>
            <br>
            <br>
            <div class="rowforms">
                <form method="post" accept-charset="utf-8">
                    <input class="buttons" type="submit" name="showmakenewpoem" value="Skriv et nytt dikt">
                </form>
                <form method="post" accept-charset="utf-8">
                    <input class="buttons" type="submit" name="deleteallmypoems" value="Slett alle dikt som tilhører deg">
                </form>
EOF
		)

fi

#Hent ut et dikt

html+=$(
	cat << EOF
    <form method="POST">
        <input type="text" name="getonepoem" placeholder="Id">
        <input class="buttons" type="submit" value="Vis dikt">
    </form>
    </div>
    <br>
EOF
)
htmlbody=$(echo $BODY | cut -f1 -d'=')
poemid=$(echo $BODY | cut -f2 -d'=')

if [ $htmlbody == "getonepoem" ]; then #her henter vi ut et dikt fra database for id nummer
		poem=$(curl -H "Accept: application/xml" -X GET $database"Dikt/$poemid/")
		one_poem=$(xmllint --xpath "//diktID/text()" - <<<"$poem")
		text=$(xmllint --format --xpath "//tekst/text()" - <<<"$poem")
 		owner=$(xmllint --xpath "//epost/text()" - <<<"$poem")

		testus="heisann"

if [ $testus == "heisann" ]; then
		button_change="<form method=\"POST\"><input class=\"buttons\" type=\"submit\" name=\"showchangepoem\" $one_poem !$text\" value= \"Endre\"></form>"
		button_delete="<form method=\"POST\"><input class=\"buttons\" type=\"submit\" name= \"deleteonepoem\" $text\" value=\"Slett\"></form>"

else
		button_change=""
		button_delete=""

fi

	if [ -z $cookie ]; then #Vis liste av dikt når bruker ikke er innlogget
		html+=$(
			cat <<EOF
              <table border='1'>
              <tr>
                    <th class="id">Id</th>
                    <th class="diktforeveryone">Dikt</th>
              </tr>
              <tr>
                    <td class="id">$one_poem</td>
                    <td class="diktforeveryone">$text</td>
              </tr>
              </table>
              <br>
EOF
		)
	else
			html+=$( # Vis dikt når bruker er innlogget
					cat << EOF
							<table border='1'>
							<tr>
									<th class="id">Id</th>
									<th class="dikt">dikt</th>
									<th class="eier">Eier</th>
									<th>Endre dikt</th>
									<th>Slette dikt</th>
							</tr>
							<tr>
									<td class="id">$one_poem</td>
									<td class="dikt">$text</td>
									<td class="eier">$owner</td>
									<td>$button_change</td>
									<td>$button_delete</td>
EOF
			)
	fi
fi

# Henter fra databsen på konteiner 2
poems=$(curl -H "Accept: application/xml" -X GET $database"Dikt/")

poems_id=$(xmllint --xpath "//diktID/text()" - <<<"$poems")
poems_text=$(xmllint --format --xpath "//tekst/text()" - <<<"$poems")
poems_owners=$(xmllint --xpath "//epost/text()" - <<<"$poems")

read -a id -d' ' <<<$poems_id
read -a email -d' ' <<<$poems_owners
IFS=$'\n'
read -a poems_string -d'\n'<<<$poems_text
IFS='\'


length=${#id[@]}

if [ -z $cookie ]; then # hvis cookie ikke eksisterer, vis alle dikt i database, BARE LESING!

	html+=$(
		cat << EOF
			<div id="alledikt">
			<h3> Alle dikt i database</h3>
			<table border ="1">
				<tr>
					<th class="id">Id</th>
					<th class="diktforeveryone">Dikt</th>
				</tr>
EOF
	)

else
	html+=$(
		cat << EOF
			<div id="poems">
			<h3> Alle dikt </h3>
			<table border="1">
				<tr>
						<th class="id">ID</th>
						<th class="diktforinnlogget">Dikt</th>
						<th class="eier">Eier</th>
						<th>Endre dikt</th>
						<th>Slette dikt</th>
				</tr>
EOF
	)
	#
fi

for ((i=0;i<$length;i++))
do

testus="heisann"

if [ $testus == "heisann" ]; then

		button_change="<form method=\"POST\"><input class=\"buttons\" type=\"submit\" name=\"showchangepoem ${id[i]} !${poems_string[i]}\" value=\"Endre\"></form>"
		button_delete="<form method=\"POST\"><input class=\"buttons\" type=\"submit\" name=\"deleteonepoem ${id[i]}\" value=\"Slett\"></form>"

else
		button_change=""
		button_delete=""
fi

if [ -z $cookie ]; then
		html+=$(
			cat << EOF
				<tr>
					<td class="id">${id[i]}</td>
					<td class="diktforeveryone">${poems_string[i]}</td>
				</tr>
				</div>
EOF
		)

else
	#EOF skriver inn så skriver ut
		html+=$(
			cat << EOF
				<tr>
					<td class="id">${id[i]}</td>
					<td class="diktforinnlogget">${poems_string[i]}</td>
					<td class="eier">${email[i]}</td>
					<td>$button_change</td>
					<td>$button_delete</td>
				</tr>
				</div>
EOF
		)
fi
done

# handlinger på buttons i de dynamiske html sidene
split_equal=$(echo $BODY | cut -f1 -d'=')
split_plus=$(echo $BODY | cut -f1 -d'+')

#vis "@" istedenfor urlencoded
if [ $split_equal == "login" ]; then
	email=$(echo $BODY | sed s/%40/@/g | cut -f1 -d'&' | cut -f2 -d'=')
	password=$(echo $BODY | cut -f3 -d'=')
	info=$(curl -H "Accept: application/xml" --cookie "session_id=$current" -d "<user><username>$email</username><password>$password</password></user>" -X POST $database"login")
  curl -H
	status=$(xmllint --xpath "//status/text()" - <<<"$info")
	session_id=$(xmllint --xpath "//sessionid/text()" - <<<"$info")
	email_login=$(xmllint --xpath "//useremail/text()" - <<<"$info")
	firstname_login=$(xmllint --xpath "//userfname/text()" - <<<"$info")
	lastname_login=$(xmllint --xpath "//userlname/text()" - <<<"$info")
#
	output+="Status: $status <br>"
	output+="SessionID: $session_id <br>"
#
	if [ $status == "1" ]; then
		output+="Logget inn <br>"
		status_user="loggedin"
	else
		output+="ikke logget inn <br>"
	fi

elif [ $split_equal == "logout" ]; then
		info=$(curl --cookie "session_id=$current" -X POST $database"logout/")
		status=$(xmllint --xpath "//status/text()" - <<<"$info")
		output+="Status: $status <br>"

		if [ $status == "1" ]; then
			output+="Logget ut <br>"
			status_user="loggedout"
		else
			output+="Logget inn <br>"
		fi


elif [ $split_equal == "newpoem" ]; then #en liten språkvask slik at alle bokstaver i nordisk alfabet fungerer med sed subititute/urlencoded/global
	new_poem=$(echo $BODY | sed s/%C3%B8/ø/g | sed s/%C3%A5/å/g | sed s/%2C/,/g | sed s/%C3%A6/æ/g | sed s/%3F/?/g | sed s/%3B/';'/g | cut -f2 -d'=' | sed s/+/" "/g)
    info=$(curl -H "Accept: application/xml" --cookie "session_id=$current" -d "<dikt><tekst>$new_poem</tekst></dikt>" -X POST $database"Dikt/")
#en liten språkvask slik at alle bokstaver i nordisk alfabet fungerer med sed subititute/urlencoded/global

elif [ $split_equal == "deleteallmypoems" ]; then
    info=$(curl -H "Accept: application/xml" --cookie "session_id=$current" -X DELETE $database"Dikt/")
		curl http://10.35.20.4:8082/cgi-bin/transfer.cgi
elif [ $split_equal == "showmakenewpoem" ]; then
    html+=$(
        cat << EOF
            <form method="POST" accept-charset="utf-8">
                <textarea rows='8' cols='70' name="newpoem" placeholder="Nytt dikt" spellcheck="false"></textarea>
                <input class="buttons" type="submit" value="Lagre">
            </form>
EOF
	 )

elif [ $split_plus == "deleteonepoem" ]; then
    id_to_delete=$(echo $BODY | cut -f2 -d'+' | cut -f1 -d'=')
    info=$(curl -H "Accept: application/xml" --cookie "session_id=$current" -X DELETE $database"Dikt/$id_to_delete/")


elif [ $split_plus == "changepoem" ]; then
    changed_poem=$(echo $BODY | sed s/%C3%B8/ø/g | sed s/%C3%A5/å/g | sed s/%2C/,/g | sed s/%C3%A6/æ/g | sed s/%3F/?/g | sed s/%3B/';'/g | cut -f2 -d'=' | sed s/+/" "/g)
    id_to_change=$(echo $BODY | cut -f2 -d'+' | cut -f1 -d'=')
    info=$(curl -H "Accept: application/xml" --cookie "session_id=$current" -d "<dikt><tekst>$changed_poem</tekst></dikt>" -X PUT $database"Dikt/$id_to_change/")


elif [ $split_plus == "showchangepoem" ]; then
    id_change_poem=$(echo $BODY | cut -f2 -d'+')
    poem_to_change=$(echo $BODY | sed s/%C3%B8/ø/g | sed s/%C3%A5/å/g | sed s/%2C/,/g | sed s/%C3%A6/æ/g | sed s/%3F/?/g | sed s/%3B/';'/g | cut -f2 -d'%' | cut -f1 -d'=' | cut -f2 -d'1' | sed s/+/" "/g)

	html+=$(
		cat << EOF
			<form method="POST" accept-charset="utf-8">
				<textarea rows='5' cols='60' name="changepoem $id_change_poem" spellcheck="false">$poem_to_change</textarea>
				<input class="buttons" type="submit" value="Endre dikt">
			</form>
EOF
	)
fi

#----------------------------------------------------------
# Avslutter den dynamiske html
html+=$(
cat << EOF
    </table>
    </body>
    </html>
EOF
)

#Headers
if [ $status_user == "loggedin" ]; then
    echo "Content-type:text/html;charset=utf-8"
    echo "Set-Cookie: session_id="$session_id"; Max-Age=7200; Path=/;"
    echo
elif [ $status_user == "loggedout" ]; then
    echo "Content-type:text/html;charset=utf-8"
    echo "Set-Cookie: session_id=; Max-Age=0; Path=/;"
    echo
else
    echo "Content-type:text/html;charset=utf-8"
    echo
fi

echo $html
