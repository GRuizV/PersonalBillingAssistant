# Loose Notes


## Next:

_Up for discussion_

- Take out the tildes from the headers and the fields names, that may cause trouble later. 
    (Is it really necessary to get rid of them?)

- Is it really necessary to transform the date if it already come in a valid format "12/05/2025"?
    If don't turn back the date transformation in the "ground_truth_data_extraction.py" file.

- Can we get rid of the extracted JSON once processed because those tend to be up to 3Mbs of load and up to certain point will consume too much memory?
    Is it really necessary to preserve those?


## Clear pendings

- Move everything to pytesting.

