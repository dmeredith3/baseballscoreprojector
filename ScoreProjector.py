import flask
from flask import Flask, jsonify, json, request
from functions import getAllLineups, getOneLineup, getLineup, getAllPitchers, getPitcher, getGame, calcTeamFip, calcRuns, getPitchHand, checkResult, checkComplete
import requests, statsapi, random
from flask_cors import CORS


app = flask.Flask(__name__)
app.config["DEBUG"] = True

CORS(app, resources={r'/*': {'origins': '*'}})

dates = {'2019-05-01','2019-05-02','2019-05-03','2019-05-04','2019-05-05','2019-05-06','2019-05-07','2019-05-08','2019-05-09','2019-05-10','2019-05-11','2019-05-12','2019-05-13','2019-05-14','2019-05-15','2019-05-16','2019-05-17',
         '2019-05-18','2019-05-19','2019-05-20','2019-05-21','2019-05-22','2019-05-23','2019-05-24','2019-05-25','2019-05-26','2019-05-27','2019-05-28','2019-05-29','2019-05-30','2019-05-31','2019-06-01','2019-06-02','2019-06-03',
         '2019-06-04','2019-06-05','2019-06-06'}

all_teams = {'Arizona Diamondbacks', 'Atlanta Braves','Baltimore Orioles', 'Boston Red Sox', 'Chicago Cubs', 'Chicago White Sox', 'Cincinnati Reds', 'Cleveland Indians',
             'Colorado Rockies', 'Detroit Tigers', 'Houston Astros', 'Kansas City Royals', 'Los Angeles Angels', 'Los Angeles Dodgers', 'Miami Marlins', 'Milwaukee Brewers',
             'Minnesota Twins', 'New York Mets', 'New York Yankees', 'Oakland Athletics', 'Philadelphia Phillies', 'Pittsburgh Pirates', 'San Diego Padres', 'San Francisco Giants',
             'Seattle Mariners', 'St. Louis Cardinals', 'Tampa Bay Rays', 'Texas Rangers', 'Toronto Blue Jays', 'Washington Nationals'}

