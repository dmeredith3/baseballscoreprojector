from flask import Flask, jsonify, json, request
import requests, statsapi, time


schedule_url = 'http://statsapi.mlb.com/api/v1/schedule/games/?sportId=1&season=2019&date=2019-06-04'
game_url = 'https://statsapi.mlb.com/api/v1/schedule?gamePk='
lineup_url = '&language=en&hydrate=lineups'
probPitcher_url = '&language=en%&hydrate=probablePitcher'
base_url =  'https://statsapi.mlb.com/api/v1/people/'
hitting_url = '/stats?stats=byDateRange&group=hitting&season=2019&leagueListId=mlb'
pitching_url = '/stats?stats=byDateRange&group=pitching&season=2019&leagueListId=mlb'
team_stats_url = 'https://statsapi.mlb.com/api/v1/stats?stats=season&teamId='
team_pitching_url = '&group=pitching&gameType=REGULAR_SEASON&season=2019&playerPool=ALL'

hr_fb_rate = 0.147
FIP_const = 3.149
league_avr_FIP = 4.41
ip_game_avr = 5.30
wOBA_BB = .690
wOBA_HBP = .720
wOBA_1B = .873
wOBA_2B = 1.227
wOBA_3B = 1.546
wOBA_HR = 1.969
avr_wOBA = .318
wOBA_const = 1.180
r_PA = .123
wOBA_level_cut = 150
wOBA_pitch_avr = .146

avr_PA_game = {"1": 4.65,
               "2": 4.55,
               "3": 4.43,
               "4": 4.33,
               "5": 4.24,
               "6": 4.13,
               "7": 4.01,
               "8": 3.90,
               "9": 3.77}

def checkResult(game_num, team, schedule_url_date):
    get_schedule = requests.get(schedule_url_date)
    schedule = get_schedule.json()
    correct = 0
    if 'isWinner' in schedule['dates'][0]['games'][game_num]['teams'][team] and str(schedule['dates'][0]['games'][game_num]['teams'][team]['isWinner']) == 'True':
        correct += 1

    return correct

def checkComplete(game_num, team, schedule_url_date):
    get_schedule = requests.get(schedule_url_date)
    schedule = get_schedule.json()
    dnf = 0
    if 'isWinner' not in schedule['dates'][0]['games'][game_num]['teams'][team]:
        dnf += 1

    return dnf

def getPitchHand(playerID):
    get_pitcher_info = requests.get(base_url + str(playerID))
    pitcher_info = get_pitcher_info.json()
    pitcher_hand = pitcher_info['people'][0]['pitchHand']['code']
    return pitcher_hand


