from datetime import datetime
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import plotly.express as px
import plotly.offline as py
import random
from sklearn.model_selection import train_test_split
from helper import *
import seaborn as sns


# load df 
df = pd.read_csv('./data/results.csv')

df['date'] = pd.to_datetime(df['date'])
df['year'] = df['date'].apply(lambda x : x.year)
df['month'] = df['date'].apply(lambda x : x.month)
df['day'] = df['date'].apply(lambda x : x.day)
df['home_team_wins'] = (df['home_score'] - df['away_score']) > 0
df['away_team_wins'] = (df['home_score'] - df['away_score']) < 0
df['draw'] = (df['home_score'] - df['away_score']) == 0


# get teams, cities and countries from the df
home_teams = df['home_team'].unique()
away_teams = df['away_team'].unique()
tournaments = df['tournament'].unique()
cities = df['city'].unique()
countries = df['country'].unique()

# load Qatar groups dataframe
qatar_teams = pd.read_csv('./data/qatar2022.csv',sep=';')
qatar_teams['Points'] = 0
### Rename countries
qatar_teams.loc[qatar_teams['Team'] == 'USA', 'Team'] = 'United States'

# get the 32 countries that play in the world cup
qatar_2022_teams_list = list(qatar_teams['Team'])
qatar_2022_results = df.loc[(df.home_team.isin(qatar_2022_teams_list)) | (df.away_team.isin(qatar_2022_teams_list)),: ]
#official_tournament = ['FIFA World Cup','FIFA World Cup qualification','Copa América','NAFU Championship','Pan American Championship','UEFA Euro qualification','CONCACAF Championship','African Cup of Nations qualification','African Cup of Nations','AFC Asian Cup qualification','Gulf Cup','AFC Asian Cup','UEFA Euro','CONCACAF Championship qualification','Kuneitra Cup','Arab Cup','CONMEBOL–UEFA Cup of Champions','Gold Cup','African Nations Championship','CONCACAF Nations League','UEFA Nations League']
### use only official matches
#qatar_2022_results = qatar_2022_results.loc[(qatar_2022_results.tournament.isin(official_tournament))]

# filter by mathes play before 2019
qatar_2022_results = qatar_2022_results[qatar_2022_results['year'] < 2019]

# get the probs in the df
hist_proba_qatar_teams = get_probs_for_WC(qatar_2022_results)

def update_table(country1,country2,result):
    if result == 'Draw':
        qatar_teams.loc[qatar_teams['Team'] == country1, 'Points'] += 1
        qatar_teams.loc[qatar_teams['Team'] == country2, 'Points'] += 1
    elif result == country1:
        qatar_teams.loc[qatar_teams['Team'] == country1, 'Points'] += 3
    elif result == country2:
        qatar_teams.loc[qatar_teams['Team'] == country2, 'Points'] += 3
        
# get the schedule for the world cup

schudule = pd.read_csv('./data/matchs-schudule.csv',sep=';')
schudule['date'] = pd.to_datetime(schudule['date'],format='%d/%m/%Y')
schudule.loc[schudule['country1'] == 'USA', 'country1'] = 'United States'
schudule.loc[schudule['coutry2'] == 'USA', 'coutry2'] = 'United States'

# the stages
groups_stage = schudule[schudule['phase'] == 'group matches']
knockout_stage = schudule[schudule['phase'] != 'group matches']
round_16 = schudule[schudule['phase'] == 'round 16']
quarter_finals = schudule[schudule['phase'] == 'quarter-finals']
semi_finals = schudule[schudule['phase'] == 'semi-finals']
third_place = schudule[schudule['phase'] == 'third place']
final = schudule[schudule['phase'] == 'final']

# get all the world cup matches in the df
wc_games = df[df['tournament'] == 'FIFA World Cup']
wc_games = wc_games[wc_games['year'] < 2019]
wc_games = wc_games[wc_games['year'] > 2001]
# get the probs for teams in the last world cups
hist_proba_wc_games = get_probs_for_WC(wc_games)