players = [
{"Max Scherzer",
"Hyun-Jin Ryu",
"Lucas Giolito",
"Lance Lynn",
"Matthew Boyd",
"Chris Sale",
"Frankie Montas",
"Gerrit Cole",
"Charlie Morton",
"Jake Odorizzi",
"Stephen Strasburg",
"Justin Verlander",
"Jacob deGrom",
"Walker Buehler",
"Mike Minor",
"German Marquez",
"Kyle Hendricks",
"Jose Berrios",
"Brandon Woodruff",
"Zack Greinke",
"Blake Snell",
"Noah Syndergaard",
"Cole Hamels",
"Tanner Roark",
"Sonny Gray",
"Marcus Stroman",
"Masahiro Tanaka",
"Trevor Bauer",
"Robbie Ray",
"Zack Wheeler",
"Luis Castillo",
"Spencer Turnbull",
"Pablo Lopez",
"Shane Bieber",
"Kyle Gibson",
"Clayton Kershaw",
"Patrick Corbin",
"Marco Gonzales",
"Brad Keller",
"Jose Quintana",
"Jon Gray",
"Joe Musgrove",
"Eduardo Rodriguez",
"Zach Eflin",
"Madison Bumgarner",
"Rick Porcello",
"Sandy Alcantara",
"Merrill Kelly",
"Wade Miley",
"Julio Teheran",
"Trent Thornton",
"Joey Lucchesi",
"Zach Davies",
"Max Fried",
"Tyler Mahle",
"Brett Anderson",
"Jack Flaherty",
"Eric Lauer",
"Aaron Nola",
"Dylan Bundy",
"Trevor Richards",
"Jose Urena",
"Adam Wainwright",
"J.A. Happ",
"Dakota Hudson",
"Mike Fiers",
"Miles Mikolas",
"Ivan Nova",
"Jakob Junis",
"Yusei Kikuchi",
"Jake Arrieta",
"Aaron Sanchez",
"Yu Darvish",
"Mike Leake",
"Reynaldo Lopez",
"Jeff Samardzija"},

{"Kirby Yates",
"Josh Hader",
"Brad Hand",
"Ken Giles",
"Aroldis Chapman",
"Jalen Beeks",
"Ryan Pressly",
"David Hernandez",
"Ty Buttrey",
"Liam Hendriks",
"Matt Barnes",
"John Gant",
"Sean Doolittle",
"Luke Jackson",
"Will Smith",
"Felipe Vazquez",
"Ian Kennedy",
"Amir Garrett",
"Nick Wittgren",
"Emilio Pagan",
"Seth Lugo",
"Hector Neris",
"Roberto Osuna",
"Trevor Gott",
"Kenley Jansen",
"Ryne Harper",
"Raisel Iglesias",
"Brandon Workman",
"Pedro Baez",
"Steve Cishek",
"Scott Oberg",
"Shane Greene",
"Robert Gsellman",
"Joakim Soria",
"Hansel Robles",
"Cam Bedrosian",
"Will Harris",
"Marcus Walden",
"Nick Anderson",
"Taylor Rogers",
"Giovanny Gallegos",
"Adrian Sampson",
"Jonathan Holder",
"Archie Bradley",
"Chad Bettis",
"Sam Dyson",
"Robert Stephenson",
"Jose Leclerc",
"Lou Trivino",
"Blake Treinen",
"Edwin Diaz",
"Jose Alvarado",
"Yoshihisa Hirano",
"Justin Anderson",
"Scott Barlow",
"Jake Diekman",
"Tommy Kahnle",
"Jordan Hicks",
"John Brebbia",
"Zack Britton",
"Adrian Houser",
"Reyes Moronta",
"Diego Castillo",
"Michael Lorenzen",
"Kyle Ryan",
"Adam Ottavino",
"Trevor May",
"Jeremy Jeffress",
"Felix Pena",
"Cory Gearrin",
"Colten Brewer",
"Wilmer Font",
"Wander Suero",
"Javy Guerra",
"Roenis Elias",
"Heath Hembree",
"Francisco Liriano",
"Greg Holland",
"Andrew Chafin",
"Shawn Kelley",
"Hector Rondon",
"Brandon Kintzler",
"Juan Nicasio",
"Junior Guerra",
"Alex Colome",
"Trey Wingenter",
"Touki Toussaint",
"Robbie Erlin",
"Matt Albers",
"Framber Valdez",
"Jared Hughes",
"Matt Wisler",
"Buck Farmer",
"Yusmeiro Petit",
"Tony Watson",
"Nick Ramirez",
"Tim Mayza",
"Brad Brach",
"Seranthony Dominguez",
"Paul Fry",
"Kyle Crick",
"Bryan Shaw",
"Chris Martin",
"Kelvin Herrera",
"Luis Perdomo",
"Tayron Guerrero",
"Chris Devenski",
"Yoan Lopez",
"Mark Melancon",
"Jeffrey Springs",
"Dylan Floro",
"Brandon Brennan",
"Connor Sadzeck",
"Brett Martin",
"Ryan Brasier",
"Wily Peralta",
"Carlos Estevez",
"Joe Jimenez",
"Josh Tomlin",
"Joe Biagini",
"Yonny Chirinos",
"Joshua James",
"Adam Cimber",
"Matt Andriese",
"Noe Ramirez",
"Austin Brice",
"Brad Boxberger",
"Miguel Castro",
"Jace Fry",
"Tyler Webb",
"Adam Kolarek",
"Thomas Pannone",
"Jose Alvarez",
"Jacob Webb",
"Jesse Chavez",
"Yimi Garcia",
"Dominic Leone",
"Tyler Kinley",
"Daniel Hudson",
"Andrew Miller",
"Luis Cessa",
"Sergio Romo",
"Matt Grace",
"Josh Osich",
"Nick Vincent",
"Dan Otero",
"Mike Wright Jr",
"Wandy Peralta",
"Sam Gaviglio",
"Adam Conley",
"Victor Alcantara",
"Mychal Givens",
"Wei-Yin Chen",
"Dan Winkler",
"Elvis Luciano",
"Zack Godley",
"Blaine Hardy",
"Alex Claudio",
"Tyler Chatwood",
"Anthony Swarzak",
"Blake Parker",
"Jeurys Familia",
"Kyle Barraclough",
"Luis Garcia",
"Craig Stammen",
"Cody Allen",
"Adam Warren",
"Richard Rodriguez"},

{"Yasmani Grandal",
"J.T. Realmuto",
"James McCann",
"Gary Sanchez",
"Robinson Chirinos",
"Willson Contreras",
"Christian Vazquez",
"Roberto Perez",
"Omar Narvaez",
"Buster Posey",
 "Jorge Alfaro",
"Austin Hedges",
"Carson Kelly",
"Tony Wolters",
"Josh Phegley",
"Austin Barnes",
"Wilson Ramos",
"Danny Jansen",
"Yadier Molina",
"Tucker Barnhart",
"Martin Maldonado",
"Yan Gomes",
"Jonathan Lucroy",
"Grayson Greiner"},

{"Max Muncy",
"Freddie Freeman",
"Peter Alonso",
"Josh Bell",
"Anthony Rizzo",
"Carlos Santana",
"Trey Mancini",
"Daniel Vogelbach",
"Edwin Encarnacion",
"Rhys Hoskins",
"Howie Kendrick",
"Luke Voit",
"Yandy Diaz",
"C.J. Cron",
"Jay Bruce",
"Paul Goldschmidt",
"Logan Forsythe",
"Pablo Sandoval",
"Christian Walker",
"Michael Chavis",
"Eric Thames",
"Ji-Man Choi",
"Matt Olson",
"Brandon Belt",
"Neil Walker",
"Jose Abreu",
"Justin Smoak",
"Mitch Moreland",
"Eric Hosmer",
"Joey Votto",
"Miguel Cabrera",
"Albert Pujols",
"Daniel Murphy",
"Tyler White",
"Yuli Gurriel",
"Ronald Guzman",
"Rowdy Tellez",
"Martin Prado",
"Jesus Aguilar",
"Kendrys Morales",
"Ryan O'Hearn",
"Chris Davis",
"Yonder Alonso"},

{"Ketel Marte",
"Max Muncy",
"Mike Moustakas",
"Brandon Lowe",
"Tommy La Stella",
"DJ LeMahieu",
"Whit Merrifield",
"Howie Kendrick",
"Derek Dietrich",
"Ozzie Albies",
"Jeff McNeil",
"Eric Sogard",
"Kolten Wong",
"Jonathan Schoop",
"David Bote",
"Michael Chavis",
"Cesar Hernandez",
"Jonathan Villar",
"Jose Altuve",
"Dee Gordon",
"Hanser Alberto",
"Greg Garcia",
"Adam Frazier",
"Brian Dozier",
"Ryan McMahon",
"Enrique Hernandez",
"Joe Panik",
"Yolmer Sanchez",
"Chad Pinder",
"Ronny Rodriguez",
"Ian Kinsler",
"Jurickson Profar",
"Jose Peraza",
"Robinson Cano",
"Daniel Robertson",
"Jason Kipnis",
"Rougned Odor",
"Daniel Descalso",
"Starlin Castro"},

{"Alex Bregman",
"Anthony Rendon",
"Nolan Arenado",
"Kris Bryant",
"Matt Chapman",
"Mike Moustakas",
"Eduardo Escobar",
"Hunter Dozier",
"Rafael Devers",
"Tommy La Stella",
"Yoan Moncada",
"David Fletcher",
"Howie Kendrick",
"Manny Machado",
"Yandy Diaz",
"Justin Turner",
"Josh Donaldson",
"Eugenio Suarez",
"Giovanny Urshela",
"Marwin Gonzalez",
"Pablo Sandoval",
"David Bote",
"Brian Anderson",
"Evan Longoria",
"Asdrubal Cabrera",
"J.D. Davis",
"Todd Frazier",
"Hanser Alberto",
"Greg Garcia",
"Matt Carpenter",
"Colin Moran",
"Vladimir Guerrero Jr",
"Rio Ruiz",
"Brandon Drury",
"Jeimer Candelario",
"Jose Ramirez",
"Ryon Healy",
"Yuli Gurriel",
"Daniel Robertson",
"Maikel Franco",
"Travis Shaw"},

{"Xander Bogaerts",
"Paul DeJong",
"Marcus Semien",
"Jorge Polanco",
"Trevor Story",
"Javier Baez",
"Corey Seager",
"Fernando Tatis Jr",
"Gleyber Torres",
"Adalberto Mondesi",
"Francisco Lindor",
"Carlos Correa",
"Tim Anderson",
"Elvis Andrus",
"Manny Machado",
"Jean Segura",
"Nick Ahmed",
"Dansby Swanson",
"Andrelton Simmons",
"Willy Adames",
"Jose Iglesias",
"Kevin Newman",
"Jonathan Villar",
"Freddy Galvis",
"Miguel Rojas",
"Ronny Rodriguez",
"Tim Beckham",
"Orlando Arcia",
"Amed Rosario",
"Brandon Crawford",
"Richie Martin Jr"},

{"Cody Bellinger",
"Mike Trout",
"Christian Yelich",
"Joey Gallo",
"Ketel Marte",
"George Springer",
"Ronald Acuna Jr",
"Kris Bryant",
"Max Kepler",
"Tommy Pham",
"Byron Buxton",
"Michael Brantley",
"Trey Mancini",
"Hunter Renfroe",
"Austin Meadows",
"Mookie Betts",
"Michael Conforto",
"Bryan Reynolds",
"Bryce Harper",
"Charlie Blackmon",
"Kevin Kiermaier",
"Hunter Pence",
"Whit Merrifield",
"Marcell Ozuna",
"Joc Pederson",
"J.D. Martinez",
"Avisail Garcia",
"Starling Marte",
"Andrew McCutchen",
"Alex Verdugo",
"Jeff McNeil",
"Alex Gordon",
"David Dahl",
"Shin-Soo Choo",
"Jake Marisnick",
"David Peralta",
"Andrew Benintendi",
"Mitch Haniger",
"Brett Gardner",
"Marwin Gonzalez",
"Josh Reddick",
"Jay Bruce",
"Dexter Fowler",
"Eddie Rosario",
"Jarrod Dyson",
"Harrison Bader",
"Niko Goodrum",
"Kole Calhoun",
"Brian Anderson",
"Juan Soto",
"Adam Eaton",
"Ramon Laureano",
"Leury Garcia",
"J.D. Davis",
"Wil Myers",
"Stephen Piscotty",
"Danny Santana",
"Robbie Grossman",
"Adam Jones",
"Lorenzo Cain",
"Nicholas Castellanos",
"Jorge Soler",
"Melky Cabrera",
"Nick Markakis",
"Albert Almora Jr",
"Nick Senzel",
"Kyle Schwarber",
"Franmil Reyes",
"Jason Heyward",
"Ben Gamel",
"Ian Desmond",
"Clint Frazier",
"Brian Goodwin",
"Domingo Santana",
"Teoscar Hernandez",
"Chad Pinder",
"Ryan Braun",
"Jackie Bradley Jr",
"Brandon Nimmo",
"Chris Taylor",
"Billy Hamilton",
"Delino DeShields",
"JaCoby Jones",
"Eloy Jimenez",
"Jose Martinez",
"Dwight Smith Jr",
"Christin Stewart",
"Victor Robles",
"Nomar Mazara",
"Steve Wilkerson",
"Manuel Margot",
"Jesse Winker",
"Mallex Smith",
"Yasiel Puig",
"Gregory Polanco",
"Randal Grichuk",
"Carlos Gonzalez",
"Gerardo Parra",
"Steven Duggar",
"Jake Bauers",
"Leonys Martin",
"Kevin Pillar",
"Raimel Tapia",
"Billy McKinney",
"Curtis Granderson"},

{"Michael Brantley",
"Austin Meadows",
"Daniel Vogelbach",
"Edwin Encarnacion",
"Hunter Pence",
"J.D. Martinez",
"Avisail Garcia",
"Luke Voit",
"Shin-Soo Choo",
"Nelson Cruz",
"Jose Abreu",
"Justin Smoak",
"Jorge Soler",
"Shohei Ohtani",
"Khris Davis",
"Miguel Cabrera",
"Renato Nunez",
"Albert Pujols",
"Tyler White",
"Jake Bauers",
"Rowdy Tellez",
"Kendrys Morales",
"Yonder Alonso"},]

