let myUrl = 'http://localhost:8081/cgi-bin/api.cgi/';
let isLoggedIn = false;

//Funksjon for å sjekke om serviveworker er installert i nettleser. Forsøker å registrere hvis ikke
function checkServiceWorker() {
    if (!('serviceWorker' in navigator)) {
        console.log("Your browser does not support 'ServiceWorker'");
    } else {
        try {
			const registration = navigator.serviceWorker.register('./serviceWorker.js')
			if (registration.installing) {
				console.log('Service worker installing');
			}
			else if (registration.waiting) {
				console.log('Service worker installed');
			}
			else if (registration.active) {
				console.log('Service worker active');
			}
        }
	catch (error) {
			console.error(`Registration failed with ${error}`);
        }
    }
}

//Funksjon for å sjekke om bruker er innlogget ved å sjekke om det finnes en cookie med gyldig sesjons-ID
function checkLogin() {
    const cookieValue = document?.cookie
  ?.split('; ')
  ?.find(row => row.startsWith('session_id='))
  ?.split('=')[1];

  if (cookieValue !== undefined) {
      isLoggedIn = true;
  }
  else {
      isLoggedIn = false;
  }
}

//Funksjon for å vise innlogget informasjon og utloggingsknapp, eller innloggingsfelter og knapp
function loginOrLogout() {
    checkLogin();
    if (isLoggedIn == true) {
        document.getElementById("loginLogout").innerHTML+=
            `<h4 class="userInfo" id="nameOfLoggedInUser"></h4>
            <input class="button" type="button" value="Logg ut" onclick="logout()">`
    } else {
        document.getElementById("loginLogout").innerHTML+=
            `<h4>Logg inn for å gjøre endringer</h4>
            <input class='loginInput' type='email' placeholder='Epost' id='username'>
            <input class='loginInput' type='password' placeholder='Passord' id='password' onKeyUp='login(event)'>
            <input class='button' type='button' value='Logg inn' onclick='login("login")'>`
    }
}

//Funksjon for å logge inn
function login(event) {
    if (event.keyCode == 13 || event == "login")  {

        let username = document.getElementById("username").value;
        let password = document.getElementById("password").value;

	//Sender innloggingsinformasjon til APIet
        fetch(`${myUrl}login`, {
            method: 'POST',
            body: "<user><username>"+username+"</username><password>"+password+"</password></user>",
            credentials: 'include',
        })
	//Skriver svaret inn i et xml skjema
        .then(response => response.text())
        .then(data => {
            const parser = new DOMParser();
            const xml = parser.parseFromString(data, 
                "application/xml")
            const callStatus = xml.getElementsByTagName("status")[0].textContent;
            const loggedInEmail = xml.getElementsByTagName("useremail")[0].textContent;
            const loggedInFname = xml.getElementsByTagName("userfname")[0].textContent;
            const loggedInLname = xml.getElementsByTagName("userlname")[0].textContent;
            const alertStatus = xml.getElementsByTagName("statustext")[0].textContent;

            if (callStatus == 1) {

                localStorage["loggedInEmail"] = loggedInEmail;
                localStorage["loggedInFname"] = loggedInFname;
                localStorage["loggedInLname"] = loggedInLname;
                location.reload();
            } else {
                alert(alertStatus);
            }
        })
    }
}

//Funksjon for å logge ut
function logout() {

    fetch(`${myUrl}logout`, {
        method: 'POST',
        credentials: 'include',
    })
    .then(response => response.text())
    .then(data => {
        const parser = new DOMParser();
        const xml = parser.parseFromString(data,
            "application/xml")
        const callStatus = xml.getElementsByTagName("status")[0].textContent;
        const alertStatus = xml.getElementsByTagName("statustext")[0].textContent;
        if (callStatus == 1) {
            location.reload();
            document.cookie= "session_id=; Max-Age=0; Path=/; SameSite=none; Secure";
        } else {
            alert(alertStatus);
        }
    })
}

//Funksjon for å hente brukernavn
function getUsername() {
    checkLogin();
    if (isLoggedIn) {
        let user = localStorage["loggedInEmail"];
    }
}

