from django.http import HttpResponse
from django.shortcuts import render,redirect
from . forms import *
from django.contrib import messages
from essential.models import *
from django.utils import timezone
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
import razorpay


razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_ID,settings.RAZORPAY_SECRET))


# Create your views here.
def index(request):
    products = Product.objects.all()
    
    context = {
        'products':products
    }
    return render(request,'essential/index.html',context)



def orderlist(request):
    if Order.objects.filter(user=request.user,ordered=False).exists():
        order = Order.objects.get(user=request.user,ordered=False)
        context = {
            'order':order
        }
        return render(request,'accounts/orderlist.html',context)
    else:
        messages.error(request,'Your cart is empty')
        return redirect('add_to_cart')


def addProduct(request):
    if request.method == 'POST':
        form = ProductForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request,'Product added successfully')
            return redirect('/')
        else:
            messages.error(request,'Product not added')
    
    else:
        form = ProductForm()
        
        
    context = {
        'form':form,
        
         }
    return render(request,'essential/add_product.html',context)


def productDesc(request,pk):
    product = Product.objects.get(id=pk)
    context = {
        'product':product,
    }
    return render(request,'essential/product_desc.html',context)



def add_to_cart(request,pk):
    product = Product.objects.get(id=pk)
    
    #create order item
    order_item, created = orderItem.objects.get_or_create(
        product = product,
        user = request.user,
        ordered = False,
    )
    
    #Get queryset of order object of particular user
    order_qs = Order.objects.filter(user=request.user,ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(product__pk=pk).exists():
            order_item.quantity +=1
            order_item.save()
            messages.success(request,'Added Quantity Item')
            return redirect('index')
        
        
        else:
            order.items.add(order_item)
            messages.success(request,'Item Added to Cart')
            return redirect('index')
        
    else:
        ordered_date = timezone.now() 
        order = Order.objects.create(user=request.user,ordered_date=ordered_date)  
        order.items.add(order_item) 
        messages.success(request,'Item Added to Cart')
        return redirect('product_desc',pk=pk)
        
        
        
def add_item(request,pk):
    product = Product.objects.get(id=pk)
    
    #create order item
    order_item, created = orderItem.objects.get_or_create(
        product = product,
        user = request.user,
        ordered = False,
    )
    
    #Get queryset of order object of particular user
    order_qs = Order.objects.filter(user=request.user,ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(product__pk=pk).exists():
            
            if order_item.quantity < product.product_available_count:   
              order_item.quantity +=1
              order_item.save()
              messages.success(request,'Added Quantity Item')
              return redirect('orderlist')
          
            else:
                messages.error(request,'Sorry product is Out Of Stock')
                return redirect('orderlist')
        
        
        else:
            order.items.add(order_item)
            messages.success(request,'Item Added to Cart')
            return redirect('product_desc',pk=pk)
        
    else:
        ordered_date = timezone.now() 
        order = Order.objects.create(user=request.user,ordered_date=ordered_date)  
        order.items.add(order_item) 
        messages.success(request,'Item Added to Cart')
        return redirect('product_desc',pk=pk)
    
    
    
def remove_item(request,pk):
    item = get_object_or_404(Product,pk=pk)
    order_qs = Order.objects.filter(
        user = request.user,
        ordered = False,
    )  
    if order_qs.exists():
        order = order_qs[0] 
        if order.items.filter(product__pk=pk).exists():
            order_item = orderItem.objects.filter(
                product = item,
                user = request.user,
                ordered = False,
            )[0]
            
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
                
            else:
                order_item.delete()
            messages.success(request,'Item Quantity updated') 
            return redirect('orderlist')
        
        else:
            messages.error(request,'This item is not in your cart')
            return redirect('orderlist')
        
    else:
        messages.error(request,'You do not have any order')
        return redirect('orderlist')
    
    
def checkout_page(request):
    if CheckoutAddress.objects.filter(user=request.user).exists():
        
        context = {
            'payment_allow':"allow",
        }  
        
        return render(request,'essential/checkout.html',context)  
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        
        if form.is_valid():
            
            street_address = form.cleaned_data.get('street_address')
            apartment_address = form.cleaned_data.get('apartment_address') 
            country = form.cleaned_data.get('country')
            zip_code = form.cleaned_data.get('zip_code')
                
            checkout_address = CheckoutAddress(
                
                user = request.user,
                street_address = street_address,
                apartment_address = apartment_address,
                country = country,
                zip_code = zip_code, 
                
                
                )
                
            checkout_address.save()
            print('It should render the summary page')
            
            context = {
                'payment_allow':"allow",
                }
            return render(request,'essential/checkout.html',context)
            
       
               
    else:
        form = CheckoutForm()  
        context = {
            'form':form,
        }  
        return render(request,'essential/checkout.html',context)  
    
    
def payment(request):
    try:
        order = Order.objects.get(user=request.user,ordered=False) 
        address = CheckoutAddress.objects.get(user=request.user)     
        order_amount = order.get_total_price()   
        order_currency = "INR" 
        order_receipt = order.order_id
        notes = {
            "street_address":address.street_address,
            "apartment_address":address.apartment_address,
            "country":address.country.name,
            "zip":address.zip_code,
        }
        
        razorpay_order = razorpay_client.order.create(
            dict(
                amount = order_amount * 100,
                currency = order_currency,
                receipt = order_receipt,
                notes = notes,
                payment_capture = "0", 
            )
        )
        print(razorpay_order["id"])
        order.razorpay_order_id = razorpay_order["id"]
        order.save()
        print("It should be render the Summary Page2") #check
        return render(request,
            "essential/paymentrazorpay.html",
            {
                "order":order,
                "order_id":razorpay_order["id"],
                "orderId":order.order_id,
                "final_price":order_amount,
                "razorpay_merchant_id":settings.RAZORPAY_ID,
            },
        )
        
        
    except Order.DoesNotExist:
        print("Order Not Found")
        return HttpResponse("404 Error")
    
    
@csrf_exempt
def handlerequest(request):
    if request.method == "POST": #check
        try:
            payment_id = request.POST.get("razorpay_payment_id","")
            order_id = request.POST.get("razorpay_order_id","")
            signature = request.POST.get("razorpay_signature","")
            print(payment_id,order_id,signature)
            params_dict = {
                "razorpay_order_id" : order_id,
                "razorpay_payment_id" : payment_id,
                "razorpay_signature" : signature,
            }
            try:
                order_db = Order.objects.get(razorpay_order_id=order_id)
                print("Order found")
            except:
                print("Order Not Found")
                return HttpResponse("505 Not Found")
            
            order_db.razorpay_payment_id = payment_id
            order_db.razorpay_signature = signature
            order_db.save()
            print("Working........") #check
            result = razorpay_client.utility.verify_payment_signature(params_dict)
            if result is not None:
                print("Working Final Fine.........")
                amount = order_db.get_total_price()
                amount = amount * 100          #we have to pass into paisa
                payment_status = razorpay_client.payment.capture(payment_id,amount)
                
                if payment_status is not None:
                    print(payment_status)
                    order_db.ordered = True
                    order_db.save()
                    print("payment success")
                    checkout_address = CheckoutAddress.objects.get(user=request.user)
                    request.session[
                        "order_complete"
                    ] = "Your Order is Successfully Place, You will receive your order within 5-10 days"
                    return render(request,'invoice/invoice.html',{"order":order_db,"payment_status":payment_status,"checkout_address":checkout_address})
                else:
                    print("Payment Failed")
                    order_db.ordered = False
                    order_db.save()
                    request.session[
                        "order_failed"
                    ] = "Unfortunately your order could not be placed,try again!"
                    return redirect("/")
                
            else:
                order_db.ordered = False
                order_db.save()
                return render(request,"essential/paymentfailed.html")
            
        except:
            print("something occured")
            return HttpResponse('Error Occured')    
        
        
def invoice(request):
    
    return render(request,"invoice/invoice.html")   


def updateProduct(request,pk):
    product = Product.objects.get(id=pk)
    
    product_form = ProductForm(instance=product)
    
    if request.method == 'POST':
        product_form=ProductForm(request.POST,request.FILES,instance=product)
    
    if product_form.is_valid() :
        product_form.save()
        messages.success(request,'product updated successfully')
    
        return redirect('/')
    else:
        messages.error(request,'some error occured')
  
    context = {
        'product_form':product_form,
    }
    return render(request,'essential/update-product.html',context)


def deleteProduct(request,pk):
    
    product = Product.objects.get(id=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request,'product deleted successfully')
    
        return redirect('/')
  
    context = {
        'product':product,
    }
  
    return render(request,'essential/delete-product.html',context)
    
    

    
    

    
    
    
                
        
            
            
    
    
            
            
        
        
        