home_team = {}
home_players = [{},{},{},{},{},{},{},{},{}]
num_home_players = 0
home_pitcher = [{}]
num_home_pitchers = 0
home_bullpen = [{}, {}, {}]
num_home_bullpens = 0
away_team = {}
away_players = [{},{},{},{},{},{},{},{},{}]
num_away_players = 0
away_pitcher = [{}]
num_away_pitchers = 0
away_bullpen = [{}, {}, {}]
num_away_bullpens = 0
ballpark = []
num_ballparks = 0
league_avr_FIP = 4.41

schedule_url = 'http://statsapi.mlb.com/api/v1/schedule/games/?sportId=1&season=2019'
game_url = 'https://statsapi.mlb.com/api/v1/schedule?gamePk='
lineup_url = '&language=en&hydrate=lineups'
probPitcher_url = '&language=en%&hydrate=probablePitcher'
base_url =  'https://statsapi.mlb.com/api/v1/people/'
hitting_url = '/stats?stats=byDateRange&group=hitting&season=2019&leagueListId=mlb'
pitching_url = '/stats?stats=byDateRange&group=pitching&season=2019&leagueListId=mlb'
fielding_url = '/stats?stats=seasonAdvanced&group=fielding&season=2019&leagueListId=mlb'

@app.route('/', methods=['GET'])
def home():
    return '''<h1>MLB Score Predictor</h1>
    <p>A score prediction system for Major League Baseball</p>'''

