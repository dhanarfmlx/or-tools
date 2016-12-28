************************************************************************
file with basedata            : md126_.bas
initial value random generator: 1532334265
************************************************************************
projects                      :  1
jobs (incl. supersource/sink ):  14
horizon                       :  96
RESOURCES
  - renewable                 :  2   R
  - nonrenewable              :  2   N
  - doubly constrained        :  0   D
************************************************************************
PROJECT INFORMATION:
pronr.  #jobs rel.date duedate tardcost  MPM-Time
    1     12      0       16        0       16
************************************************************************
PRECEDENCE RELATIONS:
jobnr.    #modes  #successors   successors
   1        1          3           2   3   4
   2        3          3           6   7  10
   3        3          2           5  11
   4        3          3           5   8   9
   5        3          3           7  10  12
   6        3          2           9  12
   7        3          1          13
   8        3          3          10  11  12
   9        3          2          11  13
  10        3          1          13
  11        3          1          14
  12        3          1          14
  13        3          1          14
  14        1          0        
************************************************************************
REQUESTS/DURATIONS:
jobnr. mode duration  R 1  R 2  N 1  N 2
------------------------------------------------------------------------
  1      1     0       0    0    0    0
  2      1     8       5    9    9    2
         2     8       6    9    8    2
         3    10       4    8    7    1
  3      1     6      10    3    8    6
         2     8      10    2    7    6
         3     9       9    1    7    5
  4      1     2       3    4   10   10
         2     5       3    4    8    8
         3     6       3    4    5    7
  5      1     5       3    7    7    5
         2     9       2    7    2    5
         3     9       3    6    3    5
  6      1     2       8    4    9    8
         2     3       3    3    7    6
         3     3       6    2    7    6
  7      1     2       9    7    6   10
         2     5       8    6    5    7
         3     8       7    5    3    5
  8      1     2       7    6    4    4
         2     8       6    6    4    3
         3    10       3    3    3    2
  9      1     1       5    3    6    9
         2     7       3    2    6    9
         3    10       2    2    5    8
 10      1     2       9    6    6    3
         2     5       8    5    4    3
         3     7       8    4    2    3
 11      1     1       9    6    6    8
         2     4       7    5    5    7
         3     7       1    4    4    7
 12      1     5       6    3   10    9
         2     6       6    2    9    8
         3     7       4    2    8    7
 13      1     1       7    9    7    6
         2     1       7   10    7    5
         3    10       6    6    6    2
 14      1     0       0    0    0    0
************************************************************************
RESOURCEAVAILABILITIES:
  R 1  R 2  N 1  N 2
   21   15   88   80
************************************************************************