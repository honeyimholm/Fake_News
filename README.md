# Abstract

With common sources of knowledge being labeled “Fake News” what online medium can we trust? By researching various feature vectors of wikipedia edits such as sentiment analysis and category distribution and by applying other NLP approaches we hope to identify biasing by individual editors and across languages. Paper of ﬁndings to be submitted to NAACL

# Approach

Our current approach involves extracting and labeling talk pages with conflicts so that we can train a classifier given our own set of conflict feature metrics. Once we have this classifier, we run it on the wikipedia corpus and perform clustering to find groups of conflicts and the strength of relation between each other. This is fed into a D3 force directed graph which can be seen below. Each color corresponds to a different group of conflicts - the topic of which (middle east, western media, religion...) becomes clear when looking at the articles within the grouping.

![Alt Text](https://github.com/honeyimholm/Fake_News/blob/master/visualizations/wikipedia_conflict_grouping.png)