def calcRuns(playerID, batting_pos, team, home_team, pitcher_hand):
    playerID = str(playerID)
    batting_pos = str(batting_pos + 1)
    get_player_info = requests.get(base_url + playerID)
    player_info = get_player_info.json()
    player_hand = player_info['people'][0]['batSide']['code']
    player_pos = int(player_info['people'][0]['primaryPosition']['code'])

    if player_hand == 'S' and pitcher_hand == 'R':
        player_hand = 'L'
    elif player_hand == 'S' and pitcher_hand == 'L':
        player_hand = 'R'

    with open('park factors.json', 'r') as pf_file:
        pf = json.load(pf_file)

    team_num = 0
    if player_hand == 'R':
        while home_team != pf[team_num]['Team']:
            team_num += 1
        pf_1B = pf[team_num]['1B as R']
        pf_2B = pf[team_num]['2B as R']
        pf_3B = pf[team_num]['3B as R']
        pf_HR = pf[team_num]['HR as R']
        team_num = 0
        while team != pf[team_num]['Team']:
            team_num += 1
        hf_1B = pf[team_num]['1B as R'] / 2 + 50
        hf_2B = pf[team_num]['2B as R'] / 2 + 50
        hf_3B = pf[team_num]['3B as R'] / 2 + 50
        hf_HR = pf[team_num]['HR as R'] / 2 + 50

    elif player_hand == 'L':
        while home_team != pf[team_num]['Team']:
            team_num += 1
        pf_1B = pf[team_num]['1B as L']
        pf_2B = pf[team_num]['2B as L']
        pf_3B = pf[team_num]['3B as L']
        pf_HR = pf[team_num]['HR as L']
        team_num = 0
        while team != pf[team_num]['Team']:
            team_num += 1
        hf_1B = pf[team_num]['1B as L'] / 2 + 50
        hf_2B = pf[team_num]['2B as L'] / 2 + 50
        hf_3B = pf[team_num]['3B as L'] / 2 + 50
        hf_HR = pf[team_num]['HR as L'] / 2 + 50

    get_player_stats = requests.get(base_url + playerID + hitting_url)
    player_stats = get_player_stats.json()
    if 'splits' in player_stats['stats']:
        player_BB = player_stats['stats'][0]['splits'][0]['stat']['baseOnBalls']
        player_HBP = player_stats['stats'][0]['splits'][0]['stat']['hitByPitch']
        player_1B = player_stats['stats'][0]['splits'][0]['stat']['hits'] - player_stats['stats'][0]['splits'][0]['stat']['doubles'] - player_stats['stats'][0]['splits'][0]['stat']['triples'] - player_stats['stats'][0]['splits'][0]['stat']['homeRuns']
        player_2B = player_stats['stats'][0]['splits'][0]['stat']['doubles']
        player_3B = player_stats['stats'][0]['splits'][0]['stat']['triples']
        player_HR = player_stats['stats'][0]['splits'][0]['stat']['homeRuns']
        player_AB = player_stats['stats'][0]['splits'][0]['stat']['atBats']
        player_IBB = player_stats['stats'][0]['splits'][0]['stat']['intentionalWalks']
        player_SF = player_stats['stats'][0]['splits'][0]['stat']['sacFlies']
        player_wOBA_PA = player_AB + player_BB - player_IBB + player_SF + player_HBP
        player_wOBA = (player_BB * wOBA_BB + player_HBP * wOBA_HBP + player_1B * (pf_1B / hf_1B) * wOBA_1B + player_2B * (pf_2B / hf_2B) * wOBA_2B + player_3B * (pf_3B / hf_3B) * wOBA_3B + player_HR * (pf_HR / hf_HR) * wOBA_HR) / player_wOBA_PA
    else:
        player_wOBA_PA = 0
        if player_pos == 1:
            player_wOBA = wOBA_pitch_avr
        else:
            player_wOBA = avr_wOBA
    if player_wOBA_PA < wOBA_level_cut:
        if player_pos == 1:
            player_wOBA = player_wOBA * (player_wOBA_PA / wOBA_level_cut) + wOBA_pitch_avr * ((wOBA_level_cut - player_wOBA_PA) / wOBA_level_cut)
        else:
            player_wOBA = player_wOBA * (player_wOBA_PA / wOBA_level_cut) + avr_wOBA * ((wOBA_level_cut - player_wOBA_PA) / wOBA_level_cut)

    player_wRAA = (player_wOBA - avr_wOBA) / wOBA_const
    player_r_PA = player_wRAA + r_PA
    player_exp_runs = player_r_PA * avr_PA_game[batting_pos]
    return float(player_exp_runs)