//Funksjon for å hente brukerens navn
function getFullName() {
    checkLogin();
    if (isLoggedIn) {
        let userName = localStorage["loggedInFname"] + localStorage["loggedInLname"];
        document.getElementById("nameOfLoggedInUser").innerHTML+=userName;
    }
}

//Funksjon for å vise felter og knapper for endring av dikt
function showChangePoem(showChangePoemId, dikt) {
    document.getElementById("showMakeNewPoem").innerHTML=""
    document.getElementById("showChangePoem").innerHTML=""
    document.getElementById("showChangePoem").innerHTML+=
    `<form class='endreDiktForm'>
        <textarea class='diktInput' rows='5' cols='60' id='changedPoem' spellcheck='false'>${dikt}</textarea>
        <input class='slettDiktButton' type='button' value='Lagre endringer' onclick='changePoem(${showChangePoemId})'>
    </form>`
}

//Funksjon for å for vise felter og knapper for oppretting av dikt
function showMakeNewPoem() {
    document.getElementById("showChangePoem").innerHTML=""
    document.getElementById("showMakeNewPoem").innerHTML=""
    document.getElementById("showMakeNewPoem").innerHTML+=
    `<form class='endreDiktForm'>
        <textarea class='diktInput' rows='5' cols='60' id='addPoem' spellcheck='false'></textarea>
        <input class='slettDiktButton' type='button' value='Lagre dikt' onclick='addNewPoem()'> 
    </form>`
}

//Funksjon for å vise aksjonsknapper og datafelter for dikt (hvis man er logget inn)
function showChangeDeletePoem() {
    checkLogin();
    if (isLoggedIn == true) {
        document.getElementById("showChangeDeletePoem").innerHTML+=
        `<input class="slettDiktButton" type="button" value="Lag nytt dikt" onclick="showMakeNewPoem()">
        <input class="slettDiktButton" type="button" value="Slett alle egne dikt" onclick="deleteAllOwnPoems()">
        <input class="idInputField" type="text" placeholder="Dikt ID" value="" id="diktId">
        <input class="findPoemButton" type="button" value="Finn dikt" onclick="getOnePoem()">`
    } else {
        document.getElementById("showChangeDeletePoem").innerHTML+=
        `<input class="idInputField" type="text" placeholder="Dikt ID" value="" id="diktId">
        <input class="findPoemButton" type="button" value="Finn dikt" onclick="getOnePoem()">`
    }
}

//Funksjon for å hente alle dikt fra databasen
function getAllPoems() {

    //Get kall for å hente alle dikt
    fetch(`${myUrl}dikt/`, {
        method: 'GET',
        Origin: 'http://localhost'
    })
	//Skriver svaret fra APIet inn i et xml skjema
    .then(response => response.text())
    .then(data => {
        const parser = new DOMParser();
        const xml = parser.parseFromString(data, 
            "application/xml")

        //Teller antall dikt 
        const count = xml.getElementsByTagName("dikt").length

        //Henter epost til innlogget bruker
        const userEmail = localStorage["loggedInEmail"];

        //Variabler som skal vise knapper for sletting og endring av dikt
        let deletePoem;
        let doChangePoem;

		//Sjekker om bruker er logget inn eller ikke
        checkLogin();

        //Sjekker om det finnes noen dikt i databasen
        if (count > 0) {

            //Sender dokument med html som viser overskriftene
            if (isLoggedIn == true) {
                document.getElementById("alleDikt").innerHTML+=
                `<table id='test'>
                <tr>
                <td class='diktID'>Dikt ID</td>
                <td class='tekst'>Dikt</td>
                <td class='epost'>Eier av dikt</td>
                <td class='slettDikt'>Slett dikt</td>
                <td class='slettDikt'>Endre dikt</td>
                </tr>
                </table>`
            } else {
                document.getElementById("alleDikt").innerHTML+=
                `<table id='test'>
                <tr>
                <td class='diktID'>Dikt ID</td>
                <td class='tekst'>Dikt</td>
                </tr>
                </table>`
            }
            //Løkke for å vise alle dikt
            for (var i = 0; i < count; i++){

                //Henter ut id, dikt og epost til hver av diktene
                const id = xml.getElementsByTagName("diktID")[i].childNodes[0].nodeValue;
                const tekst = xml?.getElementsByTagName("tekst")[i]?.childNodes[0]?.nodeValue;
                const epost = xml.getElementsByTagName("epostadresse")[i].childNodes[0].nodeValue;

                //Hvis innlogget bruker er samme som eier av dikt vises knapper for endring og sletting
                if (userEmail === epost) {
                    deletePoem = `<input type='button' class='slettDiktButton'
                    value='Slett dikt' onClick='deleteOnePoem(${id})'>`;
                    doChangePoem = `<input type='button' class='slettDiktButton' 
                    value='Endre dikt' onClick='showChangePoem(${id}, "${tekst}")'>`;
                } else {
                    deletePoem = "";
                    doChangePoem= "";
                }

                //Sender dokument med html med alle diktene i databasen
                    if (isLoggedIn == true) {
                        document.getElementById("test").innerHTML+=
                        `<tr>
                        <td class='diktID'>${id}</td>
                        <td class='tekst'>${tekst}</td>
                        <td class='epost'>${epost}</td>
                        <td class='slettDikt'>${deletePoem}</td>
                        <td class='slettDikt'>${doChangePoem}</td>
                        </tr>`
                    } else {
                        document.getElementById("test").innerHTML+=
                        `<tr>
                        <td class='diktID'>${id}</td>
                        <td class='tekst'>${tekst}</td>
                        </tr>`
                    }
            }
        }
    })
}

