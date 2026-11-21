# Exo 2 - ABCD Records 📼

Énoncé : <https://gist.github.com/bdallard/2d2407c4de4c182afca6d3ec7235e9eb>
Implémentation Python : [`abcd_records.py`](abcd_records.py)

> Mermaid n'a pas de vrai diagramme de cas d'utilisation : les use cases sont
> représentés par des ovales (`([...])`), les acteurs par des nœuds 👤, et la
> frontière du système par un `subgraph`.

## Level 1

### Task 1.1 - Use case diagram (simple)

```mermaid
flowchart LR
    M["👤 Member"]
    C["👤 Order Processing Clerk"]
    subgraph ABCD["ABCD Records system"]
        PO([Place Order])
        VM([Verify Membership])
        PR([Process Order])
        MP([Make Payment])
    end
    M --- PO
    M --- MP
    C --- VM
    C --- PR
```

### Task 1.2 - Class diagram (simple)

```mermaid
classDiagram
    class Member {
        +int member_id
        +str name
        +str address
        +place_order(items) Order
        +make_payment(order, payment)
    }
    class Order {
        +int order_id
        +date order_date
        +str status
        +add_item(item, qty)
        +total() float
    }
    class OrderProcessingClerk {
        +int employee_id
        +str name
        +verify_membership(person) bool
        +process_order(order)
    }
    Member "1" --> "0..*" Order : passe
    OrderProcessingClerk "1" --> "0..*" Order : traite
```

## Level 2

### Task 2.1 - Use case diagram complet

```mermaid
flowchart LR
    M["👤 Member"]
    RM["👤 Royal Member"]
    NM["👤 Non-Member"]
    OC["👤 Order Processing Clerk"]
    CC["👤 Collection Dept. Clerk"]

    subgraph ABCD["ABCD Records system"]
        PO([Place Order])
        VM([Verify Membership])
        VIA([Verify Item Availability])
        PR([Process Order])
        AD([Apply Discount])
        PI([Print Invoice])
        PSL([Print Shipping List])
        OUI([Order Unavailable Items])
        SMA([Send Membership Application])
        MP([Make Payment])
    end

    RM -.->|hérite de| M
    M --- PO
    M --- MP
    NM --- PO
    OC --- PR
    CC --- MP

    PO -.->|include| VM
    PR -.->|include| VIA
    PR -.->|include| PI
    PR -.->|include| PSL
    SMA -.->|extend: non membre| VM
    AD -.->|extend: Royal| PR
    OUI -.->|extend: Royal + article indisponible| PR
```

- **include** (obligatoire) : passer commande implique *toujours* de vérifier
  l'adhésion ; traiter une commande implique *toujours* de vérifier le stock,
  d'imprimer la facture et la liste d'expédition.
- **extend** (optionnel) : la remise et la commande d'articles indisponibles
  n'ont lieu que pour un membre Royal ; le formulaire d'adhésion n'est envoyé
  que si la vérification échoue.

### Task 2.2 - Class diagram complet

```mermaid
classDiagram
    class Member {
        <<abstract>>
        +int member_id
        +str name
        +str address
        +discount_rate()* float
        +can_order_unavailable()* bool
    }
    class RoyalMember {
        +discount_rate() float = 0.10
        +can_order_unavailable() bool = True
    }
    class RegularMember {
        +discount_rate() float = 0.0
        +can_order_unavailable() bool = False
    }
    class NonMember {
        +str name
        +str address
    }
    class MembershipApplication {
        +NonMember applicant
        +date sent_on
    }
    class Item {
        <<abstract>>
        +str ref
        +str title
        +str artist
        +float price
        +int stock
        +is_available(qty) bool
    }
    class CD {
        +int tracks
    }
    class Tape {
        +int duration_min
    }
    class Order {
        +int order_id
        +date order_date
        +OrderStatus status
        +subtotal() float
        +total() float
    }
    class OrderLine {
        +int quantity
        +bool backordered
        +line_total() float
    }
    class Invoice {
        +int invoice_id
        +float amount
        +print() str
    }
    class ShippingList {
        +list items
        +print() str
    }
    class Payment {
        <<abstract>>
        +float amount
        +date paid_on
        +process()* str
    }
    class Cash
    class Check {
        +str check_number
    }
    class BankDraft {
        +str bank_name
    }
    class OrderProcessingClerk {
        +verify_membership(person) bool
        +process_order(order)
    }
    class CollectionDeptClerk {
        +collect(order, payment)
    }
    class DailyRecords {
        +date day
        +save(order)
    }

    Member <|-- RoyalMember
    Member <|-- RegularMember
    Item <|-- CD
    Item <|-- Tape
    Payment <|-- Cash
    Payment <|-- Check
    Payment <|-- BankDraft

    Member "1" --> "0..*" Order : passe
    Order "1" *-- "1..*" OrderLine
    OrderLine "0..*" --> "1" Item
    Order "1" *-- "0..1" Invoice
    Order "1" *-- "0..1" ShippingList
    Order "1" -- "0..1" Payment
    NonMember "1" -- "0..1" MembershipApplication : reçoit
    OrderProcessingClerk ..> Order : traite
    CollectionDeptClerk ..> Payment : encaisse
    DailyRecords "1" o-- "0..*" Order
```

