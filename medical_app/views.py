from django.shortcuts import render, redirect
from .models import Medical_Product, Medical_Favourite, Medical_Cart, Medical_Category, Medical_Address
from .models import OrderItem, Madical_Order
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout 
from django.contrib.auth. decorators import login_required
from .templatetags.helper import get_favourites_count
from django.shortcuts import render, get_object_or_404
import random
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

#setting a razorpay client globally
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

# Create your views here.

def home_func(request):
    search = request.GET.get('search', '')
    category = request.GET.get('category', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')

    popular = request.GET.get('popular')
    new = request.GET.get('new')
    show_categories = request.GET.get('categories')

    products = Medical_Product.objects.filter(
        product_is_active=True
    )

    categories = Medical_Category.objects.all()

    # Search
    if search:
        products = products.filter(
            product_name__icontains=search
        )

    # Category
    if category:
        products = products.filter(
            product_category__category_slug=category
        )

    # Price
    if min_price:
        products = products.filter(
            product_price__gte=min_price
        )

    if max_price:
        products = products.filter(
            product_price__lte=max_price
        )

    # Popular Items
    if popular:
        products = products.filter(
            product_is_featured=True
        )

    # New Arrivals
    elif new:
        products = products.order_by(
            '-product_created_at'
        )

    context = {
        'products': products,
        'categories': categories,
        'search': search,
        'selected_category': category,
        'min_price': min_price,
        'max_price': max_price,
        'popular': popular,
        'new': new,
        'show_categories': show_categories,
    }

    return render(request, 'index.html', context)


def contact_func(request):
    return render(request,"contact.html")


def get_product_detail_view(request , pslug):
    product = Medical_Product.objects.filter(product_slug = pslug).first()
    
    context ={
        'product' : product
    }
    return render(request ,'specific_product.html', context) 


def add_to_favourites(request, userid, pid):
    if not User.objects.filter(id = userid).first():
        messages.error(request,"No User found with these user id")
        return redirect('home')
    
    if not Medical_Product.objects.filter(id = pid).first():
        messages.error(request,"No Product found with these user id")
        return redirect('home')
    
    Medical_Favourite.objects.create(
        user = User.objects.filter(id = userid).first(),
        product = Medical_Product.objects.filter(id = pid).first()
    )
    
    messages.success(request,"Product Added To Your Favourites")
    return redirect("home")

def favourites(request):
    user = request.user
    print(get_favourites_count(user.id))
    items = Medical_Favourite.objects.filter(user = user)
    context = {
        'items': items
            
    }
    return render(request, "favourites.html",context)

def remove_from_favourites(request, userid, pid):
    if not Medical_Favourite.objects.filter(user = userid).first():
        messages.error(request,"No User found with these user id")
        return redirect('home')
        
    if not Medical_Favourite.objects.filter(product = pid).first():
        messages.error(request,"No Product found with these user id")
        return redirect('home')
    
    favourites_obj = Medical_Favourite.objects.filter(user = userid, product = pid).first()
    favourites_obj.delete()
    
    messages.success(request,"Product Remove from Your Favourites")
    return redirect("favourites")
    
    
def get_cart_items(request):
    user = request.user
    items = Medical_Cart.objects.filter(user=user)
    context = {
        "items": items
    }
    return render(request,"carts.html", context)


def delete_item_from_cart(request, pid):
    user = request.user
    product = Medical_Product.objects.filter(id=pid).first()
    if not product:
        messages.error(request,"Product Not Found")
        return redirect('cart')
    
    cart_item = Medical_Cart.objects.filter(user=user, product=product).first()
    cart_item.delete()
    messages.success(request,"Product Remove from Your Cart")
    return redirect('cart')

def update_cart_item(request):
    user = request.user
    if request.method == "POST":
        product = request.POST['product']   
        quantity = request.POST['quantity']
        
        product = Medical_Product.objects.filter(id=product).first()
        cart_item = Medical_Cart.objects.filter(user=user, product=product).first()
        cart_item.quantity = quantity
        cart_item.save()
        
        messages.success(request,"Cart Item updated Successfully !")
        return redirect('cart')
    


def add_items_to_cart(request):
    if request.method == "POST":
        product = request.POST['product']
        quantity = request.POST['quantity']
        
        product = Medical_Product.objects.filter(id=product).first()
        Medical_Cart.objects.create(
            user = request.user,
            product = product,
            quantity = quantity
        )
        messages.success(request,"Product Added to Cart Successfully !")
        return redirect('cart')
    
    
def manage_address(request):

    addresses = Medical_Address.objects.filter(user=request.user).order_by('-is_default', '-created_at')

    context = {
        'addresses': addresses
    }

    return render(request, "manage_address.html", context)



def add_address(request):

    if request.method == "POST":

        Medical_Address.objects.create(
            user=request.user,
            name=request.POST.get('name'),
            mobile=request.POST.get('mobile'),
            email=request.POST.get('email'),
            address=request.POST.get('address'),
            city=request.POST.get('city'),
            state=request.POST.get('state'),
            pincode=request.POST.get('pincode'),
            landmark=request.POST.get('landmark'),
            address_type=request.POST.get('address_type'),
        )

        messages.success(
            request,
            "Address added successfully!"
        )

        return redirect('manage_address')

    return render(request, "add_address.html")



def edit_address(request, address_id):

    address = get_object_or_404(
        Medical_Address,
        id=address_id,
        user=request.user
    )

    if request.method == "POST":

        address.name = request.POST.get('name')
        address.mobile = request.POST.get('mobile')
        address.email = request.POST.get('email')
        address.address = request.POST.get('address')
        address.city = request.POST.get('city')
        address.state = request.POST.get('state')
        address.pincode = request.POST.get('pincode')
        address.landmark = request.POST.get('landmark')
        address.address_type = request.POST.get('address_type')

        address.save()

        messages.success(
            request,
            "Address updated successfully!"
        )

        return redirect('manage_address')

    context = {
        'address': address
    }

    return render(request,"edit_address.html",context)


def delete_address(request, address_id):

    address = get_object_or_404(
        Medical_Address,
        id=address_id,
        user=request.user
    )

    address.delete()

    messages.success(
        request,
        "Address deleted successfully!"
    )

    return redirect('manage_address')



def default_address(request, address_id):

    address = get_object_or_404(
        Medical_Address,
        id=address_id,
        user=request.user
    )

    # সব address থেকে default remove
    Medical_Address.objects.filter(
        user=request.user
    ).update(is_default=False)

    # এই address-টাকে default করা
    address.is_default = True
    address.save()

    messages.success(
        request,
        "Default address changed successfully!"
    )

    return redirect('manage_address')

''' Auth function here '''

def user_login(request):
    if request. method == "POST":
        username = request.POST ['username'] #Unique 
        password = request.POST ['password']
        
        
        if not User.objects.filter(username = username).first():
            messages. error (request, "User with this Username Not Exists!") 
            return redirect ('login')
        authenticated_user = authenticate(request, username = username, password = password)
        if authenticated_user:
            login (request, authenticated_user)
            return redirect ('home')
        else:
            messages. error (request, "Invalid Password !")
            return redirect('login')
        
    return render(request, "login.html")

def user_register(request):
    if request.method == "POST":
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email'] # Unique
        username = request.POST['username'] # Unique
        password = request.POST['password']
        
        if User.objects.filter (email = email).first():
            messages.error(request, "User with this Email Already Exists !")
            return redirect('register')
        
        if User.objects.filter(username = username).first():
            messages.error(request, "User with this Username Already Exists !")
            return redirect('register')
        
        user_obj = User.objects.create(
            first_name = first_name,
            last_name = last_name,
            email = email,
            username = username,
            password = make_password (password)
        )
        
        if user_obj:
            messages.success (request, "User created successfully!")
            return redirect('register')
        else:
            messages.error(request, "Server Error: User Not Create")
            return redirect('register')
        
    return render(request, "register.html")

def user_logout(request):
    logout(request)
    return redirect('login')

def checkout(request):
    total_amount = 0
    user = request.user
    cart_items = Medical_Cart.objects.filter(user = user)
    address = Medical_Address.objects.filter(user = user)
    
    for i in cart_items:
        total_amount += i.product.product_price * i.quantity
    
    context = {
        'cart_items':cart_items,
        'total_amount' : total_amount,
        'address' : address
    }
    return render(request, "checkout.html", context)


def process_order(request):
    user = request.user
    if request.method == "POST":
        if 'address' not in request.POST:
            messages.error(request, "Address not selected !")
            return redirect('checkout')
        
        if 'payment_mode' not in request.POST:
            messages.error(request, "Payment Method not selected !")
            return redirect('checkout')
                
        address_id = request.POST['address']
        payment_mode = request.POST['payment_mode']
        
        address = Medical_Address.objects.filter(id=address_id).first()
        cart_items = Medical_Cart.objects.filter(user = user)
        
        if not cart_items.exists():
            messages.error(request, "There are no Products inside your cart !")
            return redirect('checkout')
        
        total_amount = sum(items.product.product_price * items.quantity for items in cart_items )
        tracking_no = 'MED' + str(random.randint(11111, 99999))
        
        if payment_mode == 'cod':
            try:
                #creating new Order
                new_order = Madical_Order.objects.create(
                    user = user,
                    shipping_address = address,
                    total_amount = total_amount,
                    payment_mode = 'cod',
                    payment_status = 'Pending',
                    tracking_no = tracking_no,
                )
                
                #  Move data from cart items to Orderitems
                for items in cart_items:
                    OrderItem.objects.create(
                        order = new_order,
                        product = items.product,
                        quantity = items.quantity
                    )
                cart_items.delete()
                context = {
                    'orderid' : new_order.order_id,
                    'date' : new_order.created_at,
                    'total' : new_order.total_amount
                }
                return render(request, 'success.html', context)
            
            except Exception as e:
                messages.warning(request, "Order not Generate Due to : ", e)
                return redirect('checkout')
            
        elif payment_mode == 'upi':
            razorpay_amount = int(total_amount*100)
            razorpay_order = client.order.create({
                'amount' : razorpay_amount,
                'currency' : 'INR',
                'payment_capture' : 1
            })
            new_order = Madical_Order.objects.create(
                user = request.user,
                shipping_address = address,
                total_amount = total_amount,
                payment_mode = 'online',
                payment_status = 'completed',
                tracking_no = tracking_no,
                razorpay_order_id = razorpay_order['id']
            )
            
            for items in cart_items:
                OrderItem.objects.create(
                    order = new_order,
                    product = items.product,
                    quantity = items.quantity
                )
            cart_items.delete()
            
            context = {
                'order': new_order,
                'razorpay_order_id' : razorpay_order ['id'],
                'razorpay_key_id': settings.RAZORPAY_KEY_ID,
                'amount': razorpay_amount,
                'currency':'INR',
                'callback_url': request.build_absolute_uri('/payment-callback/')
            }
            return render(request, 'razorpay_checkout.html', context)
            
            
        else:
            pass
        
    return HttpResponse("Order Processed")

def user_orders(request):
    user = request.user
    orders = Madical_Order.objects.filter(user=user)
    context ={
        'orders' : orders
        
    }
    return render(request,"orders.html", context)

def get_order_items(request, orderid):
    order = Madical_Order.objects.filter(order_id = orderid).first()
    orderitems = OrderItem.objects.filter(order = order)
    
    context = {
        'orderitems' : orderitems,
        'orderid' : orderid
    }
    return render(request, 'orderitems.html', context)
    

def cancel_order(request, orderid):
    user = request.user
    order = Madical_Order.objects.filter(order_id=orderid).first()
    order.delete()
    messages.success(request,f"Order #{orderid} cancelled and deleted successfully.")
    return redirect('orders')



@csrf_exempt
def payment_callback(request):
    if request.method == "POST":
        razorpay_payment_id = request.POST.get('razorpay_payment_id', '')
        razorpay_order_id = request.POST.get('razorpay_order_id', '')
        razorpay_signature = request.POST.get('razorpay_signature', '')

        order = Madical_Order.objects.filter(razorpay_order_id=razorpay_order_id).first()
        if not order:
            messages.error(request, "Order not found.")
            return redirect('checkout')

        # Verify signature with Razorpay SDK
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }

        try:
            client.utility.verify_payment_signature(params_dict)

            # Signature matches - complete the order
            order.payment_status = 'completed'
            order.razorpay_payment_id = razorpay_payment_id
            order.razorpay_signeture = razorpay_signature
            order.save()

            # Empty user's cart
            Medical_Cart.objects.filter(user=order.user).delete()

            messages.success(request, f"Payment successful! Your order has been placed. {razorpay_signature}")
            return redirect('home')

        except razorpay.errors.SignatureVerificationError:
            order.payment_status = 'Failed'
            order.save()
            messages.error(request, "Payment verification failed. Please try again.")
            return redirect('checkout')


    return redirect('checkout')