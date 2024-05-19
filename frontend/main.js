const HOST = "localhost:8000"
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
    var url = "http://" + HOST + "/new_game";
    const response = await fetch(url, {
        method: "POST",
        headers: {"Content-Type": "application/json",},
        cache: "no-cache",
    });
    if(response.status != 200){
        alert("Error (ID: 1)");
        return;
    }
    var game_obj = await response.json();
    gid = game_obj.game_id;
    console.log("INFO: Game ID is " + gid)
    document.getElementById("gid_field").value = gid;
    switch_view("JOIN");
}

async function login_to_game(game_id, player_name) {
    var url = "http://" + HOST + "/" + game_id + "/join?player_name=" + player_name;
    const response = await fetch(url, {
        method: "POST",
        headers: {"Content-Type": "application/json",},
        cache: "no-cache",
    });
    if(response.status != 200){
        alert("Error (ID: 2)");
        console.log(response);
        return;
    }
    var token_obj = await response.json();
    PLAYER_TOKEN = token_obj.token;
    PLAYER_NAME = token_obj.player_name;
    GAME_ID = game_id
    console.log("INFO: Your token is " + PLAYER_TOKEN);
    document.getElementById("display_game_id").textContent=GAME_ID;
    switch_view("PLAY")
    PERIODIC_CALL = setInterval(process_events, 2000);
}

async function process_events() {
    var url = "http://" + HOST + "/" + GAME_ID + "/event?from_event_id=" + EVENT_ID;
    const response = await fetch(url, {
        method: "GET",
        headers: {"Content-Type": "application/json",},
        cache: "no-cache",
    });
    if(response.status != 200){
        alert("Error (ID: 3)");
        console.log(response);
        return;
    }
    var event_list = await response.json();
    event_list.forEach( (e) => {
        console.log(e);
        EVENT_ID = e.e_id + 1;
        switch(e.e_type){
            case "KARTE":
                TABLE_CARDS[e.sender] = e.content;
                CURRENT_TURN = (CURRENT_TURN + 1) % 4;
                update_table();
                break;
            case "VORBEHALT":
                TABLE_VORBEHALTE[e.sender] = e.content;
                CURRENT_TURN = (CURRENT_TURN + 1) % 4;
                update_table();
                break;
            case "PLAYER_JOINED":
                var joined_name = e.text_content;
                TABLE_PLAYERS.push(joined_name);
                TABLE_CARDS[joined_name];
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
    var url = "http://" + HOST + "/" + GAME_ID + "/cards?player_token=" + PLAYER_TOKEN + "&player_name=" + PLAYER_NAME;
    const response = await fetch(url, {
        method: "GET",
        headers: {"Content-Type": "application/json",},
        cache: "no-cache",
    });
    if(response.status != 200){
        alert("Error (ID: 4)");
        console.log(response);
        return;
    }
    HAND_CARDS = await response.json();
    sort_cards();
    console.log(HAND_CARDS);
    for(i = 0; i < HAND_CARDS.length; i++){
        document.getElementById("card_"+i).textContent=HAND_CARDS[i];
    }
    for(i = HAND_CARDS.length; i < 12; i++){
        document.getElementById("card_"+i).textContent="--";
    }
}

async function lay_card(card_slot) {
    var card_content = HAND_CARDS[card_slot];
    var event = {
        "sender": PLAYER_NAME,
        "e_type": "KARTE",
        "content": card_content,
    }
    if(await send_event(event)){
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
    if(await send_event(event)){
        document.getElementById("vorbehalt_"+vorbehalt).disabled = true;
    } else {
        console.log("Vorbehalt is not allowed.");
    }
}

async function send_event(event) {
    var url = "http://" + HOST + "/" + GAME_ID + "/event?player_token=" + PLAYER_TOKEN;
    const response = await fetch(url, {
        method: "POST",
        headers: {"Content-Type": "application/json",},
        cache: "no-cache",
        body: JSON.stringify(event),
    });
    if(response.status != 200){
        alert("Error (ID: 5)");
        console.log(response);
        return false;
    }
    var event_resp = await response.json();
    return event_resp.successful;
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
