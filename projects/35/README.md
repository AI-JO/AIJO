# Project 35

<img src="https://raw.githubusercontent.com/salahkhenfer/AIJO/main/images/ai_strategy_and_implementation_plan-_final%20(2)-068.jpg" >


## About This Project 
- Emergency patient scheduling involves anticipating the time frame in which healthcare services will be provided to patients in the midst of congestion, existing medical conditions, 
  and the number of healthcare staff available on duty at the location. I'll explain this in a simpler manner:

  When there's a lot of people needing medical attention at the emergency room, scheduling becomes crucial. It's about deciding who gets treated first based on how sick they are and how   many medical staff are available. Here are the main steps:

  ####   Assessing the situation :
  Patients are evaluated based on how severe their health condition is and how urgently they need care.

  ####  Prioritization:
  Patients are given priority based on their health condition and how it affects their life. For instance, critical emergencies like shock or life-threatening situations are prioritized.

  ####  Estimating wait times:
  Using past data and knowledge of how long similar cases take, an estimate is made for when each patient is likely to receive care.
  
  ####  Updating and monitoring the list:
  The list is regularly updated to make sure patients remain in the same health condition as initially assessed and to monitor the expected time for care.
## Technology used in this project  : 
The project will be a mobile application using the hospital system
- mobile application : used by the ambulance truck driver or any patient transporter
- hospital system : In order to know the number of patients and how long it takes to begin treating the patient in the ambulance
  
### As Front-end :
 We want to create an interface for the driver that, once the mobile application is opened, gives us the route to the selected hospital after the filtering process
  - you can use (java kotlin or dart flutter ... )
  - also we need Integrate GPS functionality to get the driver's current location.
### As Back-end : 
To create a database that tracks the number of patients, along with the time taken for each patient, in the hall of each hospital, you'll need to design an appropriate schema and set up a mechanism to update the database with this information periodically ( e.g., every minute).
- Database Schema Design:

```
Table: Hospital
Columns:
- HospitalID (Primary Key)
- HospitalName
- Location
- ...

Table: Patient
Columns:
- PatientID (Primary Key)
- HospitalID (Foreign Key referencing Hospital)
- TimeIn (timestamp of when the patient entered the hall)
- TimeOut (timestamp of when the patient left the hall, null if still in the hall)

  ```
<img src="https://raw.githubusercontent.com/salahkhenfer/AIJO/main/projects/35/Screenshot%202023-09-22%20164207.png" >

- Database Setup:

Set up a database using a database management system (e.g., MySQL, PostgreSQL) and create the tables according to the designed schema.

- Script to Update Patient Information:

Write a script or program that runs every minute to update patient information. This script would query the database to get the current patient count for each hospital and update the patient records with the time taken for each patient.
- Choosing Hospital with Least Patients:

To choose the hospital with the least number of patients