@app.route('/createplayerdatabase', methods=['GET'])
def playerdatabase():
    playerset_num = 0
    player_database = [[],[],[],[],[],[],[],[],[],[],[]]
    for playerset in players:
        playerset_database = []
        player_num = 0
        for player in playerset:
            print(len(playerset))
            print(player_num)
            if statsapi.lookup_player(player) != [] and statsapi.lookup_player(player) != 'none':
                if playerset_num == 0 or playerset_num == 1:
                    player_ID = str(statsapi.lookup_player(player)[0]['id'])
                    get_player_stats = requests.get(base_url + player_ID + pitching_url)
                    player_stats = get_player_stats.json()
                    new_player = {
                        "player_name": player,
                        "era": player_stats['stats'][0]['splits'][0]['stat']['era'],
                        "k_per_9": player_stats['stats'][0]['splits'][0]['stat']['strikeoutsPer9Inn'],
                        "k_per_w": player_stats['stats'][0]['splits'][0]['stat']['strikeoutWalkRatio'],
                        "whip": player_stats['stats'][0]['splits'][0]['stat']['whip'],
                        "wins": player_stats['stats'][0]['splits'][0]['stat']['wins'],
                        "player_team": str(statsapi.lookup_team(statsapi.lookup_player(player)[0]['currentTeam']['id'])[0]['name']),
                        "player_id": player_ID
                    }
                    playerset_database.append(new_player)
                else:
                    player_ID = str(statsapi.lookup_player(player)[0]['id'])
                    print(player_ID)
                    get_player_stats = requests.get(base_url + player_ID + hitting_url)
                    player_stats = get_player_stats.json()
                    if playerset_num == 8:
                        player_defense = []
                    else:
                        get_player_fielding = requests.get(base_url + player_ID + fielding_url)
                        player_fielding = get_player_fielding.json()
                        index = 0
                        num_indexes = len((player_fielding['stats'][0]['splits']))
                        player_defense = []
                        while index < num_indexes:
                            new_position = {
                                "position": player_fielding['stats'][0]['splits'][index]['stat']['position']['abbreviation'],
                                "fielding_perc": player_fielding['stats'][0]['splits'][index]['stat']['fielding'],
                            }
                            player_defense.append(new_position)
                            index += 1


                    new_player = {
                         "player_name": player,
                         "average": player_stats['stats'][0]['splits'][0]['stat']['avg'],
                         "on_base_per": player_stats['stats'][0]['splits'][0]['stat']['obp'],
                         "slugging_per": player_stats['stats'][0]['splits'][0]['stat']['slg'],
                         "homeruns": player_stats['stats'][0]['splits'][0]['stat']['homeRuns'],
                         "stolen_bases": player_stats['stats'][0]['splits'][0]['stat']['stolenBases'],
                         "player_team": str(statsapi.lookup_team(statsapi.lookup_player(player)[0]['currentTeam']['id'])[0]['name']),
                         "player_id": player_ID,
                         "fielding_perc": player_defense
                    }
                    playerset_database.append(new_player)
            player_num += 1
        player_database[playerset_num] = playerset_database
        playerset_num += 1
    return jsonify(player_database)

@app.route('/select/<int:player_type>', methods=['GET'])
def playerOptions(player_type):
    with open('player_database.json', 'r') as pd_file:
        player_database = json.load(pd_file)

    player_selection_pool = []
    if player_type >= 7 and player_type <= 9:
        player_type = 7
    elif player_type == 10:
        player_type = 8
    player_pos = int(player_type)
    player_type = player_database[player_pos]
    num_players = len(player_type)
    selections = []
    player1 = player_type[random.randrange(num_players)]
    player2 = player1
    player3 = player1

    while player2 == player1:
        player2 = player_type[random.randrange(num_players)]

    while player3 == player1 or player3 == player2:
        player3 = player_type[random.randrange(num_players)]

    selections.append(player1)
    selections.append(player2)
    selections.append(player3)
    return jsonify(selections)

@app.route('/myteams', methods=['GET'])
def returnAll():
    return jsonify(home_team, away_team)

@app.route('/lineups', methods=['GET'])
def todaysLineups():
    lineups = getAllLineups(all_teams)
    return(jsonify({'Todays Lineups': lineups}))

@app.route('/lineups/<string:team_name>', methods=['GET'])
def getTeamLineup(team_name):
    lineup = getOneLineup(team_name)
    return jsonify(lineup)

@app.route('/probablepitchers', methods=['GET'])
def getProbPitchers():
    probPitchers = getAllPitchers(all_teams)
    return(jsonify({'Probable Pitchers': probPitchers}))

