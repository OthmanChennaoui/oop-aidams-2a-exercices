# Exo 1 - Hospital Management System 🏥

Énoncé : <https://gist.github.com/bdallard/2d2407c4de4c182afca6d3ec7235e9eb>
Implémentation Python : [`hospital.py`](hospital.py)

## Task 1 - Diagramme de classes de base

```mermaid
classDiagram
    class Patient {
        -int id
        -str name
        -str password
        -str email
        +post_problem(description) HealthProblem
        +pay(prescription, method) Payment
        +view_prescriptions() list
    }
    class Organizer {
        -int id
        -str name
        -str password
        +read_problem(problem)
        +consult_doctor(problem, doctor)
        +send_prescription(prescription)
        +forward_payment(payment)
    }
    class Doctor {
        -int id
        -str name
        -str password
        -str specialty
        +provide_prescription(problem, content) Prescription
        +receive_payment(amount)
    }

    Patient "1..*" -- "1" Organizer : soumet ses problèmes à
    Organizer "1" -- "1..*" Doctor : consulte
    Organizer "1" -- "0..*" Patient : envoie prescriptions / gère comptes
```

## Task 2 - Diagramme complet (6 classes)

- **Composition** `Patient *-- HealthProblem` : un problème n'existe pas sans son patient.
- **Composition** `HealthProblem *-- Prescription` : la prescription répond à un problème.
- **Inheritance** pour les moyens de paiement (`Payment` abstrait → `Check`, `Cash`, `CreditCard`).

```mermaid
classDiagram
    class Patient {
        +int id
        +str name
        +str password
        +post_problem(description) HealthProblem
        +pay(prescription, method) Payment
    }
    class Doctor {
        +int id
        +str name
        +str specialty
        +provide_prescription(problem, content) Prescription
        +receive_payment(amount)
    }
    class Organizer {
        +int id
        +str name
        +consult_doctor(problem, doctor) Prescription
        +send_prescription(prescription)
        +forward_payment(payment)
    }
    class HealthProblem {
        +int id
        +str description
        +datetime created_at
    }
    class Prescription {
        +int id
        +str content
        +float fee
        +datetime issued_at
    }
    class Payment {
        <<abstract>>
        +float amount
        +datetime paid_at
        +process()* str
    }
    class Check {
        +str check_number
        +process() str
    }
    class Cash {
        +process() str
    }
    class CreditCard {
        +str card_number
        +process() str
    }

    Patient "1" *-- "0..*" HealthProblem : poste
    HealthProblem "1" *-- "0..1" Prescription : reçoit
    Doctor "1" --> "0..*" Prescription : rédige
    Organizer "1" --> "0..*" HealthProblem : traite
    Prescription "1" -- "0..1" Payment : réglée par
    Payment <|-- Check
    Payment <|-- Cash
    Payment <|-- CreditCard
```

### Séquence : un patient soumet un problème, reçoit une prescription et paie

```mermaid
sequenceDiagram
    actor P as Patient
    participant O as Organizer
    participant D as Doctor

    P->>O: post_problem(description)
    activate O
    O->>O: read_problem(problem)
    O->>D: consult(problem)
    activate D
    D-->>O: Prescription
    deactivate D
    O-->>P: send_prescription(prescription)
    deactivate O
    P->>O: pay(prescription, CreditCard)
    activate O
    O->>D: forward_payment(amount)
    D-->>O: ack
    O-->>P: receipt
    deactivate O
```

## Task 3 - Version avancée

Ajouts : superclasse `User` (id, name, password, login/logout), statut
`ProblemStatus` (PENDING → IN_REVIEW → RESOLVED), timestamps, historique des
prescriptions, paiement modélisé par **polymorphisme (pattern Strategy)**.

