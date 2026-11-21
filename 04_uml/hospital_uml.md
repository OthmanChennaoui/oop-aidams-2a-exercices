# Exo 1 - Hospital Management System 🏥

Exercise: <https://gist.github.com/bdallard/2d2407c4de4c182afca6d3ec7235e9eb>
Python implementation: [`hospital.py`](hospital.py)

## Task 1 - Basic class diagram

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

    Patient "1..*" -- "1" Organizer : submits problems to
    Organizer "1" -- "1..*" Doctor : consults
    Organizer "1" -- "0..*" Patient : sends prescriptions / manages accounts
```

## Task 2 - Complete diagram (6 classes)

- **Composition** `Patient *-- HealthProblem`: a problem cannot exist without its patient.
- **Composition** `HealthProblem *-- Prescription`: a prescription answers one problem.
- **Inheritance** for the payment methods (abstract `Payment` → `Check`, `Cash`, `CreditCard`).

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

    Patient "1" *-- "0..*" HealthProblem : posts
    HealthProblem "1" *-- "0..1" Prescription : receives
    Doctor "1" --> "0..*" Prescription : writes
    Organizer "1" --> "0..*" HealthProblem : handles
    Prescription "1" -- "0..1" Payment : paid by
    Payment <|-- Check
    Payment <|-- Cash
    Payment <|-- CreditCard
```

### Sequence: a patient submits a problem, receives a prescription and pays

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

## Task 3 - Advanced version

Additions: a `User` superclass (id, name, password, login/logout), a
`ProblemStatus` (PENDING → IN_REVIEW → RESOLVED), timestamps, prescription
history, and payment modelled with **polymorphism (Strategy pattern)**.

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
    HealthProblem "0..*" --> "0..1" Doctor : assigned to
    HealthProblem "1" *-- "0..*" Prescription : history
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
    O-->>O: gives the id + password to the patient
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

1. **A patient consulting several doctors?** Each `HealthProblem` holds its
   own `doctor` reference: a patient has several problems, and each one can be
   assigned to a different doctor (`Patient 1 -- * HealthProblem * -- 0..1 Doctor`).
   For one problem seen by several doctors, replace the attribute with a list
   of `Consultation(doctor, date, notes)`.
2. **Should prescriptions be reusable?** Yes for a renewable treatment: keep
   the history (`HealthProblem *-- Prescription`) and add a `renew()` method
   that creates a new `Prescription` linked to the original one
   (`renewed_from`), rather than modifying the old one (traceability).
3. **Which pattern fits the payment system?** **Strategy**: `PaymentMethod` is
   the interface, `CheckPayment` / `CashPayment` / `CreditCardPayment` are
   interchangeable strategies. A **Factory** can create the right strategy
   from the patient's choice.
4. **Data integrity when payments are processed?** An atomic transaction (the
   payment and the `paid` flag succeed or fail together), no double payment
   (`if prescription.paid: raise`), idempotency through a transaction id, an
   audit log, amounts checked server-side, and `forward_payment` impossible
   twice (`forwarded`).

---

## Exo 2 - ABCD Records

See [`abcd_records_uml.md`](abcd_records_uml.md).