@app.route('/scorepredictions/may', methods=['GET'])
def predscoresmay():
    correct = []
    num_right = 0
    total_num_games = 0
    for date in dates:
        print(date)
        schedule_url_date = schedule_url
        if date != "":
            schedule_url_date += "&date=" + date
        get_schedule = requests.get(schedule_url_date)
        schedule = get_schedule.json()
        num_games = schedule['dates'][0]['totalGames']
        total_num_games += num_games
        games = []
        game_num = 0
        while game_num < num_games:
            home_team = getGame(game_num, 'home', schedule)
            away_team = getGame(game_num, 'away', schedule)
            home_lineup = getLineup(home_team, schedule, game_num, 'home')
            home_pitcher = getPitcher(home_team, schedule, game_num, 'home')
            away_lineup = getLineup(away_team, schedule, game_num, 'away')
            away_pitcher = getPitcher(away_team, schedule, game_num, 'away')
            if home_lineup == None or home_lineup == "" or away_lineup == "" or away_lineup == None or home_pitcher == "" or away_pitcher == "":
                if home_lineup == "":
                    home_lineup = "No lineup yet, please check again later"
                if away_lineup == "":
                    away_lineup = "No lineup yet, please check again later"
                new_game = [{"Away": {away_team: away_lineup}}, {"Home":{home_team: home_lineup}}]
                games.append({"Game" + str(game_num + 1): new_game})
                game_num += 1
                total_num_games -= 1
            else:
                home_pitcher_id = str(home_pitcher[home_team]['id'])
                away_pitcher_id = str(away_pitcher[away_team]['id'])
                home_team_fip = calcTeamFip(home_pitcher_id, home_team)
                away_team_fip = calcTeamFip(away_pitcher_id, away_team)
                home_pitcher_hand = getPitchHand(home_pitcher_id)
                away_pitcher_hand = getPitchHand(away_pitcher_id)

                home_player_num = 0
                home_runs = 0
                home_team_exp_score = []
                home_players = []
                while home_player_num < 9:
                    home_player_scores = {}
                    player_id = home_lineup[home_team][home_player_num]['id']
                    player_name = home_lineup[home_team][home_player_num]['fullName']
                    expRuns = calcRuns(player_id, home_player_num, home_team, home_team, away_pitcher_hand)
                    home_runs += expRuns
                    home_player_scores["player_exp_runs"] = expRuns
                    home_player_scores["player_name"] = player_name
                    home_players.append(home_player_scores)
                    home_player_num += 1
                home_runs = home_runs * away_team_fip / league_avr_FIP
                home_team_total = {home_team: home_runs}
                home_team_exp_score.append(home_team_total)
                home_team_exp_score.append({'players': home_players})

                away_player_num = 0
                away_runs = 0
                away_team_exp_score = []
                away_players = []
                while away_player_num < 9:
                    away_player_scores = {}
                    player_id = away_lineup[away_team][away_player_num]['id']
                    player_name = away_lineup[away_team][away_player_num]['fullName']
                    expRuns = calcRuns(player_id, away_player_num, away_team, home_team, home_pitcher_hand)
                    away_runs += expRuns
                    away_player_scores["player_exp_runs"] = expRuns
                    away_player_scores["player_name"] = player_name
                    away_players.append(away_player_scores)
                    away_player_num += 1
                away_runs = away_runs * home_team_fip / league_avr_FIP
                away_team_total = {
                    "team_name": away_team,
                    "team_prediction": away_runs}
                away_team_exp_score.append(away_team_total)
                away_team_exp_score.append({'players:': away_players})

                #new_game = {"away": away_team_exp_score}, {"away": away_team_exp_score}
                #games.append({f"game_{game_num + 1}": new_game})

                if home_runs > away_runs:
                    num_right += checkResult(game_num, 'home', schedule_url_date)
                    total_num_games -= checkComplete(game_num, 'home', schedule_url_date)
                    print("Number Correct: " + str(num_right) + " Total Number: " + str(total_num_games))
                else:
                    num_right += checkResult(game_num, 'away', schedule_url_date)
                    total_num_games -= checkComplete(game_num, 'away', schedule_url_date)
                    print("Number Correct: " + str(num_right) + " Total Number: " + str(total_num_games))

                game_num += 1
        total_games = {"Total Games": total_num_games}
        correct_games = {"Number of Correct Games": num_right}
    correct.append(total_games)
    correct.append(correct_games)
    return jsonify(correct)

@app.route('/scorepredictions/<string:date>', methods=['GET'])
def predscores(date):
    schedule_url_date = schedule_url
    if date != "":
        schedule_url_date += "&date=" + date
    get_schedule = requests.get(schedule_url_date)
    schedule = get_schedule.json()
    num_games = schedule['dates'][0]['totalGames']
    total_num_games = num_games
    games = []
    correct = []
    game_num = 0
    num_right = 0
    while game_num < num_games:
        home_team = getGame(game_num, 'home', schedule)
        away_team = getGame(game_num, 'away', schedule)
        home_lineup = getLineup(home_team, schedule, game_num, 'home')
        home_pitcher = getPitcher(home_team, schedule, game_num, 'home')
        away_lineup = getLineup(away_team, schedule, game_num, 'away')
        away_pitcher = getPitcher(away_team, schedule, game_num, 'away')
        if home_lineup == None or home_lineup == "" or away_lineup == "" or away_lineup == None or home_pitcher == "" or away_pitcher == "":
            home_team_exp_score = []
            away_team_exp_score = []
            if home_lineup == "":
                home_lineup = "No lineup yet, please check again later"
            if away_lineup == "":
                away_lineup = "No lineup yet, please check again later"

            new_game = {
                "game": game_num + 1,
                "away": {
                    "team_name": away_team,
                    "team_prediction": 'NA',
                    "players": away_lineup
                },
                "home": {
                    "team_name": home_team,
                    "team_prediction": 'NA',
                    "players": home_lineup
                }
            }

            games.append(new_game)

            game_num += 1
            total_num_games -= 1
        else:
            home_pitcher_id = str(home_pitcher[home_team]['id'])
            away_pitcher_id = str(away_pitcher[away_team]['id'])
            home_team_fip = calcTeamFip(home_pitcher_id, home_team)
            away_team_fip = calcTeamFip(away_pitcher_id, away_team)
            home_pitcher_hand = getPitchHand(home_pitcher_id)
            away_pitcher_hand = getPitchHand(away_pitcher_id)

            home_player_num = 0
            home_runs = 0
            home_team_exp_score = []
            home_players = []
            while home_player_num < 9:
                home_player_scores = {}
                player_id = home_lineup[home_team][home_player_num]['id']
                player_name = home_lineup[home_team][home_player_num]['fullName']
                expRuns = calcRuns(player_id, home_player_num, home_team, home_team, away_pitcher_hand)
                home_runs += expRuns
                home_player_scores["player_exp_runs"] = expRuns
                home_player_scores["player_name"] = player_name
                home_players.append(home_player_scores)
                home_player_num += 1
            home_runs = home_runs * away_team_fip / league_avr_FIP
            home_runs = round(home_runs, 2)

            away_player_num = 0
            away_runs = 0
            away_team_exp_score = []
            away_players = []
            while away_player_num < 9:
                away_player_scores = {}
                player_id = away_lineup[away_team][away_player_num]['id']
                player_name = away_lineup[away_team][away_player_num]['fullName']
                expRuns = calcRuns(player_id, away_player_num, away_team, home_team, home_pitcher_hand)
                away_runs += expRuns
                away_player_scores["player_exp_runs"] = expRuns
                away_player_scores["player_name"] = player_name
                away_players.append(away_player_scores)
                away_player_num += 1
            away_runs = away_runs * home_team_fip / league_avr_FIP
            away_runs = round(away_runs, 2)


            new_game = {
                "game": game_num + 1,
                "away": {
                    "team_name": away_team,
                    "team_prediction": away_runs,
                    "players": away_players
                },
                "home": {
                    "team_name": home_team,
                    "team_prediction": home_runs,
                    "players": home_players
                }
            }

            games.append(new_game)

            if home_runs > away_runs:
                num_right += checkResult(game_num, 'home', schedule_url_date)
                total_num_games -= checkComplete(game_num, 'home', schedule_url_date)
                print("Number Correct: " + str(num_right) + " Total Number: " + str(total_num_games))
            else:
                num_right += checkResult(game_num, 'away', schedule_url_date)
                total_num_games -= checkComplete(game_num, 'away', schedule_url_date)
                print("Number Correct: " + str(num_right) + " Total Number: " + str(total_num_games))

            game_num += 1
        total_games = {"Total Games": total_num_games}
        correct_games = {"Number of Correct Games": num_right}
    #games.append(total_games)
    #games.append(correct_games)
    return jsonify(games)

