#!/bin/sh


produce_xml() {
    echo '<?xml version="1.0" encoding ="utf-8"?>'
    echo '<login
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:noNamespaceSchemaLocation="http://10.35.20.4:8082/schema.xsd\">'

# login funksjon
    case $1 in
        login)
            echo '<bruker>'
            echo '<epostadresse>'$2'</epostadresse>'
            echo '<passordhash>'$3'</passordhash>'
            echo '</bruker>'
        ;;
        addPoem)
        echo '<Dikt>'
        echo '<dikt>'$2'</dikt>'
        echo '</Dikt>'
        ;;
    esac
    echo '</login>'
    
}
        



if [ -z "$HTTP_COOKIE" ]; then #setter http cookie
    
    cookie_value=$(pwgen -s 16 1)
    echo "Set-Cookie: sesjon=$cookie_value"
fi

sessionID=$(echo $HTTP_COOKIE | cut -d "=" -f 2)
response=$(wget -O -S --header="Cookie: $HTTP_Cookie" http://10.35.20.4:8081/Dikt/sesjon/$sessionID)
loginStatus=$(echo $response | xmlstarlet sel -t -v "//sessionID" -n)
status="Temp"
if [ "$sessionID" = "$loginStatus" ]; then
    status="Logget inn!"
else
    status="Du er IKKE Logget inn!"
fi

if [ "$REQUEST_METHOD" = "GET" ]; then
   echo "Content-type:text/xml;charset=utf-8"
   echo
    
    wget -qO- http://10.20.35.4:8082/form.html | sed "s/validate/$status/"
fi

if [ "$REQUEST_METHOD" = "POST" ]; then

    read POST_STRING # leser argumentene sendt med POST http metode
    decode=$(printf '%b' "${POST_STRING//%\\x}")
    
    name=$(echo -n $decode | cut -d '=' f2 | cut -d '&' -f1) # får tak i navn på funksjonen som skal sendes i html form. Deretter vil funksjonene nedenfor utføres i henhold til navn på felt i html form
    
    case $name in
    
        login)
            email=$(echo $decode | cut -d '=' -f3 | cut -d '&' -f1)
            password=$(echo $decode | cut -d '=' -f4 | cut -d '&' -f1)
            
	    echo "Content-type:text/html;charset=utf-8"
	    echo

            XML=$(make_xml login $email $password)
             
            APIANSWER=$(wget -O- -S --header='Content-Type: text/xml' --header "Cookie: $HTTP_COOKIE" --post-data "$XML" http://10.35.20.4:8081/Dikt/sesjon/) #til database tabell
            
            case $APIANSWER in
            1)
     	        wget -O- -q http://10.35.20.4:8082/login.html | sed "s/validate/Invalid login/"
	            ;;
            2)
	            echo  '<body>'
	            echo  'Login successful'
	            echo  '<button onclick="window.location.href=`http://158.248.21.214:8082/cgi-bin/cgi.cgi`">Go Back</button>'
      	            echo  '</body>'
	            ;;
             3)
	            wget -O- -q http://10.35.20.4:8082/login.html | sed "s/validate/Already logged inn/"
	            ;;
            esac
            ;;

            
        getPoem)
            echo "Content-type:text/html;charset=utf-8"
            echo

            poemID=$(echo $decode | cut -d '=' -f3)
            RESPONSE=$(wget -qO- -S --header='Content-type:text/plain' http://10.35.20.4:8081/Dikt/dikt/$poemID) #til attributt i database
            echo '<body>
            <center>'
            echo $RESPONSE | xmlstarlet tr --omit-decl http://10.35.20.4:8082/poem.xsl
            echo    '</center>'
            echo  '<button onclick="window.location.href=`http://10.35.20.4:8082/cgi-bin/cgi.cgi`">Go Back</button>' #fall back function
            echo  '</body>'
            ;;
        
        addPoem)
            poem=$(echo $decode | cut -d '=' -f3)
            file=$(make_xml addPoem $poem)

            echo "Content-type:text/html;charset=utf-8"
      	    echo

            RESPONSE=$(wget -O- -S --header='Content-Type: text/xml' --header "Cookie: $HTTP_COOKIE" --post-data "$file" http://10.35.20.4:8081/Dikt/dikt/)
            wget -qO- --header="Cookie: $HTTP_COOKIE" http://10.35.20.4:8082/cgi-bin/cgi.cgi
            ;;
        changePoem)
            echo "Content-type:text/html;charset=utf-8"
            echo

            MidDiktID=$(echo $decode | cut -d '=' -f3)
            diktID=$(echo $MidDiktID | cut -d '&' -f1)
            dikt=$(echo $decode | cut -d '=' -f4)

            XML=$(make_xml addPoem $dikt)
            RESPONSE=$(wget -O- -S --header='Content-Type: text/xml' --header "Cookie: $HTTP_COOKIE" --method=PUT --body-data="$XML" http://10.35.20.4:8081/Dikt/dikt/$diktID)
            wget -qO- --header="Cookie: $HTTP_COOKIE" http://10.35.20.4:8082/cgi-bin/cgi.cgi
            ;;
        deletePoem)
            
	    echo "Content-type:text/html;charset=utf-8"
            echo
            
            DiktID=$(echo $decode | cut -d '=' -f3)

            RESPONSE=$(wget -O- -S --header "Cookie: $HTTP_COOKIE" --method=DELETE http://10.35.20.4:8081/Dikt/dikt/$DiktID)
            wget -qO- --header="Cookie: $HTTP_COOKIE" http://10.35.20.4:8082/cgi-bin/cgi.cgi
            ;;
        showLogin)

            echo "Content-type:text/html;charset=utf-8"
            echo

            wget -O- -q http://10.35.20.4:8082/login.html | sed "s/validate/Logg inn/"
            ;;
            
        logout)
	        echo "Content-type:text/html;charset=utf-8"
	        echo

	        RESPONSE=$(wget -O- -S --header "Cookie: $HTTP_COOKIE" --method=DELETE http://10.35.20.4:8081/Dikt/sesjon/)
	        wget -qO- --header="Cookie: $HTTP_COOKIE" http://10.35.20.4:8080/cgi-bin/cgi.cgi
	        ;;

    esac
fi
