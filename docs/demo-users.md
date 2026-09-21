## All accounts use the same password: Demo@1234

## Student (6 accounts, each with a different skill profile — good for showing varied match scores):


| Email                    | Profile | 
|--------------------------|-----------------------------------------------------| 
| diya.patel@niat.edu.in   | Web track (React.js, JavaScript, HTML/CSS, Node.js)                                      |
| rohan.verma@niat.edu.in  | Cloud track (AWS, Docker, Linux, CI/CD)                                     |
| ishita.nair@niat.edu.in  | Generalist (Python, React.js, SQL — moderate everywhere)                                    |
| kabir.singh@niat.edu.in  | 	Early-stage (mostly soft skills, weak technical — good low-match example)                                            |
| meera.iyer@niat.edu.in   | 	ML/AI track (Python, Machine Learning, Deep Learning, Statistics) |


## Academician (1 account — tied to the seeded institution):

| Email                    | Profile | 
|--------------------------|-----------------------------------------------------| 
| academician@niat.edu.in   | Dr. Anjali Mehta, CSE Dept, National Institute of Applied Technology |

## Industry (3 accounts, one per seeded company):
| Email                    | Company                                                  | 
|--------------------------|----------------------------------------------------------| 
| recruiter@vertexanalytics.io  | Vertex Analytics Solutions      |
| recruiter@cloudpeak.io  | CloudPeak Systems                  |
| recruiter@nimbusweb.io  | Nimbus Web Technologies |

## Good demo pairings to try first:
- Log in as aarav.sharma@niat.edu.in → once recommended-opportunities is built, he should rank highest on Vertex's Data Analyst / ML Intern postings.
- Log in as recruiter@vertexanalytics.io → candidates list should rank Aarav/Meera high, Kabir low.

## Test Flow 1
- log in as aarav.sharma@niat.edu.in 
- Dashboard should show a skill score and top matches 
- Skill Mapping should show his strengths + top skill gaps 
- Opportunities should show all 5 ranked with Apply buttons 
- apply to one 
- Applications page should show it under "Submitted."

## Test Flow 2
- log in as recruiter@vertexanalytics.io 
- Dashboard should show 2 postings 
- Post a new opportunity 
- My Opportunities should show 3 
- Candidates page, pick "Data Analyst Intern" 
- Aarav/Meera should rank highest, Kabir lowest.

## Test Flow 3
- log in as academician@niat.edu.in 
- Dashboard should show the real student count (6) and top skill gap (should surface REST API Design, held by zero students) 
- Skill Gap Report should show the full ranked list with progress bars.