@app.route('/hometeam', methods=['GET'])
def getHome():
    home_team['home_players'] = home_players
    home_team['home_pitcher'] = home_pitcher
    home_team['home_bullpen'] = home_bullpen
    return jsonify(home_team)


@app.route('/hometeam/players', methods=['POST'])
def addHomePlayer():
    players = request.get_json()["players"]
    with open('player_database.json', 'r') as pd_file:
        player_database = json.load(pd_file)

    for player in players:
        player['position'] = int(player['position'])
        if(player['position'] <= 6):
            player_type = player_database[player['position']]
        elif(player['position'] <= 9):
            player_type = player_database[7]
        else:
            player_type = player_database[8]

        if player['position'] == 2:
            player['position'] = 'C'
        elif player['position'] == 3:
            player['position'] = '1B'
        elif player['position'] == 4:
            player['position'] = '2B'
        elif player['position'] == 5:
            player['position'] = '3B'
        elif player['position'] == 6:
            player['position'] = 'SS'
        elif player['position'] == 7:
            player['position'] = 'LF'
        elif player['position'] == 8:
            player['position'] = 'CF'
        elif player['position'] == 9:
            player['position'] = 'RF'
        elif player['position'] == 10:
            player['position'] = 'DH'
        index = 0
        while (player['player_name'] != player_type[index]['player_name']):
            index += 1
        new_player = player_type[index]

        if (player['position'] == 'DH'):
            new_player['fielding_perc'] = 1
        else:
            index = 0
            player['temp_position'] = player['position']
            num_indexes = len(new_player['fielding_perc'])
            while (new_player['fielding_perc'][index]['position'] != player['temp_position']):
                    print(player['temp_position'] + ' does not equal ' + new_player['fielding_perc'][index]['position'])
                    print(str(index) + ' out of ' + str(num_indexes))
                    index += 1
                    if index >= num_indexes:
                        if player['temp_position'] == 'CF':
                            player['temp_position'] = 'RF'
                            index = 0
                        elif player['temp_position'] == 'RF':
                            player['temp_position'] = 'LF'
                            index = 0
                        else:
                            player['temp_position'] = 'CF'
                            index = 0
            new_player['fielding_perc'] = new_player['fielding_perc'][index]['fielding_perc']
        new_player['position'] = player['position']

    return jsonify(new_player)


@app.route('/hometeam/pitcher', methods=['POST'])
def addHomePitcher():
    num_home_players = 0
    pitcher = request.get_json()
    if num_home_pitchers < 1:
        with open('player_database.json', 'r') as pd_file:
            player_database = json.load(pd_file)
        index = 0
        while (pitcher['player_name'] != player_database[0][index]['player_name']):
            index += 1
        new_player = player_database[0][index]
        new_player['position'] = 'SP'
        return jsonify(new_player)

    else:
        return "home Team can only have 1 pitcher."

@app.route('/hometeam/bullpen', methods=['POST'])
def addhomeBullpen():
    num_home_pitchers = 0
    pitcher = request.get_json()
    if num_home_pitchers < 4:
        with open('player_database.json', 'r') as pd_file:
            player_database = json.load(pd_file)

        index = 0
        while (pitcher['player_name'] != player_database[1][index]['player_name']):
            index += 1
        new_player = player_database[1][index]
        new_player['position'] = 'RP'
        return jsonify(new_player)
    else:
        return "home Team can only have 1 bullpen"

@app.route('/hometeam/players/<string:id>', methods=['DELETE'])
def deleteHomePlayer(id):
    global num_home_players
    for player in home_players:
        if player['player_id'] == str(id):
            home_players.remove(player)
            num_home_players -= 1
    return jsonify({'home_players' : home_players})

@app.route('/awayteam/pitcher', methods=['DELETE'])
def deleteHomePitcher():
    global num_home_pitchers
    for i,q in enumerate(home_pitcher):
        del home_pitcher[i]
    num_home_pitchers = 0
    return jsonify({'home_pitcher' : home_pitcher})

