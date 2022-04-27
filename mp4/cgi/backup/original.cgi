#!/bin/bash

read BODY

###Variables###
url_base=http://172.17.0.1:8180/cgi-bin/diktbase.cgi/
html=""
output=""
session_id=""
cookie=$HTTP_COOKIE
user_status=""
current_session=""
logged_in_email=""
logged_in_fname=""
logged_in_lname=""

current_session=$(echo $cookie | cut -f2 -d'=')

html+=$(cat << EOF
    <!DOCTYPE html>
    <html>
    <head><link rel="stylesheet" href="http://localhost/nytest.css"><title>diktbase</title></head>
    <body>
    <div class="topdiv">
        <h1 class="headline">Gruppe 12 sin diktbase</h1>
EOF
)


if [ -z $cookie ]; then
    html+=$(
        cat << EOF
            <form class="loginform" method="post" accept-charset="utf-8">
                <input class="logininput" type="text" name="login" placeholder="email" id="email">
                <input class="logininput" type="password" name="passw" placeholder="Passord" id="passw">
                <input class="loginlogoutbutton" type="submit" value="Logg inn">
            </form>
            </div>
            <a class="homepageLink" href="http://localhost">Gruppe 12 sin hjemmeside</a>
            <br>
            <br>
EOF
    )
else
    html+=$(
        cat << EOF
            <form class="logoutform" method="post" accept-charset="utf-8">
                <h4>$logged_in_fname</h4>
                <input class="loginlogoutbutton" type="submit" name="logout" value="logout">
            </form>
            </div>
            <a class="homepageLink" href="http://localhost">Gruppe 12 sin hjemmeside</a>
            <br>
            <br>
            <div class="rowforms">
                <form method="post" accept-charset="utf-8">
                    <input class="buttons" type="submit" name="showmakenewpoem" value="Lag nytt dikt">
                </form>
                <form method="post" accept-charset="utf-8">
                    <input class="buttons" type="submit" name="deleteallmypoems" value="Slett alle egne dikt">
                </form>

EOF
    )
fi


#Hente et dikt
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
body=$(echo $BODY | cut -f1 -d'=')
one_poem_id=$(echo $BODY | cut -f2 -d'=')

if [ $body == "getonepoem" ]; then
    one_poem=$(curl -H "Accept: application/xml" -X GET $url_base"dikt/$one_poem_id")
    id_one_poem=$(xmllint --xpath "//diktID/text()" - <<<"$one_poem")
    one_poem_text=$(xmllint --format --xpath "//tekst/text()" - <<<"$one_poem")
    one_poem_owner=$(xmllint --xpath "//epostadresse/text()" - <<<"$one_poem")

    ting="hei"


if [ $ting == "hei" ]; then
    change_poem_button="<form method=\"POST\"><input class=\"buttons\" type=\"submit\" name=\"showchangepoem $id_one_poem !$one_poem_text\" value=\"Endre\"></form>"
    delete_poem_button="<form method=\"POST\"><input class=\"buttons\" type=\"submit\" name=\"deleteone_poem $one_poem_text\" value=\"Slett\"></form>"

else
    change_poem_button=""
    delete_poem_button=""
fi

    if [ -z $cookie ]; then
        html+=$(
            cat << EOF
                <table border='1'>
                <tr>
                    <th class="id">Id</th>
                    <th class="diktforalle">Dikt</th>
                </tr>
                <tr>
                    <td class="id">$id_one_poem</td>
                    <td class="diktforalle">$one_poem_text</td>
                </tr>
                </table>
                <br>
EOF
        )
    else
        html+=$(
            cat << EOF
                <table border='1'>
                <tr>
                    <th class="id">Id</th>
                    <th class="diktforinnlogget">poems</th>
                    <th clasecho $htmls="eier">Eier</th>
                    <th>Endre poems</th>
                    <th>Slette poems</th>
                </tr>
                <tr>
                    <td class="id">$id_one_poem</td>
                    <td class="diktforinnlogget">$one_poem_text</td>
                    <td class="eier">$one_poem_owner</td>
                    <td>$change_poem_button</td>
                    <td>$delete_poem_button</td>
                </tr>
                </table>
                <br>
EOF
        )
    fi
