import pandas as pd


def get_results_for_2_countries(df, country1, country2):
    results_of_two_countries = df.loc[((df.home_team == country1) & (df.away_team == country2)) 
                                           | ((df.home_team == country2) & (df.away_team == country1)), :]
    #returns a new df with rows of the two countries 
    return results_of_two_countries


def get_dict_of_results_for_2_countries(df, country1, country2):
    probs = dict()
    # get results of country1 and country2
    temp = get_results_for_2_countries(df, country1, country2)
    temp = temp[['home_team', 'away_team', 'home_team_wins', 'away_team_wins',  'draw']]
    temp = temp.groupby(['home_team', 'away_team']).sum()
    
    probs[(country1, country2)] = {'Win' : 0, 'Loose' : 0, 'Draw' : 0, 'Games' : 0 }
    
    if len(temp) == 2: # games are played in country1 and country2
        probs[(country1, country2)]['Win'] = temp.loc[(country1, country2)]['home_team_wins'] + temp.loc[(country2, country1)]['away_team_wins']
        probs[(country1, country2)]['Loose'] = temp.loc[(country1, country2)]['away_team_wins'] + temp.loc[(country2, country1)]['home_team_wins']
        probs[(country1, country2)]['Draw'] = temp.loc[(country1, country2)]['draw'] + temp.loc[(country2, country1)]['draw']
        n_games = probs[(country1, country2)]['Win'] + probs[(country1, country2)]['Loose'] + probs[(country1, country2)]['Draw']
        
        if n_games > 0 :
            probs[(country1, country2)]['Win'] = probs[(country1, country2)]['Win']/n_games
            probs[(country1, country2)]['Loose'] = probs[(country1, country2)]['Loose']/n_games
            probs[(country1, country2)]['Draw'] = probs[(country1, country2)]['Draw']/n_games
            probs[(country1, country2)]['Games'] = n_games
            
    
    if len(temp) == 1: # games are played in one country only
        if (country1, country2) in temp.index: # all games were played in country1, so use (country1, country2) as index for temp
            probs[(country1, country2)]['Win'] = temp.loc[(country1, country2)]['home_team_wins']
            probs[(country1, country2)]['Loose'] = temp.loc[(country1, country2)]['away_team_wins']
            probs[(country1, country2)]['Draw'] = temp.loc[(country1, country2)]['draw']
            n_games = probs[(country1, country2)]['Win'] + probs[(country1, country2)]['Loose'] + probs[(country1, country2)]['Draw']
        
            if n_games > 0 :
                probs[(country1, country2)]['Win'] = probs[(country1, country2)]['Win']/n_games
                probs[(country1, country2)]['Loose'] = probs[(country1, country2)]['Loose']/n_games
                probs[(country1, country2)]['Draw'] = probs[(country1, country2)]['Draw']/n_games
                probs[(country1, country2)]['Games'] = n_games
        else: # all games were played in country2, so use (country2, country1) as index for temp
            probs[(country1, country2)]['Win'] = temp.loc[(country2, country1)]['away_team_wins']
            probs[(country1, country2)]['Loose'] = temp.loc[(country2, country1)]['home_team_wins']
            probs[(country1, country2)]['Draw'] = temp.loc[(country2, country1)]['draw']
            n_games = probs[(country1, country2)]['Win'] + probs[(country1, country2)]['Loose'] + probs[(country1, country2)]['Draw']
        
            if n_games > 0 :
                probs[(country1, country2)]['Win'] = probs[(country1, country2)]['Win']/n_games
                probs[(country1, country2)]['Loose'] = probs[(country1, country2)]['Loose']/n_games
                probs[(country1, country2)]['Draw'] = probs[(country1, country2)]['Draw']/n_games
                probs[(country1, country2)]['Games'] = n_games
                                                    
    #returns dict containing the probabilities for a result in a match 
    return probs


def get_probs_for_WC(df): # not using results to avoid ambiguity !
    # get all pairs of countries having played a match
    matches = list(df[['home_team', 'away_team', 'home_score']].groupby(['home_team', 'away_team']).sum().index)
    
    # get ride of (country2, country1) if (country1, country2) already exist in the list
    matches2 = [] # new list after removing duplicates
    for m in matches:
        if ((m[0], m[1]) in matches2) or ((m[1], m[0]) in matches2):
            continue
        else:
            matches2.append(m)
    
    countries1 = [] # first country : country1
    countries2 = [] # second country : country2
    games = [] # number of games played by that pair of countries (country1, country2)
    wins = []  # number of games wined by country1 for the pair (country1, country2)
    looses = [] # number of games lost by country1 for the pair (country1, country2)
    draws = [] # number of draws for the pair (country1, country2)
    for m in matches2:
        temp = get_dict_of_results_for_2_countries(df,  m[0], m[1])
        # we have to add two raws : one for country1, country2 and the other for country2, country1
        # country1, country2
        countries1.append(m[0])
        countries2.append(m[1])
        games.append(temp[m]['Games'])
        wins.append(temp[m]['Win'])
        looses.append(temp[m]['Loose'])
        draws.append(temp[m]['Draw'])
        # country2, country1
        countries1.append(m[1])
        countries2.append(m[0])
        games.append(temp[m]['Games']) # games played is the same
        wins.append(temp[m]['Loose']) # for win and loose we have to switch !
        looses.append(temp[m]['Win']) # for win and loose we have to switch !
        draws.append(temp[m]['Draw']) # draw  is the same
        
    
    historical_ratios = pd.DataFrame({'country1' : countries1 , 'country2' : countries2 ,'games' : games,'wins' : wins, 'looses' : looses,  'draws' : draws})

    historical_ratios = historical_ratios.set_index(['country1', 'country2'])

    return historical_ratios