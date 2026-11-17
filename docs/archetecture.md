 # How data is created, read, updated and deleted

| Data | Create | Read | Update | Delete |
| --- | --- | --- | --- | --- |
| Users | Patients: sign-up.<br>Doctors/pharmacists: admin | Own profile; admin list | Admin activates/deactivates | Not deleted, deactivated (keeps the audit trail intact) |
| Prescriptions + items | Doctor | Owner patient, issuing doctor, a pharmacy with a live grant | Status only: cancelled (doctor), filled (dispense), expired (automatic) | Never; history is kept |
| Access grants | Patient | Patient; pharmacy during the window | `revoked_at` set on revoke or after dispensing | Never; kept as history |
| Stock | Pharmacist (own pharmacy) | Everyone logged in, via search | Pharmacist edits, dispensing subtracts | Not exposed in the API |
| Medicines | Seed data; pharmacist adds missing ones | Everyone logged in | - | - |
| Audit log | Written by the API on every sensitive action | Admin | Never | Never |
| Notifications | Written when a prescription is issued or dispensed | Recipient | `read_at` | Cascades if the user row is removed |

## Entity relationship diagram

The diagram below shows the main entities in PharmaFinder and how they relate. A user can have a patient, doctor, or pharmacist profile. Doctors create prescriptions for patients, prescriptions contain medicine items, and pharmacies manage stock and access grants. Reservations connect patients to available stock, while the audit log records sensitive user actions.

This diagram shows the relationships between users, prescriptions, pharmacies, medicines, stock, reservations, and audit records.

![Entity relationship diagram](screenshot/Screenshot%202.png)

## System architecture

The system is organized into four layers. The presentation layer contains the patient, doctor, pharmacist, and administrator interfaces. These clients communicate with the backend over HTTPS using JSON requests.

The application layer contains authentication, reservation, access-grant, e-prescription, stock, search, notification, and logging services. It reads and writes data in the database layer, while also connecting to external services for email and SMS notifications and map data through OpenMap.

This separation keeps the user interface independent from business rules and storage details. It also makes sensitive operations, such as authentication, prescription sharing, and audit logging, pass through the backend where they can be validated and recorded.

![PharmaFinder system architecture](screenshot/Screenshot%203.png)

## Layered architecture diagram

This diagram presents the main technical layers of PharmaFinder. Patients, doctors, pharmacists, and administrators use the frontend, which communicates with the backend through HTTPS and JSON requests.

The backend groups the core application services, including authentication, reservations, access grants, e-prescriptions, stock management, search, notifications, and logging. It connects to the data layer through SQL and stored QR-code files, and uses external services for email, SMS, and map functionality.

![PharmaFinder layered architecture](screenshot/Screenshot%201.png)

## Domain class diagram

This class diagram describes the main objects and relationships in the system. The `User` entity is specialized into doctor, patient, administrator, and pharmacist roles, while the audit log records important user actions.

Patients can search for medicines, make reservations, and grant pharmacies temporary access. Doctors manage prescriptions, pharmacists manage pharmacies and stock, and prescription items connect medicines with the prescriptions that contain them. These relationships represent the core business rules behind the application data model.

![PharmaFinder domain class diagram](screenshot/Screenshot%204.png)









