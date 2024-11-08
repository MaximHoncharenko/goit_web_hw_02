from collections import UserDict
from datetime import datetime, timedelta
import pickle


# Декоратор для обработки ошибок
def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (ValueError, KeyError, IndexError) as e:
            return f"Error: {e}"
    return wrapper

# Классы для полей
class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if not self.validate(value):
            raise ValueError("Неправильний формат номера телефону")
        super().__init__(value)

    @staticmethod
    def validate(value):
        return len(value) == 10 and value.isdigit()

class Birthday(Field):
    def __init__(self, value):
        if not self.validate(value):
            raise ValueError("Неправильний формат дати. Використовуйте формат: ДД.ММ.РРРР")
        super().__init__(value)

    @staticmethod
    def validate(value):
        try:
            datetime.strptime(value, "%d.%m.%Y")
            return True
        except ValueError:
            return False

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        new_phone = Phone(phone)
        if new_phone not in self.phones:
            self.phones.append(new_phone)

    def edit_phone(self, old_phone, new_phone):
        for i, p in enumerate(self.phones):
            if p.value == old_phone:
                self.phones[i] = Phone(new_phone)
                return f"Телефон {old_phone} змінено на {new_phone}"
        return f"Телефон {old_phone} не знайдено"

    def show_phones(self):
        return ', '.join(phone.value for phone in self.phones)

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def show_birthday(self):
        if self.birthday:
            return self.birthday.value
        return "День народження не встановлено"

    def get_days_to_birthday(self):
        if self.birthday:
            today = datetime.now().date()
            birthday_this_year = datetime.strptime(self.birthday.value, "%d.%m.%Y").replace(year=today.year).date()
            if birthday_this_year < today:
                birthday_this_year = birthday_this_year.replace(year=today.year + 1)
            return (birthday_this_year - today).days
        return None

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self):
        today = datetime.now().date()
        upcoming_birthdays = []
        for record in self.data.values():
            days_to_birthday = record.get_days_to_birthday()
            if days_to_birthday is not None and 0 <= days_to_birthday <= 7:
                birthday_date = today + timedelta(days=days_to_birthday)
                if birthday_date.weekday() >= 5:  # якщо субота або неділя
                    birthday_date += timedelta(days=(7 - birthday_date.weekday()))  # перенос на понеділок
                upcoming_birthdays.append({"name": record.name.value, "birthday": birthday_date.strftime("%d.%m.%Y")})
        return upcoming_birthdays

# Функции-обработчики команд
@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_phone(args, book: AddressBook):
    name, old_phone, new_phone = args
    record = book.find(name)
    if record:
        return record.edit_phone(old_phone, new_phone)
    return f"Контакт {name} не знайдено"

@input_error
def show_phone(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record:
        return f"Телефони {name}: {record.show_phones()}"
    return f"Контакт {name} не знайдено"

@input_error
def show_all(book: AddressBook):
    if not book.data:
        return "Адресна книга порожня."
    return "\n".join([f"{name}: {record.show_phones()}" for name, record in book.data.items()])

@input_error
def add_birthday(args, book: AddressBook):
    name, birthday = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return f"День народження для {name} встановлено: {birthday}"
    return f"Контакт {name} не знайдено"

@input_error
def show_birthday(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record:
        return f"День народження {name}: {record.show_birthday()}"
    return f"Контакт {name} не знайдено"

@input_error
def birthdays(book: AddressBook):
    upcoming_birthdays = book.get_upcoming_birthdays()
    if upcoming_birthdays:
        return "\n".join([f"{item['name']} - {item['birthday']}" for item in upcoming_birthdays])
    return "Немає днів народження на наступному тижні"

# Вспомогательная функция для парсинга ввода
def parse_input(user_input):
    return user_input.split()


def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()





# Основная функция
def main():
    # book = AddressBook()
    book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            save_data(book)
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_phone(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            print(show_all(book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(book))

        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
