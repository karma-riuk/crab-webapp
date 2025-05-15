# User stories Batch 1

## [x] As a user I want to be able to download the dataset for EITHER comment generation OR code refinment

- When asking for the dataset, there is a parameter to say whether you want to download the context or
  not (the state of the repo before the PR).

- TODO: actually build the datasets

## [x] As a user I want to be able to submit my predictions for the given downloaded dataset

## [x] As a user I want to be able to see the results of the code refinment, whether the compiled and tested successfully

## [x] Add a download button to the page that gives the user a slightly more detailed version of the result, showing the bleu score for each paraphrase and the number of tests passed for code refinement (?)

## [x] As a user I want to be able to see the performance of my predictions against the benchmark (comment generation: bleu score, code refinement: # tests passed)

# Work flow

First I'll do a basic express server to serve the datasets. No login no frontend. I'll implement
Batch 1 then move on to some other features (frontend, maybe auth).

# Batch 2

## [ ] As a dev I want to be able to deploy my webapp into a container

## [x] As a user I want to have a webpage to make all the actions mentioned above

## [x] As a user I want to see what the webpage is used for (inspired from https://seart-ghs.si.usi.ch)

# DATASET

## [x] Rebuild the dataset (is doing)

## [ ] Match all the current entries in dataset.json and put the selection thing inside dataset.dont-care.json

## [ ] Go through manual selection of dataset.dont-care.json to fill missing repos

## [ ] The step above will already create all the archives

## [ ] Signal the instances that are actually covered

## [ ] When submitting for refinement, give the user a link that he can put in a text box to see the results

# Paper

## [ ] Write paper
