import flask
from flask import Flask, jsonify, json, request
from functions import getAllLineups, getOneLineup, getLineup, getAllPitchers, getPitcher, getGame, calcTeamFip, calcRuns, getPitchHand, checkResult, checkComplete
import requests, statsapi


app = flask.Flask(__name__)
app.config["DEBUG"] = True

all_teams = {'Arizona Diamondbacks', 'Atlanta Braves','Baltimore Orioles', 'Boston Red Sox', 'Chicago Cubs', 'Chicago White Sox', 'Cincinnati Reds', 'Cleveland Indians',
             'Colorado Rockies', 'Detroit Tigers', 'Houston Astros', 'Kansas City Royals', 'Los Angeles Angels', 'Los Angeles Dodgers', 'Miami Marlins', 'Milwaukee Brewers',
             'Minnesota Twins', 'New York Mets', 'New York Yankees', 'Oakland Athletics', 'Philadelphia Phillies', 'Pittsburgh Pirates', 'San Diego Padres', 'San Francisco Giants',
             'Seattle Mariners', 'St. Louis Cardinals', 'Tampa Bay Rays', 'Texas Rangers', 'Toronto Blue Jays', 'Washington Nationals'}
home_team = {}
home_players = []
num_home_players = 0
home_pitcher = []
num_home_pitchers = 0
home_bullpen = []
num_home_bullpens = 0
away_team = {}
away_players = []
num_away_players = 0
away_pitcher = []
num_away_pitchers = 0
away_bullpen = []
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

@app.route('/', methods=['GET'])
def home():
    return '''<h1>MLB Score Predictor</h1>
    <p>A score prediction system for Major League Baseball</p>'''

@app.route('/myteams', methods=['GET'])
def returnAll():
    return jsonify({'Home Team' : home_team}, {'Away Team': away_team})

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

            new_game = {"away": away_team_exp_score}, {"home": home_team_exp_score}
            games.append({f"game_{game_num + 1}": new_game})

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
    games.append(total_games)
    games.append(correct_games)
    return jsonify(games)

@app.route('/hometeam', methods=['GET'])
def getHome():
    home_team['home_players'] = home_players
    home_team['home_pitcher'] = home_pitcher
    home_team['home_bullpen'] = home_bullpen
    return jsonify(home_team)

@app.route('/hometeam/players', methods=['POST'])
def addHomePlayer():
    player = request.get_json()
    global num_home_players
    if num_home_players < 9:
        if statsapi.lookup_player(player) != [] and statsapi.lookup_player(player) != None:
            new_player = {}
            player_id = str(statsapi.lookup_player(player)[0]['id'])
            player_team = str(statsapi.lookup_team(statsapi.lookup_player(player)[0]['currentTeam']['id'])[0]['name'])
            new_player["player_id"] = player_id
            new_player["player_name"] = player
            new_player["player_team"] = player_team
            home_players.append(new_player)
            num_home_players += 1
            return jsonify({'home_players' : home_players})
        else:
            return f"{player} not found."
    else:
        return "Home Team can only have 9 players."

@app.route('/hometeam/pitcher', methods=['POST'])
def addHomePitcher():
    pitcher = request.get_json()
    global num_home_pitchers
    if num_home_pitchers < 1:
        if statsapi.lookup_player(pitcher) != [] and statsapi.lookup_player(pitcher) != None:
            new_player = {}
            player_id = str(statsapi.lookup_player(pitcher)[0]['id'])
            player_team = str(statsapi.lookup_team(statsapi.lookup_player(pitcher)[0]['currentTeam']['id'])[0]['name'])
            new_player["player_id"] = player_id
            new_player["player_name"] = pitcher
            new_player["player_team"] = player_team
            home_pitcher.append(new_player)
            num_home_pitchers += 1
            return jsonify({'home_pitcher' : home_pitcher})
        else:
            return f"{pitcher} not found."
    else:
        return "Home Team can only have 1 pitcher."

@app.route('/hometeam/bullpen', methods=['POST'])
def addHomeBullpen():
    global num_home_bullpens
    team = request.get_json()
    if num_home_bullpens < 1:
        if statsapi.lookup_team(team) != [] and statsapi.lookup_team(team) != None:
            new_bullpen = {}
            new_bullpen["team_name"] = team
            home_bullpen.append(new_bullpen)
            num_home_bullpens += 1
            return jsonify({'home_bullpen' : home_bullpen})
        else:
            return f"{team} not found."
    else:
        return "Home Team can only have 1 bullpen"

@app.route('/hometeam/deleteplayer/<string:name>', methods=['DELETE'])
def deleteHomePlayer(name):
    global num_home_players
    for i,q in enumerate(home_players):
      if q == name:
        del home_players[i]
        num_home_players -= 1
    return jsonify({'home_players' : home_players})

@app.route('/awayteam/deletepitcher', methods=['DELETE'])
def deleteHomePitcher():
    global num_home_pitchers
    for i,q in enumerate(home_pitcher):
        del home_pitcher[i]
    num_home_pitchers = 0
    return jsonify({'home_pitcher' : home_pitcher})

@app.route('/awayteam/deletebullpen', methods=['DELETE'])
def deleteHomeBullpen():
    global num_home_bullpens
    for i,q in enumerate(home_bullpen):
        del home_bullpen[i]
    num_home_bullpens = 0
    return jsonify({'home_bullpen' : home_bullpen})

@app.route('/hometeam/deleteall', methods=['DELETE'])
def deleteAllHome():
    global num_home_players
    for i,q in enumerate(home_players):
      del home_players[i]
    num_home_players = 0
    return jsonify({'home_players' : home_players})