#### Scénario : un membre Royal commande 2 CDs (dont un indisponible) et paie par chèque

Diagramme d'objets (état après traitement) :

```mermaid
classDiagram
    class alice["alice : RoyalMember"] {
        member_id = 42
        discount_rate = 0.10
    }
    class order["o1 : Order"] {
        status = PARTIALLY_SHIPPED
        subtotal = 30.00
        total = 27.00
    }
    class line1["l1 : OrderLine"] {
        quantity = 1
        backordered = False
    }
    class line2["l2 : OrderLine"] {
        quantity = 1
        backordered = True
    }
    class cd1["cd1 : CD"] {
        title = "Kind of Blue"
        stock = 4
    }
    class cd2["cd2 : CD"] {
        title = "Abbey Road"
        stock = 0
    }
    class pay["p1 : Check"] {
        check_number = "000123"
        amount = 27.00
    }
    alice --> order
    order *-- line1
    order *-- line2
    line1 --> cd1
    line2 --> cd2
    order -- pay
```

## Level 3 - Sequence diagrams

### 1. Complete Order Processing Flow

```mermaid
sequenceDiagram
    actor M as Member
    participant OPC as Order Processing Clerk
    participant INV as Inventory
    participant O as Order
    participant CDC as Collection Dept. Clerk
    participant DR as Daily Records

    M->>OPC: place_order(items)
    OPC->>OPC: verify_membership(M)
    OPC->>O: create(member, items)
    loop pour chaque article
        OPC->>INV: is_available(item, qty)
        INV-->>OPC: True / False
    end
    OPC->>O: apply_discount(member.discount_rate)
    OPC->>O: print_invoice()
    OPC->>O: print_shipping_list()
    OPC->>CDC: send invoice
    M->>CDC: make_payment(payment)
    CDC-->>M: receipt
    OPC->>DR: save(order)
```

### 2. Membership Verification (succès et échec)

```mermaid
sequenceDiagram
    actor P as Person
    participant OPC as Order Processing Clerk
    participant DB as Member Registry

    P->>OPC: place_order(items)
    OPC->>DB: find_member(id)
    alt membre trouvé
        DB-->>OPC: Member
        OPC-->>P: commande acceptée
    else non membre
        DB-->>OPC: None
        OPC->>OPC: create MembershipApplication
        OPC-->>P: send_membership_application()
    end
```

### 3. Payment Processing (tous les types)

```mermaid
sequenceDiagram
    actor M as Member
    participant CDC as Collection Dept. Clerk
    participant PAY as Payment
    participant BANK as Bank

    M->>CDC: make_payment(order, payment)
    CDC->>PAY: process()
    alt Cash
        PAY-->>CDC: encaissement immédiat
    else Check
        PAY->>BANK: deposit(check_number, amount)
        BANK-->>PAY: cleared
        PAY-->>CDC: ok
    else Bank Draft
        PAY->>BANK: verify_draft(bank_name, amount)
        BANK-->>PAY: guaranteed
        PAY-->>CDC: ok
    end
    CDC->>CDC: order.status = PAID
    CDC-->>M: receipt
```

### 4. Item Reordering for Royal Members

```mermaid
sequenceDiagram
    actor RM as Royal Member
    participant OPC as Order Processing Clerk
    participant INV as Inventory
    participant SUP as Supplier
    participant O as Order

    RM->>OPC: place_order([cd2])
    OPC->>INV: is_available(cd2)
    INV-->>OPC: False
    alt member.can_order_unavailable()
        OPC->>O: add_line(cd2, backordered=True)
        OPC->>SUP: reorder(cd2, qty)
        SUP-->>INV: delivery (plus tard)
        INV-->>OPC: cd2 available
        OPC->>O: ship backordered line
    else Regular member
        OPC-->>RM: article indisponible, refusé
    end
```