fi


#Hente alle dikt
poems=$(curl -H "Accept: application/xml" -X GET $url_base"dikt/")

poems_id=$(xmllint --xpath "//diktID/text()" - <<<"$poems")
poems_text=$(xmllint --format --xpath "//tekst/text()" - <<<"$poems")
poems_owner=$(xmllint --xpath "//epostadresse/text()" - <<<"$poems")

read -a id -d' ' <<<$poems_id
read -a email -d' ' <<<$poems_owner
IFS=$"\n""""
read -a poems_array -d'\n'<<<$poems_text
IFS="\"

length=${#id[@]}

if [ -z $cookie ]; then
    html+=$(
        cat << EOF
            <div id="alledikt">
            <h2>Alle dikt</h2>
            <table border="1">
                <tr>
                    <th class="id">Id</th>
                    <th class="diktforalle">Dikt</th>
                </tr>
EOF
    )
else
    html+=$(
        cat << EOF
            <div id="allepoems">
            <h2>Alle dikt</h2>
            <table border="1">
                <tr>
                    <th class="id">Id</th>
                    <th class="diktforinnlogget">Dikt</th>
                    <th class="eier">Eier</th>
                    <th>Endre dikt</th>
                    <th>Slette dikt</th>
                </tr>
EOF
    )
fi


for ((i=0; i<$length;i++))
do

ting="hei"


if [ $ting == "hei" ]; then
    change_poem_button="<form method=\"POST\"><input class=\"buttons\" type=\"submit\" name=\"showchangepoem ${id[i]} !${poems_array[i]}\" value=\"Endre\"></form>"
    delete_poem_button="<form method=\"POST\"><input class=\"buttons\" type=\"submit\" name=\"deleteonepoem ${id[i]}\" value=\"Slett\"></form>"

else
    change_poem_button=""
    delete_poem_button=""
fi

if [ -z $cookie ]; then
    html+=$(
        cat << EOF
            <tr>
                <td class="id">${id[i]}</td>
                <td class="diktforalle">${poems_array[i]}</td>
            </tr>
            </div>
EOF
    )
else

    html+=$(
        cat << EOF
            <tr>
                <td class="id">${id[i]}</td>
                <td class="diktforinnlogget">${poems_array[i]}</td>
                <td class="eier">${email[i]}</td>
                <td>$change_poem_button</td>
                <td>$delete_poem_button</td>
            </tr>
            </div>
EOF
    )
fi
done




#Handlinger
split_at_equal=$(echo $BODY | cut -f1 -d'=')
split_at_plus=$(echo $BODY | cut -f1 -d'+')

if [ $split_at_equal == "login" ]; then
    email=$(echo $BODY | sed s/%40/@/g | cut -f1 -d'&' | cut -f2 -d'=')
    password=$(echo $BODY | cut -f3 -d'=')
    info=$(curl -H "Accept: application/xml" --cookie "session_id=$current_session" -d "<user><username>$email</username><password>$password</password></user>" -X POST $url_base"login")

    status=$(xmllint --xpath "//status/text()" - <<<"$info")
    session_id=$(xmllint --xpath "//sessionid/text()" - <<<"$info")
    logged_in_email=$(xmllint --xpath "//useremail/text()" - <<<"$info")
    logged_in_fname=$(xmllint --xpath "//userfname/text()" - <<<"$info")
    logged_in_lname=$(xmllint --xpath "//userlname/text()" - <<<"$info")


    output+="Status $status <br>"
    output+="Sessionid: $session_id <br>"

    if [ $status == "1" ]; then
        output+="Logget inn <br>"
        user_status="loggedin"
    else
        output+="Ikke logget inn <br>"
    fi



elif [ $split_at_equal == "logout" ]; then
    info=$(curl --cookie "session_id=$current_session" -X POST $url_base"logout")
    status=$(xmllint --xpath "//status/text()" - <<<"$info")
    output+="Status $status <br>"

    if [ $status == "1" ]; then
        output+="Logget ut <br>"
        user_status="loggedout"
    else
        output+="Ikke logget ut <br>"
    fi

elif [ $split_at_equal == "newpoem" ]; then
    new_poem=$(echo $BODY | sed s/%C3%B8/ø/g | sed s/%C3%A5/å/g | sed s/%2C/,/g | sed s/%C3%A6/æ/g | sed s/%3F/?/g | sed s/%3B/';'/g | cut -f2 -d'=' | sed s/+/" "/g)
    info=$(curl -H "Accept: application/xml" --cookie "session_id=$current_session" -d "<dikt><tekst>$new_poem</tekst></dikt>" -X POST $url_base"dikt")

elif [ $split_at_plus == "deleteonepoem" ]; then
    id_to_delete=$(echo $BODY | cut -f2 -d'+' | cut -f1 -d'=')
    info=$(curl -H "Accept: application/xml" --cookie "session_id=$current_session" -X DELETE $url_base"dikt/$id_to_delete")

elif [ $split_at_plus == "changepoem" ]; then
    changed_poem=$(echo $BODY | sed s/%C3%B8/ø/g | sed s/%C3%A5/å/g | sed s/%2C/,/g | sed s/%C3%A6/æ/g | sed s/%3F/?/g | sed s/%3B/';'/g | cut -f2 -d'=' | sed s/+/" "/g)
    id_to_change=$(echo $BODY | cut -f2 -d'+' | cut -f1 -d'=')
    info=$(curl -H "Accept: application/xml" --cookie "session_id=$current_session" -d "<dikt><tekst>$changed_poem</tekst></dikt>" -X PUT $url_base"Dikt/$id_to_change")

elif [ $split_at_equal == "deleteallmypoems" ]; then
    info=$(curl -H "Accept: application/xml" --cookie "session_id=$current_session" -X DELETE $url_base"dikt")

elif [ $split_at_plus == "showchangepoem" ]; then
    id_change_poem=$(echo $BODY | cut -f2 -d'+')
    poem_to_change=$(echo $BODY | sed s/%C3%B8/ø/g | sed s/%C3%A5/å/g | sed s/%2C/,/g | sed s/%C3%A6/æ/g | sed s/%3F/?/g | sed s/%3B/';'/g | cut -f2 -d'%' | cut -f1 -d'=' | cut -f2 -d'1' | sed s/+/" "/g)

    html+=$(
    cat << EOF
        <form method="post" accept-charset="utf-8">
            <textarea rows='5' cols='60' name="changepoem $id_change_poem" spellcheck="false">$poem_to_change</textarea>
            <input class="buttons" type="submit" value="Endre dikt">
        </form>
EOF
    )
elif [ $split_at_equal == "showmakenewpoem" ]; then
    html+=$(
        cat << EOF
            <form method="post" accept-charset="utf-8">
                <textarea rows='5' cols='60' name="newpoem" placeholder="Nytt dikt" spellcheck="false"></textarea>
                <input class="buttons" type="submit" value="Lagre">
            </form>
EOF
    )
fi

#Avslutter html
html+=$(
cat << EOF
    </table>
    </body>
    </html>
EOF
)

#Headers
if [ $user_status == "loggedin" ]; then
    echo "Content-type:text/html;charset=utf-8"
    echo "Set-Cookie: session_id="$session_id"; Max-Age=7200; Path=/;"
    echo
elif [ $user_status == "loggedout" ]; then
    echo "Content-type:text/html;charset=utf-8"
    echo "Set-Cookie: session_id=; Max-Age=0; Path=/;"
    echo
else
    echo "Content-type:text/html;charset=utf-8"
    echo
fi

echo $html