@app.route('/awayteam/bullpen', methods=['DELETE'])
def deleteHomeBullpen():
    global num_home_bullpens
    for i,q in enumerate(home_bullpen):
        del home_bullpen[i]
    num_home_bullpens = 0
    return jsonify({'home_bullpen' : home_bullpen})

@app.route('/hometeam/players', methods=['DELETE'])
def deleteAllHome():
    global num_home_players
    for i,q in enumerate(home_players):
      del home_players[i]
    num_home_players = 0
    return jsonify({'home_players' : home_players})

@app.route('/autoselect/<int:team_type>', methods=['GET'])
def autoSelect(team_type):
    with open('player_database.json', 'r') as pd_file:
        player_database = json.load(pd_file)
    team = [{},{},{},{},{},{},{},{},{},{},{},{},{},{}]
    player_num = 0
    positions = [0, 1, 1, 1, 2, 3, 4, 5, 6, 7, 7, 7, 8]
    if team_type == 0:
        select_stat = 'average'
    elif team_type == 1:
        select_stat = 'homeruns'
    else:
        select_stat = 'stolen_bases'

    for position in positions:
        player_type = player_database[position]
        num_players = len(player_type)
        selections = []
        player1 = player_type[random.randrange(num_players)]
        player2 = player1
        player3 = player1

        while player2 == player1:
            player2 = player_type[random.randrange(num_players)]

        while player3 == player1 or player3 == player2:
            player3 = player_type[random.randrange(num_players)]

        if position == 0 or position == 1:
            selected_player = player1
            if selected_player['era'] < player2['era']:
                selected_player = player2
            if selected_player['era'] < player3['era']:
                selected_player = player3

            if position == 0:
                selected_player['position'] = 'SP'
            else:
                selected_player['position'] = 'RP'

        else:
            selected_player = player1
            if selected_player[select_stat] < player2[select_stat]:
                selected_player = player2
            if selected_player[select_stat] < player3[select_stat]:
                selected_player = player3

            if player_num == 4:
                selected_player['position'] = 'C'
            elif player_num == 5:
                selected_player['position'] = '1B'
            elif player_num == 6:
                selected_player['position'] = '2B'
            elif player_num == 7:
                selected_player['position'] = '3B'
            elif player_num == 8:
                selected_player['position'] = 'SS'
            elif player_num == 9:
                selected_player['position'] = 'LF'
            elif player_num == 10:
                selected_player['position'] = 'CF'
            elif player_num == 11:
                selected_player['position'] = 'RF'
            elif player_num == 12:
                selected_player['position'] = 'DH'
            print(selected_player)

            if (selected_player['position'] == 'DH'):
                selected_player['fielding_perc'] = 1
            else:
                index = 0
                temp_position = selected_player['position']
                num_indexes = len(selected_player['fielding_perc'])
                while (selected_player['fielding_perc'][index]['position'] != temp_position):
                    print(temp_position + ' does not equal ' + selected_player['fielding_perc'][index]['position'])
                    print(str(index) + ' out of ' + str(num_indexes))
                    index += 1
                    if index >= num_indexes:
                        if temp_position == 'CF':
                            temp_position = 'RF'
                            index = 0
                        elif temp_position == 'RF':
                            temp_position = 'LF'
                            index = 0
                        else:
                            selected_player['temp_position'] = 'CF'
                            index = 0
                selected_player['fielding_perc'] = selected_player['fielding_perc'][index]['fielding_perc']

        team[player_num] = selected_player
        player_num += 1
    return jsonify(team)


@app.route('/awayteam', methods=['GET'])
def getAway():
    away_team['away_players'] = away_players
    away_team['away_pitcher'] = away_pitcher
    away_team['away_bullpen'] = away_bullpen
    return jsonify(away_team)


@app.route('/awayteam/players', methods=['POST'])
def addAwayPlayer():
    players = request.get_json()["players"]
    with open('player_database.json', 'r') as pd_file:
        player_database = json.load(pd_file)

    for player in players:
        player['position'] = int(player['position'])
        if(player['position'] <= 6):
            player_type = player_database[player['position']]
        elif(player['position'] <= 9):
            player_type = player_database[7]
        else:
            player_type = player_database[8]

        if player['position'] == 2:
            player['position'] = 'C'
        elif player['position'] == 3:
            player['position'] = '1B'
        elif player['position'] == 4:
            player['position'] = '2B'
        elif player['position'] == 5:
            player['position'] = '3B'
        elif player['position'] == 6:
            player['position'] = 'SS'
        elif player['position'] == 7:
            player['position'] = 'LF'
        elif player['position'] == 8:
            player['position'] = 'CF'
        elif player['position'] == 9:
            player['position'] = 'RF'
        elif player['position'] == 10:
            player['position'] = 'DH'
        index = 0
        while (player['player_name'] != player_type[index]['player_name']):
            index += 1
        new_player = player_type[index]

        if (player['position'] == 'DH'):
            new_player['fielding_perc'] = 1
        else:
            index = 0
            player['temp_position'] = player['position']
            num_indexes = len(new_player['fielding_perc'])
            while (new_player['fielding_perc'][index]['position'] != player['temp_position']):
                    print(player['temp_position'] + ' does not equal ' + new_player['fielding_perc'][index]['position'])
                    print(str(index) + ' out of ' + str(num_indexes))
                    index += 1
                    if index >= num_indexes:
                        if player['temp_position'] == 'CF':
                            player['temp_position'] = 'RF'
                            index = 0
                        elif player['temp_position'] == 'RF':
                            player['temp_position'] = 'LF'
                            index = 0
                        else:
                            player['temp_position'] = 'CF'
                            index = 0
            new_player['fielding_perc'] = new_player['fielding_perc'][index]['fielding_perc']
        new_player['position'] = player['position']

    return jsonify(new_player)


