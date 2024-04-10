from django.shortcuts import render
from django.http import JsonResponse, request
from .models import (Account)
from django.shortcuts import render
from .models import Account

#def add_account_data():
#     # Sample data
#     accounts_data = [
#         {'owner': 'John Doe', 'pin': '1234', 'balance': 5000, 'movements': [200, -450, -400, 3000, -650, -130, 70, 1300]},
#         {'owner': 'Alice Smith', 'pin': '5678', 'balance': 7000, 'movements': [1000, -800, 600, -300, 1200]},
#         {'owner': 'Bob Johnson', 'pin': '9012', 'balance': 3000, 'movements': [400, -200, 1000, -500]}
#     ]
    
#     # Loop through the sample data and create Account instances
#     for account_data in accounts_data:
#         account = Account(
#             owner=account_data['owner'],
#             pin=account_data['pin'],
#             balance=account_data['balance'],
#             movements=account_data['movements']
#         )
#         account.save() 

def single_page_functionality(request):
    
    if request.method == 'GET':
        # Render the index.html template
        return render(request, 'index.html')

    elif request.method == 'POST':
        action = request.POST.get('action')

        if action == 'login':
            # Handle login action
            username = request.POST.get('username')
            pin = request.POST.get('pin')

            try:
                account = Account.objects.filter(owner=username, pin=pin).first()
            except Account.DoesNotExist:
                return render(request, 'index.html', {'error': 'Invalid credentials'})

            # Construct user data dictionary
            user_data = {
                'name': account.owner,
                'balance': account.balance,
                'movements': account.movements,  # Convert movements to list if needed
            }

            total_incomes = sum(mov for mov in account.movements if mov > 0)
            total_outgoing = sum(-mov for mov in account.movements if mov < 0)
            interest_earned = total_incomes - total_outgoing

            user_data['total_incomes'] = total_incomes
            user_data['total_outgoing'] = total_outgoing
            user_data['interest_earned'] = interest_earned

            return render(request, 'index.html', {'user_data': user_data})

        elif action == 'transfer':
            # Handle transfer action
            recipient = request.POST.get('recipient')
            amount = int(request.POST.get('amount'))
            sender_username = request.POST.get('username')

            try:
                sender_account = Account.objects.get(owner=sender_username)
                receiver_account = Account.objects.get(owner=recipient)
            except Account.DoesNotExist:
                return render(request, 'index.html', {'error': 'Sender or receiver account not found'})

            if amount <= 0:
                return render(request, 'index.html', {'error': 'Invalid transfer amount'})

            if sender_account.balance < amount:
                return render(request, 'index.html', {'error': 'Insufficient balance for transfer'})

            sender_movements = sender_account.movements
            receiver_movements = receiver_account.movements

            sender_movements.append(-amount)
            receiver_movements.append(amount)
            sender_account.balance -= amount
            receiver_account.balance += amount

            # Save the changes to the database
            sender_account.save()
            receiver_account.save()

            user_data = {
                'name': sender_account.owner,
                'balance': sender_account.balance,
                'movements': sender_movements
            }
            return render(request, 'index.html', {'user_data': user_data})

        elif action == 'loan':
            # Handle loan action
            username = request.POST.get('username')
            amount = int(request.POST.get('loan_amount'))

            try:
                account = Account.objects.get(owner=username)
            except Account.DoesNotExist:
                return render(request, 'index.html', {'error': 'Account not found'})

            if amount <= 0:
                return render(request, 'index.html', {'error': 'Invalid loan amount'})

            if any(mov >= amount * 0.1 for mov in account.movements):
                account.movements.append(amount)
                account.balance += amount
                account.save()

                user_data = {
                    'name': account.owner,
                    'balance': account.balance,
                    'movements': account.movements
                }
                return render(request, 'index.html', {'user_data': user_data})
            else:
                return render(request, 'index.html', {'error': 'Insufficient history for loan'})

        elif action == 'close_account':
            # Handle close account action
            username = request.POST.get('username')
            pin = request.POST.get('pin')

            try:
                account = Account.objects.get(owner=username, pin=pin)
                account.delete()
                request.session.clear()
                return render(request, 'index.html')
            except Account.DoesNotExist:
                return render(request, 'index.html', {'error': 'Invalid username or PIN'})

        elif action == 'sort_movements':
            # Handle sort movements action
            username = request.POST.get('username')

            try:
                account = Account.objects.get(owner=username)
                account.movements.sort(reverse=True)
                user_data = {
                    'name': account.owner,
                    'balance': account.balance,
                    'movements': account.movements
                }
                return render(request, 'index.html', {'user_data': user_data})
            except Account.DoesNotExist:
                return render(request, 'index.html', {'error': 'Account not found'})

    # Default response
    return render(request, 'index.html', {'error': 'Invalid request'})
