var PLAYER_TOKEN = "";
var PLAYER_NAME = "";
var PLAYER_POSITION = 0;
var GAME_ID = "";
var EVENT_ID = 0;
var PERIODIC_CALL = 0;
var PERIODIC_CALL_INTERVAL = 5000
var TABLE_PLAYERS = {0: "--", 1: "--", 2: "--", 3: "--"};
var TABLE_CARDS = {0: "--", 1: "--", 2: "--", 3: "--"};
var TABLE_VORBEHALTE = {0: "--", 1: "--", 2: "--", 3: "--"};
var HAND_CARDS = [];
var GAMEMODE = "GESUND";
var CURRENT_TURN = 0;
var DEBUG = true;

async function api_get(url) {
    const response = await fetch(url, {
        method: "GET",
        headers: {"Content-Type": "application/json",},
        cache: "no-cache",
    });
    if(response.status != 200){
        alert("Error while calling API");
		console.log(response);
        return;
    }
    var ret = await response.json();
    if(DEBUG){
        console.log(ret);
    }
    return ret;
}

async function api_post(url) {
    const response = await fetch(url, {
        method: "POST",
        headers: {"Content-Type": "application/json",},
        cache: "no-cache",
    });
    if(response.status != 200){
        alert("Error while calling API");
				console.log(response);
        return;
    }
    var ret = await response.json();
    if(DEBUG){
        console.log(ret);
    }
    return ret;
}

async function api_post_body(url, body) {
    const response = await fetch(url, {
        method: "POST",
        headers: {"Content-Type": "application/json",},
        cache: "no-cache",
        body: JSON.stringify(body),
    });
    if(response.status != 200){
        alert("Error (ID: 5)");
        console.log(response);
        return false;
    }
    var ret = await response.json();
    if(DEBUG){
        console.log(ret);
    }
    return ret;
}

function switch_view(view){
    if(view === "CREATE"){
        document.getElementById("create").style.display = "block";
        document.getElementById("login").style.display = "none";
        document.getElementById("play").style.display = "none";
    }
    if(view === "JOIN"){
        document.getElementById("create").style.display = "none";
        document.getElementById("login").style.display = "block";
        document.getElementById("play").style.display = "none";
    }
    if(view === "PLAY"){
        document.getElementById("create").style.display = "none";
        document.getElementById("login").style.display = "none";
        document.getElementById("play").style.display = "block";
    }
}

async function create_new_game() {
    var url = "/api/new_game";
    var resp = await api_post(url);
    document.getElementById("gid_field").value = resp.game_id;
    switch_view("JOIN");
}

async function login_to_game(game_id, player_name) {
    var url = "/api/" + game_id + "/join?player_name=" + player_name;
    var player_private = await api_post(url);
    PLAYER_TOKEN = player_private.token;
    PLAYER_NAME = player_private.player_name;
    PLAYER_POSITION = player_private.position;
    GAME_ID = game_id
    document.getElementById("display_game_id").textContent=GAME_ID;
    switch_view("PLAY")
    PERIODIC_CALL = setInterval(process_events, PERIODIC_CALL_INTERVAL);
}

async function process_events() {
    var url = "/api/" + GAME_ID + "/event?from_event_id=" + EVENT_ID;
    var event_list = await api_get(url);
    event_list.forEach( (e) => {
        EVENT_ID = e.e_id + 1;
        switch(e.e_type){
            case "KARTE":
                TABLE_CARDS[e.content.played_by.position] = e.content.card;
                CURRENT_TURN = (CURRENT_TURN + 1) % 4;
                update_table();
                break;
            case "VORBEHALT":
                TABLE_VORBEHALTE[e.content.said_by.position] = e.content.vorbehalt;
                CURRENT_TURN = (CURRENT_TURN + 1) % 4;
                update_table();
                break;
            case "PLAYER_JOINED":
                TABLE_PLAYERS[e.content.position] = e.content.name;
                update_table();
                break;
            case "GAME_STATE_CHANGED":
                switch(e.content.state){
                    case "WAIT_VORBEHALT":
                        update_own_cards();
                        document.getElementById("vorbehalt").style.display = "block";
                        document.getElementById("absage").style.display = "none";
                        document.querySelectorAll("[id^=card_]").forEach(item => item.disabled = true);
                        document.querySelectorAll("[id^=vorbehalt_]").forEach(item => item.disabled = false);
                        TABLE_VORBEHALTE = {0:"", 1:"", 2:"", 3:""};
                        update_table();
                        break;
                    case "ROUND_STARTED":
                        document.querySelectorAll("[id^=card_]").forEach(item => item.disabled = false);
                        document.getElementById("vorbehalt").style.display = "none";
                        document.getElementById("absage").style.display = "block";
                        GAMEMODE = e.content.mode;
                        document.getElementById("display_game_mode").textContent=GAMEMODE;
                        CURRENT_TURN = e.content.whose_turn;
                        update_table();
                        break;
                }
        }
    })
}

