==========================================================================================

         Introduction to Human Computer Interaction Assignment 1
               Name: Hemasai Aishwarya Vijayakumar
                       SBU ID: 112673842
 
==========================================================================================

1. This assignment includes:

  - generation of 100 sample points for the gesture 
  - implementation of pruning to narrow down the number of valid words
  - Obtain shape score for every valid word
  - Obtain location score for every valid word
  - Get the best n words

2. Generation of 100 sample points for a gesture:
   
  - Numpy library and interp1d has been used  to obtain 100 sample   
    points on a line with given start and end point.

3. Pruning:
   
  - Get the distance between the start and end points of the 
    input gestures and the template gestures.
  - Discard gestures which have start distance or end distance 
    from the template words greater than the given threshold

4. Shape score:

  - Normalize all the gesture sample points and template sample  
    points
  - Scale all the points
  - Get the total distance divided by 100 and append it to the 
    shape score

5. Location Score:
  
   - Followed the algorithm described in the paper

6. Best words:

  - Best words have the least integration scores. Used 
    integration scores to obtain the best words.

7. This folder includes:

  - SHARK2 Folder
  - README text file
  