var PLAYER_TOKEN = "";
var PLAYER_NAME = "";
var GAME_ID = "";
var EVENT_ID = 0;
var PERIODIC_CALL = 0;
var TABLE_PLAYERS = [];
var TABLE_CARDS = {};
var TABLE_VORBEHALTE = {};
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
		if(DEBUG){
			console.log(response.json());
		}
    return await response.json();
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
		if(DEBUG){
			console.log(response.json());
		}
    return await response.json();
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
    return await response.json();
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
    var game_obj = await api_post(url);
    gid = game_obj.game_id;
    document.getElementById("gid_field").value = gid;
    switch_view("JOIN");
}

async function login_to_game(game_id, player_name) {
    var url = "/api/" + game_id + "/join?player_name=" + player_name;
    var token_obj = await api_post(url);
    PLAYER_TOKEN = token_obj.token;
    PLAYER_NAME = token_obj.player_name;
    GAME_ID = game_id
    document.getElementById("display_game_id").textContent=GAME_ID;
    switch_view("PLAY")
    PERIODIC_CALL = setInterval(process_events, 2000);
}

async function process_events() {
    var url = "/api/" + GAME_ID + "/event?from_event_id=" + EVENT_ID;
    var event_list = await api_get(url);
    event_list.forEach( (e) => {
        EVENT_ID = e.e_id + 1;
        switch(e.e_type){
            case "KARTE":
                TABLE_CARDS[e.sender] = e.content;
                CURRENT_TURN = (CURRENT_TURN + 1) % 4;
                update_table();
                break;
            case "VORBEHALT":
						//Todo
                TABLE_VORBEHALTE[e.content.name] = e.content.vorbehalt;
                CURRENT_TURN = (CURRENT_TURN + 1) % 4;
                update_table();
                break;
            case "PLAYER_JOINED":
                var joined_name = e.content.name;
                TABLE_PLAYERS.push(joined_name);
                update_table();
                break;
            case "WAIT_VORBEHALT":
                update_own_cards();
                document.getElementById("vorbehalt").style.display = "block";
                document.getElementById("absage").style.display = "none";
                document.querySelectorAll("[id^=card_]").forEach(item => item.disabled = true);
                document.querySelectorAll("[id^=vorbehalt_]").forEach(item => item.disabled = false);
                CURRENT_TURN = TABLE_PLAYERS.indexOf(e.text_content);
                TABLE_VORBEHALTE = {};
                update_table();
                break;
            case "GAMEMODE":
                document.getElementById("vorbehalt").style.display = "none";
                document.getElementById("absage").style.display = "block";
                GAMEMODE = e.content;
                document.getElementById("display_game_mode").textContent=GAMEMODE;
                break;
            case "ROUND_STARTED":
                document.querySelectorAll("[id^=card_]").forEach(item => item.disabled = false);
                CURRENT_TURN = TABLE_PLAYERS.indexOf(e.text_content);
                update_table();
                break;
        }
    })
}

function update_table(){
    var own_index = TABLE_PLAYERS.indexOf(PLAYER_NAME);
    var own_name = TABLE_PLAYERS[own_index];
    var left_name = TABLE_PLAYERS[(own_index + 1) % 4];
    if(left_name == undefined) left_name = "--";
    var front_name = TABLE_PLAYERS[(own_index + 2) % 4];
    if(front_name == undefined) front_name = "--";
    var right_name = TABLE_PLAYERS[(own_index + 3) % 4];
    if(right_name == undefined) right_name = "--";

    document.getElementById("player_self").textContent=own_name;
    document.getElementById("player_left").textContent=left_name;
    document.getElementById("player_front").textContent=front_name;
    document.getElementById("player_right").textContent=right_name;

    document.getElementById("table_card_self").textContent=TABLE_CARDS[own_name];
    document.getElementById("table_card_left").textContent=TABLE_CARDS[left_name];
    document.getElementById("table_card_front").textContent=TABLE_CARDS[front_name];
    document.getElementById("table_card_right").textContent=TABLE_CARDS[right_name];

    document.getElementById("table_vorbehalt_self").textContent=TABLE_VORBEHALTE[own_name];
    document.getElementById("table_vorbehalt_left").textContent=TABLE_VORBEHALTE[left_name];
    document.getElementById("table_vorbehalt_front").textContent=TABLE_VORBEHALTE[front_name];
    document.getElementById("table_vorbehalt_right").textContent=TABLE_VORBEHALTE[right_name];

    document.getElementById("player_self").classList.remove("table_name_active");
    document.getElementById("player_left").classList.remove("table_name_active");
    document.getElementById("player_front").classList.remove("table_name_active");
    document.getElementById("player_right").classList.remove("table_name_active");
    switch(CURRENT_TURN){
        case own_index: document.getElementById("player_self").classList.add("table_name_active"); break;
        case (own_index + 1) % 4: document.getElementById("player_left").classList.add("table_name_active"); break;
        case (own_index + 2) % 4: document.getElementById("player_front").classList.add("table_name_active"); break;
        case (own_index + 3) % 4: document.getElementById("player_right").classList.add("table_name_active"); break;
    }
}

async function update_own_cards(){
    var url = "/api/" + GAME_ID + "/cards?player_token=" + PLAYER_TOKEN + "&player_name=" + PLAYER_NAME;
    HAND_CARDS = await api_get(url);
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
		//TODO
    var event = {
        "sender": PLAYER_NAME,
        "e_type": "KARTE",
        "content": card_content,
    }
    if(await api_post_body(event).successful){
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
    var event = {
        "sender": PLAYER_NAME,
        "e_type": "VORBEHALT",
        "content": vorbehalt,
    }
    if(await api_post_body(event).successful){
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