function update_table(){
    document.getElementById("player_self").textContent=TABLE_PLAYERS[PLAYER_POSITION];
    document.getElementById("player_left").textContent=TABLE_PLAYERS[(PLAYER_POSITION+1)%4];
    document.getElementById("player_front").textContent=TABLE_PLAYERS[(PLAYER_POSITION+2)%4];
    document.getElementById("player_right").textContent=TABLE_PLAYERS[(PLAYER_POSITION+3)%4];

    document.getElementById("table_card_self").textContent=TABLE_CARDS[PLAYER_POSITION];
    document.getElementById("table_card_left").textContent=TABLE_CARDS[(PLAYER_POSITION+1)%4];
    document.getElementById("table_card_front").textContent=TABLE_CARDS[(PLAYER_POSITION+2)%4];
    document.getElementById("table_card_right").textContent=TABLE_CARDS[(PLAYER_POSITION+3)%4];

    document.getElementById("table_vorbehalt_self").textContent=TABLE_VORBEHALTE[PLAYER_POSITION];
    document.getElementById("table_vorbehalt_left").textContent=TABLE_VORBEHALTE[(PLAYER_POSITION+1)%4];
    document.getElementById("table_vorbehalt_front").textContent=TABLE_VORBEHALTE[(PLAYER_POSITION+2)%4];
    document.getElementById("table_vorbehalt_right").textContent=TABLE_VORBEHALTE[(PLAYER_POSITION+3)%4];

    document.getElementById("player_self").classList.remove("table_name_active");
    document.getElementById("player_left").classList.remove("table_name_active");
    document.getElementById("player_front").classList.remove("table_name_active");
    document.getElementById("player_right").classList.remove("table_name_active");
    switch(CURRENT_TURN){
        case PLAYER_POSITION: document.getElementById("player_self").classList.add("table_name_active"); break;
        case (PLAYER_POSITION + 1) % 4: document.getElementById("player_left").classList.add("table_name_active"); break;
        case (PLAYER_POSITION + 2) % 4: document.getElementById("player_front").classList.add("table_name_active"); break;
        case (PLAYER_POSITION + 3) % 4: document.getElementById("player_right").classList.add("table_name_active"); break;
    }
}

async function update_own_cards(){
    var url = "/api/" + GAME_ID + "/playerinfo?player_token=" + PLAYER_TOKEN;
    var resp = await api_get(url)
    HAND_CARDS = resp.cards;
    sort_cards();
    for(i = 0; i < HAND_CARDS.length; i++){
        document.getElementById("card_"+i).textContent=HAND_CARDS[i];
    }
    for(i = HAND_CARDS.length; i < 12; i++){
        document.getElementById("card_"+i).textContent="--";
    }
}

async function lay_card(card_slot) {
    var card_content = HAND_CARDS[card_slot];
	var url = "/api/" + GAME_ID + "/lay_card?player_token=" + PLAYER_TOKEN + "&card=" + card_content;
    var resp = await api_post(url);
    if(resp.successful){
        HAND_CARDS.splice(card_slot, 1);
        for(i = 0; i < HAND_CARDS.length; i++){
            document.getElementById("card_"+i).textContent=HAND_CARDS[i];
        }
        for(i = HAND_CARDS.length; i < 12; i++){
            document.getElementById("card_"+i).textContent="--";
        }
        document.getElementById("table_card_self").textContent=card_content;
    } else {
        console.log("Card is not allowed.");
    }
}

async function vorbehalt(vorbehalt) {
	var url = "/api/" + GAME_ID + "/say_vorbehalt?player_token=" + PLAYER_TOKEN + "&vorbehalt=" + vorbehalt;
    var resp = await api_post(url);
    if(resp.successful){
        document.getElementById("vorbehalt_"+vorbehalt).disabled = true;
    } else {
        console.log("Vorbehalt is not allowed.");
    }
}

function sort_cards(){
    ranking = [];
    if(GAMEMODE == "GESUND"){
        ranking = [
            "SUPERSCHWEIN", "SCHWEIN", "H10", "CQ", "SQ", "HQ", "DQ", "CJ", "SJ", "HJ", "DJ",
            "DA", "D10", "DK", "D9", "CA", "C10", "CK", "C9", "SA", "S10", "SK", "S9", "HA", "HK", "H9",
        ]
    }
    HAND_CARDS.sort((a, b) => ranking.indexOf(a) - ranking.indexOf(b));
}
