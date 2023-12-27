import tkinter as tk
import json
import re
import smtplib
import os

from email.mime.text import MIMEText
from dotenv import load_dotenv
from datetime import datetime
from tkinter.font import Font
from tkinter.scrolledtext import ScrolledText
from tkinter import messagebox


load_dotenv()


class SplitWise(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)

        self.title('SplitWise')
        self.resizable(False, False)
        
        self.font = Font(
            family='MS Sans Serif',
            size=12
        )

        self.font_title = Font(
            family='MS Sans Serif',
            size=16,
            weight='bold'
        )

        self.include_var = tk.IntVar()

        self.login_frame = tk.Frame(master=self)

        self.email_input = tk.Entry(
            master=self.login_frame,
            width=25,
            background='#EEEEEF',
            font=self.font
        )

        self.password_input = tk.Entry(
            master=self.login_frame,
            width=25,
            background='#EEEEEF',
            show='●',
            font=self.font
        )

        self.show_password_var = tk.IntVar()

        self.home_frame = tk.Frame(master=self)
        self.records_frame = tk.Frame(master=self.home_frame)
        self.add_record_frame = tk.Frame(master=self.home_frame)
        self.settle_up_frame = tk.Frame(master=self.home_frame)


    def load_data(self):
        with open('data/data.json', 'r') as f:
            data = json.load(f)

        return data


    def load_credentials(self):
        with open('data/credentials.json', 'r') as f:
            credentials = json.load(f)

        return credentials


    def get_highest_tid(self, email, person, date):
        data = self.load_data()

        if email not in data:
            return 0

        if person not in data[email]:
            return 0

        else:
            try:
                transaction_ids = data[email][person][date].keys()

            except KeyError:
                return 0


            try:
                highest_key = int(list(transaction_ids)[-1])
                return highest_key

            except IndexError:
                return 0


    def show_password(self, text_box: tk.Entry):
        if self.show_password_var.get() == 0:
            text_box.config(show='●')

        else:
            text_box.config(show='')    
    

    def get_email_from_name(self, name):
        credentials = self.load_credentials()

        for email in credentials:
            if credentials[email]['name'] == name.lower():
                return email
            
        return None
        
    
    def get_name_from_email(self, email):
        credentials = self.load_credentials()

        if email in credentials:
            return credentials[email]['name']
        
        else:
            return None
     

    def login(self, email, password):
        credentials = self.load_credentials()

        email = email.lower()

        if email in credentials:
            if password == credentials[email]['password']:
                self.create_home_page(email)

            else:
                messagebox.showerror('Error', 'Incorrect email or password')
        
        else:
            messagebox.showerror('Error', "Couldn't find an account with those details")


    def logout(self):
        self.destroy()
        self.__init__()
        self.create_login_page()


    def check_email(self, email):
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'

        if re.fullmatch(regex, email):
            return True
        else:
            return False


    def signup(self, name, email, password):
        credentials = self.load_credentials()

        name = name.lower()
        email = email.lower()

        if name == "":
            messagebox.showerror('Error', 'Name cannot be empty')

        else:
            if email not in credentials:
                email_check = self.check_email(email)

                if email_check:
                    credentials[email] = {
                        'name': name,
                        'password': password
                    }

                    with open('data/credentials.json', 'w') as f:
                        json.dump(credentials, f, indent=2)

                    message = MIMEText('Account successfully created on SplitWise!! \n Enjoy the ease of tracking shared expenses.')
                    message['Subject'] = 'Sign Up Confirmation'
                    message['From'] = 'SplitWise Team'
                    message['To'] = email

                    try:
                        server = smtplib.SMTP(
                            host='smtp.office365.com',
                            port=587,
                        )
                        server.ehlo()
                        server.starttls()
                        server.login(
                            user=os.getenv('OUTLOOK_EMAIL'),
                            password=os.getenv('OUTLOOK_PASSWORD')
                        )
                        server.sendmail(
                            from_addr=os.getenv('OUTLOOK_EMAIL'),
                            to_addrs=email,
                            msg=message.as_string()
                        )
                        server.quit()

                    except smtplib.SMTPRecipientsRefused as e:
                        print('Receiver error')
                        print(e)

                    except smtplib.SMTPAuthenticationError as e:
                        print('Login error')
                        print(e)

                    except smtplib.SMTPSenderRefused as e:
                        print('Email settings error')
                        print(e)

                    except smtplib.SMTPServerDisconnected as e:
                        print('Server error')
                        print(e)

                    except Exception as e:
                        print(e)

                    self.create_home_page(email)

                else:
                    messagebox.showerror('Error', 'Invalid email')

            else:
                messagebox.showerror('Error', 'Account with that email already exists')


    def add_record(self, email, people: list, amount: int, reason, date):
        data = self.load_data()
        credentials = self.load_credentials()

        self_name = self.get_name_from_email(email)

        if self.include_var.get() == 1:
            people.append(self_name)

        split_between = len(people)
        amount = amount / split_between

        show_confirmation = True

        for person in people:
            person = person.lower()

            if person != self_name:
                if email not in data:
                    data[email] = {}

                if person not in data[email]:
                    data[email][person] = {}

                if date not in data[email][person]:
                    data[email][person][date] = {}

                transaction_id = self.get_highest_tid(email, person, date) + 1

                data[email][person][date][str(transaction_id)] = {
                    reason: amount
                }

                person_email = self.get_email_from_name(person)

                if person_email is None:
                    messagebox.showerror('Error', f'User not found with name "{person.capitalize()}"')
                    show_confirmation = False
                    break
                
                else:
                    transaction_id_person = self.get_highest_tid(person_email, self_name, date) + 1
                    
                    if person_email not in data:
                        data[person_email] = {}

                    if self_name not in data[person_email]:
                        data[person_email][self_name] = {}

                    if date not in data[person_email][self_name]:
                        data[person_email][self_name][date] = {}

                    data[person_email][self_name][date][transaction_id_person] = {
                        reason: amount * -1
                    }


        if show_confirmation:
            with open('data/data.json', 'w') as f:
                json.dump(data, f, indent=2)

            messagebox.showinfo('Success', 'Record added successfully')

            self.create_home_page(email)


    def settle_up(self, email, name, amount_head, amount_value):
        data = self.load_data()

        person_email = self.get_email_from_name(name.lower())
        self_name = self.get_name_from_email(email)
    
        amount = 0
        multiplier = 1

        for date in data[person_email][self_name]:
            for transaction_id in data[person_email][self_name][date]:
                for transaction in data[person_email][self_name][date][transaction_id]:
                    amount += data[person_email][self_name][date][transaction_id][transaction]

        date = datetime.now().strftime('%d.%m.%y')
        person_tid = self.get_highest_tid(person_email, self_name, date) + 1
        self_tid = self.get_highest_tid(email, name, date) + 1

        if amount > 0:
            data[email][name][date][self_tid] = {
                "Settle Up" : amount * multiplier
            }
            data[person_email][self_name][person_tid] = {
                'Settle Up': amount
            }
            amount_head.configure(text='Paying')

        elif amount == 0:
            messagebox.showerror('Hooray', 'You are already settled up')
        
        else:
            amount_head.configure(text='Receiving')
            multiplier = -1
            data[person_email][self_name][date][person_tid] = {
                "Settle Up" : amount * multiplier
            }
            data[email][name][date][self_tid] = {
                'Settle Up': amount
            }

        with open('data/data.json', 'w') as f:
            json.dump(data, f, indent=2)

        messagebox.showinfo('Hooray', f"You're settled up with {name.capitalize()}")

        self.create_home_page(email)