# load shootouts dataframe
shootouts = pd.read_csv('./data/shootouts.csv')
shootouts['date'] = pd.to_datetime(shootouts['date'])
shootouts['home_team_wins'] = np.where(shootouts['winner'] == shootouts['home_team'], True, False)
shootouts['away_team_wins'] = np.where(shootouts['winner'] == shootouts['away_team'], True, False)
# columns in order to re use the get probs func
shootouts['home_score'] = 0
shootouts['draw'] = False
qatar_2022_shootouts = shootouts.loc[(shootouts.home_team.isin(qatar_2022_teams_list)) | (shootouts.away_team.isin(qatar_2022_teams_list)),: ]
# get the probs for the shootouts
hist_proba_qatar_teams_shootouts = get_probs_for_WC(qatar_2022_shootouts)
## load the data from Fbref 
wc_teams =  pd.read_csv('./data/teams/world_cup_teams.csv')
wc_teams.loc[wc_teams['home_team'] == 'IR Iran', 'home_team'] = 'Iran'
wc_teams.loc[wc_teams['away_team'] == 'IR Iran', 'away_team'] = 'Iran'
wc_teams.loc[wc_teams['home_team'] == 'Korea Republic', 'home_team'] = 'South Korea'
wc_teams.loc[wc_teams['away_team'] == 'Korea Republic', 'away_team'] = 'South Korea'
hist_proba_qatar_teams_fbref = get_probs_for_WC(wc_teams)

# func that get the result of a match

def get_result_for_match(team1,team2):
    seed = random.randint(1, 1000)
    #print(seed)
    r = random.Random(seed)
    #weights = hist_proba_qatar_teams.loc[(team1, team2)].to_list()[1:]
    try:
        historic = hist_proba_qatar_teams.loc[(team1, team2)].to_list()[1:]
    except:
        historic = [0,0,0]
        #historic = [0.33,0.33,0.33]
    ### get prob for the fbref data
    try:
        fbref = hist_proba_qatar_teams_fbref.loc[(team1, team2)].to_list()[1:]
    except:
        #fbref = [0.33,0.33,0.33]
        fbref = [0,0,0]
    ''' 
    try:
        wc_hist = hist_proba_wc_games.loc[(team1, team2)].to_list()[1:]
    except:
        wc_hist = [0,0,0]
    '''
    try:
        team1_wc = hist_proba_wc_games.loc[(team1)].mean().to_list()[1:]
    except:
        team1_wc = [0,0,0]
    try:
        team2_wc = hist_proba_wc_games.loc[(team2)].mean().to_list()[1:]
    except:
        team2_wc = [0,0,0]
        
    # get the prob for the team 1 to win,draw, loss
    team1_fbref = hist_proba_qatar_teams_fbref.loc[(team1)].mean().to_list()[1:]
    team2_fbref = hist_proba_qatar_teams_fbref.loc[(team2)].mean().to_list()[1:]
    # swap two positions 
    team2_fbref[0], team2_fbref[1] = team2_fbref[1], team2_fbref[0]
    team2_wc[0], team2_wc[1] = team2_wc[1], team2_wc[0]
    
    team1_team2= [x+y for x,y in zip(historic,fbref)]
    team1_team2= [x+y for x,y in zip(team1_team2,team1_fbref)]
    team1_team2= [x+y for x,y in zip(team1_team2,team2_fbref)]
    #team1_team2= [x+y for x,y in zip(team1_team2,wc_hist)]
    team1_team2= [x+y for x,y in zip(team1_team2,team1_wc)]
    team1_team2= [x+y for x,y in zip(team1_team2,team2_wc)]
    
    total = sum(team1_team2)
    weights = [((edge*1)/total) for edge in team1_team2]
    
    population = [team1,team2,'Draw']
    
    winner = r.choices(population=population,weights=weights)[0]
    #print(winner)
    return winner

# func tha get the winner in the shootouts
def get_result_for_shootout(team1,team2):
    #weights = hist_proba_qatar_teams.loc[(team1, team2)].to_list()[1:]
    try:
        historic = hist_proba_qatar_teams_shootouts.loc[(team1, team2)].mean().to_list()[1:3]
    except:
        historic = [0,0]
        historic = [0.5,0.5]
    try:
        # get the prob for the team 1 to win,draw, loss
        team1_shootout = hist_proba_qatar_teams_shootouts.loc[(team1)].mean().to_list()[1:3]
    except:
        team1_shootout = [0.5,0.5]
    try:
        team2_shootout = hist_proba_qatar_teams_shootouts.loc[(team2)].mean().to_list()[1:3]
    except:
        team2_shootout =  [0.5,0.5]
    # swap two positions 
    team2_shootout[0], team2_shootout[1] = team2_shootout[1], team2_shootout[0]
    
    ## generate random number 
    a = random.uniform(0, 1)
    b = 1 - a 
    random_list = [a,b]
    
    team1_team2= [x+y for x,y in zip(historic,team1_shootout)]
    team1_team2= [x+y for x,y in zip(team1_team2,team2_shootout)]
    team1_team2= [x+y for x,y in zip(team1_team2,random_list)]
    
    total = sum(team1_team2)
    weights = [((edge*1)/total) for edge in team1_team2]
    
    population = [team1,team2]
   
    return random.choices(population=population,weights=weights)[0]

