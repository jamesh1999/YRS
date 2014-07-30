import re, collections, json
#from http://norvig.com/spell-correct.html

def words(text): return re.findall('[a-z]+', text.lower()) 

def train(features): #generates probability data from a large text sample
    model = collections.defaultdict(lambda: 1) 
    #default dict means that any novel word has been seen once
    for f in features:
        model[f] += 1
    return model #model[f] contains a count of how many times the word f has been seen

NWORDS = train(words(file('big.txt').read())) #big.txt contains a large number of works from project gutenburg, war and peace, wiktionary and other sources (~1.5 million words)
spell_check_model = open("spell_check_model.json","w")
spell_check_model.write(json.dumps(NWORDS))
spell_check_model.close()

alphabet = 'abcdefghijklmnopqrstuvwxyz'


#this piece of code calculates the probability of the author meaning to write a particular real word given that they have written an incorrectly spelled word

#need to calculate and maximise p(c|w) #probability that they meant to write word c when they have written incorrect word w

#Bayes' theorem:
  #p(a and b) = p(a|b) * p(b) = p(a) * p(b|a)
  #Therefore p(a|b) = p(a)/p(b) * p(b|a)

#so p(c|w) = p(w|c)*P(c)/p(w)
#p(w) is always the same so does not make  difference to the maximisation
#so we need to maximise p(w|c)*p(c)
#p(w|c) is the probability that w could be formed by editting c (the "edit distance")
#p(c) is the probability that c stands as a correct word on its own

def edits1(word): #returns the set of all words of an edit distance of 1 away from "word"
   splits     = [(word[:i], word[i:]) for i in range(len(word) + 1)]
   deletes    = [a + b[1:] for a, b in splits if b] #words that can be generated by deleting letters
   transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b)>1] #words that can be generated by transposing letters
   replaces   = [a + c + b[1:] for a, b in splits for c in alphabet if b] #words that can be generated by replacing letters
   inserts    = [a + c + b     for a, b in splits for c in alphabet] #words that can be generated by insertin letters
   return set(deletes + transposes + replaces + inserts)

def known_edits2(word): #the set of all words of two edits away from the word
    return set(e2 for e1 in edits1(word) for e2 in edits1(e1) if e2 in NWORDS)

def known(words): return set(w for w in words if w in NWORDS) #reduces the set of words to ones which have been seen before

def correct(word):
    candidates = known([word]) or known(edits1(word)) or known_edits2(word) or [word] #assembles all possible candidates 
    return max(candidates, key=NWORDS.get) #gets the best candidate