//Funksjon for å hente ett bestemt dikt
function getOnePoem() {

    //Fjerner forrige resultat hvis det er noe
    document.getElementById("ettDikt").innerHTML="";

    //Henter diktid som er tastet inn
    let id = document.getElementById("diktId").value;

    //Setter diktid feltet tomt etter at diktid er hentet
    document.getElementById("diktId").value = "";

    //Kjører GET kall mot API for den bestemte dikt-IDen
    fetch(`${myUrl}dikt/${id}`, {
        method: 'GET',
        Origin: 'http://localhost'
    })
    .then(response => response.text())
    .then(data => {
        const parser = new DOMParser();
        const xml = parser.parseFromString(data, 
            "application/xml")

        //Teller antall tegn
        const exist = xml?.getElementsByTagName("dikt")[0]?.textContent;

        //Lagrer eposten til bruker som er logget inn
        const userEmail = localStorage["loggedInEmail"];

        const alertStatus = xml?.getElementsByTagName("statustext")[0]?.textContent;

        //Variabler som skal vise slett dikt og endre dikt knappene
        let deletePoem;
        let doChangePoem;

        //Sjekker at kallet inneholder et dikt
        if (exist != undefined) {

            //Sender dokument med html som viser overskriftene
            if (isLoggedIn == true) {
                document.getElementById("ettDikt").innerHTML+=
                    `<table id='test2'>
                    <tr>
                    <td class='diktID'>Dikt ID</td>
                    <td class='tekst'>Dikt</td>
                    <td class='epost'>Eier av dikt</td>
                    <td class='slettDikt'>Slett dikt</td>
                    <td class='slettDikt'>Endre dikt</td>
                    </tr>
                    </table>`
            } else {
                document.getElementById("ettDikt").innerHTML+=
                    `<table id='test2'>
                    <tr>
                    <td class='diktID'>Dikt ID</td>
                    <td class='tekst'>Dikt</td>
                    </tr>
                    </table>`
            }
                //Henter id, dikt og epost til valgt dikt fra databasen
                const id = xml.getElementsByTagName("diktID")[0].childNodes[0].nodeValue;
                const poem = xml.getElementsByTagName("tekst")[0].childNodes[0].nodeValue;
                const email = xml.getElementsByTagName("epostadresse")[0].childNodes[0].nodeValue;

                //Hvis eier av dikt er samme som er logget inn, vis knappene, hvis ikke: ikke vis dem
                if (userEmail === email) {
                    deletePoem = `<input type='button' class='slettDiktButton'
                    value='Slett dikt' onClick='deleteOnePoem(${id})'>`;
                    doChangePoem = `<input type='button' class='slettDiktButton' 
                    value='Endre dikt' onClick='showChangePoem(${id}, "${poem}")'>`;
                } else {
                    deletePoem = "";
                    doChangePoem= "";
                }

                //Sender HTML-dokument med det valgte diktet
                if (isLoggedIn == true) {
                    document.getElementById("test2").innerHTML+=
                        `<tr>
                            <td class='diktID'>${id}</td>
                            <td class='tekst'>${poem}</td>
                            <td class='epost'>${email}</td>
                            <td class='slettDikt'>${deletePoem}</td>
                            <td class='slettDikt'>${doChangePoem}</td>
                        </tr>`
                } else {
                    document.getElementById("test2").innerHTML+=
                        `<tr>
                            <td class='diktID'>${id}</td>
                            <td class='tekst'>${poem}</td>
                        </tr>`
                }
        } else {
            alert(alertStatus);
        }
    })
}