# func that simulates the group_stage
def simulate_group_stage():
    group_stage_matchs_id = groups_stage['match'].values.tolist()
    group_stage_match = []
    cont = 0
    for i in group_stage_matchs_id:
        game = groups_stage.loc[groups_stage['match']==i, ['country1','coutry2']].values.tolist()[0]
        group_stage_match.append(game)
        try:
            result = get_result_for_match(*game)
            update_table(*game,result)
        except:
            cont +=1
            print(game)
            
# get the winners of the group stage
def get_next_stages():
    groups = {
    'A': qatar_teams.loc[qatar_teams['Group']=='A',['Team','Points']].sort_values(by=['Points'], ascending=False).head(2).values.tolist(),
    'B': qatar_teams.loc[qatar_teams['Group']=='B',['Team','Points']].sort_values(by=['Points'], ascending=False).head(2).values.tolist(),
    'C': qatar_teams.loc[qatar_teams['Group']=='C',['Team','Points']].sort_values(by=['Points'], ascending=False).head(2).values.tolist(),
    'D': qatar_teams.loc[qatar_teams['Group']=='D',['Team','Points']].sort_values(by=['Points'], ascending=False).head(2).values.tolist(),
    'E': qatar_teams.loc[qatar_teams['Group']=='E',['Team','Points']].sort_values(by=['Points'], ascending=False).head(2).values.tolist(),
    'F': qatar_teams.loc[qatar_teams['Group']=='F',['Team','Points']].sort_values(by=['Points'], ascending=False).head(2).values.tolist(),
    'G': qatar_teams.loc[qatar_teams['Group']=='G',['Team','Points']].sort_values(by=['Points'], ascending=False).head(2).values.tolist(),
    'H': qatar_teams.loc[qatar_teams['Group']=='H',['Team','Points']].sort_values(by=['Points'], ascending=False).head(2).values.tolist(),
    }
    ## get only the names of the countries
    groups['A'] = [groups['A'][0][0],groups['A'][1][0]]
    groups['B'] = [groups['B'][0][0],groups['B'][1][0]]
    groups['C'] = [groups['C'][0][0],groups['C'][1][0]]
    groups['D'] = [groups['D'][0][0],groups['D'][1][0]]
    groups['E'] = [groups['E'][0][0],groups['E'][1][0]]
    groups['F'] = [groups['F'][0][0],groups['F'][1][0]]
    groups['G'] = [groups['G'][0][0],groups['G'][1][0]]
    groups['H'] = [groups['H'][0][0],groups['H'][1][0]]
    return groups

# set the 16 round
def set_round_16(next_stages):
    round_16.loc[round_16['country1'] == '1A', 'country1'] = next_stages['A'][0]
    round_16.loc[round_16['country1'] == '1C', 'country1'] = next_stages['C'][0]
    round_16.loc[round_16['country1'] == '1B', 'country1'] = next_stages['B'][0]
    round_16.loc[round_16['country1'] == '1D', 'country1'] = next_stages['D'][0]
    round_16.loc[round_16['country1'] == '1E', 'country1'] = next_stages['E'][0]
    round_16.loc[round_16['country1'] == '1G', 'country1'] = next_stages['G'][0]
    round_16.loc[round_16['country1'] == '1F', 'country1'] = next_stages['F'][0]
    round_16.loc[round_16['country1'] == '1H', 'country1'] = next_stages['H'][0]

    round_16.loc[round_16['coutry2'] == '2A', 'coutry2'] = next_stages['A'][1]
    round_16.loc[round_16['coutry2'] == '2C', 'coutry2'] = next_stages['C'][1]
    round_16.loc[round_16['coutry2'] == '2B', 'coutry2'] = next_stages['B'][1]
    round_16.loc[round_16['coutry2'] == '2D', 'coutry2'] = next_stages['D'][1]
    round_16.loc[round_16['coutry2'] == '2E', 'coutry2'] = next_stages['E'][1]
    round_16.loc[round_16['coutry2'] == '2G', 'coutry2'] = next_stages['G'][1]
    round_16.loc[round_16['coutry2'] == '2F', 'coutry2'] = next_stages['F'][1]
    round_16.loc[round_16['coutry2'] == '2H', 'coutry2'] = next_stages['H'][1]