@app.route('/awayteam', methods=['GET'])
def getAway():
    away_team['away_players'] = away_players
    away_team['away_pitcher'] = away_pitcher
    away_team['home_bullpen'] = away_bullpen
    return jsonify(away_team)

@app.route('/awayteam/players', methods=['POST'])
def addAwayPlayer():
    players = request.get_json()["players"]
    global num_away_players
    response_players = []
    for player in players:
        if num_away_players < 9:
            if statsapi.lookup_player(player) != [] and statsapi.lookup_player(player) != None:
                new_player = {}
                player_id = str(statsapi.lookup_player(player)[0]['id'])
                player_team = str(statsapi.lookup_team(statsapi.lookup_player(player)[0]['currentTeam']['id'])[0]['name'])
                new_player["player_id"] = player_id
                new_player["player_name"] = player
                new_player["player_team"] = player_team
                away_players.append(new_player)
                num_away_players += 1
                #return jsonify({'away_players': away_players})
                response_players.append(new_player)
            else:
                return f"{player} not found."
        else:
            return "Away Team can only have 9 players."
    return jsonify(response_players)


@app.route('/awayteam/pitcher', methods=['POST'])
def addAwayPitcher():
    pitcher = request.get_json()
    global num_away_pitchers
    if num_away_pitchers < 1:
        if statsapi.lookup_player(pitcher) != [] and statsapi.lookup_player(pitcher) != None:
            new_player = {}
            player_id = str(statsapi.lookup_player(pitcher)[0]['id'])
            player_team = str(statsapi.lookup_team(statsapi.lookup_player(pitcher)[0]['currentTeam']['id'])[0]['name'])
            new_player["player_id"] = player_id
            new_player["player_name"] = pitcher
            new_player["player_team"] = player_team
            away_pitcher.append(new_player)
            num_away_pitchers += 1
            return jsonify({'away_pitcher' : away_pitcher})
        else:
            return f"{pitcher} not found."
    else:
        return "Away Team can only have 1 pitcher."

@app.route('/awayteam/bullpen', methods=['POST'])
def addAwayBullpen():
    global num_away_bullpens
    team = request.get_json()
    if num_away_bullpens < 1:
        if statsapi.lookup_team(team) != [] and statsapi.lookup_team(team) != None:
            new_bullpen = {}
            new_bullpen["team_name"] = team
            away_bullpen.append(new_bullpen)
            num_away_bullpens += 1
            return jsonify({'away_bullpen' : away_bullpen})
        else:
            return f"{team} not found."
    else:
        return "Away Team can only have 1 bullpen"

@app.route('/awayteam/deleteplayer/<string:name>', methods=['DELETE'])
def deleteAwayPlayer(name):
    global num_home_players
    for i,q in enumerate(away_players):
      if q == name:
        del away_players[i]
        num_away_players -= 1
    return jsonify({'away_players' : away_players})

@app.route('/awayteam/deletepitcher', methods=['DELETE'])
def deleteAwayPitcher():
    global num_away_pitchers
    for i,q in enumerate(away_pitcher):
        del away_pitcher[i]
    num_away_pitchers = 0
    return jsonify({'away_pitcher' : away_pitcher})

@app.route('/awayteam/deletebullpen', methods=['DELETE'])
def deleteAwayBullpen():
    global num_away_bullpens
    for i,q in enumerate(away_bullpen):
        del away_bullpen[i]
    num_away_bullpens = 0
    return jsonify({'away_bullpen' : away_bullpen})

@app.route('/awayteam/deleteall', methods=['DELETE'])
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
            games = []
            home = ballpark['ballpark'][0]
            home_pitcher_id = str(home_pitcher['id'])
            away_pitcher_id = str(away_pitcher['id'])
            home_team_fip = calcTeamFip(home_pitcher_id, home_bullpen)
            away_team_fip = calcTeamFip(away_pitcher_id, away_bullpen)
            home_pitcher_hand = getPitchHand(home_pitcher_id)
            away_pitcher_hand = getPitchHand(away_pitcher_id)

            home_player_num = 0
            home_runs = 0
            home_team_exp_score = []
            home_players = []
            while home_player_num < 9:
                home_player_scores = {}
                player_id = home_players[home_player_num]['player_id']
                player_name = home_players[home_player_num]['player_name']
                team = home_players[home_player_num]['player_team']
                expRuns = calcRuns(player_id, home_player_num, team, home, away_pitcher_hand)
                home_runs += expRuns
                home_player_scores["player_exp_runs"] = expRuns
                home_player_scores["player_name"] = player_name
                home_players.append(home_player_scores)
                home_player_num += 1
            home_runs = home_runs * away_team_fip / league_avr_FIP
            home_team_total = {
                "team_name": home_team,
                "team_prediction": home_runs}
            home_team_exp_score.append(home_team_total)
            home_team_exp_score.append({'players': home_players})

            away_player_num = 0
            away_runs = 0
            away_team_exp_score = []
            away_players = []
            while away_player_num < 9:
                away_player_scores = {}
                player_id =away_players[away_player_num]['player_id']
                player_name = away_players[away_player_num]['player_name']
                team = away_players[away_player_num]['player_team']
                expRuns = calcRuns(player_id, away_player_num, team, home, home_pitcher_hand)
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
            away_team_exp_score.append({'players': away_players})

            games["Predicted Score"] = {"away": away_team_exp_score}, {"home": home_team_exp_score}

    return jsonify(games)

app.run(port=4000)




