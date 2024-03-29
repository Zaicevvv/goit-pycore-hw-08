import pickle
from collections import UserDict
from datetime import datetime, timedelta

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[str(record.name)] = record

    def find(self, name):
        if name in self.data:
            return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self):
        upcoming_birthdays = []
        today = datetime.today().date()
        days = 7

        for obj in self.data:
            user = self.find(obj)
            birthday_this_year = user.birthday.value.date()\
                .replace(year = today.year)
            if birthday_this_year < today:
                birthday_this_year = birthday_this_year.replace(year = today.year + 1)
            if 0 <= (birthday_this_year - today).days <= days:
                if birthday_this_year.weekday() >= 5:
                    birthday_this_year = birthday_this_year + timedelta(days = 1) \
                        if birthday_this_year.weekday() == 6 \
                        else birthday_this_year + timedelta(days = 2)
                upcoming_birthdays.append({
                    "name": user.name.value, 
                    "congratulation_date": birthday_this_year.strftime('%d.%m.%Y')
                })

        if upcoming_birthdays:
            for congratulation in upcoming_birthdays:
                print(f'{congratulation['name']}: {congratulation['congratulation_date']}')
        else:
            print('No upcoming birthdays found.')

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
	pass

class Phone(Field):
    def __init__(self, phone):
        if len(str(phone)) == 10 and all([i.isdigit() for i in str(phone)]):
            super().__init__(phone)
        else:
            raise ValueError("Phone number must be 10 digits. ")
        
class Birthday(Field):
    def __init__(self, value):
        try:
            super().__init__(datetime.strptime(value, '%d.%m.%Y'))
        except ValueError:
            raise ValueError("Invalid date format. Use <DD.MM.YYYY>. ")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def edit_phone(self, old, new):
        if self.phones:
            for i, phone in enumerate(self.phones):
                if phone.value == old:
                    self.phones[i] = Phone(new)
                    return
            raise ValueError("Phone number is not exist. ")
        else:
            raise ValueError("Phone number is not exist. ")

    def find_phone(self, to_find):
        if self.phones:
            for phone in self.phones:
                if phone.value == to_find:
                    return to_find
            raise ValueError("Phone number is not exist. ")
        else:
            raise ValueError("Phone number is not exist. ")

    def remove_phone(self, to_delete):
        if self.phones:
            for i, phone in enumerate(self.phones):
                if phone.value == to_delete:
                    self.phones.pop(i)
                    return
            raise ValueError("Phone number is not exist. ")
        else:
            raise ValueError("Phone number is not exist. ")

    def add_birthday(self, birthday):
        if self.birthday:
            raise ValueError('Birthday is already set. ')
        self.birthday = Birthday(birthday)

    def __str__(self):
        return f"Contact name: {self.name.value}, "\
               f"phones: {'; '.join(str(p.value) for p in self.phones)}, "\
               f"birthday: {self.birthday.value.strftime('%d.%m.%Y') if self.birthday else ''}"

def input_error(func):
    msg = "Use format: <command> <name> <value>[ <other value>]. "
    def inner(*args):
        try:
            return func(*args)
        except ValueError as e:
            if str(e) == 'Phone number must be 10 digits. ' or \
               str(e) == "Invalid date format. Use <DD.MM.YYYY>. " or \
               str(e) == "Phone number is not exist. " or \
               str(e) == 'Birthday is already set. ':
                nonlocal msg
                msg = str(e)
            return msg + \
                   "Enter 'list' to see all commands and their format."
        except KeyError:
            return f"Contact '{args[0][0]}' doesn't exists. To add it "\
                    "use command 'add'. Enter 'list' to see all commands and their format."
        except IndexError:
            return "Not enough arguments. "\
                   "Enter 'list' to see all commands and their format."

    return inner

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

@input_error
def add_contact(args, book):
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
def change_contact(args, book):
    name, old, new = args
    record = book.find(name)
    if not record:
        raise KeyError
    record.edit_phone(old, new)
    return "Contact changed."

@input_error 
def show_phone(args, book):
    name, = args
    record = book.find(name)
    if not record:
        raise KeyError
    return record

@input_error
def add_birthday(args, book):
    name, birthday = args
    record = book.find(name)
    if not record:
        raise KeyError
    record.add_birthday(birthday)
    return "Birthday added."

@input_error
def show_birthday(args, book):
    name, = args
    record = book.find(name)
    if not record:
        raise KeyError
    return record

@input_error
def birthdays(book):
    if book.data.items():
        return book.get_upcoming_birthdays()
    else:
        return "No contacts."

def show_all(book):
    if book.data.items():
        for name, record in book.data.items():
            print(record)
    else:
        return "No contacts."

def show_all_comands():
    print('hello - Say Hello')
    print('add - add contact, add phone, format: add <name> <phone number: 10 digits>')
    print('change - change contact, format: change <name> <old phone number: 10 digits> <new phone number: 10 digits>')
    print('phone - show contacts phone number(s), format: phone <name>')
    print('all - show all contacts with details, format: all')
    print('add-birthday - add birthday to contact, format: add-birthday <name> <DD.MM.YYYY>')
    print('show-birthday - show contacts birthday, format: show-birthday <name>')
    print('birthdays - show upcoming birthdays, format: birthdays')

def main():
    book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book)
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            show_all(book)
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            birthdays(book)
        elif command == "list":
            print(show_all_comands())
        else:
            print("Invalid command. "\
                  "Enter 'list' to see all commands and their format.")

if __name__ == "__main__":
    main()