//Funksjon for å legge til et nytt dikt
function addNewPoem() {

    let newPoem = document.getElementById("addPoem").value;

    //POST kall mot APIet
    fetch(`${myUrl}dikt`, {
        method: 'POST',
        credentials: 'include',
        body: "<dikt><tekst>"+newPoem+"</tekst></dikt>"
    })
    .then(response => response.text())
    .then(data => {
        const parser = new DOMParser();
        const xml = parser.parseFromString(data, 
            "application/xml")
        const callStatus = xml.getElementsByTagName("status")[0].textContent;
        const alertStatus = xml.getElementsByTagName("statustext")[0].textContent;
        if (callStatus == 1) {
            location.reload();
        } else {
            alert(alertStatus);
        }
    })
}

//Funksjon for å endre et bestemt dikt. Nytter PUT for å oppdatere verdi i databasen
function changePoem(id) {
    let changedPoem = document.getElementById("changedPoem").value;

    //PUT kall mot API
    fetch(`${myUrl}dikt/${id}`, {
        method: 'PUT',
        credentials: 'include',
        body: "<dikt><tekst>"+changedPoem+"</tekst></dikt>"
    })
    .then(response => response.text())
    .then(data => {
        const parser = new DOMParser();
        const xml = parser.parseFromString(data,
            "application/xml")
        const callStatus = xml.getElementsByTagName("status")[0].textContent;
        const alertStatus = xml.getElementsByTagName("statustext")[0].textContent;
        if (callStatus == 1) {
            location.reload();
        } else {
            alert(alertStatus);
        }
    })
}

//Funksjon for å slette et bestemt dikt. Nytter Delete for å fjerne et valgt innslag (diktID) fra databasen
function deleteOnePoem(id) {

    fetch(`${myUrl}dikt/${id}`, {
        method: 'DELETE',
        credentials: 'include',
    })
    .then(response => response.text())
    .then(data => {
        const parser = new DOMParser();
        const xml = parser.parseFromString(data, 
            "application/xml")
        const callStatus = xml.getElementsByTagName("status")[0].textContent;
        const alertStatus = xml.getElementsByTagName("statustext")[0].textContent;
        if (callStatus == 1) {
            location.reload();
        } else {
            alert(alertStatus);
        }
    })
}

//Funksjon for å slette alle egne dikt. Nytter Delete på alle dikt med matchende eier (e-post) i databasen
function deleteAllOwnPoems() {

    if (confirm("Er du sikker på at du vil slette alle diktene dine?") == true) {
        fetch(`${myUrl}dikt`, {
            method: 'DELETE',
            credentials: 'include',
        })
        .then(response => response.text())
        .then(data => {
            const parser = new DOMParser();
            const xml = parser.parseFromString(data,
                "application/xml")
            const callStatus = xml.getElementsByTagName("status")[0].textContent;
            const alertStatus = xml.getElementsByTagName("statustext")[0].textContent;
            if (callStatus == 1) {
                location.reload();
            } else {
                alert(alertStatus);
            }
        })
    }
}