# simulate_rounds func
def simulate_rounds(current_round,next_round_df):
    stage_matchs_id = current_round['match'].values.tolist()
    cont = 0
    for i in stage_matchs_id:
        game = current_round.loc[current_round['match']==i, ['country1','coutry2']].values.tolist()[0]
        result = get_result_for_match(*game)
        if result == 'Draw':
            result = get_result_for_shootout(*game)
        # set the next round
        match = 'W'+str(i)
        next_round_df.loc[next_round_df['country1'] == match, 'country1'] = result
        next_round_df.loc[next_round_df['coutry2'] == match, 'coutry2'] = result
        '''
        # set the third_place match
        if match == 'W61' or match == 'W62':
            third_place.loc[third_place['country1'] == 'L61', 'country1'] = game[0] if result == game[1] else game[1]
            third_place.loc[third_place['coutry2'] == 'L62', 'coutry2'] = game[0] if result == game[1] else game[1]
        '''   
        #print('Match ',i,*game,' Winner: ',result)
        
def simulate_final():
    stage_matchs_id = final['match'].values.tolist()
    cont = 0
    for i in stage_matchs_id:
        game = final.loc[final['match']==i, ['country1','coutry2']].values.tolist()[0]
        result = get_result_for_match(*game)
        if result == 'Draw':
            result = get_result_for_shootout(*game)
    return result

def clean_dfs():
    global qatar_teams
    global knockout_stage
    global round_16
    global quarter_finals
    global semi_finals
    global third_place
    global final
    qatar_teams['Points'] = 0
    knockout_stage = schudule[schudule['phase'] != 'group matches']
    round_16 = schudule[schudule['phase'] == 'round 16']
    quarter_finals = schudule[schudule['phase'] == 'quarter-finals']
    semi_finals = schudule[schudule['phase'] == 'semi-finals']
    third_place = schudule[schudule['phase'] == 'third place']
    final = schudule[schudule['phase'] == 'final']
    
def sim_world_cup(num):
    winners = {}
    for _ in range(num):
        #simulate grpup stage
        simulate_group_stage()
        # get the qualified teams
        next_stages =get_next_stages()
        # set the round of 16
        set_round_16(next_stages)
        #print(set_round_16['country1','country2'])
        # simualte the round of 16 in thsi func we set up the quarter final
        simulate_rounds(round_16,quarter_finals)
        #print(round_16)
        #print('\n')
        # simualte quarter_finals in this func we set up the quarter final
        simulate_rounds(quarter_finals,semi_finals)
        #print(quarter_finals)
        #print('\n')
        # simualte quarter_finals in this func we set up the quarter final
        simulate_rounds(semi_finals,final)
        #simualte the final
        winner = simulate_final()
        # add the winner of this simulation to a dict or sum another win
        if winner not in winners:
            winners[winner] = 1
        else:
            winners[winner] += 1
        ## clean the data set for the next sim
        clean_dfs()
        #print(winner)
    # get the prob of a country to win the world cup 
    winners = {key: value / num for key, value in winners.items()}
    #print(winners)
    return winners

sns.set_theme(style="whitegrid")
sns.set(rc={'figure.figsize':(14,10)})
def graph_probs(winners, num):
    countries = winners.keys()
    probs = winners.values()
    data = {
        'country': countries,
        'probs': probs
    } 
    df = pd.DataFrame.from_dict(data)
    # Draw a nested barplot by Team and Step
    
    g = sns.barplot(data=df, x="probs",y='country',estimator=sum, palette="dark", alpha=.6)
    g.set(title = 'Probabilities of a Country to win The World Cup in ' + str(num) + ' simulations')
    plt.show()
    
num = 100
graph_probs(sim_world_cup(num),num)

num = 250
graph_probs(sim_world_cup(num),num)

num = 500
graph_probs(sim_world_cup(num),num)

num = 750
graph_probs(sim_world_cup(num),num)

num = 1000
graph_probs(sim_world_cup(num),num)

num = 10000
graph_probs(sim_world_cup(num),num)