def calcTeamFip(playerID, team):
    team_info = statsapi.lookup_team(team)
    jsonify(team_info)
    team_id = str(team_info[0]['id'])
    get_pitcher_stats = requests.get(base_url + playerID + pitching_url)
    pitcher_stats = get_pitcher_stats.json()
    if 'splits' in pitcher_stats['stats']:
        pitcher_gs = float(pitcher_stats['stats'][0]['splits'][0]['stat']['gamesStarted'])
        if pitcher_gs == 0:
            pitcher_gs = 1
        pitcher_ip_game = float(pitcher_stats['stats'][0]['splits'][0]['stat']['inningsPitched']) / pitcher_gs
        if pitcher_ip_game > 1.35 * ip_game_avr or pitcher_ip_game < 0.65 * ip_game_avr:
            pitcher_ip_game = ip_game_avr
        pitcher_hrs = float(pitcher_stats['stats'][0]['splits'][0]['stat']['homeRuns'])
        pitcher_bb =  float(pitcher_stats['stats'][0]['splits'][0]['stat']['baseOnBalls'])
        pitcher_hbp = float(pitcher_stats['stats'][0]['splits'][0]['stat']['hitBatsmen'])
        pitcher_k = float(pitcher_stats['stats'][0]['splits'][0]['stat']['strikeOuts'])
        pitcher_ip = float(pitcher_stats['stats'][0]['splits'][0]['stat']['inningsPitched'])
        pitcher_Fip = (13 * (pitcher_hrs) + 3 * (pitcher_bb + pitcher_hbp) - 2 * pitcher_k) / pitcher_ip + FIP_const
    else:
        pitcher_Fip = league_avr_FIP
        pitcher_ip_game = ip_game_avr
    get_reliever_stats = requests.get(team_stats_url + team_id + team_pitching_url)
    reliever_stats = get_reliever_stats.json()
    num_pitchers = int(reliever_stats['stats'][0]['totalSplits'])
    pitcher_num = 0
    reliever_hrs = 0.0
    reliever_bb = 0.0
    reliever_hbp = 0.0
    reliever_k = 0.0
    reliever_ip = 0.0
    while pitcher_num < num_pitchers:
        if float(reliever_stats['stats'][0]['splits'][pitcher_num]['stat']['gamesPitched'] / 2 > float(reliever_stats['stats'][0]['splits'][pitcher_num]['stat']['gamesStarted'])):
            reliever_hrs += float(reliever_stats['stats'][0]['splits'][pitcher_num]['stat']['homeRuns'])
            reliever_bb += float(reliever_stats['stats'][0]['splits'][pitcher_num]['stat']['baseOnBalls'])
            reliever_hbp += float(reliever_stats['stats'][0]['splits'][pitcher_num]['stat']['hitBatsmen'])
            reliever_k += float(reliever_stats['stats'][0]['splits'][pitcher_num]['stat']['strikeOuts'])
            reliever_ip += float(reliever_stats['stats'][0]['splits'][pitcher_num]['stat']['inningsPitched'])
        pitcher_num += 1
    reliever_Fip = (13 * (reliever_hrs) + 3 * (reliever_bb + reliever_hbp) - 2 * reliever_k) / reliever_ip + FIP_const
    team_Fip = pitcher_Fip * (pitcher_ip_game / 9) + reliever_Fip * ((9 - pitcher_ip_game) / 9)
    return team_Fip



def getGame(game_num, team_loc, schedule):
    games = []
    num_games = schedule['dates'][0]['totalGames']
    while game_num < num_games:
        new_game =  [{'Home Team' : schedule['dates'][0]['games'][game_num]['teams']['home']['team']['name']}, {'Away Team' : schedule['dates'][0]['games'][game_num]['teams']['away']['team']['name']}]
        games.append(new_game)
        game_num += 1
    if team_loc == 'home':
        return (games[0][0]['Home Team'])
    elif team_loc == 'away':
        return (games[0][1]['Away Team'])


