# User stories Batch 1

## [x] As a user I want to be able to download the dataset for EITHER comment generation OR code refinment

- When asking for the dataset, there is a parameter to say whether you want to download the context or
  not (the state of the repo before the PR).

- TODO: actually build the datasets

## [x] As a user I want to be able to submit my predictions for the given downloaded dataset

## [ ] As a user I want to be able to see the results of the code refinment, whether the compiled and tested successfully

## [ ] Add a download button to the page that gives the user a slightly more detailed version of the result, showing the bleu score for each paraphrase and the number of tests passed for code refinement (?)

## [ ] As a user I want to be able to see the performance of my predictions against the benchmark (comment generation: bleu score, code refinement: # tests passed)

# Work flow

First I'll do a basic express server to serve the datasets. No login no frontend. I'll implement
Batch 1 then move on to some other features (frontend, maybe auth).

# Batch 2

## [ ] As a dev I want to be able to deploy my webapp into a container

## [ ] As a user I want to have a webpage to make all the actions mentioned above