# BACKEND
##############################
# FRONTEND


    def create_login_page(self):
        title = tk.Label(
            master=self.login_frame,
            text='Login',
            font=self.font_title
        )
        title.grid(pady=10, row=0, column=1)

        name_label = tk.Label(
            master=self.login_frame,
            text='Name:',
            font=self.font
        )
        name_label.grid(row=1, column=0, padx=10, pady=10, sticky='w')

        name_input = tk.Entry(
            master=self.login_frame,
            width=25,
            background='#EEEEEF',
            font=self.font
        )
        name_input.grid(row=1, column=1, columnspan=10, padx=10, pady=10)

        email_label = tk.Label(
            master=self.login_frame,
            text='Email:',
            font=self.font
        )
        email_label.grid(padx=10, pady=10, row=2, column=0, sticky='w')

        self.email_input.grid(padx=10, pady=10, row=2, column=1, columnspan=10)

        password_label = tk.Label(
            master=self.login_frame,
            text='Password:',
            font=self.font
        )
        password_label.grid(padx=10, pady=10, row=3, column=0, sticky='w')

        self.password_input.grid(row=3, column=1, columnspan=10, padx=10, pady=10)

        show_pass = tk.Checkbutton(
            master=self.login_frame,
            text='Show password',
            variable=self.show_password_var,
            command=lambda: self.show_password(self.password_input)
        )
        show_pass.grid(row=4, column=1)

        login_button = tk.Button(
            master=self.login_frame,
            text='Login',
            command=lambda: self.login(self.email_input.get(), self.password_input.get())
        )
        login_button.grid(row=6, column=1, ipadx=10)

        signup_button = tk.Button(
            master=self.login_frame,
            text='Sign Up',
            command=lambda: self.signup(name_input.get(), self.email_input.get(), self.password_input.get())
        )
        signup_button.grid(pady=15, row=7, column=1, ipadx=10)

        self.login_frame.grid(row=0, column=0)


    def create_home_page(self, email):
        self.destroy()
        self.__init__()

        data = self.load_data()

        if email not in data:
            data[email] = {}

            with open('data/data.json', 'w') as f:
                json.dump(data, f, indent=2)

        menu = tk.Menu(self)

        account_menu = tk.Menu(menu)
        account_menu.add_command(label='Logout', command=self.logout)

        menu.add_cascade(label='Account', menu=account_menu)
        menu.add_cascade(label='Account', menu=account_menu)
        self.config(menu=menu)

        records = ScrolledText(
            master=self.records_frame,
            state='normal'
        )

        for person in data[email]:
            for date in data[email][person]:
                for _id in data[email][person][date]:
                    for transaction in data[email][person][date][_id]:
                      
                        transaction_record = data[email][person][date][_id]
                        
                        if transaction_record[transaction] < 0:
                            records.insert(
                                tk.END,
                                f"You borrowed {-1 * transaction_record[transaction]} from {person.capitalize()}.\nOn: {date}\nFor: {transaction}\n\n"
                            )

                        else:
                            records.insert(
                                tk.END,
                                f"{person.capitalize()} owes you {transaction_record[transaction]}.\nOn: {date}\nFor: {transaction}\n\n"
                            )
                        
        
        records.config(state='disabled')
        records.grid(row=0, column=0)

        add_button = tk.Button(
            master=self.records_frame,
            text='Add Record',
            font=self.font,
            command=lambda: self.create_add_record_page(email=email)
        )
        add_button.grid(row=1, column=0, pady=15, ipadx=10, ipady=5)

        settle_button = tk.Button(
            master=self.records_frame,
            text='Settle Record',
            font=self.font,
            command=lambda: self.create_settle_up_page(email=email)
        )
        settle_button.grid(row=2, column=0, pady=15, ipadx=10, ipady=5)


        self.home_frame.grid(row=0, column=0)
        self.records_frame.grid(row=0, column=0)


    def create_add_record_page(self, email):
        self.destroy()
        self.__init__()

        menu = tk.Menu(self)

        account_menu = tk.Menu(menu)
        account_menu.add_command(label='Logout', command=self.logout)

        app_menu = tk.Menu(menu)
        app_menu.add_command(label='Back', command=lambda: self.create_home_page(email))

        menu.add_cascade(
            label='Go To',
            menu=app_menu
        )
        menu.add_cascade(
            label='Account',
            menu=account_menu
        )
        self.config(menu=menu)

        head = tk.Label(
            master=self.add_record_frame,
            text='Add a Record',
            font=self.font_title
        )
        head.grid(row=0, column=1, pady=15)
        
        name_head = tk.Label(
            master=self.add_record_frame,
            text='Name:',
            font=self.font
        )
        name_head.grid(row=1, column=0, padx=10, pady=10, sticky='w')

        name_input = tk.Entry(
            master=self.add_record_frame,
            font=self.font
        )
        name_input.grid(row=1, column=1, columnspan=20, padx=10, pady=10)

        include_me = tk.Checkbutton(
            master=self.add_record_frame, text
            ='Include me',
            variable=self.include_var
        )
        include_me.grid(row=2, column=0, padx=10, pady=10)

        amount_head = tk.Label(
            master=self.add_record_frame,
            text='Amount:',
            font=self.font
        )
        amount_head.grid(row=3, column=0, padx=10, pady=10, sticky='w')

        amount_input = tk.Entry(
            master=self.add_record_frame,
            font=self.font
        )
        amount_input.grid(row=3, column=1, columnspan=20, padx=10, pady=10)

        for_head = tk.Label(
            master=self.add_record_frame,
            text='Reason:',
            font=self.font
        )
        for_head.grid(row=4, column=0, padx=10, pady=10, sticky='w')

        for_input = tk.Entry(
            master=self.add_record_frame,
            font=self.font
        )
        for_input.grid(row=4, column=1, columnspan=20, padx=10, pady=10)

        date = datetime.now().strftime('%d.%m.%y')

        borrowed_button = tk.Button(
            master=self.add_record_frame,
            text='Borrowed',
            command=lambda: self.add_record(email, name_input.get().split(' '), (-1*int(amount_input.get())), for_input.get(), date)
        )
        borrowed_button.grid(row=5, column=0, padx=10, pady=20)

        lent_button = tk.Button(
            master=self.add_record_frame,
            text='Lent',
            command=lambda: self.add_record(email, name_input.get().split(' '), (int(amount_input.get())), for_input.get(), date)
        )
        lent_button.grid(row=5, column=2, padx=10, pady=20, ipadx=5)

        self.home_frame.grid(row=0, column=0)
        self.add_record_frame.grid(row=0, column=0)


    def create_settle_up_page(self, email):
        self.destroy()
        self.__init__()

        menu = tk.Menu(self)

        account_menu = tk.Menu(menu)
        account_menu.add_command(label='Logout', command=self.logout)

        app_menu = tk.Menu(menu)
        app_menu.add_command(label='Back', command=lambda: self.create_home_page(email))

        menu.add_cascade(label='Go To', menu=app_menu)
        menu.add_cascade(label='Account', menu=account_menu)
        self.config(menu=menu)

        head = tk.Label(
            master=self.settle_up_frame,
            text='Settle Up',
            font=self.font_title
        )
        head.grid(row=0, column=1, pady=15)

        name_head = tk.Label(
            master=self.settle_up_frame,
            text='Name:',
            font=self.font
        )
        name_head.grid(row=1, column=0, padx=10, pady=10, sticky='w')

        name_input = tk.Entry(
            master=self.settle_up_frame,
            font=self.font
        )
        name_input.grid(row=1, column=1, columnspan=20, padx=10, pady=10)

        next_button = tk.Button(
            master=self.settle_up_frame,
            text='Next',
            command=lambda: self.update_settle_up_page(email, name_input.get(), next_button, name_input)
        )
        next_button.grid(row=3, column=3, padx=10, pady=20, sticky='e')

        self.home_frame.grid(row=0, column=0)
        self.settle_up_frame.grid(row=0, column=0)


    def update_settle_up_page(self, email, name, button: tk.Button, text_box: tk.Entry):
        name = name.lower()
        data = self.load_data()

        if name == "":
            messagebox.showerror('Error', 'Please enter a name')
        else:    
            person_email = self.get_email_from_name(name.lower())
            self_name = self.get_name_from_email(email)

            if name == self_name:
                messagebox.showerror('Error', 'You cannot settle up with yourself')
            
            elif person_email is None:
                messagebox.showerror('Error', 'User not found')

            amount_head = tk.Label(
                master=self.settle_up_frame,
                text='',
                font=self.font
            )
            amount_value = tk.Label(
                master=self.settle_up_frame,
                text='', font=self.font
            )
            
            if person_email not in data:
                amount_value.configure(text='0')

            elif self_name not in data[person_email]:
                amount_value.configure(text='0')

            else:
                amount = 0
                multiplier = 1

                for date in data[person_email][self_name]:
                    for transaction_id in data[person_email][self_name][date]:
                        for transaction in data[person_email][self_name][date][transaction_id]:
                            amount += data[person_email][self_name][date][transaction_id][transaction]
                
                if amount > 0:
                    amount_head.configure(text='Paying')

                if amount == 0:
                    messagebox.showerror('Hooray', 'You are already settled up')

                else:
                    amount_head.configure(text='Receiving')
                    multiplier = -1
                
                amount *= multiplier

                amount_value.configure(text=f'{amount}')

                amount_head.grid(row=2, column=0, padx=10, pady=10, sticky='e')
                amount_value.grid(row=2, column=1, columnspan=20, padx=10, pady=10, sticky='w')


            text_box.configure(state='disabled')
            button.configure(text='Settle Up', command=lambda: self.settle_up(email, name, amount_head, amount_value))


app = SplitWise()
app.create_login_page()
app.mainloop()