```mermaid
classDiagram
    class User {
        <<abstract>>
        +int id
        +str name
        -str password_hash
        +bool logged_in
        +login(password) bool
        +logout()
    }
    class Patient {
        +list~HealthProblem~ problems
        +post_problem(description) HealthProblem
        +past_prescriptions() list~Prescription~
        +pay(prescription, method) Payment
    }
    class Doctor {
        +str specialty
        +float balance
        +provide_prescription(problem, content, fee) Prescription
        +receive_payment(amount)
    }
    class Organizer {
        +dict members
        +register_member(user) User
        +assign(problem, doctor)
        +deliver(problem) Prescription
        +forward_payment(payment)
    }
    class ProblemStatus {
        <<enumeration>>
        PENDING
        IN_REVIEW
        RESOLVED
    }
    class HealthProblem {
        +int id
        +str description
        +ProblemStatus status
        +datetime created_at
        +datetime updated_at
        +Doctor doctor
    }
    class Prescription {
        +int id
        +str content
        +float fee
        +datetime issued_at
        +bool paid
    }
    class PaymentMethod {
        <<interface>>
        +pay(amount)* str
    }
    class Payment {
        +float amount
        +PaymentMethod method
        +datetime paid_at
        +bool forwarded
    }

    User <|-- Patient
    User <|-- Doctor
    User <|-- Organizer
    Patient "1" *-- "0..*" HealthProblem
    HealthProblem --> ProblemStatus
    HealthProblem "0..*" --> "0..1" Doctor : assigné à
    HealthProblem "1" *-- "0..*" Prescription : historique
    Prescription "1" -- "0..1" Payment
    Payment o-- PaymentMethod
    PaymentMethod <|.. CheckPayment
    PaymentMethod <|.. CashPayment
    PaymentMethod <|.. CreditCardPayment
```

### SSD 1 - Patient Registration

```mermaid
sequenceDiagram
    actor O as Organizer
    participant S as System
    O->>S: register_member("Patient", name, password)
    S->>S: generate member id + hash password
    S-->>O: Patient(id)
    O-->>O: communique id + mot de passe au patient
```

### SSD 2 - Consultation Flow

```mermaid
sequenceDiagram
    actor P as Patient
    participant S as System
    actor O as Organizer
    actor D as Doctor
    P->>S: login(id, password)
    P->>S: post_problem(description)
    S-->>P: HealthProblem [PENDING]
    O->>S: assign(problem, doctor)
    S-->>O: HealthProblem [IN_REVIEW]
    D->>S: provide_prescription(problem, content, fee)
    O->>S: deliver(problem)
    S-->>P: Prescription
    Note over S: status = RESOLVED
```

### SSD 3 - Payment Processing

```mermaid
sequenceDiagram
    actor P as Patient
    participant S as System
    actor O as Organizer
    actor D as Doctor
    P->>S: pay(prescription, method)
    S->>S: method.pay(fee)  (Check / Cash / CreditCard)
    S-->>P: Payment receipt
    O->>S: forward_payment(payment)
    S->>D: receive_payment(amount)
    S-->>O: payment.forwarded = True
```

## Questions to consider

1. **Patient qui consulte plusieurs médecins ?** Chaque `HealthProblem` porte
   sa propre référence `doctor` : un patient a plusieurs problèmes, chacun
   pouvant être assigné à un médecin différent (relation `Patient 1 -- * HealthProblem * -- 0..1 Doctor`).
   Pour un même problème vu par plusieurs médecins, on remplace l'attribut par
   une liste de `Consultation(doctor, date, notes)`.
2. **Prescriptions réutilisables ?** Oui pour un traitement renouvelable : on
   garde l'historique (`HealthProblem *-- Prescription`) et on ajoute une
   méthode `renew()` qui crée une nouvelle `Prescription` liée à l'originale
   (`renewed_from`), plutôt que de modifier l'ancienne (traçabilité).
3. **Pattern pour le paiement ?** **Strategy** : `PaymentMethod` est
   l'interface, `CheckPayment` / `CashPayment` / `CreditCardPayment` sont les
   stratégies interchangeables. Une **Factory** peut créer la bonne stratégie
   à partir du choix du patient.
4. **Intégrité des paiements ?** Transaction atomique (le paiement et le
   marquage `paid` réussissent ou échouent ensemble), interdiction du double
   paiement (`if prescription.paid: raise`), idempotence via un id de
   transaction, journal d'audit, montants vérifiés côté serveur,
   `forward_payment` impossible deux fois (`forwarded`).

---

## Exo 2 - ABCD Records

Voir [`abcd_records_uml.md`](abcd_records_uml.md).
