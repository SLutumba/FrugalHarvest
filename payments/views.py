from django.shortcuts import render, redirect
from cart.cart import Cart
from payments.forms import ShippingForm, PaymentForm
from payments.models import ShippingAddress, Order, OrderItem
from django.contrib.auth.models import User
from django.contrib import messages
from store.models import Product
def payment_success(request):
    return render(request, 'payments/payment_success.html', {})

def checkout(request):
    cart = Cart(request)
    cart_products = cart.get_prods
    quantities = cart.get_quants
    totals = cart.cart_total()

    if request.user.is_authenticated:
        shippng_user = ShippingAddress.objects.get(user__id=request.user.id)
        shipping_form = ShippingForm(request.POST or None, instance=shippng_user)
        return render(request, "payments/checkout.html", {"cart_products":cart_products, "quantities":quantities, "totals": totals, 'shipping_form':shipping_form})
    else:
        shipping_form = ShippingForm(request.POST or None)
        return render(request, "payments/checkout.html", {"cart_products":cart_products, "quantities":quantities, "totals": totals, 'shipping_form':shipping_form })
    
def billing_info(request):
    if request.POST:
        cart = Cart(request)
        cart_products = cart.get_prods
        quantities = cart.get_quants
        totals = cart.cart_total()
        my_shipping = request.POST
        request.session['my_shipping'] = my_shipping
        if request.user.is_authenticated:
            billing_form = PaymentForm()
            return render(request, "payments/billing_info.html", {"cart_products":cart_products, "quantities":quantities, "totals": totals, 'shipping_info':request.POST, 'billing_form':billing_form})
        else:
            billing_form = PaymentForm()
            return render(request, "payments/billing_info.html", {"cart_products":cart_products, "quantities":quantities, "totals": totals, 'shipping_info':request.POST, 'billing_form':billing_form})
        
        shipping_form = request.POST
        return render(request, "payments/billing_info.html", {"cart_products":cart_products, "quantities":quantities, "totals": totals, 'shipping_form':shipping_form})
    else:
        messages.success(request, "Access Denied. You must be logged in and have a pending order")
        return redirect('home')
    
def process_order(request):
    if request.POST:
        cart = Cart(request)
        cart_products = cart.get_prods
        quantities = cart.get_quants
        totals = cart.cart_total()
        payment_form = PaymentForm(request.POST or None)
        my_shipping = request.session.get('my_shipping')
        
        
        full_name = my_shipping['shipping_full_name']
        email = my_shipping['shipping_email']
        
        
        shipping_address = f"{my_shipping['shipping_address1']}\n{my_shipping['shipping_address2']}\n{my_shipping['shipping_city']}\n{my_shipping['shipping_state']}\n{my_shipping['shipping_zipcode']}\n{my_shipping['shipping_country']}\n"
        amount_paid = totals
        if request.user.is_authenticated:
            user = request.user
            create_order = Order(user=user, full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid)
            create_order.save()
            order_id = create_order.pk
            for product in cart_products():
                product_id = product.id
                price = product.price
                for key,value in quantities().items():
                    if int(key) == product_id:
                        create_order_item = OrderItem(order_id=order_id, product_id=product_id, user=user, quantity=value, price=price)
                        create_order_item.save()

            for key in list(request.session.keys()):
                if key == 'session_key':
                    del request.session[key]

            messages.success(request, "Order Placed!")
            return redirect('home')
        else:
            create_order = Order(user=user, full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid)
            create_order.save()

            order_id = create_order.pk
            for product in cart_products():
                product_id = product.id
                price = product.price
                for key,value in quantities().items():
                    if int(key) == product_id:
                        create_order_item = OrderItem(order_id=order_id, product_id=product_id, quantity=value, price=price)
                        create_order_item.save()
            for key in list(request.session.keys()):
                if key == 'session_key':
                    del request.session[key]
            messages.success(request, "Order Placed!")
            return redirect('home')
    else:
        messages.success(request, "Access Denied. You must be logged in and have a pending order")
        return redirect('home')
    
def shipped_dash(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped=True)
        return render(request, "payments/shipped_dash.html", {'orders':orders})
    else:
        messages.success(request, "Access Denied")
        return redirect('home')
def not_shipped_dash(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped=False)
        return render(request, "payments/not_shipped_dash.html", {'orders':orders})
    else:
        messages.success(request, "Access Denied")
        return redirect('home')