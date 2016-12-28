************************************************************************
file with basedata            : md237_.bas
initial value random generator: 545309769
************************************************************************
projects                      :  1
jobs (incl. supersource/sink ):  18
horizon                       :  123
RESOURCES
  - renewable                 :  2   R
  - nonrenewable              :  2   N
  - doubly constrained        :  0   D
************************************************************************
PROJECT INFORMATION:
pronr.  #jobs rel.date duedate tardcost  MPM-Time
    1     16      0       26       11       26
************************************************************************
PRECEDENCE RELATIONS:
jobnr.    #modes  #successors   successors
   1        1          3           2   3   4
   2        3          3           5   6  14
   3        3          3           5   9  14
   4        3          2          15  17
   5        3          3           8  11  16
   6        3          3           7  10  12
   7        3          3           9  13  16
   8        3          2          10  12
   9        3          1          15
  10        3          1          13
  11        3          1          12
  12        3          2          13  15
  13        3          1          17
  14        3          2          16  17
  15        3          1          18
  16        3          1          18
  17        3          1          18
  18        1          0        
************************************************************************
REQUESTS/DURATIONS:
jobnr. mode duration  R 1  R 2  N 1  N 2
------------------------------------------------------------------------
  1      1     0       0    0    0    0
  2      1     2       7    1    7    4
         2     2       6    1    6    5
         3    10       5    1    6    3
  3      1     7       6    4    6    5
         2     9       5    3    4    4
         3    10       3    3    2    4
  4      1     1       5    9    8   10
         2     2       2    9    7    9
         3     6       1    8    6    8
  5      1     2       6    7    4   10
         2     2       7    9    4    8
         3     3       6    4    4    5
  6      1     1       8    7    3    8
         2     6       7    6    2    7
         3    10       6    5    1    5
  7      1     1       8    8    8    6
         2     2       8    6    6    4
         3     3       8    5    1    3
  8      1     1       7    8    3    6
         2     4       6    8    3    5
         3    10       4    8    2    5
  9      1     1       8    4   10    7
         2     4       6    2    5    7
         3     4       7    3    2    7
 10      1     2      10    6   10    7
         2     7       7    6    8    3
         3     7       9    3    9    4
 11      1     1       4    8    3    5
         2     4       4    8    2    4
         3     5       3    8    2    3
 12      1     9       6    8    7    7
         2    10       4    2    2    1
         3    10       2    2    5    1
 13      1     5       9    5    6    5
         2     6       7    5    5    3
         3     6       7    4    6    5
 14      1     3       5    8    9   10
         2     8       5    4    8    7
         3    10       4    2    8    6
 15      1     2       8    9    7    9
         2     5       4    4    6    9
         3     9       4    2    6    9
 16      1     2       7    7    7    7
         2     5       7    7    6    7
         3    10       4    6    4    7
 17      1     2       8    6    8    2
         2     3       7    6    8    2
         3    10       6    5    8    1
 18      1     0       0    0    0    0
************************************************************************
RESOURCEAVAILABILITIES:
  R 1  R 2  N 1  N 2
   12   12   87   91
************************************************************************