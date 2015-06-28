import learn
import string
import random

class TeamsPool :
    def __init__(self) :
        self.IdToName = []
        self.NameToId = {}
        self.TeamGames = []
        self.Count = 0
    
    def GetId(self, name) :
        if name in self.NameToId :
            teamId = self.NameToId[name]
            self.TeamGames[teamId] += 1
            return teamId
        else :
            res = self.Count
            self.NameToId[name] = res
            self.IdToName.append(name)
            self.TeamGames.append(1)
            self.Count += 1
            return res
    
    def SearchName(self, name) :
        if name in self.NameToId :
            teamId = self.NameToId[name]
            return teamId
        else :
            return -1
    
    def GetName(self, id) :
        return self.IdToName[id]
        
    def GetTeamGames(self, id) :
        return self.TeamGames[id]

class Result :
    def __init__(self, line, pool) :
        (tournamentId, self.TournamentName, date1, date2, teamId, teamName, teamCity, place, bonusA, bonusB, d) = line.split('\t')
        self.TournamentId = int(tournamentId)
        self.Place = float(place)
        self.TeamId = pool.GetId(teamName)

class Tournament :
    def __init__(self, result) :
        self.Id = result.TournamentId
        self.Name = result.TournamentName
        self.Teams = {}
        self.AddResult(result)
    
    def AddResult(self, result) :
        if result.TournamentId != self.Id :
            raise ValueError('Something went wrong')
        self.Teams[result.TeamId] = result.Place
    
    def GenerateSamples(self, pool, threshold, maxDiff) :
        samples = []
        for (teamId1, place1) in self.Teams.iteritems() :
            for (teamId2, place2) in self.Teams.iteritems() :
                if (teamId1 != teamId2 and pool.GetTeamGames(teamId1) >= threshold and pool.GetTeamGames(teamId2) >= threshold) :
                    if (maxDiff > 0 and abs(place1 - place2) > maxDiff) :
                        continue
                    if (place1 < place2) :
                        r = 1
                    elif (place2 > place1) :
                        r = 0
                    else :
                        r = 0.5
                    samples.append([teamId1, teamId2, r])
        return samples

def LoadTournamentResults(filename) :
    pool = TeamsPool()
    firstLine = True
    tournaments = []
    for line in open(filename, 'rb') :
        if firstLine :
            firstLine = False
            continue
        try:
            result = Result(line, pool)
        except :
            print "Failed to parse line: %s" % line
        if (len(tournaments) == 0 or tournaments[-1].Id != result.TournamentId) :
            newTournament = Tournament(result)
            tournaments.append(newTournament)
        else :
            tournaments[-1].AddResult(result)
    return (pool, tournaments)

def GenerateSamples(pool, tournaments, threshold, maxDiff) :
    samples = []
    for tournament in tournaments :
        for sample in tournament.GenerateSamples(pool, threshold, maxDiff) :
            samples.append(sample)
    return samples

def FilterSamples(samples, threshold) :
    random.shuffle(samples)
    result = []
    teamSamples = {}
    for sample in samples :
        teamSamples.setdefault(sample[0], 0)
        teamSamples.setdefault(sample[1], 0)
        if (teamSamples[sample[0]] < threshold or teamSamples[sample[1]] < threshold) :
            result.append(sample)
            teamSamples[sample[0]] += 1
            teamSamples[sample[1]] += 1
    return result

def LearnRating(pool, samples, alpha, threshold) :
    learner = learn.SGDlearn(pool.Count, samples)
    learner.RunLearn(alpha, threshold)
    return learner

def PrepareResult(pool, learner, sampleGamesThreshold) :
    teams = []
    for i in xrange(pool.Count) :
        m = learner.Distributions[i].M
        s = learner.Distributions[i].Sigma
        name = pool.GetName(i)
        if (pool.GetTeamGames(i) >= sampleGamesThreshold) :
            teams.append((m, s, name))
    teams.sort()
    teams.reverse()
    return teams

def RunRating(tournamentsFile, sampleGamesThreshold, samplePlacesDiffThreshold, filterThreshold, learnAlpha, learnThreshold) :
    (pool, tournaments) = LoadTournamentResults(tournamentsFile)
    print "Loaded %d tournaments" % len(tournaments)
    samples = GenerateSamples(pool, tournaments, sampleGamesThreshold, samplePlacesDiffThreshold)
    print "Generated %d samples with min games threshold = %d and max places diff = %d" % (len(samples), sampleGamesThreshold, samplePlacesDiffThreshold)
    filteredSamples = FilterSamples(samples, filterThreshold)
    print "Filtered samples to %d with min samples for team = %d" % (len(filteredSamples), filterThreshold)
    print "Learning with params: alpha = %f, threshold = %f" % (learnAlpha, learnThreshold)
    learner = LearnRating(pool, samples, learnAlpha, learnThreshold)
    return PrepareResult(pool, learner, sampleGamesThreshold)
    