def getAllLineups(all_teams):
    lineups = []
    for team in all_teams:
        team_loc = ''
        game_num = 0
        get_schedule = requests.get(schedule_url)
        schedule = get_schedule.json()
        num_games = schedule['dates'][0]['totalGames']
        while game_num < num_games:
            current_home_team = schedule['dates'][0]['games'][game_num]['teams']['home']['team']['name']
            curennt_away_team = schedule['dates'][0]['games'][game_num]['teams']['away']['team']['name']
            current_gamePk = schedule['dates'][0]['games'][game_num]['gamePk']
            if team == current_home_team:
                team_loc = 'home'
                gamePk = str(current_gamePk)
                get_game = requests.get(game_url + gamePk + lineup_url)
                game = get_game.json()
            if team == curennt_away_team:
                team_loc = 'away'
                gamePk = str(current_gamePk)
                get_game = requests.get(game_url + gamePk + lineup_url)
                game = get_game.json()
            game_num += 1
        if team_loc == 'home':
            if 'lineups' in game['dates'][0]['games'][0] and 'homePlayers' in game['dates'][0]['games'][0]['lineups']:
                team_lineup = game['dates'][0]['games'][0]['lineups']['homePlayers']
                new_team = {team: team_lineup}
                lineups.append(new_team)
            else:
                new_team = {team: 'No Lineup yet, check again closer to game time'}
                lineups.append(new_team)
        elif team_loc == 'away':
            if 'lineups' in game['dates'][0]['games'][0] and 'awayPlayers' in game['dates'][0]['games'][0]['lineups']:
                team_linup = game['dates'][0]['games'][0]['lineups']['awayPlayers']
                new_team = {team: team_linup}
                lineups.append(new_team)
            else:
                new_team = {team: 'No Lineup yet, check again closer to game time'}
                lineups.append(new_team)
        else:
            new_team = {team: 'No Game Today'}
            lineups.append(new_team)
    return(lineups)


def getOneLineup(team_name):
    team_loc = ''
    game_num = 0
    gamePk = 0
    get_schedule = requests.get(schedule_url)
    schedule = get_schedule.json()
    num_games = schedule['dates'][0]['totalGames']
    while game_num < num_games:
        current_home_team = schedule['dates'][0]['games'][game_num]['teams']['home']['team']['name']
        curennt_away_team = schedule['dates'][0]['games'][game_num]['teams']['away']['team']['name']
        current_gamePk = schedule['dates'][0]['games'][game_num]['gamePk']
        if team_name == current_home_team:
            team_loc = 'home'
            gamePk = str(current_gamePk)
            get_game = requests.get(game_url + gamePk + lineup_url)
            game = get_game.json()
        if team_name == curennt_away_team:
            team_loc = 'away'
            gamePk = str(current_gamePk)
            get_game = requests.get(game_url + gamePk + lineup_url)
            game = get_game.json()
        game_num += 1
    if team_loc == 'home':
        if 'lineups' not in game['dates'][0]['games'][0] or 'homePlayers' not in game['dates'][0]['games'][0]['lineups']:
            return'''<h1>No Lineup Found</h1>
            <p>Please check again closer to gametime</p>'''
        else:
            team_linup = game['dates'][0]['games'][0]['lineups']['homePlayers']
            return(jsonify({team_name +' Lineup' : team_linup}))
    elif team_loc == 'away':
        if 'lineups' not in game['dates'][0]['games'][0] or 'awayPlayers' not in game['dates'][0]['games'][0]['lineups']:
            return '''<h1>No Lineup Found</h1>
            <p>Please check again closer to gametime</p>'''
        else:
            team_linup = game['dates'][0]['games'][0]['lineups']['awayPlayers']
            return(jsonify({team_name +' Lineup' : team_linup}))
    else:
        return '''<h1>No Game Today</h1>
            <p>Please check again tommorow</p>'''