@app.route('/awayteam/pitcher', methods=['POST'])
def addAwayPitcher():
    num_away_players = 0
    pitcher = request.get_json()
    if num_away_pitchers < 1:
        with open('player_database.json', 'r') as pd_file:
            player_database = json.load(pd_file)
        index = 0
        while (pitcher['player_name'] != player_database[0][index]['player_name']):
            index += 1
        new_player = player_database[0][index]
        new_player['position'] = 'SP'
        return jsonify(new_player)

    else:
        return "Away Team can only have 1 pitcher."

@app.route('/awayteam/bullpen', methods=['POST'])
def addAwayBullpen():
    num_away_pitchers = 0
    pitcher = request.get_json()
    if num_away_pitchers < 4:
        with open('player_database.json', 'r') as pd_file:
            player_database = json.load(pd_file)

        index = 0
        while (pitcher['player_name'] != player_database[1][index]['player_name']):
            index += 1
        new_player = player_database[1][index]
        new_player['position'] = 'RP'
        return jsonify(new_player)
    else:
        return "Away Team can only have 1 bullpen"

@app.route('/awayteam/players/<string:id>', methods=['DELETE'])
def deleteAwayPlayer(id):
    global num_away_players
    for player in away_players:
        if player['player_id'] == str(id):
            away_players.remove(player)
            num_away_players -= 1
    return jsonify({'away_players' : away_players})

@app.route('/awayteam/pitcher', methods=['DELETE'])
def deleteAwayPitcher():
    global num_away_pitchers
    for i,q in enumerate(away_pitcher):
        del away_pitcher[i]
    num_away_pitchers = 0
    return jsonify({'away_pitcher' : away_pitcher})

@app.route('/awayteam/bullpen', methods=['DELETE'])
def deleteAwayBullpen():
    global num_away_bullpens
    for i,q in enumerate(away_bullpen):
        del away_bullpen[i]
    num_away_bullpens = 0
    return jsonify({'away_bullpen' : away_bullpen})

@app.route('/awayteam/players', methods=['DELETE'])
def deleteAllAway():
    global num_away_players
    for i,q in enumerate(away_players):
      del away_players[i]
    num_away_players = 0
    return jsonify({'away_players' : away_players})

@app.route('/ballpark', methods=['POST'])
def addBallpark():
    global num_ballparks
    home = request.get_json()
    if num_ballparks < 1:
        if statsapi.lookup_team(home) != [] and statsapi.lookup_team(home) != None:
            new_ballpark = {}
            new_ballpark["ballpark"] = home
            ballpark.append(new_ballpark)
            num_ballparks += 1
            return jsonify({'ballpark' : ballpark})
        else:
            return f"{ballpark} not found."
    else:
        return "There can be only 1 ballpark."

@app.route('/deleteballpark/', methods=['DELETE'])
def deleteBallpark():
    global num_ballparks
    for i,q in enumerate(ballpark):
        del ballpark[i]
    num_ballparks = 0
    return jsonify({'ballpark' : ballpark})

@app.route('/calcScore', methods=['GET'])
def calcscores():
    if num_ballparks != 1:
        return "Number of ballparks must equal 1."
    elif num_home_players != 9:
        return "Number of home players must equal 9."
    elif num_home_pitchers != 1:
        return "Number of home pitchers must equal 1."
    elif num_home_bullpens != 1:
        return "Number of home bullpens must equal 1."
    elif num_away_players != 9:
        return "Number of away players must equal 9."
    elif num_away_pitchers != 1:
        return "Number of away pitchers must equal 1."
    elif num_away_bullpens != 1:
        return "Number of away bullpens must equal 1."
    else:
            games = {}
            home = ballpark[0]['ballpark']
            home_pitcher_id = str(home_pitcher[0]['player_id'])
            away_pitcher_id = str(away_pitcher[0]['player_id'])
            home_team_bullpen = home_bullpen[0]['team_name']
            away_team_bullpen = away_bullpen[0]['team_name']
            home_team_fip = calcTeamFip(home_pitcher_id, home_team_bullpen)
            away_team_fip = calcTeamFip(away_pitcher_id, away_team_bullpen)
            home_pitcher_hand = getPitchHand(home_pitcher_id)
            away_pitcher_hand = getPitchHand(away_pitcher_id)

            home_player_num = 0
            home_runs = 0
            home_team_exp_score = []
            return_home_players = []
            while home_player_num < 9:
                home_player_scores = {}
                player_id = home_players[home_player_num]['player_id']
                player_name = home_players[home_player_num]['player_name']
                team = home_players[home_player_num]['player_team']
                expRuns = calcRuns(player_iscored, home_player_num, team, home, away_pitcher_hand) * away_team_fip / league_avr_FIP
                print(expRuns)
                print(player_id)
                home_runs += expRuns
                home_player_scores["player_exp_runs"] = expRuns
                home_player_scores["player_name"] = player_name
                return_home_players.append(home_player_scores)
                home_player_num += 1
            home_team_total = {
                "team_name": home_team,
                "team_prediction": home_runs}
            home_team_exp_score.append(home_team_total)
            home_team_exp_score.append({'players': return_home_players})

            away_player_num = 0
            away_runs = 0
            away_team_exp_score = []
            return_away_players = []
            while away_player_num < 9:
                away_player_scores = {}
                player_id = away_players[away_player_num]['player_id']
                player_name = away_players[away_player_num]['player_name']
                team = away_players[away_player_num]['player_team']
                expRuns = calcRuns(player_id, away_player_num, team, home, home_pitcher_hand) * home_team_fip / league_avr_FIP
                print(expRuns)
                print(player_id)
                away_runs += expRuns
                away_player_scores["player_exp_runs"] = expRuns
                away_player_scores["player_name"] = player_name
                return_away_players.append(away_player_scores)
                away_player_num += 1
            away_team_total = {
                "team_name": away_team,
                "team_prediction": away_runs}
            away_team_exp_score.append(away_team_total)
            away_team_exp_score.append({'players': return_away_players})

            games["Predicted Score"] = {"away": away_team_exp_score}, {"home": home_team_exp_score}

    return jsonify(games)






