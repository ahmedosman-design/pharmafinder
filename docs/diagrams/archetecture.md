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

![Entity relationship diagram](./entity-relationship-diagram.png)

