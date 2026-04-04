# Firebase — Структура данных
*[[System Architecture|← Architecture]] | [[01-moc/PhotoDesk MOC|← MOC]]*

---

## Проект

**ID:** `photodesk-45381`
**Регион:** По умолчанию (us-central1 или europe-west)

---

## Коллекции Firestore

### `listings/` — Объекты недвижимости

```
listings/{listingId}
├── address        string    Адрес объекта
├── city           string    Город
├── district       string    Район
├── rooms          number    Кол-во комнат
├── bathrooms      number    Кол-во санузлов
├── floor          number    Этаж
├── area           number    Площадь м²
├── year           number    Год постройки
├── status         enum      נכס חדש | ממתין | מתוכנן | צולם | בעיבוד | נמסר | בוטל
├── packageType    string    Basic | Premium | Unlimited
├── clientId       string    → customers/{id}
├── paymentStatus  enum      unpaid | deposit | paid
├── deliveryStatus object    { photos, videos, plans } : boolean
├── photos         array     URL список
├── videos         array     URL список
├── floorPlans     array     URL список
├── shootDate      timestamp Дата съёмки
├── price          number    Стоимость ₪
├── notes          string    Заметки
├── createdAt      timestamp
└── updatedAt      timestamp
```

**Статусы listing:**
| Код | Иврит | Значение |
|---|---|---|
| new | נכס חדש | Новый объект |
| pending | ממתין | Ожидает подтверждения |
| scheduled | מתוכנן | Запланирован |
| shot | צולם | Снят |
| processing | בעיבוד | В обработке |
| delivered | נמסר | Доставлен |
| cancelled | בוטל | Отменён |

---

### `customers/` — Клиенты (агенты)

```
customers/{customerId}
├── name           string
├── phone          string
├── email          string
├── companyId      string    → companies/{id}
├── type           enum      agent | office
├── notes          string
├── totalShots     number    Всего съёмок
├── totalRevenue   number    Общая выручка ₪
├── lastShoot      timestamp Последняя съёмка
└── createdAt      timestamp
```

---

### `companies/` — Компании (офисы недвижимости)

```
companies/{companyId}
├── name           string
├── city           string
├── country        string    IL (Израиль)
├── agentCount     number
├── totalRevenue   number    ₪
├── activeListings number
└── createdAt      timestamp
```

---

### `bookings/` — Входящие заявки (из booking.html)

```
bookings/{bookingId}
├── clientName     string
├── clientPhone    string
├── clientEmail    string
├── address        string
├── city           string
├── packageType    string
├── preferredDate  string
├── flexibility    string    exact | week | asap
├── notes          string
├── status         enum      new | approved | rejected
├── bookingNumber  string    Уникальный номер
└── createdAt      timestamp
```

---

### `store/` — Настройки системы (singleton)

```
store/{docId}
├── settings
│   ├── businessName      string
│   ├── photographerName  string
│   ├── email             string
│   ├── phone             string
│   ├── logo              string    Base64 или URL
│   └── timezone          string
├── packages              array     [{id, name, price, features[]}]
├── services              array     [{id, name, price, type}]
├── promotions            array     [{code, discount, active}]
└── archive
    ├── listings          array
    ├── customers         array
    └── companies         array
```

---

## Firebase Auth

- **Метод:** Email + Password
- **Пользователи:** Только Дорон (один аккаунт)
- **Правила:** Только authenticated user имеет доступ к Firestore

---

## ⚠️ Известные риски

| Риск | Описание |
|---|---|
| Security Rules | Должны разрешать только auth users — не `allow all` |
| No Storage | Firebase Storage не подключён (файлы не сохраняются) |
| No Listeners | Нет `onSnapshot()` — нужен ручной refresh |
| Одиночный юзер | При расширении на несколько фотографов нужна multi-tenant архитектура |