def getLineup(team_name, schedule, game_num, team_loc):
    gamePk = str(schedule['dates'][0]['games'][game_num]['gamePk'])
    get_game = requests.get(game_url + gamePk + lineup_url)
    game = get_game.json()
    if team_loc == 'home':
        if 'lineups' not in game['dates'][0]['games'][0] or 'homePlayers' not in game['dates'][0]['games'][0]['lineups']:
            if game['totalGames'] > 1:
                if 'lineups' in game['dates'][1]['games'][0] and 'homePlayers' in game['dates'][1]['games'][0]['lineups']:
                    team_linup = game['dates'][1]['games'][0]['lineups']['homePlayers']
                    return ({team_name: team_linup})
            else:
                return ""
        else:
            team_linup = game['dates'][0]['games'][0]['lineups']['homePlayers']
            return({team_name : team_linup})
    elif team_loc == 'away':
        if 'lineups' not in game['dates'][0]['games'][0] or 'awayPlayers' not in game['dates'][0]['games'][0]['lineups']:
            if game['totalGames'] > 1:
                    if 'lineups' in game['dates'][1]['games'][0] and 'awayPlayers' in game['dates'][1]['games'][0]['lineups']:
                        team_linup = game['dates'][1]['games'][0]['lineups']['awayPlayers']
                        return ({team_name: team_linup})
            else:
               return ""
        else:
            team_linup = game['dates'][0]['games'][0]['lineups']['awayPlayers']
            return({team_name : team_linup})
    else:
        return ''


def getAllPitchers(all_teams):
    probPitchers = []
    for team in all_teams:
        team_loc = ''
        game_num = 0
        get_schedule = requests.get(schedule_url)
        schedule = get_schedule.json()
        num_games = schedule['dates'][0]['totalGames']
        while game_num < num_games:
            current_home_team = schedule['dates'][0]['games'][game_num]['teams']['home']['team']['name']
            curennt_away_team = schedule['dates'][0]['games'][game_num]['teams']['away']['team']['name']
            current_gamePk = schedule['dates'][0]['games'][game_num]['gamePk']
            if team == current_home_team:
                team_loc = 'home'
                gamePk = str(current_gamePk)
                get_game = requests.get(game_url + gamePk + probPitcher_url)
                game = get_game.json()
            if team == curennt_away_team:
                team_loc = 'away'
                gamePk = str(current_gamePk)
                get_game = requests.get(game_url + gamePk + probPitcher_url)
                game = get_game.json()
            game_num += 1
        if team_loc == 'home':
            if 'probablePitcher' in game['dates'][0]['games'][0]['teams']['home']:
                team_pitcher = game['dates'][0]['games'][0]['teams']['home']['probablePitcher']
                new_team = {team: team_pitcher}
                probPitchers.append(new_team)
            else:
                new_team = {team: 'No probable pitcher yet, check again closer to game time'}
                probPitchers.append(new_team)
        elif team_loc == 'away':
            if 'probablePitcher' in game['dates'][0]['games'][0]['teams']['away']:
                team_pitcher = game['dates'][0]['games'][0]['teams']['away']['probablePitcher']
                new_team = {team: team_pitcher}
                probPitchers.append(new_team)
            else:
                new_team = {team: 'No probable pitcher yet, check again closer to game time'}
                probPitchers.append(new_team)
        else:
            new_team = {team: 'No Game Today'}
            probPitchers.append(new_team)
    return(probPitchers)

def getPitcher(team_name, schedule, game_num, team_loc):
        gamePk = str(schedule['dates'][0]['games'][game_num]['gamePk'])
        get_game = requests.get(game_url + gamePk + probPitcher_url)
        game = get_game.json()
        if team_loc == 'home':
            if 'probablePitcher' in game['dates'][0]['games'][0]['teams']['home']:
                team_pitcher = game['dates'][0]['games'][0]['teams']['home']['probablePitcher']
                probPitcher = {team_name: team_pitcher}
                return probPitcher
            else:
                probPitcher = ""
                return probPitcher
        elif team_loc == 'away':
            if 'probablePitcher' in game['dates'][0]['games'][0]['teams']['away']:
                team_pitcher = game['dates'][0]['games'][0]['teams']['away']['probablePitcher']
                probPitcher = {team_name: team_pitcher}
                return probPitcher
            else:
                probPitcher = ""
                return probPitcher
        else:
            probPitcher = ""
            return probPitcher